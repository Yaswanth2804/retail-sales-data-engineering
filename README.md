# Retail Sales Data Engineering Pipeline

An end-to-end retail sales data engineering pipeline built using Python, AWS S3, Snowflake, dbt, Docker, and Apache Airflow.

The pipeline generates retail sales data in batches, uploads the data to Amazon S3, loads new files into Snowflake, transforms the data using dbt, validates the transformed data, and orchestrates the complete workflow using Airflow.

## Architecture

```text
Python Data Generator
        |
        v
  Retail CSV Batch
        |
        v
     AWS S3
   Raw Data Layer
        |
        v
   Snowflake RAW
        |
        v
        dbt
        |
        +-------------------+
        |                   |
        v                   v
   Dimension Tables    FACT_SALES
                            |
                            v
                      SALES_DAILY
                            |
                            v
                     Analytics Layer

Apache Airflow
orchestrates the complete workflow
Technology Stack
Technology	Purpose
Python	Data generation and ingestion scripts
Pandas	Dataset creation and processing
NumPy	Synthetic data generation
AWS S3	Cloud object storage for raw files
Snowflake	Cloud data warehouse
dbt	Data transformation and data-quality testing
Apache Airflow	Pipeline orchestration
Docker	Containerized Airflow environment
PostgreSQL	Airflow metadata database
SQL	Data loading and analytics
Git	Version control
Pipeline Workflow

The Airflow DAG executes the following tasks:

generate_data
      |
      v
upload_to_s3
      |
      v
load_snowflake
      |
      v
dbt_run
      |
      v
dbt_test
1. Generate Data

Python generates a new retail sales batch containing 5,000 records.

The dataset contains:

Order ID
Order date
Customer ID
Product
Category
Quantity
Unit price
City
Payment method
Total amount

Each execution generates a new batch with unique order IDs and a timestamp-based filename.

Example:

retail_sales_20260913161039.csv
2. Upload to Amazon S3

The generated CSV is uploaded to:

s3://retail-sales-analytics-pipeline-2728/raw/

Each batch is stored as a separate object.

This allows the pipeline to process new files without repeatedly loading the same source file.

3. Load Data into Snowflake

Snowflake accesses the S3 bucket through an external stage and storage integration.

The setup uses:

AWS IAM Role
       |
       v
Snowflake Storage Integration
       |
       v
External Stage
       |
       v
Snowflake RAW table

Snowflake load history prevents an already processed file from being loaded again.

4. dbt Transformations

dbt transforms the Snowflake RAW table into analytics models.

Current models:

stg_retail_sales
        |
        +----------------+
        |                |
        v                v
 dim_customer       dim_product
        \                /
         \              /
          v            v
            fact_sales
                |
                v
           sales_daily
Data Models
stg_retail_sales

A staging model used to prepare source data for downstream transformations.

dim_customer

Customer-level dimension containing customer information such as customer ID and city.

dim_product

Product-level dimension containing product, category, and pricing information.

fact_sales

Incremental fact model containing sales transactions.

The model uses ORDER_ID as the unique key and processes newly arriving records based on the maximum existing order ID.

Conceptually:

WHERE ORDER_ID > (
    SELECT MAX(ORDER_ID)
    FROM {{ this }}
)
sales_daily

Daily sales aggregation containing:

Sales date
Total orders
Total units sold
Total revenue
Average order value
Incremental Processing

The pipeline is designed to process new data batches incrementally.

For example:

Batch 1
5,000 records
       |
       v
RAW
5,000

Batch 2
5,000 records
       |
       v
RAW
10,000

Batch 3
5,000 records
       |
       v
RAW
15,000

Additional records already present in the RAW table are not duplicated in the dbt incremental fact model.

The project was tested through multiple Airflow runs and currently processed:

RAW rows:       20,003
FACT_SALES rows: 20,003
Data Quality

The generated dataset intentionally contains missing payment methods to demonstrate data-quality validation.

dbt tests currently include 21 tests.

The latest full dbt test run completed successfully:

PASS=21
WARN=0
ERROR=0

Examples of validation areas include:

Required field validation
Unique order IDs
Accepted values
Referential relationships
Source data checks
Airflow

Airflow runs inside Docker.

Main services:

PostgreSQL
Airflow API Server
Airflow Scheduler
Airflow DAG Processor

The production DAG is:

retail_sales_pipeline

DAG location:

airflow/dags/retail_sales_pipeline.py

The DAG is currently manually triggerable and executes:

Generate data
      ↓
Upload to S3
      ↓
Load Snowflake RAW
      ↓
Run dbt
      ↓
Run dbt tests

A complete end-to-end DAG execution has been successfully tested multiple times.

Project Structure
Retail-Sales-Data-Engineering/
|
├── airflow/
│   ├── dags/
│   │   └── retail_sales_pipeline.py
│   ├── Dockerfile
│   └── docker-compose.yaml
|
├── data/
│   ├── raw/
│   └── processed/
|
├── retail_sales_dbt/
│   ├── dbt_project.yml
│   ├── models/
│   │   ├── staging/
│   │   ├── marts/
│   │   └── schema.yml
│   └── ...
|
├── scripts/
│   ├── generate_retail_data.py
│   ├── upload_to_s3.py
│   └── load_snowflake.py
|
├── sql/
│   └── ...
|
├── docs/
│   └── ...
|
├── .gitignore
└── README.md
AWS S3 Configuration

The pipeline uses Amazon S3 as the raw data landing zone.

The Snowflake integration uses an AWS IAM role instead of embedding AWS credentials inside the Snowflake stage configuration.

This provides a cleaner separation between:

AWS IAM
Snowflake Storage Integration
S3 External Stage
Snowflake Architecture

Database:

RETAIL_SALES_DB

Schemas:

RAW
ANALYTICS

Raw table:

RETAIL_SALES_DB.RAW.RETAIL_SALES

Analytics models:

RETAIL_SALES_DB.ANALYTICS.STG_RETAIL_SALES
RETAIL_SALES_DB.ANALYTICS.DIM_CUSTOMER
RETAIL_SALES_DB.ANALYTICS.DIM_PRODUCT
RETAIL_SALES_DB.ANALYTICS.FACT_SALES
RETAIL_SALES_DB.ANALYTICS.SALES_DAILY
Running the Pipeline

Start the Docker services:

docker compose up -d

Check the Airflow services:

docker compose ps

Open Airflow:

http://localhost:8080

Trigger the DAG:

docker compose exec airflow-scheduler airflow dags trigger retail_sales_pipeline

Check the DAG run:

docker compose exec airflow-scheduler airflow dags list-runs retail_sales_pipeline
Running dbt Manually

From inside the Airflow container:

docker compose exec airflow-scheduler bash -c "cd /opt/dbt/retail_sales_dbt && dbt run"

Run data-quality tests:

docker compose exec airflow-scheduler bash -c "cd /opt/dbt/retail_sales_dbt && dbt test"
Example Analytics

The sales_daily model supports analysis such as:

Daily revenue
Daily order volume
Units sold
Average order value
Product performance
Customer activity
Category-level sales

Example query:

SELECT
    SALES_DATE,
    TOTAL_ORDERS,
    TOTAL_UNITS_SOLD,
    TOTAL_REVENUE,
    AVERAGE_ORDER_VALUE
FROM RETAIL_SALES_DB.ANALYTICS.SALES_DAILY
ORDER BY SALES_DATE DESC;
Key Data Engineering Concepts Demonstrated

This project demonstrates:

Batch data ingestion
Cloud object storage
AWS IAM roles
Snowflake external stages
Snowflake storage integrations
RAW and analytics layers
Dimensional modeling
Incremental dbt models
dbt data-quality testing
Airflow orchestration
Docker containerization
Python-based data generation
SQL transformations
Idempotent file ingestion through Snowflake load history
Challenges Solved
Snowflake and AWS authentication

Configured a Snowflake storage integration with an AWS IAM role and external ID rather than using static AWS credentials for Snowflake access.

Airflow 3 execution API

Configured the Airflow scheduler to communicate with the Airflow execution API inside Docker.

Dockerized dbt

Built a custom Airflow Docker image with:

dbt-core 1.12.4
dbt-snowflake 1.12.0
Incremental processing

Designed timestamped source files and unique order IDs so new batches can be processed incrementally.

Duplicate file protection

Snowflake load history prevents the same staged file from being loaded multiple times.

Project Outcome

The final pipeline successfully performs:

Python
→ AWS S3
→ Snowflake RAW
→ dbt
→ Snowflake Analytics
→ dbt Tests

and is orchestrated end-to-end by Apache Airflow running inside Docker.

The pipeline has been executed successfully across multiple incremental batches, with the current Snowflake RAW and FACT tables each containing 20,003 records.

Future Improvements

Possible future enhancements include:

Scheduled daily Airflow execution
Cloud-based Airflow deployment
More granular data-quality rules
Slowly Changing Dimensions
Snowflake warehouse optimization
Data observability and alerting
CI/CD for dbt
GitHub Actions
Dashboard integration using Power BI or Tableau
Author

Yaswanth

Data Engineering Portfolio Project