import os
import json
from passlib.hash import pbkdf2_sha256
from Utils.auth_utils import generate_jwt_token, log_login, log_logout, validate_jwt_token
from bson import ObjectId
from fastapi import HTTPException
from datetime import datetime
from s3_utils import upload_to_s3


class UserDataHandler:
    def __init__(self, username, password, email, otp_handler):
        self.username = username
        self.password = password
        self.email = email
        self.otp_handler = otp_handler


    async def authenticate_user(self, db):
        try:
            # Check if the user exists
            user = await db.user.find_one({"user_name": self.username})

            if not user:
                return {'statusCode': 401, 'body': json.dumps({'message': 'Invalid credentials'})}

            hashed_password = user['password_hash']

            # Verify the password
            if not pbkdf2_sha256.verify(self.password, hashed_password):
                return {'statusCode': 401, 'body': json.dumps({'message': 'Invalid credentials'})}

            # Generate a JWT token
            token_data = generate_jwt_token(self.username)

            # Log the login time
            token_data = log_login(self.username, token_data)

            session_start = await db.session.insert_one(token_data)

            return {'statusCode': 200,
                    'body': json.dumps({'message': 'Login successful', 'session_start': str(session_start),
                                        'session_token': token_data['token']})}
        except Exception as e:
            # Log the exception
            print(f"Exception in authenticate_user: {str(e)}")
            return {'statusCode': 500, 'body': json.dumps({'message': 'Internal Server Error'})}

    async def logout_user(self, db, token):
        try:
            # Validate the JWT token
            decoded_token = validate_jwt_token(token)

            if decoded_token and decoded_token['sub'] == self.username:
                # Search for the user's session record
                session_record = await db.session.find_one({"username": self.username})

                if session_record:
                    # Log the logout time and obtain token data
                    token_data = log_logout(decoded_token['sub'], session_record)

                    # Append token_data to the existing session record
                    updated_session_record = {**session_record, **token_data}

                    # Update the user's session record in the database
                    await db.session.update_one({"username": self.username}, {"$set": updated_session_record})

                    return {'statusCode': 200, 'body': json.dumps({'message': 'Logout successful'})}

                else:
                    return {'statusCode': 404, 'body': json.dumps({'message': 'User session not found'})}
            else:
                return {'statusCode': 401, 'body': json.dumps({'message': 'Invalid or expired token'})}
        except Exception as e:
            # Log the exception
            print(f"Exception in logout_user: {str(e)}")
            return {'statusCode': 500, 'body': json.dumps({'message': 'Internal Server Error'})}

    async def put_user_data(self, db, image_data):
        try:
            # Insert new user data into MongoDB
            user_data = {
                "user_name": self.username,
                "email_id": self.email,
                "password_hash": pbkdf2_sha256.hash(self.password),
            }
            result = await db.user.insert_one(user_data)
            # Call put_profile_picture to upload the profile picture
            await self.put_profile_picture(db, str(result.inserted_id), image_data)

            # Send OTP
            await self.otp_handler.send_otp_sms(phone_number="user_phone_number", username=self.username)

            return {"message": "Data inserted successfully", "user_id": str(result.inserted_id)}
        except Exception as e:
            # Log the exception
            print(f"Exception in put_user_data: {str(e)}")
            return {'statusCode': 500, 'body': json.dumps({'message': 'Internal Server Error'})}

    async def get_user_data(self, db):
        try:
            # Retrieve user data based on username
            user_data = await db.user.find_one({"user_name": self.username})

            if user_data:
                return {
                    "user_data": {
                        "user_name": user_data["user_name"],
                        "email_id": user_data["email_id"],
                        "profile_picture": user_data.get("profile_picture", None),
                    }
                }
            else:
                raise HTTPException(status_code=404, detail="User not found")
        except Exception as e:
            # Log the exception
            print(f"Exception in get_user_data: {str(e)}")
            return {'statusCode': 500, 'body': json.dumps({'message': 'Internal Server Error'})}

    async def put_profile_picture(self, db, user_id, image_data):
        try:
            # Upload image to S3 using the utility function
            bucket_name = os.environ.get('S3_BUCKET_NAME')
            file_name = f"{user_id}.png"  # Assuming the image is in PNG format
            s3_url = upload_to_s3(bucket_name, file_name, image_data)

            # Update user data in the database with the S3 URL
            await db.user.update_one({"user_name": self.username}, {"$set": {"profile_picture": s3_url}})

            return {"message": "Profile picture uploaded successfully"}
        except Exception as e:
            # Log the exception
            print(f"Exception in put_profile_picture: {str(e)}")
            return {"statusCode": 500, "body": json.dumps({'message': 'Internal Server Error'})}

# Example usage:
# user_handler = UserDataHandler(username="john_doe", password="password123", email="john_doe@example.com")
# response = user_handler.authenticate_user(db)
# print(response)
