# trip_data_handler.py
# import random
# import json
# from bson import ObjectId, json_util
# from fastapi import APIRouter, HTTPException, Depends
# from fastapi.security import OAuth2AuthorizationCodeBearer
# from Utils.auth_utils import validate_jwt_token
# from Classes.messaging_room_handler import MessagingRoom
# import datetime


# # from auth_utils import db

# class TripDataHandler:
#     def __init__(self, db):
#         self.db = db

#     async def create_trip(self, event):
#         try:
#             current_time = datetime.datetime.utcnow().isoformat()

#             trip_details = {
#                 'creator_email': event.get('creator_email'),  # Use creator's email instead of username
#                 'start_date': datetime.datetime.strptime(event.get('start_date'), '%a %b %d %Y %H:%M:%S %Z%z').strftime('%Y-%m-%d'),  # Include start date
#                 'end_date': datetime.datetime.strptime(event.get('end_date'), '%a %b %d %Y %H:%M:%S %Z%z').strftime('%Y-%m-%d'),  # Include end date
#                 # 'time': body.get('time'),
#                 'location': event.get('location'),
#                 'description': event.get('description'),
#                 'participants': [event.get('creator_email')],
#                 # add in max people to trip data
#                 'max_people': event.get('participants'),
#                 'trip_id': ''.join([str(random.randint(0, 9)) for _ in range(10)]),
#                 'created_at': current_time  # Include the time and date of creation
#             }

#             result = await self.db.trip.insert_one(trip_details)

#             # README: unsure if room id is needed? as trip id is already unique so it could be used to identify unique rooms as well
#             # README: participants in messaging room will just be a copy of the ones in trip document so unsure if needed?
#             room_id = ''.join([str(random.randint(0, 9)) for _ in range(10)])
#             messaging_room = MessagingRoom(db=self.db, room_id=room_id, trip_id=trip_details['trip_id'],
#                                            participants=[{trip_details.get('creator_email'): 'Name'}])

#             # Save the messaging room details in the database
#             await self.db.messaging_room.insert_one(messaging_room.to_dict())

#             return {'statusCode': 200, 'body': json.dumps(
#                 {'message': 'Trip and messaging room created successfully', 'trip_id': trip_details['trip_id'],
#                  'room_id': room_id})}
#         except Exception as e:
#             print(e)
#             return {'statusCode': 500, 'body': json.dumps({'message': 'Internal Server Error', 'Exception': str(e)})}

#     async def join_trip(self, event):
#         try:
#             # Extract trip ID and username from the request
#             trip_id = event.get('trip_id')
#             email = event.get('email')

#             # Validate the presence of required parameters
#             if not (trip_id or email):
#                 return {'statusCode': 400, 'body': json.dumps({'message': 'Missing required parameters'})}

#             # Check if the trip exists
#             trip = await self.db.trip.find_one({"trip_id": trip_id})
#             if not trip:
#                 return {'statusCode': 404, 'body': json.dumps({'message': 'Trip not found'})}

#             # Add the username to the list of participants
#             await self.db.trip.update_one({"trip_id": trip_id}, {'$addToSet': {'participants': email}})

#             # Add the username to the messaging room participants
#             await self.db.messaging_room.update_one(
#                 {"trip_id": trip_id},
#                 {'$addToSet': {'participants': email}}
#             )
#             # TODO: also add in a joined message to the messaging room -> sender=email, message='', joined=true


#             return {'statusCode': 200, 'body': json.dumps({'message': 'Joined trip successfully'})}

#         except Exception as e:
#             return {'statusCode': 500, 'body': json.dumps({'message': 'Internal Server Error'})}

#     async def leave_trip(self, event):
#         try:
#             # Extract trip ID and user ID from the request
#             trip_id = event.get('trip_id')
#             email = event.get('email')

#             # Validate the presence of required parameters
#             if not trip_id or not email:
#                 return {'statusCode': 400, 'body': json.dumps({'message': 'Missing required parameters'})}

#             # Check if the trip exists
#             trip = await self.db.trip.find_one({"trip_id": trip_id})
#             if not trip:
#                 return {'statusCode': 404, 'body': json.dumps({'message': 'Trip not found'})}

#             # Remove the user from the list of participants
#             await self.db.trip.update_one({"trip_id": trip_id}, {'$pull': {'participants': email}})

#             # Remove the user from the messaging room participants
#             # TODO: method doesnt remove the email from message room participants
#             await self.db.messaging_room.update_one(
#                 {"trip_id": trip_id},
#                 {'$pull': {'participants': email}}
#             )
#             # TODO: also add in a left message to the messaging room -> sender=email, message='', left=true


