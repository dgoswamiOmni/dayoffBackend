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

    async def send_message(self,event):
        try:
            # Extract data from the request payload
            token = event['headers'].get('Authorization', '').split('Bearer ')[-1]
            decoded_token = validate_jwt_token(token)


            if not decoded_token:
                return {'statusCode': 401, 'body': json.dumps({'message': 'Invalid or expired token'})}

            body = json.loads(event['body'])
            room_id = body.get('room_id')
            sender = decoded_token['sub']
            message_text = body.get('message')

            # Add logic to send messages to the messaging room
            timestamp = datetime.utcnow()
            message = {'sender': sender, 'message': message_text, 'timestamp': timestamp}

            # Update the messaging room in the database with the new message
            await self.db.messaging_room.update_one(
                {'room_id': room_id},
                {'$addToSet': {'messages': message}}
            )

            return {'statusCode': 200, 'body': json.dumps({'message': 'Message sent successfully'})}
        except Exception as e:
            return {'statusCode': 500, 'body': json.dumps({'message': 'Internal Server Error', 'Exception': str(e)})}

    async def get_messages(self, room_id):
        try:
            # Add logic to retrieve messages from the messaging room
            messaging_room = await self.db.messaging_room.find_one({'room_id': room_id})

            if messaging_room:
                messages = messaging_room.get('messages', [])
                return {'statusCode': 200, 'body': json.dumps({'messages': messages})}
            else:
                return {'statusCode': 404, 'body': json.dumps({'message': 'Messaging room not found'})}
        except Exception as e:
            return {'statusCode': 500, 'body': json.dumps({'message': 'Internal Server Error', 'Exception': str(e)})}
