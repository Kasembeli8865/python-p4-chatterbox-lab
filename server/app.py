from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)
@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if request.method == 'GET':
        # Query the database to get all messages, ordered by created_at in ascending order
        messages = Message.query.order_by(Message.created_at.asc()).all()

        # Serialize the messages into a list of dictionaries
        messages_list = [{
            'username': message.username,
            'body': message.body,
            'created_at': message.created_at
        } for message in messages]

        # Create a JSON response with the ordered messages
        response = jsonify(messages_list)
        return response, 200

    elif request.method == 'POST':
        # Create a new message using data from the request form
        username = request.form.get('username')
        body = request.form.get('body')
        new_message = Message(username=username, body=body)

        db.session.add(new_message)
        db.session.commit()

        message_dict = {
            'username': new_message.username,
            'body': new_message.body,
            'created_at': new_message.created_at
        }

        # Create a JSON response with the newly created message
        response = jsonify(message_dict)
        return response, 201

@app.route('/messages/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def message_by_id(id):
    message = Message.query.get(id)

    if not message:
        return jsonify({'message': 'Message not found'}), 404

    if request.method == 'GET':
        message_dict = {
            'username': message.username,
            'body': message.body,
            'created_at': message.created_at
        }

        response = jsonify(message_dict)
        return response, 200

    elif request.method == 'PATCH':
        # Update the body of the message using data from the request form
        new_body = request.form.get('body')
        message.body = new_body
        db.session.commit()

        message_dict = {
            'username': message.username,
            'body': message.body,
            'created_at': message.created_at
        }

        response = jsonify(message_dict)
        return response, 200

    elif request.method == 'DELETE':
        db.session.delete(message)
        db.session.commit()

        response_body = {
            'delete_successful': True,
            'message': 'Message deleted.'
        }

        response = jsonify(response_body)
        return response, 200

if __name__ == '__main__':
    app.run(port=5555)