import json
import os
import time
import random
from pymongo import MongoClient
import boto3


# class OtpHandler:
#     def __init__(self, db):
#         self.otp_collection = db.otp_collection
#         self.sns_client = boto3.client('sns', region_name=os.environ.get('AWS_REGION'))

#     async def send_otp_sms(self, email, username):
#         generated_otp = str(random.randint(100000, 999999))
#         expiration_time = int(time.time()) + 300  # OTP expires in 5 minutes

#         # Store OTP and expiration time in MongoDB
#         await self.otp_collection.update_one(
#             {'email': email},
#             {'$set': {'otp': generated_otp, 'expiration_time': expiration_time}},
#             upsert=True
#         )

#         # Send OTP via SNS
#         message = f'Hello {username}, your OTP is: {generated_otp}'
#         self.sns_client.publish(
#             TopicArn='Your Tpoic Arn',
#             Message=message,
#             Subject='OTP Verification'
#         )

#         return {"message": "OTP sent successfully!"}
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
# from sendgrid.helpers.exceptions import SendGridError


SENDGRID_API_KEY = "YOUR SENDGRID API KEY"

class OtpHandler:
    def __init__(self, db):
        self.otp_collection = db.otp_collection
        self.sendgrid_api_key = SENDGRID_API_KEY
        self.sendgrid_api_key = os.environ.get('SENDGRID_API_KEY')

    async def send_otp_sms(self, email, username):
        generated_otp = str(random.randint(100000, 999999))
        expiration_time = int(time.time()) + 300  # OTP expires in 5 minutes

        # Store OTP and expiration time in MongoDB
        await self.otp_collection.update_one(
            {'email': email},
            {'$set': {'otp': generated_otp, 'expiration_time': expiration_time}},
            upsert=True
        )

        # Send OTP via SendGrid
        sg = sendgrid.SendGridAPIClient(api_key=self.sendgrid_api_key)
        from_email = Email("YOUR AUTHENTICTAED EMAIL")  # Replace with your verified sender email
        to_email = To(email)
        subject = "OTP Verification"
        content = Content("text/plain", f"Hello {username}, your OTP is: {generated_otp}")
        mail = Mail(from_email, to_email, subject, content)

        try:
            response = sg.send(mail)
            if response.status_code == 202:
                return {"message": "OTP sent successfully!"}
            else:
                return {"message": "Failed to send OTP. Please try again later."}
        except Exception as e:
            return {"message": "An error occurred while sending OTP. Please try again later."}


    async def validate_otp_message(self, email, otp_from_user):
        stored_data = await self.otp_collection.find_one({'email': email})

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
