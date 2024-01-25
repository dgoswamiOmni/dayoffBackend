from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from Classes.user_data_handler import UserDataHandler
from Classes.trip_data_handler import TripDataHandler
from Classes.messaging_room_handler import MessagingRoom
from Utils.mongo_utils import MongoUtils

app = FastAPI()
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

user_instance = MongoUtils(collection_name="user")
user = user_instance.connect_to_database()

trip_handler = TripDataHandler(user)


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
async def login_user(username: str, password: str):
    user_handler = UserDataHandler(username=username, password=password, email="")
    return await user_handler.authenticate_user(user)


@app.post("/logout", response_model=dict)
async def logout_user(username: str, token: str):
    user_handler = UserDataHandler(username=username, password="", email="")
    return await user_handler.logout_user(user, token)


@app.post("/putUserData", response_model=dict)
async def put_user_data(username: str, email: str, password: str, image_data: bytes):
    user_handler = UserDataHandler(username=username, password=password, email=email)
    return await user_handler.put_user_data(user, image_data)


@app.get("/getUserData", response_model=dict)
async def get_user_data(username: str):
    try:
        user_handler = UserDataHandler(username=username, password="", email="")
        return await user_handler.get_user_data(user)
    except HTTPException as e:
        # If it's an HTTPException, return a detailed error response
        return {"statusCode": e.status_code, "error": str(e.detail)}


@app.post("/trips/create", response_model=dict)
async def create_trip(event: dict):
    return await trip_handler.create_trip(event)


@app.post("/trips/join", response_model=dict)
async def join_trip(event: dict):
    return await trip_handler.join_trip(event)


@app.post("/trips/leave", response_model=dict)
async def leave_trip(event: dict):
    return await trip_handler.leave_trip(event)


@app.post("/trips/invite", response_model=dict)
async def send_trip_invitation(event: dict):
    return await trip_handler.send_trip_invitation(event)


@app.get("/trips/filter", response_model=dict)
async def filter_and_sort_trips(event: dict):
    return await trip_handler.filter_and_sort_trips(event)


@app.post("/messaging/send", response_model=dict)
async def send_message_to_room(event: dict):
    messaging_handler = MessagingRoom(db=user, room_id=None, trip_id=None)
    return await messaging_handler.send_message(event)


@app.get("/messaging/retrieve", response_model=dict)
async def retrieve_messages_from_room(room_id: str):
    messaging_handler = MessagingRoom(db=user, room_id=room_id, trip_id=None)
    return await messaging_handler.get_messages(room_id)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8090)
