from datetime import datetime
import json
from Utils.auth_utils import validate_jwt_token


class MessagingRoom:

    def __init__(self, db , room_id, trip_id, participants=None, messages=None):
        self.db = db
        self.room_id = room_id
        self.trip_id = trip_id
        self.participants = participants or []
        self.messages = messages or []

    def to_dict(self):
        return {
            'room_id': self.room_id,
            'trip_id': self.trip_id,
            'participants': self.participants,
            'messages': self.messages,

        }

    """ TODO: get the room id from the trip id? trip id id unique and each group will only have 1 chat so trip id could be used for identifying
     unique chats """
    # there is a one-to-one relationship between trip id and room id
    def get_room_id(self, trip_id: str):
        return "11"

    async def send_message(self, event):
        try:
            # Extract data from the request payload
            trip_id = event.get('trip_id')
            sender = event.get('user_email')
            message_text = event.get('message')

            # Add logic to send messages to the messaging room
            timestamp = str(datetime.utcnow())
            message = {'sender': sender, 'message': message_text, 'timestamp': timestamp}

            # Update the messaging room in the database with the new message
            await self.db.messaging_room.update_one(
                {'trip_id': trip_id},
                {'$addToSet': {'messages': message}}
            )

            return {'statusCode': 200, 'body': json.dumps({'message': 'Message sent successfully'})}
        except Exception as e:
            return {'statusCode': 500, 'body': json.dumps({'message': 'Internal Server Error', 'Exception': str(e)})}

    async def get_messages(self, trip_id):
        try:
            # Add logic to retrieve messages from the messaging room
            messaging_room = await self.db.messaging_room.find_one({'trip_id': trip_id})

            if messaging_room:
                messages = messaging_room.get('messages', [])
                return {'statusCode': 200, 'body': json.dumps({'messages': messages})}
            else:
                return {'statusCode': 404, 'body': json.dumps({'message': 'Messaging room not found', 'messages': []})}
        except Exception as e:
            return {'statusCode': 500, 'body': json.dumps({'message': 'Internal Server Error', 'Exception': str(e)})}
