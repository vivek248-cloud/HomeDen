import boto3
from botocore.client import Config

# Configs from your environment
AWS_ACCESS_KEY_ID = "03c4319a97af9e9668580bb7ee075a5e"
AWS_SECRET_ACCESS_KEY = "f4b502c4930a9b2d63fd02e5a6a259132b97488c71dbd65ff407f38324fe9c27"
AWS_STORAGE_BUCKET_NAME = "web"
AWS_S3_ENDPOINT_URL = "https://6f8ee577ee779928f03c50fd3fbd2988.r2.cloudflarestorage.com"

# Setup S3 client for Cloudflare R2
s3 = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    endpoint_url=AWS_S3_ENDPOINT_URL,
    config=Config(signature_version='s3v4'),
)

# Upload test file
file_path = "test_upload.txt"
key = "home_slider/test_upload.txt"

# Create test file
with open(file_path, "w") as f:
    f.write("Hello from R2 upload test!")

# Upload file
s3.upload_file(file_path, AWS_STORAGE_BUCKET_NAME, key, ExtraArgs={'ACL': 'public-read'})

print(f"Uploaded successfully: https://media.elitedreambuilders.in/{key}")