#             return {'statusCode': 200, 'body': json.dumps({'message': 'Left trip successfully'})}
#         except Exception as e:
#             return {'statusCode': 500, 'body': json.dumps({'message': 'Internal Server Error'})}

#     async def send_trip_invitation(self, event):
#         try:
#             token = event['headers'].get('Authorization', '').split('Bearer ')[-1]
#             decoded_token = validate_jwt_token(token)

#             if decoded_token:

#                 body = json.loads(event['body'])
#                 invited_user_id = body['invited_user_id']
#                 trip_id = body['trip_id']

#                 result = await self.db.trips.update_one(
#                     {"trip_id": trip_id},
#                     {'$addToSet': {'invitations': {'user_id': invited_user_id, 'status': 'pending'}}}
#                 )

#                 if result.matched_count > 0 and result.modified_count > 0:
#                     return {'statusCode': 200, 'body': json.dumps({'message': 'Invitation sent successfully'})}
#                 else:
#                     return {'statusCode': 404, 'body': json.dumps({'message': 'Trip not found'})}
#             else:
#                 return {'statusCode': 401, 'body': json.dumps({'message': 'Invalid or expired token'})}
#         except Exception as e:
#             return {'statusCode': 500, 'body': json.dumps({'message': 'Internal Server Error'})}

#     # async def filter_and_sort_trips(self, event):
#     #     try:
#     #         # Get query parameters from the event
#     #         creator_email = event.get('creator_email')
#     #         user_email = event.get('user_email')
#     #         location = event.get('location')
#     #         start_date = event.get('start_date')
#     #         end_date = event.get('end_date')

#     #         # Define a base query
#     #         query = {}

#     #         # Add filters based on user preferences

#     #         # used to get the user's created trips
#     #         if creator_email:
#     #             query['creator_email'] = creator_email

#     #         # used to get any trips that the user has joined
#     #         if user_email:
#     #             query['participants'] = {"$in": [user_email]}

#     #         if location:
#     #             query['location'] = location

#     #         if start_date and end_date:
#     #             query['start_date'] = {'$gte': start_date, '$lte': end_date}
#     #             query['end_date'] = {'$gte': start_date, '$lte': end_date}

#     #         # TODO: add in functionality to also handle an array of locations and array of start date and end dates
#     #         # TODO: only return open trips -> ones where the number of non-null participants < max_people
#     #         # Fetch trips from the database based on the query
#     #         # remove the oid from results as its unneeded
#     #         cursor = self.db.trip.find(query, {'_id': 0})

#     #         # parse data so its more readable
#     #         def parse_json(data):
#     #             return json.loads(json_util.dumps(data))

#     #         # .find() returns a cursor so async iterate through to get every document
#     #         trips = []
#     #         async for doc in cursor:
#     #             trips.append(parse_json(doc))

#     #         # Sort trips based on a specific criterion (e.g., date)
#     #         sorted_trips = sorted(trips, key=lambda x: x.get('start_date', ''))

#     #         # Return the filtered and sorted trips
#     #         return {
#     #             'statusCode': 200,
#     #             'body': json.dumps({'message': 'Trips filtered and sorted successfully', 'trips': sorted_trips})
#     #         }
#     #     except Exception as e:
#     #         print("error", e)
#     #         return {'statusCode': 500, 'body': json.dumps({'message': 'Internal Server Error'})}
#     async def filter_and_sort_trips(self, event):
#         try:
#             # Get query parameters from the event
#             creator_email = event.get('creator_email')
#             user_email = event.get('user_email')
#             locations = event.get('locations', [])  # Assuming locations is a list of dictionaries
#             dates = event.get('dates', [])  # Assuming dates is a list of lists containing start and end dates

#             # Define a base query
#             query = {}

#             # Add filters based on user preferences

#             # Used to get the user's created trips
#             if creator_email:
#                 query['creator_email'] = creator_email

#             # Used to get any trips that the user has joined
#             if user_email:
#                 query['participants'] = {"$in": [user_email]}

#             # Adding location and date filters
#             query["$or"] = []
#             if locations:
#                 query["$or"].append({"location": {"$in": locations}})

#             if dates:
#                 date_query = {"$or": []}
#                 for date_range in dates:
#                     start_date, end_date = date_range
#                     date_query["$or"].append({"start_date": {"$gte": start_date, "$lte": end_date}})
#                     date_query["$or"].append({"end_date": {"$gte": start_date, "$lte": end_date}})
#                 query["$or"].append(date_query)

#             if not query["$or"]:
#                 del query["$or"]

#             # Fetch trips from the database based on the query
#             cursor = self.db.trip.find(query)

#             # Parse data so it's more readable
#             def parse_json(data):
#                 return json.loads(json_util.dumps(data))

