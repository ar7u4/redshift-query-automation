# Redshift Lambda Function to query SQL file - Automation
![s3red](https://github.com/ar7u4/redshift-query-automation/assets/109585047/1b6e854f-fb46-433d-b744-84a689e1dbe2)

## Overview

This repository contains a Lambda function written in Python that interacts with Amazon Redshift using the Redshift Data API. The Lambda function is designed to execute SQL queries stored in an Amazon S3 bucket on a Redshift cluster.

## Lambda Function

### datasqlapi.py

The main Lambda function is implemented in `datasqlapi.py`. It consists of the following key components:

- **`lambda_handler` Function:**
  - This function is the entry point for the Lambda execution.
  - It retrieves SQL queries from an S3 bucket and executes them on a Redshift cluster.

- **Helper Functions:**
  - `get_secret_pwd`: Retrieves credentials from AWS Secrets Manager.
  - `read_sql`: Reads SQL scripts from an S3 bucket.
  - `exec_redshift`: Executes SQL commands on a Redshift cluster.


## Environment Variables

The Lambda function relies on the following environment variables for configuration:

- `secret_name`: The name of the AWS Secrets Manager secret containing Redshift credentials.
 ![seceret_key-value](https://github.com/ar7u4/redshift-query-automation/assets/109585047/cb08236e-b4e4-42cb-8fc2-a4fc51e9d2c7)
    - `seceret-manager`: secret manager should have **secret value** 
       ```
        - username: Redshift user name
        - password: password generated while craeting redshift
        - ClusterName: name of the redshift cluster
        - databaseName: database name
      ```
- `region`: The AWS region where the Redshift cluster is located.
- `sql_bucket`: The name of the S3 bucket containing SQL scripts.
- `sql_prefix`: The prefix within the S3 bucket where SQL scripts are stored.

## Usage

1. **Clone the Repository:**
```bash
 git clone https://github.com/ar7u4/redshift-query-automation.git
 cd redshift-query-automation
```
   
2. **There are two files in repo:**
- `datasqlapi.py` (runs only one .sql file)
- `s3multiplesql.py` (runs all .sql file within S3 )

2. ## Set Environment Variables:
![s3-lambda-env](https://github.com/ar7u4/redshift-query-automation/assets/109585047/a963a6a2-2a3f-46f4-a5ee-a750fb3e75fa)
```bash   
  'secret_name'=your_secret_name  
  'region'=your_aws_region
  'sql_bucket'=your_s3_bucket
  'sql_prefix'=your_s3_prefix
```

3.  ## Deploy to Lambda:
- Package and deploy the Lambda function to AWS Lambda. The deployment process may vary based on your preferred deployment method.

4.  ## Invoke the Lambda Function:
- Create a Lambda Trigger for S3 events.
- Trigger the Lambda function to execute SQL queries on your Redshift cluster.
- Monitor the Lambda function's execution in the AWS Lambda console.

6. ## Create Pipeline: 
- Create a pipeline to sync AWS s3 location, so whenever there is change in Github pipeline will sync and trigger Lambda
- store AWS credentials in Pipeline as secrets (Here I have used Github actions)
