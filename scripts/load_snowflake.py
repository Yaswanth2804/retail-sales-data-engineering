import snowflake.connector
import yaml
from pathlib import Path

PROFILE_FILE = Path("/home/airflow/.dbt/profiles.yml")

DATABASE = "RETAIL_SALES_DB"
SCHEMA = "RAW"
STAGE = "RETAIL_SALES_STAGE"
TABLE = "RETAIL_SALES"

with open(PROFILE_FILE, "r") as file:
    profiles = yaml.safe_load(file)

profile_name = next(iter(profiles))
profile_config = profiles[profile_name]
target_name = profile_config["target"]
profile = profile_config["outputs"][target_name]

connection = snowflake.connector.connect(
    account=profile["account"],
    user=profile["user"],
    password=profile["password"],
    warehouse=profile["warehouse"],
    database=profile["database"],
    schema=profile["schema"],
    role=profile["role"],
)

cursor = connection.cursor()

try:
    cursor.execute(
        f"LIST @{DATABASE}.{SCHEMA}.{STAGE}"
    )

    files = cursor.fetchall()

    csv_files = [
        row[0]
        for row in files
        if row[0].lower().endswith(".csv")
    ]

    if not csv_files:
        raise FileNotFoundError(
            "No CSV files found in Snowflake stage."
        )

    latest_file = max(csv_files)
    filename = latest_file.split("/")[-1]

    print(f"Latest file detected: {filename}")

    cursor.execute(
        f"""
        COPY INTO {DATABASE}.{SCHEMA}.{TABLE}
        FROM @{DATABASE}.{SCHEMA}.{STAGE}
        FILES = ('{filename}')
        FILE_FORMAT = (
            TYPE = CSV
            SKIP_HEADER = 1
            FIELD_OPTIONALLY_ENCLOSED_BY = '"'
            NULL_IF = ('')
        )
        ON_ERROR = 'CONTINUE'
        """
    )

    results = cursor.fetchall()

    print("COPY INTO result:")

    for row in results:
        print(row)

    print("Snowflake RAW load completed successfully!")

finally:
    cursor.close()
    connection.close()