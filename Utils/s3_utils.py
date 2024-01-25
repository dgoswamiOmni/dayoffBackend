import os
import boto3
from botocore.exceptions import NoCredentialsError

def upload_to_s3(bucket_name, file_name, file_data):
    try:
        s3 = boto3.client('s3',
                          aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                          aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'))
        s3.upload_fileobj(file_data, bucket_name, file_name)
        return f"s3://{bucket_name}/{file_name}"
    except NoCredentialsError:
        raise Exception("S3 credentials not available")
    except Exception as e:
        raise Exception(f"Exception in upload_to_s3: {str(e)}")
