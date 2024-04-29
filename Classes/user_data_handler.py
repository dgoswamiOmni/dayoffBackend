# import os
# import json
# from passlib.hash import pbkdf2_sha256
# from Utils.auth_utils import generate_jwt_token, log_login, log_logout, validate_jwt_token
# from bson import ObjectId
# from fastapi import HTTPException
# from datetime import datetime
# from s3_utils import upload_to_s3


# class UserDataHandler:
#     def __init__(self, username, password, email, otp_handler):
#         self.username = username
#         self.password = password
#         self.email = email
#         self.otp_handler = otp_handler


#     async def authenticate_user(self, db):
#         try:
#             # Check if the user exists
#             user = await db.user.find_one({"email_id": self.email})

#             if not user:
#                 return {'statusCode': 401, 'body': json.dumps({'message': 'Invalid credentials'})}

#             hashed_password = user['password_hash']


#             # Verify the password
#             if not pbkdf2_sha256.verify(self.password, hashed_password):
#                 return {'statusCode': 401, 'body': json.dumps({'message': 'Invalid credentials'})}

#             # Generate a JWT token
#             token_data = generate_jwt_token(self.username)

#             # Log the login time
#             token_data = log_login(self.username, token_data)

#             session_start = await db.session.insert_one(token_data)

#             return {'statusCode': 200,
#                     'body': json.dumps({'message': 'Login successful', 'session_start': str(session_start),
#                                         'session_token': token_data['token']})}
#         except Exception as e:
#             # Log the exception
#             print(f"Exception in authenticate_user: {str(e)}")
#             return {'statusCode': 500, 'body': json.dumps({'message': 'Internal Server Error'})}

#     async def logout_user(self, db, token):
#         try:
#             # Validate the JWT token
#             decoded_token = validate_jwt_token(token)

#             if decoded_token and decoded_token['sub'] == self.username:
#                 # Search for the user's session record
#                 session_record = await db.session.find_one({"username": self.username})

#                 if session_record:
#                     # Log the logout time and obtain token data
#                     token_data = log_logout(decoded_token['sub'], session_record)

#                     # Append token_data to the existing session record
#                     updated_session_record = {**session_record, **token_data}

#                     # Update the user's session record in the database
#                     await db.session.update_one({"username": self.username}, {"$set": updated_session_record})

#                     return {'statusCode': 200, 'body': json.dumps({'message': 'Logout successful'})}

#                 else:
#                     return {'statusCode': 404, 'body': json.dumps({'message': 'User session not found'})}
#             else:
#                 return {'statusCode': 401, 'body': json.dumps({'message': 'Invalid or expired token'})}
#         except Exception as e:
#             # Log the exception
#             print(f"Exception in logout_user: {str(e)}")
#             return {'statusCode': 500, 'body': json.dumps({'message': 'Internal Server Error'})}

#     async def put_user_data(self, db):
#         try:
#             # Insert new user data into MongoDB
#             user_data = {
#                 "user_name": self.username,
#                 "email_id": self.email,
#                 "password_hash": pbkdf2_sha256.hash(self.password),
#             }
#             result = await db.user.insert_one(user_data)
#             # Call put_profile_picture to upload the profile picture
#             #await self.put_profile_picture(db, str(result.inserted_id))

#             # Send OTP
#             #await self.otp_handler.send_otp_sms(email=self.email, username=self.username)

#             return {"message": "Data inserted successfully", "user_id": str(result.inserted_id)}
#         except Exception as e:
#             # Log the exception
#             print(f"Exception in put_user_data: {str(e)}")
#             return {'statusCode': 500, 'body': json.dumps({'message': 'Internal Server Error'})}

#     async def get_user_data(self, db):
#         try:
#             # Retrieve user data based on username
#             user_data = await db.user.find_one({"user_name": self.username})

