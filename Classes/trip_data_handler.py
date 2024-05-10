
import random
import json
from bson import ObjectId
from fastapi import HTTPException
from Classes.messaging_room_handler import MessagingRoom
import datetime
import logging
from Utils.mongo_utils import MongoUtils

mongo_instance = MongoUtils()
mongo = mongo_instance.connect_to_database()


# from auth_utils import db

class TripDataHandler:
    def __init__(self, db):
        self.db = db

    async def create_trip(self, event):
        try:
            current_time = datetime.datetime.utcnow().isoformat()
            # Check if start_date and end_date are provided and not None
            start_date_str = event.get('start_date')
            end_date_str = event.get('end_date')
            if start_date_str is None or end_date_str is None:
                return {'statusCode': 400, 'body': json.dumps({'message': 'start_date or end_date is missing'})}

            trip_details = {
                'creator_email': event.get('creator_email'),  # Use creator's email instead of username
                'start_date': datetime.datetime.strptime(start_date_str, '%a %b %d %Y %H:%M:%S %Z%z').strftime(
                    '%Y-%m-%d'),  # Include start date
                'end_date': datetime.datetime.strptime(end_date_str, '%a %b %d %Y %H:%M:%S %Z%z').strftime('%Y-%m-%d'),
                # Include end date
                # 'time': body.get('time'),
                'location': event.get('location'),
                'description': event.get('description'),
                'participants': [event.get('creator_email')] + event.get('participants', []),
                # Include creator's email and other participants
                # add in max people to trip data
                'max_people': len(event.get('participants', [])) + 1,  # Count total participants including creator
                'trip_id': ''.join([str(random.randint(0, 9)) for _ in range(10)]),
                'created_at': current_time  # Include the time and date of creation
            }

            result = await self.db.trip.insert_one(trip_details)

            # README: unsure if room id is needed? as trip id is already unique so it could be used to identify unique rooms as well
            # README: participants in messaging room will just be a copy of the ones in trip document so unsure if needed?
            room_id = ''.join([str(random.randint(0, 9)) for _ in range(10)])
            messaging_room = MessagingRoom(db=self.db, room_id=room_id, trip_id=trip_details['trip_id'],
                                           participants=[{trip_details.get('creator_email'): 'Created the trip'}])

            # Save the messaging room details in the database
            await self.db.messaging_room.insert_one(messaging_room.to_dict())
            await self.db.messaging_room.update_one(
                {"trip_id": trip_details['trip_id']},
                {'$push': {'messages': {'sender': trip_details.get('creator_email'), 'message': 'Joined Trip Successfully', 'joined': True}}}
            )

            return {'statusCode': 200, 'body': json.dumps(
                {'message': 'Trip and messaging room created successfully', 'trip_id': trip_details['trip_id'],
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
            await self.db.messaging_room.update_one(
                {"trip_id": trip_id},
                {'$push': {'messages': {'sender': email, 'message': 'Joined Trip Successfully', 'joined': True}}}
            )

            # Get the updated trip document
            updated_trip = await self.db.trip.find_one({"trip_id": trip_id})
            # Get the current number of participants (excluding the creator)
            current_participants = len(updated_trip.get('participants', []))  # Add 1 for the creator
            print("current_participants", current_participants)

            # Update the max_people field in the trip document
            await self.db.trip.update_one({"trip_id": trip_id}, {'$set': {'max_people': current_participants}})


            return {'statusCode': 200, 'body': json.dumps({'message': 'Joined trip successfully'})}

        except Exception as e:
            return {'statusCode': 500, 'body': json.dumps({'message': 'Internal Server Error'})}

    async def leave_trip(self, event):
        try:
            # Extract trip ID and user email from the request
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

            # Add a message to the messaging room indicating the user has left
            await self.db.messaging_room.update_one(
                {"trip_id": trip_id},
                {'$push': {'messages': {'sender': email, 'message': f'{email} left the messaging room', 'left': True}}}
            )

            # Check if the leaving user is the creator
            if email == trip['creator_email']:
                # If the leaving user is the creator, decrement max_people by 1
                new_max_people = max(0, trip.get('max_people', 0) - 1)
            else:
                # Get the updated trip document
                updated_trip = await self.db.trip.find_one({"trip_id": trip_id})

                # Check if 'invitations' field exists in the document
                if 'invitations' in updated_trip:
                    # Remove the user from the invited_user_email arrays in invitations
                    await self.db.trip.update_one({"trip_id": trip_id},
                                                  {'$pull': {'invitations.$[].invited_user_email': email}})

                # Calculate the number of participants left
                participants_left = len(updated_trip.get('participants', []))

                # Update the max_people count by subtracting the number of participants left
                new_max_people = max(0, trip.get('max_people', 0) - participants_left)

            # Update the trip document with the new max_people count
            await self.db.trip.update_one({"trip_id": trip_id}, {'$set': {'max_people': new_max_people}})

            return {'statusCode': 200, 'body': json.dumps({'message': 'Left trip successfully'})}
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")  # Log the error
            return {'statusCode': 500, 'body': json.dumps({'message': 'Internal Server Error'})}


    async def fetch_joined_invitees(self, db, trip_id: str):
        try:
            # Find the messaging room for the given trip ID
            messaging_room = await db["messaging_room"].find_one({"trip_id": trip_id})
            if messaging_room:
                # Fetch participants with joined=true from messaging_room
                messaging_room_joined = await db["messaging_room"].find_one(
                    {"trip_id": trip_id, "messages.joined": True})
                if messaging_room_joined:
                    messages = messaging_room_joined.get("messages", [])
                    last_joined_message = next(
                        (
                            message
                            for message in reversed(messages)
                            if "joined" in message and message["joined"]
                        ),
                        None,
                    )
                    print("last_joined_message", last_joined_message)
                    # Fetch user details for users who have not left
                    valid_emails = set()
                    for message in messages:
                        if "joined" in message and message["joined"]:
                            valid_emails.add(message["sender"])
                        if "left" in message and message["left"]:
                            valid_emails.discard(message["sender"])

                    return {"joined_emails": valid_emails}
                else:
                    return {"joined_emails": [], "message": "No participants have joined the messaging room"}
            else:
                return {"joined_emails": [],
                        "message": "No messaging room found for the trip ID"}  # Return empty list if no messaging room found for the trip ID
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))



    async def send_trip_invitation(self, event):
        try:
            # body = json.loads(event["body"])  # Parse the JSON body
            invited_user_emails = [event.get("invited_user_emails", [])]
            trip_id = event.get("trip_id")

            if not invited_user_emails or not trip_id:
                return {'statusCode': 400, 'body': json.dumps({'message': 'Invalid payload'})}

            # Find the trip document using its ID
            trip = await self.db.trip.find_one({"trip_id": trip_id})
            print("trip:", trip)

            if not trip:
                # If not found, try finding the trip by _id
                trip = await self.db.trips.find_one({"_id": ObjectId(trip_id)})
                if not trip:
                    return {'statusCode': 404, 'body': json.dumps({'message': 'Trip not found'})}

            # Check if the user is already a member
            participants = trip.get('participants', [])
            print("participants:", participants)
            for invited_user_email in invited_user_emails:
                if invited_user_email in participants:
                    return {'statusCode': 400,
                            'body': json.dumps({'message': 'User is already a member of the trip'})}

            # Check if the user has already been invited
            invitations = trip.get('invitations', [])

            # Check if the user has already been invited
            for invited_user_email in invited_user_emails:
                if any(isinstance(invitation, dict) and invitation.get('invited_user_email') == invited_user_email
                       for
                       invitation in invitations):
                    return {'statusCode': 400,
                            'body': json.dumps({'message': 'User has already been invited to the trip'})}
                print("invited_user_emails:", invited_user_emails)

            if 'invitations' not in trip:
                trip['invitations'] = []

            # Add the new invitations
            new_invitations = [{'invited_user_email': invited_user_email, 'status': 'invited'} for
                               invited_user_email in
                               invited_user_emails]
            trip['invitations'].extend(new_invitations)
            print(new_invitations)
            trips_id = trip.get("_id")
            print(trips_id)
            # Calculate total participants considering both participants and invited users
            group_members_response = await self.fetch_joined_invitees(trip_id=trip_id, db=mongo)
            group_members = group_members_response.get("joined_emails", [])
            print("group_members", group_members)
            total_participants = len(trip.get('participants', []))
            print("total_participants", total_participants)
            if group_members:
                total_participants += len(group_members)
                print("total_participants", total_participants)
            trip['max_people'] = total_participants
            if not trips_id:
                return {'statusCode': 404, 'body': json.dumps({'message': 'Trip not found'})}

            # Update the trip document with the new 'invitations' list
            result = await self.db.trip.update_one(
                {"_id": ObjectId(trips_id)},
                {'$set': {"invitations": trip['invitations'], "max_people": total_participants}}
            )
            # print(result)
            if result.matched_count > 0 and result.modified_count > 0:
                return {'statusCode': 200, 'body': json.dumps({'message': 'Invitations sent successfully'})}
            else:
                return {'statusCode': 500, 'body': json.dumps({'message': 'Failed to update trip document'})}
        except json.JSONDecodeError as json_error:
            return {'statusCode': 400, 'body': json.dumps({'message': 'Invalid JSON format in request body'})}
        except Exception as e:
            return {'statusCode': 500, 'body': json.dumps({'message': str(e)})}  # Convert the exception to string


    async def filter_and_sort_trips(self, event):
        try:
            # Get query parameters from the event
            creator_email = event.get("creator_email")
            users = event.get("users", [])
            locations = event.get("location", [])
            dates = event.get("dates", [])

            # Define a base query
            query = {'creator_email': creator_email}

            # Add filters based on users
            if users:
                query['participants'] = {'$in': users}

            # Add filters based on locations and dates
            location_date_queries = []
            for location in locations:
                date_queries = []
                for start_date, end_date in dates:
                    date_query = {
                        '$and': [
                            {'start_date': {'$gte': start_date, '$lte': end_date}},
                            {'end_date': {'$gte': start_date, '$lte': end_date}}
                        ]
                    }
                    date_queries.append(date_query)

                location_date_query = {
                    'location': location,
                    '$or': date_queries
                }
                location_date_queries.append(location_date_query)

            query['$or'] = location_date_queries
            if not query['creator_email']:
                del query['creator_email']
            if not query['$or']:
                del query['$or']


            # Fetch trips from the database based on the query
            cursor = self.db.trip.find(query)

            # Parse data so it's more readable
            trips = [doc async for doc in cursor]
            for trip in trips:
                trip['_id'] = str(trip['_id'])

            # Sort trips based on start_date
            sorted_trips = sorted(trips, key=lambda x: x.get("start_date", ""))

            # Return the filtered and sorted trips
            return {
                'statusCode': 200,
                'body': json.dumps({'message': 'Trips filtered and sorted successfully', 'trips': sorted_trips})
            }
        except Exception as e:
            print("Error:", e)
            return {'statusCode': 500, 'body': json.dumps({'message': 'Internal Server Error'})}

    async def update_trip(self, event: dict):
        try:
            # Extract trip ID and other details from the event
            trip_id = event.get('trip_id')
            num_people = event.get('num_people')
            description = event.get('description')

            # Validate if trip_id is provided
            if not trip_id:
                return {'statusCode': 400, 'body': json.dumps({'message': 'Missing trip_id'})}

            # Update the trip details in the database
            result = await self.db.trip.update_one(
                {"trip_id": trip_id},
                {'$set': {'num_people': num_people, 'description': description}}
            )

            if result.matched_count > 0 and result.modified_count > 0:
                return {'statusCode': 200, 'body': json.dumps({'message': 'Trip updated successfully'})}
            else:
                return {'statusCode': 404, 'body': json.dumps({'message': 'Trip not found'})}
        except Exception as e:
            return {'statusCode': 500, 'body': json.dumps({'message': str(e)})}  # Return 500 for internal server error


    async def delete_trip(self, event: dict):
        try:
            # Extract trip ID from the event
            trip_id = event.get('trip_id')

            # Validate if trip_id is provided
            if not trip_id:
                return {'statusCode': 400, 'body': json.dumps({'message': 'Missing trip_id'})}

            # Delete the trip from the database
            result = await self.db.trip.delete_one({"trip_id": trip_id})

            if result.deleted_count > 0:
                return {'statusCode': 200, 'body': json.dumps({'message': 'Trip deleted successfully'})}
            else:
                return {'statusCode': 404, 'body': json.dumps({'message': 'Trip not found'})}
        except Exception as e:
            return {'statusCode': 500, 'body': json.dumps({'message': str(e)})}  # Return 500 for internal server error


    # async def get_trip_details(self, event: dict):
    #     # TODO: return trip details from db -> for use in chat screen and group info screen
    #     # event will only have tripid, and user email
    #     # verify that the data should be returned only if the user email is in list of participants, otherwise dont return
    #     # return the details of the trip record
    #     query = {}
    #     query['trip_id'] = event.get('trip_id')
    #     query['participants'] = {"$in": [event.get('user_email')]}
    #
    #     return await self.db.trip.find_one(query, {'_id': 0})

    async def get_trip_details(self, event: dict):
        try:
            # Get trip_id and user_email from the event
            trip_id = event.get('trip_id')
            creator_email = event.get('creator_email')

            # Check if trip_id and user_email are provided
            if not trip_id or not creator_email:
                return {'statusCode': 400, 'body': json.dumps({'message': 'Missing trip_id or creator_email'})}

            # Query to find the trip details
            query = {
                'trip_id': trip_id,
                'participants': creator_email
            }

            # Find the trip details from the database
            trip_details = await self.db.trip.find_one(query, {'_id': 0})

            if trip_details:
                return {'statusCode': 200,
                        'body': json.dumps({'message': 'Trip details found', 'trip_details': trip_details})}
            else:
                return {'statusCode': 404, 'body': json.dumps({'message': 'Trip not found or user not a participant'})}
        except Exception as e:
            # Log the exception for debugging purposes
            # logging.error(f"An error occurred: {str(e)}")
            return {'statusCode': 500, 'body': json.dumps({'message': 'Internal Server Error'})}

