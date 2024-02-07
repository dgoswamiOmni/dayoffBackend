import json
import os
import time
import random
from pymongo import MongoClient
import boto3


class OtpHandler:
    def __init__(self, otp_collection):
        self.otp_collection = otp_collection
        self.sns_client = boto3.client('sns', region_name=os.environ.get('AWS_REGION'))

    def send_otp_sms(self, email, username):
        generated_otp = str(random.randint(100000, 999999))
        expiration_time = int(time.time()) + 300  # OTP expires in 5 minutes

        # Store OTP and expiration time in MongoDB
        self.otp_collection.update_one(
            {'email': email},
            {'$set': {'otp': generated_otp, 'expiration_time': expiration_time}},
            upsert=True
        )

        # Send OTP via SNS
        message = f'Hello {username}, your OTP is: {generated_otp}'
        self.sns_client.publish(
            Email=email,
            Message=message
        )

        return {"message": "OTP sent successfully!"}

    def validate_otp_message(self, username, otp_from_user):
        stored_data = self.otp_collection.find_one({'username': username})

        if not stored_data:
            return {'statusCode': 400, 'body': json.dumps('No OTP found for the provided username')}

        stored_otp_value = stored_data['otp']
        stored_expiration_time = stored_data['expiration_time']

        if int(stored_expiration_time) < int(time.time()):
            return {'statusCode': 400, 'body': json.dumps('Time Over. OTP has expired.')}
        else:
            if stored_otp_value == otp_from_user:
                return {'statusCode': 200, 'body': json.dumps('OTP Verified!')}
            else:
                return {
                    'statusCode': 400,
                    'body': json.dumps(f'Wrong OTP! Expected: {stored_otp_value}, Received: {otp_from_user}')
                }