#             if user_data:
#                 return {
#                     "user_data": {
#                         "user_name": user_data["user_name"],
#                         "email_id": user_data["email_id"],
#                         "profile_picture": user_data.get("profile_picture", None),
#                     }
#                 }
#             else:
#                 raise HTTPException(status_code=404, detail="User not found")
#         except Exception as e:
#             # Log the exception
#             print(f"Exception in get_user_data: {str(e)}")
#             return {'statusCode': 500, 'body': json.dumps({'message': 'Internal Server Error'})}

#     async def put_profile_picture(self, db, user_id, image_data):
#         try:
#             # Upload image to S3 using the utility function
#             bucket_name = os.environ.get('S3_BUCKET_NAME')
#             file_name = f"{user_id}.png"  # Assuming the image is in PNG format
#             s3_url = upload_to_s3(bucket_name, file_name, image_data)

#             # Update user data in the database with the S3 URL
#             await db.user.update_one({"user_name": self.username}, {"$set": {"profile_picture": s3_url}})

#             return {"message": "Profile picture uploaded successfully"}
#         except Exception as e:
#             # Log the exception
#             print(f"Exception in put_profile_picture: {str(e)}")
#             return {"statusCode": 500, "body": json.dumps({'message': 'Internal Server Error'})}

# # Example usage:
# # user_handler = UserDataHandler(username="john_doe", password="password123", email="john_doe@example.com")
# # response = user_handler.authenticate_user(db)
# # print(response)
import os
import json
from passlib.hash import pbkdf2_sha256
from Utils.auth_utils import generate_jwt_token, log_login, log_logout, validate_jwt_token
from bson import ObjectId
from fastapi import HTTPException
from datetime import datetime
from Utils.s3_utils import upload_to_s3


