-- DDL (Data Definition Language)
CREATE TABLE public.LargeDataTable (
    ID INT IDENTITY(1,1) PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Age INT,
    Email VARCHAR(100)
);
