import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

NUM_RECORDS = 5000

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "data" / "raw"


# ---------------------------------------------------------
# Generate a unique batch identifier
# ---------------------------------------------------------

batch_timestamp = datetime.now()

# Example:
# 20260913161530
batch_id = batch_timestamp.strftime("%Y%m%d%H%M%S")

# Create order IDs that are always greater than the old
# 100001-style IDs and unique for each generated batch.
order_id_start = int(batch_timestamp.strftime("%y%m%d%H%M%S")) * 1000

order_ids = range(
    order_id_start,
    order_id_start + NUM_RECORDS
)


# ---------------------------------------------------------
# Random generator
# ---------------------------------------------------------

rng = np.random.default_rng()


# ---------------------------------------------------------
# Reference data
# ---------------------------------------------------------

products = [
    "Laptop",
    "Smartphone",
    "Headphones",
    "Keyboard",
    "Mouse",
    "Monitor",
    "Tablet",
    "Smartwatch",
]

categories = {
    "Laptop": "Electronics",
    "Smartphone": "Electronics",
    "Headphones": "Accessories",
    "Keyboard": "Accessories",
    "Mouse": "Accessories",
    "Monitor": "Electronics",
    "Tablet": "Electronics",
    "Smartwatch": "Wearables",
}

cities = [
    "Chennai",
    "Bangalore",
    "Hyderabad",
    "Pune",
    "Mumbai",
    "Delhi",
    "Kolkata",
    "Coimbatore",
]

payment_methods = [
    "Credit Card",
    "Debit Card",
    "UPI",
    "Cash",
]

product_prices = {
    "Laptop": 65000,
    "Smartphone": 30000,
    "Headphones": 3000,
    "Keyboard": 1500,
    "Mouse": 800,
    "Monitor": 15000,
    "Tablet": 25000,
    "Smartwatch": 8000,
}


# ---------------------------------------------------------
# Generate sales data
# ---------------------------------------------------------

dates = pd.date_range(
    start=batch_timestamp - pd.Timedelta(days=30),
    end=batch_timestamp,
    periods=NUM_RECORDS,
)

product = rng.choice(products, NUM_RECORDS)

quantity = rng.integers(
    low=1,
    high=5,
    size=NUM_RECORDS
)

base_prices = np.array(
    [product_prices[p] for p in product]
)

unit_price = (
    base_prices * rng.uniform(
        0.90,
        1.10,
        NUM_RECORDS
    )
).round(2)


sales = pd.DataFrame(
    {
        "order_id": order_ids,
        "order_date": dates,
        "customer_id": rng.integers(
            1001,
            3001,
            NUM_RECORDS
        ),
        "product": product,
        "category": [
            categories[p]
            for p in product
        ],
        "quantity": quantity,
        "unit_price": unit_price,
        "city": rng.choice(
            cities,
            NUM_RECORDS
        ),
        "payment_method": rng.choice(
            payment_methods,
            NUM_RECORDS
        ),
    }
)


# ---------------------------------------------------------
# Calculate total amount
# ---------------------------------------------------------

sales["total_amount"] = (
    sales["quantity"]
    * sales["unit_price"]
).round(2)


# ---------------------------------------------------------
# Introduce controlled data-quality issues
# ---------------------------------------------------------

missing_count = min(
    10,
    NUM_RECORDS
)

missing_indices = rng.choice(
    sales.index,
    size=missing_count,
    replace=False
)

sales.loc[
    missing_indices,
    "payment_method"
] = None


# ---------------------------------------------------------
# Save batch file
# ---------------------------------------------------------

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

output_file = (
    OUTPUT_DIR
    / f"retail_sales_{batch_id}.csv"
)

sales.to_csv(
    output_file,
    index=False
)


# ---------------------------------------------------------
# Output information
# ---------------------------------------------------------

print("Dataset created successfully!")
print(f"Batch ID: {batch_id}")
print(f"Records: {len(sales)}")
print(f"First order ID: {sales['order_id'].min()}")
print(f"Last order ID: {sales['order_id'].max()}")
print(f"File: {output_file}")