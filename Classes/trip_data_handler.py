# trip_data_handler.py
import random
import json
from bson import ObjectId, json_util
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2AuthorizationCodeBearer
from Utils.auth_utils import validate_jwt_token
from Classes.messaging_room_handler import MessagingRoom
import datetime


# from auth_utils import db

class TripDataHandler:
    def __init__(self, db):
        self.db = db

    async def create_trip(self, event):
        try:
            current_time = datetime.datetime.utcnow().isoformat()

            trip_details = {
                'creator_email': event.get('creator_email'),  # Use creator's email instead of username
                'start_date': datetime.datetime.strptime(event.get('start_date'), '%a %b %d %Y %H:%M:%S %Z%z').strftime('%Y-%m-%d'),  # Include start date
                'end_date': datetime.datetime.strptime(event.get('end_date'), '%a %b %d %Y %H:%M:%S %Z%z').strftime('%Y-%m-%d'),  # Include end date
                # 'time': body.get('time'),
                'location': event.get('location'),
                'description': event.get('description'),
                'participants': [0 for _ in range(event.get('participants'))],
                'trip_id': ''.join([str(random.randint(0, 9)) for _ in range(10)]),
                'created_at': current_time  # Include the time and date of creation
            }
            trip_details['participants'][0] = event.get('creator_email')

            result = await self.db.trip.insert_one(trip_details)

            room_id = ''.join([str(random.randint(0, 9)) for _ in range(10)])
            messaging_room = MessagingRoom(db=self.db, room_id=room_id, trip_id=trip_details['trip_id'],
                                           participants=[{trip_details.get('creator_email'): 'Name'}])

            # Save the messaging room details in the database
            await self.db.messaging_room.insert_one(messaging_room.to_dict())

            return {'statusCode': 200, 'body': json.dumps(
                {'message': 'Trip and messaging room created successfully', 'trip_id': str(result.inserted_id),
                 'room_id': room_id})}
        except Exception as e:
            print(e)
            return {'statusCode': 500, 'body': json.dumps({'message': 'Internal Server Error', 'Exception': str(e)})}

    async def join_trip(self, event):
        try:
            # Extract trip ID and username from the request
            trip_id = event.get('trip_id')
            email = event.get('email')

            # Validate the presence of required parameters
            if not (trip_id or email):
                return {'statusCode': 400, 'body': json.dumps({'message': 'Missing required parameters'})}

            # Check if the trip exists
            trip = await self.db.trip.find_one({"trip_id": trip_id})
            if not trip:
                return {'statusCode': 404, 'body': json.dumps({'message': 'Trip not found'})}

            # Add the username to the list of participants
            await self.db.trip.update_one({"trip_id": trip_id}, {'$addToSet': {'participants': email}})

            # Add the username to the messaging room participants
            await self.db.messaging_room.update_one(
                {"trip_id": trip_id},
                {'$addToSet': {'participants': email}}
            )

            return {'statusCode': 200, 'body': json.dumps({'message': 'Joined trip successfully'})}

        except Exception as e:
            return {'statusCode': 500, 'body': json.dumps({'message': 'Internal Server Error'})}

    async def leave_trip(self, event):
        try:
            # Extract trip ID and user ID from the request
            trip_id = event.get('trip_id')
            email = event.get('email')

            # Validate the presence of required parameters
            if not trip_id or not email:
                return {'statusCode': 400, 'body': json.dumps({'message': 'Missing required parameters'})}

            # Check if the trip exists
            trip = await self.db.trip.find_one({"trip_id": trip_id})
            if not trip:
                return {'statusCode': 404, 'body': json.dumps({'message': 'Trip not found'})}

            # Remove the user from the list of participants
            await self.db.trip.update_one({"trip_id": trip_id}, {'$pull': {'participants': email}})

            # Remove the user from the messaging room participants
            await self.db.messaging_room.update_one(
                {"trip_id": trip_id},
                {'$pull': {'participants': email}}
            )

            return {'statusCode': 200, 'body': json.dumps({'message': 'Left trip successfully'})}
        except Exception as e:
            return {'statusCode': 500, 'body': json.dumps({'message': 'Internal Server Error'})}

    async def send_trip_invitation(self, event):
        try:
            token = event['headers'].get('Authorization', '').split('Bearer ')[-1]
            decoded_token = validate_jwt_token(token)

            if decoded_token:

                body = json.loads(event['body'])
                invited_user_id = body['invited_user_id']
                trip_id = body['trip_id']

                result = await self.db.trips.update_one(
                    {"trip_id": trip_id},
                    {'$addToSet': {'invitations': {'user_id': invited_user_id, 'status': 'pending'}}}
                )

                if result.matched_count > 0 and result.modified_count > 0:
                    return {'statusCode': 200, 'body': json.dumps({'message': 'Invitation sent successfully'})}
                else:
                    return {'statusCode': 404, 'body': json.dumps({'message': 'Trip not found'})}
            else:
                return {'statusCode': 401, 'body': json.dumps({'message': 'Invalid or expired token'})}
        except Exception as e:
            return {'statusCode': 500, 'body': json.dumps({'message': 'Internal Server Error'})}

    async def filter_and_sort_trips(self, event):
        try:
            # Get query parameters from the event
            creator_email = event.get('creator_email')
            user_email = event.get('user_email')
            location = event.get('location')
            start_date = event.get('start_date')
            end_date = event.get('end_date')

            # Define a base query
            query = {}

            # Add filters based on user preferences

            # used to get the user's created trips
            if creator_email:
                query['creator_email'] = creator_email

            # used to get any trips that the user has joined
            if user_email:
                query['participants'] = {"$in": [user_email]}

            if location:
                query['location'] = location

            if start_date and end_date:
                query['start_date'] = {'$gte': start_date, '$lte': end_date}
                query['end_date'] = {'$gte': start_date, '$lte': end_date}

            # TODO: handle getting trips when an array is passed to location and start_date and end_date
            # Fetch trips from the database based on the query
            cursor = self.db.trip.find(query)

            # parse data so its more readable
            def parse_json(data):
                return json.loads(json_util.dumps(data))

            # .find() returns a cursor so async iterate through to get every document
            trips = []
            async for doc in cursor:
                trips.append(parse_json(doc))

            # Sort trips based on a specific criterion (e.g., date)
            sorted_trips = sorted(trips, key=lambda x: x.get('start_date', ''))

            # Return the filtered and sorted trips
            return {
                'statusCode': 200,
                'body': json.dumps({'message': 'Trips filtered and sorted successfully', 'trips': sorted_trips})
            }
        except Exception as e:
            print("error", e)
            return {'statusCode': 500, 'body': json.dumps({'message': 'Internal Server Error'})}

    async def update_trip(self, event: dict):
        #TODO: update the trip in the database
        return None
