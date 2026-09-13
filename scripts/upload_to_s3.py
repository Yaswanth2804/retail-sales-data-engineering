import boto3
from pathlib import Path


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

BUCKET_NAME = "retail-sales-analytics-pipeline-2728"
S3_PREFIX = "raw"


# ---------------------------------------------------------
# Locate the latest generated batch
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "raw"

files = sorted(
    DATA_DIR.glob("retail_sales_*.csv"),
    key=lambda file: file.stat().st_mtime,
    reverse=True
)

if not files:
    raise FileNotFoundError(
        f"No retail batch files found in {DATA_DIR}"
    )

file_path = files[0]


# ---------------------------------------------------------
# Upload to S3
# ---------------------------------------------------------

s3 = boto3.client("s3")

s3_key = f"{S3_PREFIX}/{file_path.name}"

s3.upload_file(
    str(file_path),
    BUCKET_NAME,
    s3_key
)


# ---------------------------------------------------------
# Output
# ---------------------------------------------------------

print("Upload successful!")
print(f"Local file: {file_path}")
print(f"S3 location: s3://{BUCKET_NAME}/{s3_key}")