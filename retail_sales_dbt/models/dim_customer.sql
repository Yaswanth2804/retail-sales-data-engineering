{{ config(materialized='table') }}

SELECT
    CUSTOMER_ID,
    MAX(CITY) AS CITY
FROM {{ ref('stg_retail_sales') }}
GROUP BY CUSTOMER_ID
