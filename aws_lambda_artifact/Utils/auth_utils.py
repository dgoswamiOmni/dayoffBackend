import os
import random
from datetime import datetime, timedelta

import jwt
from pymongo import MongoClient

# # MongoDB connection details
# MONGO_URI = "mongodb+srv://devarshigoswami97:AoKUNhswGnboFmWt@dayoff.c1bq6uj.mongodb.net/?retryWrites=true&w=majority"
# MONGO_DB_NAME = "your_database_name"  # Replace with your MongoDB database name
# MONGO_COLLECTION_NAME = "session"

SECRET_KEY = 'secret_key'
ALGORITHM = 'HS256'


# # Connect to MongoDB
# client = MongoClient(MONGO_URI)
# db = client[MONGO_DB_NAME]

def validate_jwt_token(token):
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded_token
    except jwt.ExpiredSignatureError:
        return None  # Token has expired
    except jwt.InvalidTokenError:
        return None  # Invalid token


def generate_jwt_token(username):
    expiration_time = datetime.utcnow() + timedelta(hours=24)  # You may adjust the expiration time
    payload = {
        'sub': username,
        'exp': expiration_time,
        'iat': datetime.utcnow(),
        'jti': ''.join([str(random.randint(0, 9)) for _ in range(10)])  # Unique identifier for the token
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    # Store the token in the MongoDB collection
    token_data = {
        'username': username,
        'token': token
    }

    return token_data


def log_login(username, token_data):
    login_timestamp = datetime.utcnow()
    token_data.update({
        'login_time': login_timestamp,
        'user_name': username
    })
    return token_data


def log_logout(username, token_data):
    logout_timestamp = datetime.utcnow()
    token_data.update({
        'logout_time': logout_timestamp,
        'active': False
    })
    return token_data