#             # .find() returns a cursor so async iterate through to get every document
#             trips = []
#             async for doc in cursor:
#                 trips.append(parse_json(doc))

#             # Sort trips based on a specific criterion (e.g., date)
#             sorted_trips = sorted(trips, key=lambda x: x.get('start_date', ''))

#             # Return the filtered and sorted trips
#             return {
#                 'statusCode': 200,
#                 'body': json.dumps({'message': 'Trips filtered and sorted successfully', 'trips': sorted_trips})
#             }
#         except Exception as e:
#             print("error", e)
#             return {'statusCode': 500, 'body': json.dumps({'message': 'Internal Server Error'})}


#     def update_trip(self, event: dict):
#         # TODO: update the trip in the database
#         # event will have the keys: tripid, numpeople, description
#         return None

#     def delete_trip(self, event: dict):
#         # TODO: remove trip from the db
#         # event will have the keys: tripid, numpeople
#         # shouldnt allow deletion if theres >1 num people
#         return None

#     async def get_trip_details(self, event: dict):
#         # TODO: return trip details from db -> for use in chat screen and group info screen
#         # event will only have tripid, and user email
#         # verify that the data should be returned only if the user email is in list of participants, otherwise dont return
#         # return the details of the trip record
#         query = {}
#         query['trip_id'] = event.get('trip_id')
#         query['participants'] = {"$in": [event.get('user_email')]}

#         return await self.db.trip.find_one(query, {'_id': 0})
import random
import json
from bson import ObjectId
from Utils.auth_utils import validate_jwt_token
from Classes.messaging_room_handler import MessagingRoom
import datetime
import logging


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
                                           participants=[{trip_details.get('creator_email'): 'Name'}])

            # Save the messaging room details in the database
            await self.db.messaging_room.insert_one(messaging_room.to_dict())

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
            # TODO: also add in a joined message to the messaging room -> sender=email, message='', joined=true

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
            print(trip)

            # Remove the user from the invited_user_email arrays in invitations
            await self.db.trip.update_one({"trip_id": trip_id},
                                          {'$pull': {'invitations.$[].invited_user_email': email}})
            print(trip)

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

            return {'statusCode': 200, 'body': json.dumps({'message': 'Left trip successfully'})}
        except Exception as e:
            return {'statusCode': 500, 'body': json.dumps({'message': 'Internal Server Error'})}


    async def send_trip_invitation(self, event):
        try:
            token = event['headers'].get('Authorization', '').split('Bearer ')[-1]
            decoded_token = validate_jwt_token(token)

            if decoded_token:
                body = json.loads(event["body"])  # Parse the JSON body
                invited_user_emails = [body.get("invited_user_emails")]
                trip_id = body.get("trip_id")

                if not invited_user_emails or not trip_id:
                    return {'statusCode': 400, 'body': json.dumps({'message': 'Invalid payload'})}

                # Find the trip document using its ID
                trip = await self.db.trip.find_one({"trip_id": trip_id})
                print("trip:",trip)

                if not trip:
                    # If not found, try finding the trip by _id
                    trip = await self.db.trips.find_one({"_id": ObjectId(trip_id)})
                    if not trip:
                        return {'statusCode': 404, 'body': json.dumps({'message': 'Trip not found'})}

                # Check if the user is already a member
                participants = trip.get('participants', [])
                print("participants:",participants)
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
                    print("invited_user_emails:",invited_user_emails)

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
                # Calculate total participants and invited users count
                total_participants = len(participants) + sum(1 for inv in trip['invitations'] if inv.get('invited_user_email'))
                # total_participants = len([participants]+[invited_user_emails])
                # Update max_people field
                trip['max_people'] = total_participants
                if not trips_id:
                    return {'statusCode': 404, 'body': json.dumps({'message': 'Trip not found'})}

                # Update the trip document with the new 'invitations' list
                result = await self.db.trip.update_one(
                    {"_id": ObjectId(trips_id)},
                    {'$set': {"invitations": trip['invitations'], "max_people": total_participants}}
                )
                print(result)
                if result.matched_count > 0 and result.modified_count > 0:
                    return {'statusCode': 200, 'body': json.dumps({'message': 'Invitations sent successfully'})}
                else:
                    return {'statusCode': 500, 'body': json.dumps({'message': 'Failed to update trip document'})}
            else:
                return {'statusCode': 401, 'body': json.dumps({'message': 'Invalid or expired token'})}
        except json.JSONDecodeError as json_error:
            return {'statusCode': 400, 'body': json.dumps({'message': 'Invalid JSON format in request body'})}
        except Exception as e:
            return {'statusCode': 500, 'body': json.dumps({'message': str(e)})}  # Convert the exception to string

    #         # TODO: add in functionality to also handle an array of locations and array of start date and end dates

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

