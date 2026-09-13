{{ config(materialized='view') }}

WITH source_data AS (

    SELECT *
    FROM {{ source('retail_sales', 'retail_sales') }}

)

SELECT
    ORDER_ID,
    ORDER_DATE,
    CUSTOMER_ID,
    PRODUCT,
    CATEGORY,
    QUANTITY,
    UNIT_PRICE,
    CITY,
    PAYMENT_METHOD,
    TOTAL_AMOUNT
FROM source_data