class UserDataHandler:
    def __init__(self, username, password, email, otp_handler):
        self.username = username
        self.password = password
        self.email = email
        self.otp_handler = otp_handler

    async def authenticate_user(self, db):
        try:
            # Check if the user exists
            user = await db.user.find_one({"email_id": self.email})

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

    # async def put_user_data(self, db):
    #     try:
    #         # Insert new user data into MongoDB
    #         user_data = {
    #             "user_name": self.username,
    #             "email_id": self.email,
    #             "password_hash": pbkdf2_sha256.hash(self.password),
    #         }
    #
    #         # TODO: check if a user with the same email id exists already -> if so then return an error status
    #
    #         result = await db.user.insert_one(user_data)
    #         # Create a new document for user preferences
    #         user_preferences = {
    #             "email_id": self.email,
    #             "preferred_dates": [],
    #             "preferred_countries": [],
    #         }
    #         await db.user_preferences.insert_one(user_preferences)
    #
    #         # Call put_profile_picture to upload the profile picture
    #         # await self.put_profile_picture(db, str(result.inserted_id))
    #
    #         # Send OTP
    #         # await self.otp_handler.send_otp_sms(email=self.email, username=self.username)
    #
    #         return {"message": "Data inserted successfully", "user_id": str(result.inserted_id)}
    #     except Exception as e:
    #         # Log the exception
    #         print(f"Exception in put_user_data: {str(e)}")
    #         return {'statusCode': 500, 'body': json.dumps({'message': 'Internal Server Error'})}
    async def put_user_data(self, db, image_data=None):
        try:
            # Insert new user data into MongoDB
            user_data = {
                "user_name": self.username,
                "email_id": self.email,
                "password_hash": pbkdf2_sha256.hash(self.password),
            }

            # Check if a user with the same email id exists already
            if await self.user_exists(db, self.email):
                return {'statusCode': 400, 'body': json.dumps({'message': 'User with this email already exists'})}

            result = await db.user.insert_one(user_data)

            # Create a new document for user preferences
            user_preferences = {
                "email_id": self.email,
                "preferred_dates": [],
                "preferred_countries": [],
            }
            await db.user_preferences.insert_one(user_preferences)

            # Call put_profile_picture to upload the profile picture
            if image_data:
                await self.put_profile_picture(db, str(result.inserted_id), image_data=image_data)

            # Send OTP
            await self.otp_handler.send_otp_sms(self.email, self.username)

            return {"message": "Data inserted successfully", "user_id": str(result.inserted_id)}
        except Exception as e:
            # Log the exception
            print(f"Exception in put_user_data: {str(e)}")
            return {'statusCode': 500, 'body': json.dumps({'message': 'Internal Server Error'})}

    async def user_exists(self, db, email):
        return await db.user.find_one({"email_id": email}) is not None

    async def send_otp_sms(self):
        # Assuming implementation for sending OTP SMS
        pass

    async def get_user_preferences(self, db, email):
        try:
            # Retrieve user preferences based on email
            user_preferences = await db.user_preferences.find_one({"email_id": email})

            if user_preferences:
                return {
                    "preferred_dates": user_preferences.get("preferred_dates", []),
                    "preferred_countries": user_preferences.get("preferred_countries", []),
                }
            else:
                return {"message": "User preferences not found"}
        except Exception as e:
            # Log the exception
            print(f"Exception in get_user_preferences: {str(e)}")
            return {'statusCode': 500, 'body': json.dumps({'message': 'Internal Server Error'})}

        async def update_user_preferences(self, db, email, preferred_dates=None, preferred_countries=None):
        try:
            # Check if user preferences record exists
            existing_record = await db.user_preferences.find_one({"email_id": email})

            if existing_record:
                # Update user preferences
                await db.user_preferences.update_one(
                    {"email_id": email},
                    {"$set": {
                        "preferred_dates": preferred_dates if preferred_dates else [],
                        "preferred_countries": preferred_countries if preferred_countries else [],
                    }}
                )
                return {"message": "User preferences updated successfully"}
            else:
                # Insert new user preferences record
                await db.user_preferences.insert_one({
                    "email_id": email,
                    "preferred_dates": preferred_dates if preferred_dates else [],
                    "preferred_countries": preferred_countries if preferred_countries else [],
                })
                return {"message": "New user preferences record created successfully"}

        except Exception as e:
            # Log the exception
            print(f"Exception in update_user_preferences: {str(e)}")
            return {'statusCode': 500, 'body': json.dumps({'message': 'Internal Server Error'})}


    async def get_user_data(self, db):
        try:
            # Retrieve user data based on username
            user_data = await db.user.find_one({"email_id": self.email})

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

    # async def put_profile_picture(self, db, user_id, image_data):
    #     try:
    #         # Upload image to S3 using the utility function
    #         bucket_name = os.environ.get('S3_BUCKET_NAME')
    #         file_name = f"{user_id}.png"  # Assuming the image is in PNG format
    #         s3_url = upload_to_s3(bucket_name, file_name, image_data)
    #
    #         # Update user data in the database with the S3 URL
    #         await db.user.update_one({"user_name": self.username}, {"$set": {"profile_picture": s3_url}})
    #
    #         return {"message": "Profile picture uploaded successfully"}
    #     except Exception as e:
    #         # Log the exception
    #         print(f"Exception in put_profile_picture: {str(e)}")
    #         return {"statusCode": 500, "body": json.dumps({'message': 'Internal Server Error'})}
    async def put_profile_picture(self, db, user_id, image_data):
        try:
            # Assuming image_data is a file-like object or a file path
            # If image_data is a file path, open the file in binary mode
            if isinstance(image_data, str):  # Check if image_data is a file path
                with open(image_data, 'rb') as file:
                    image_data = file.read()

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

    async def put_residence(self, db, residence):
        # TODO: function to upload text country of residence to user record
        pass

    async def put_job(self, db, job):
        # TODO: upload text job to user record
        pass

# Example usage:
# user_handler = UserDataHandler(username="john_doe", password="password123", email="john_doe@example.com")
# response = user_handler.authenticate_user(db)
# print(response)

