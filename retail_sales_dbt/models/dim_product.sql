{{ config(materialized='table') }}

SELECT
    PRODUCT,
    MAX(CATEGORY) AS CATEGORY,
    MAX(UNIT_PRICE) AS UNIT_PRICE
FROM {{ ref('stg_retail_sales') }}
GROUP BY PRODUCT