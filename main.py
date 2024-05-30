import json
from fastapi import FastAPI, HTTPException, Query, UploadFile, File,Form
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from Classes.user_data_handler import UserDataHandler
from Classes.trip_data_handler import TripDataHandler
from Classes.messaging_room_handler import MessagingRoom
from Classes.otp_handler import OtpHandler
from Utils.mongo_utils import MongoUtils
from typing import Dict

app = FastAPI(title="DayOff APIs")
handler = Mangum(app)

# Enable CORS (Cross-Origin Resource Sharing) for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create an instance with collection_names "session"
# session_instance = MongoUtils(collection_name="session")
# session = session_instance.connect_to_database()
#
# trip_instance = MongoUtils(collection_name="trip")
# trip = trip_instance.connect_to_database()

mongo_instance = MongoUtils()
mongo = mongo_instance.connect_to_database()

# initialize an instance of the trip_data_handler and otp_handler class
trip_handler = TripDataHandler(mongo)
otp_handler = OtpHandler(mongo)

# oauth2_scheme = OAuth2AuthorizationCodeBearer(tokenUrl="token")
#
#
#
#
# async def get_current_user(token: str = Depends(oauth2_scheme)):
#     user = validate_jwt_token(token)
#     if not user:
#         raise HTTPException(status_code=401, detail="Invalid or expired token")
#     return user

@app.post("/login", response_model=dict)
async def login_user(event: dict):
    print("login called")
    password, email = event.get('password'), event.get('email')
    user_handler = UserDataHandler(username="", password=password, email=email, otp_handler=otp_handler)
    return await user_handler.authenticate_user(mongo)


@app.post("/logout", response_model=dict)
async def logout_user(event: dict):
    email, token = event.get('email'), event.get('token')
    user_handler = UserDataHandler(username="", password="", email=email, otp_handler=otp_handler)
    return await user_handler.logout_user(mongo, token)

@app.post("/fetch_token_by_email", response_model=dict)
async def logout_user(event: dict):
    email = event.get('email')
    user_handler = UserDataHandler(username="", password="", email=email, otp_handler=otp_handler)
    return await user_handler.get_token_by_email(mongo, email)

@app.post("/forgot-password",response_model=dict)
async def forgot_password(event: dict):
    email = event.get('email')
    user_data_handler = UserDataHandler(username=None, password=None, email=email, otp_handler=otp_handler)
    return await user_data_handler.forgot_password(mongo,event)


@app.post("/reset-password",response_model=dict)
async def reset_password(event: dict):
    email = event.get('email')
    otp = event.get('otp')
    new_password = event.get('new_password')
    user_data_handler = UserDataHandler(username=None, password=new_password, email=email, otp_handler=otp_handler)
    return await user_data_handler.reset_password(mongo, event)

@app.post("/putUserData", response_model=dict)
async def put_user_data(event: dict):
    username, email, password = event.get('username'), event.get('email'), event.get('password')
    user_handler = UserDataHandler(username=username, password=password, email=email, otp_handler=otp_handler)
    return await user_handler.put_user_data(mongo)

@app.post("/user/putProfpic", response_model=dict)
async def put_profile_pic(email: str = Form(...), file: UploadFile = File(...)):
    try:
        # Create an instance of UserDataHandler
        user_handler = UserDataHandler(username="", password="", email=email, otp_handler=otp_handler)

        # Call put_profile_picture directly on user_handler
        image_url = await user_handler.put_profile_picture(mongo, email, file)
        return {"message": f"Image uploaded successfully, image url: {image_url}"}
    except Exception as e:
        # Log the exception
        print(f"Exception in put_profile_picture: {str(e)}")
        return {"statusCode": 500, "body": json.dumps({'message': 'Internal Server Error'})}

# @app.post("/user/putExtra", response_model=dict)
# async def put_extra_data(event: dict):
#     print("putting extra data", event)
#     email, photo, residence, job = event.get('email'), event.get('photo_data'), event.get('country'), event.get('job')
#     user_handler = UserDataHandler(username="", password="", email=email, otp_handler=otp_handler)
#     if not email:
#         # if no email passed then return error
#         return {"statusCode": 400, "error": "no email passed"}
#     # upload non-null data to the db
#     if photo:
#         await user_handler.put_profile_picture(mongo, email, photo)
#     if residence:
#         await user_handler.put_residence(mongo, residence)
#     if job:
#         await user_handler.put_job(mongo, job)
#     # if data uploaded successfully then return a valid status code
#     return {'statusCode': 200}


# class Params(BaseModel):
#     email: str = Form(...),
#     country: str = Form(...),
#     job: str = Form(...),
#     linkedin: str = Form(...),
#     photo: UploadFile = File(...)

# @app.post("/user/putExtra", response_model=dict)
# async def put_extra_data(event: Request):
#     event = await event.json()
#     event = event["formData"]["_parts"]

#     event_dict = {}
#     for data in event:
#         event_dict[data[0]] = data[1]

#     event = event_dict

#     email, country, job, linkedin, photo = event.get("email"), event.get("country"), event.get("job"), event.get("linkedin"), event.get("photo")
#     photo = UploadFile(photo)

#     print(email, country, job, linkedin, photo)

