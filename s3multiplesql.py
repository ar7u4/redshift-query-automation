import json
import boto3
import os
import logging
import botocore
from datetime import datetime, timezone
import traceback
import time
import base64
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    message = 'Success'
    status_code = 200
    payload = ''

    try:
        message = exec_redshift(os.environ['secret_name'].strip(),
                                os.environ['region'].strip(),
                                os.environ['sql_bucket'].strip(),
                                os.environ['sql_prefix'].strip())
    except Exception as e:
        status_code = 400
        payload = traceback.format_exc()
        message = 'Failed'

    return {
        'statusCode': status_code,
        'message': message,
        'payload': json.loads(json.dumps(payload, default=str))
    }
    
def get_secret_pwd(secret_name: str, region_name: str):
    """
    Retrieve secret from AWS Secret manager
    """

    # Create a Secrets Manager client
    session = boto3.session.Session()

    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)

    except ClientError as e:
        get_secret_value_response = e
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            # An error occurred on the server side.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            # You provided an invalid value for a parameter.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            # You provided a parameter value that is not valid for the current state of the resource.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            # We can't find the resource that you asked for.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e

    secret = get_secret_value_response['SecretString']

    return json.loads(secret)

def read_sql(bucket: str, prefix: str):
    """
    Read SQL scripts from S3
    """
    client = boto3.client("s3")

    # List objects in the specified prefix
    response = client.list_objects_v2(Bucket=bucket, Prefix=prefix)

    # Filter only .sql files
    sql_files = [obj['Key'] for obj in response.get('Contents', []) if obj['Key'].lower().endswith('.sql')]

    # Read and concatenate SQL statements from each file
    sql_statements = ""
    for sql_file in sql_files:
        file_content = client.get_object(Bucket=bucket, Key=sql_file)['Body'].read().decode("utf8")
        sql_statements += file_content

    return sql_statements

def exec_redshift(secret_name: str, region_name: str, sql_bucket: str, sql_prefix: str):
    """
    Execute SQL commands in Redshift cluster
    """
    
    response = get_secret_pwd(secret_name, region_name)

    pwd = response['password']
    cluster_name = response['ClusterName']
    db_name = response['databaseName']
    db_user = response['username']

    sql_statements = read_sql(sql_bucket, sql_prefix)

    redshift_data_client = boto3.client("redshift-data")

    result = redshift_data_client.execute_statement(
        ClusterIdentifier=cluster_name,
        Database=db_name,
        DbUser=db_user,
        Sql=sql_statements
    )

    id = result['Id']
    statement = ''
    status = ''

    # We have to wait in loop for the SQL commands to finish executing
    while status != 'FINISHED' and status != 'FAILED' and status != 'ABORTED':
        statement = redshift_data_client.describe_statement(Id=id)
        status = statement['Status']
        time.sleep(2)

    status = statement['Status']

    if status == "FAILED":
        raise Exception(statement['Error'])

    return status
