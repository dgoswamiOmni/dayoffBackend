import boto3
import json

def get_secret():
    secret_name = "your_secret_name"  # Replace with your secret name
    region_name = "your_aws_region"  # Replace with your AWS region

    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager', region_name=region_name)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except Exception as e:
        print("Error retrieving secret:", e)
        raise

    secret_string = get_secret_value_response['SecretString']
    return json.loads(secret_string)


# # Get secret values from AWS Secrets Manager
secrets = get_secret()