#     try:
#         user_handler = UserDataHandler(username="", password="", email=email, otp_handler=otp_handler)
#         if not email:
#             # if no email passed then return error
#             return {"statusCode": 400, "error": "no email passed"}
#         # upload non-null data to the db
#         if photo:
#             await user_handler.put_profile_picture(mongo, email, photo)
#         if country:
#             await user_handler.put_residence(mongo, country)
#         if job:
#             await user_handler.put_job(mongo, job)
#         if linkedin:
#             await user_handler.put_linkedin(mongo, linkedin)
#         # if data uploaded successfully then return a valid status code
#         return {'statusCode': 200}
#     except Exception as e:
#         print(f"Exception in put_extra_data: {str(e)}")
#         return {"statusCode": 500, "body": json.dumps({'message': 'Internal Server Error'})}

@app.post("/user/putExtra", response_model=dict)
async def put_extra_data(email: str = Form(...),photo: str = Form(...), country: str = Form(...), job: str = Form(...), linkedin: str = Form(...)):
    try:
        print(email,photo, country, job, linkedin)

        user_handler = UserDataHandler(username="", password="", email=email, otp_handler=otp_handler)
        if not email:
            return {"statusCode": 400, "error": "no email passed"}
        if country:
            await user_handler.put_residence(mongo, country)
        if photo:
            await mongo.user.update_one({"email_id": email}, {"$set": {"profile_picture": photo}})
        if job:
            await user_handler.put_job(mongo, job)
        if linkedin:
            await user_handler.put_linkedin(mongo, linkedin)

        return {'statusCode': 200,'message':"Profile inserted successfully"}
    except Exception as e:
        print(f"Exception in put_extra_data: {str(e)}")
        return {"statusCode": 500, "body": json.dumps({'message': 'Internal Server Error'})}


@app.post("/user/putPref", response_model=dict)
async def put_user_preferences(event: dict):
    email, dates, countries = event.get('email'), event.get('dates'), event.get('countries')
    user_handler = UserDataHandler(username="", password="", email=email, otp_handler=otp_handler)
    return await user_handler.update_user_preferences(mongo, email, dates, countries)

@app.post("/user/getPref", response_model=dict)
async def get_user_preferences(event: dict):
    email = event.get('email')
    user_handler = UserDataHandler(username="", password="", email=email, otp_handler=otp_handler)
    return await user_handler.get_user_preferences(mongo, email)


@app.post("/getUserData", response_model=dict)
async def get_user_data(event: dict):
    try:
        email = event.get('email')
        user_handler = UserDataHandler(username="", password="", email=email, otp_handler=otp_handler)
        return await user_handler.get_user_data(mongo)
    except HTTPException as e:
        # If it's an HTTPException, return a detailed error response
        return {"statusCode": e.status_code, "error": str(e.detail)}

@app.post("/fetch_group_members", response_model=dict)
async def fetch_group_members(trip_id: str = Query(..., description="ID of the trip")):
    user_handler = UserDataHandler(email=" ", username="", password="", otp_handler=otp_handler)
    return await user_handler.fetch_group_members(mongo,trip_id)


@app.post("/trips/create", response_model=dict)
async def create_trip(event: dict):
    return await trip_handler.create_trip(event)

@app.post("/trips/update", response_model=dict)
async def update_trip(event: dict):
    return await trip_handler.update_trip(event)

@app.post("/trips/delete", response_model=dict)
async def delete_trip(event: dict):
    return await trip_handler.delete_trip(event)


@app.post("/trips/join", response_model=dict)
async def join_trip(event: dict):
    return await trip_handler.join_trip(event)


@app.post("/trips/leave", response_model=dict)
async def leave_trip(event: dict):
    return await trip_handler.leave_trip(event)


@app.post("/trips/invite", response_model=dict)
async def send_trip_invitation(event: dict):
    return await trip_handler.send_trip_invitation(event)


@app.post("/trips/filter", response_model=dict)
async def filter_and_sort_trips(event: dict):
    return await trip_handler.filter_and_sort_trips(event)

@app.post("/trips/details", response_model=dict)
async def get_trip_info(event: dict):
    return await trip_handler.get_trip_details(event)

@app.post("/trips/matching-users", response_model=Dict)
async def find_matching_users(event: dict):
    try:
        result = await trip_handler.find_users_with_matching_preferences(event)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/trips/participants", response_model=Dict)
async def find_participants(event: dict):
    try:
        result = await trip_handler.get_trip_participants(event)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/messaging/send", response_model=dict)
async def send_message_to_room(event: dict):
    messaging_handler = MessagingRoom(db=mongo, room_id=None, trip_id=None)
    return await messaging_handler.send_message(event)


@app.post("/messaging/retrieve", response_model=dict)
async def retrieve_messages_from_room(event: dict):
    messaging_handler = MessagingRoom(db=mongo, room_id=None, trip_id=None)
    return await messaging_handler.get_messages(event.get('trip_id'))


@app.post("/send-otp", response_model=dict)
async def send_otp_message(event: dict):
    email = event.get('email')
    username = event.get('username')
    if not email or not username:
        raise HTTPException(status_code=400, detail="Email and username are required")
    return await otp_handler.send_otp_sms(email, username)

@app.post("/validate-otp", response_model=dict)
async def validate_otp_message(event: dict):
    email = event.get('email')
    otp = event.get('otp')
    return await otp_handler.validate_otp_message(email, otp)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="192.168.1.116", port=8090)
