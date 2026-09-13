{{ config(
    materialized='incremental',
    unique_key='ORDER_ID'
) }}

SELECT
    ORDER_ID,
    ORDER_DATE,
    CUSTOMER_ID,
    PRODUCT,
    QUANTITY,
    UNIT_PRICE,
    PAYMENT_METHOD,
    TOTAL_AMOUNT
FROM {{ ref('stg_retail_sales') }}

{% if is_incremental() %}

WHERE ORDER_ID > (
    SELECT MAX(ORDER_ID)
    FROM {{ this }}
)

{% endif %}