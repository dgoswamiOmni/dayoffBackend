# trip_data_handler.py
import random
import json
from bson import ObjectId
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2AuthorizationCodeBearer
from Utils.auth_utils import validate_jwt_token
from Classes.messaging_room_handler import MessagingRoom


# from auth_utils import db

class TripDataHandler:
    def __init__(self, db):
        self.db = db

    async def create_trip(self, event):
        try:
            token = event['headers'].get('Authorization', '').split('Bearer ')[-1]
            decoded_token = validate_jwt_token(token)

            if decoded_token:
                # User is authenticated, proceed with creating a trip
                body = json.loads(event['body'])
                trip_details = {
                    'username': decoded_token['sub'],
                    'date': body.get('date'),
                    'time': body.get('time'),
                    'location': body.get('location'),
                    'description': body.get('description'),
                    'participants': [decoded_token['sub']],
                    'trip_id': ''.join([str(random.randint(0, 9)) for _ in range(10)])
                }
                result = await self.db.trip.insert_one(trip_details)
                room_id = ''.join([str(random.randint(0, 9)) for _ in range(10)])
                messaging_room = MessagingRoom(db=self.db, room_id=room_id, trip_id=trip_details['trip_id'],
                                               participants=[decoded_token['sub']])

                # Save the messaging room details in the database
                await self.db.messaging_room.insert_one(messaging_room.to_dict())

                return {'statusCode': 200, 'body': json.dumps(
                    {'message': 'Trip and messaging room created successfully', 'trip_id': str(result.inserted_id),
                     'room_id': room_id})}
            else:
                return {'statusCode': 401, 'body': json.dumps({'message': 'Invalid or expired token'})}
        except Exception as e:
            return {'statusCode': 500, 'body': json.dumps({'message': 'Internal Server Error', 'Exception': e})}

    async def join_trip(self, event):
        try:
            # Extract trip ID and username from the request
            body = json.loads(event['body'])
            trip_id = body.get('trip_id')
            username = body.get('username')

            # Validate the presence of required parameters
            if not (trip_id or username):
                return {'statusCode': 400, 'body': json.dumps({'message': 'Missing required parameters'})}

            # Check if the trip exists
            trip = await self.db.trip.find_one({"trip_id": trip_id})
            if not trip:
                return {'statusCode': 404, 'body': json.dumps({'message': 'Trip not found'})}

            # Add the username to the list of participants
            await self.db.trip.update_one({"trip_id": trip_id}, {'$addToSet': {'participants': username}})

            # Add the username to the messaging room participants
            await self.db.messaging_room.update_one(
                {"trip_id": trip_id},
                {'$addToSet': {'participants': username}}
            )

            return {'statusCode': 200, 'body': json.dumps({'message': 'Joined trip successfully'})}

        except Exception as e:
            return {'statusCode': 500, 'body': json.dumps({'message': 'Internal Server Error'})}

    async def leave_trip(self, event):
        try:
            # Extract trip ID and user ID from the request
            body = json.loads(event['body'])
            trip_id = body.get('trip_id')
            username = body.get('username')

            # Validate the presence of required parameters
            if not trip_id or not username:
                return {'statusCode': 400, 'body': json.dumps({'message': 'Missing required parameters'})}

            # Check if the trip exists
            trip = await self.db.trip.find_one({"trip_id": trip_id})
            if not trip:
                return {'statusCode': 404, 'body': json.dumps({'message': 'Trip not found'})}

            # Remove the user from the list of participants
            await  self.db.trip.update_one({"trip_id": trip_id}, {'$pull': {'participants': username}})

            # Remove the user from the messaging room participants
            await self.db.messaging_room.update_one(
                {"trip_id": trip_id},
                {'$pull': {'participants': username}}
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

    def filter_and_sort_trips(self, event):
        try:
            # Get query parameters from the URL
            location = event['queryStringParameters'].get('location')
            date = event['queryStringParameters'].get('date')

            # Define a base query
            query = {}

            # Add filters based on user preferences
            if location:
                query['location'] = location

            if date:
                query['date'] = date

            # Fetch trips from the database based on the query
            trips = self.db.trip.find(query)

            # Sort trips based on a specific criterion (e.g., date)
            sorted_trips = sorted(trips, key=lambda x: x.get('date', ''))

            # Return the filtered and sorted trips
            return {
                'statusCode': 200,
                'body': json.dumps({'message': 'Trips filtered and sorted successfully', 'trips': sorted_trips})
            }
        except Exception as e:
            return {'statusCode': 500, 'body': json.dumps({'message': 'Internal Server Error'})}
