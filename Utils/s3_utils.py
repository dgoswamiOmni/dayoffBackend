import os
import boto3
from botocore.exceptions import NoCredentialsError

S3_BUCKET=os.environ.get('S3_BUCKET')
S3_REGION=os.environ.get('S3_REGION')

def upload_to_s3(bucket_name, file_name, file_data):
    try:
        s3 = boto3.client('s3',
                          aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                          aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),region_name=os.environ.get('S3_REGION'))
        s3.upload_fileobj(file_data, bucket_name, file_name,ExtraArgs={'ContentType': 'image/jpeg'})
        return f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{filename}"
    except NoCredentialsError:
        raise Exception("S3 credentials not available")
    except Exception as e:
        raise Exception(f"Exception in upload_to_s3: {str(e)}")
