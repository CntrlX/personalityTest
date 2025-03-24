import os
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from dotenv import load_dotenv
from models.mbti_analyzer import MBTIAnalyzer

# Load environment variables
load_dotenv()

# Check for OpenAI API key
if not os.environ.get("OPENAI_API_KEY"):
    print("WARNING: OPENAI_API_KEY environment variable is not set.")
    print("Please add it to your .env file or environment variables.")

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'mbti-personality-test'
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize MBTI analyzer
mbti_analyzer = MBTIAnalyzer()

@app.route('/')
def index():
    """Render the main page of the application."""
    return render_template('index.html')

@app.route('/result')
def result():
    """Render the result page of the application."""
    return render_template('result.html')

@socketio.on('message')
def handle_message(data):
    """Handle incoming messages from the client."""
    user_message = data.get('message', '')
    
    # Process the message and get a response
    response, is_complete, mbti_result = mbti_analyzer.process_message(user_message)
    
    # Emit the response back to the client
    emit('response', {
        'message': response,
        'is_complete': is_complete,
        'mbti_result': mbti_result
    })

if __name__ == '__main__':
    socketio.run(app, debug=True) 