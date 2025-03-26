import os
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from dotenv import load_dotenv
from models.mbti_analyzer import MBTIAnalyzer
from models.voice_processor import VoiceProcessor

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

# Initialize MBTI analyzer and voice processor
mbti_analyzer = MBTIAnalyzer()
voice_processor = VoiceProcessor()

@app.route('/')
def index():
    """Render the main page of the application."""
    return render_template('index.html')

@app.route('/result')
def result():
    """Render the result page of the application."""
    return render_template('result.html')

def handle_voice_input(text):
    """Handle voice input from the speech recognition."""
    # Process the voice input and emit response
    response, is_complete, mbti_result = mbti_analyzer.process_message(text)
    
    # Emit the response back to the client
    socketio.emit('response', {
        'message': response,
        'is_complete': is_complete,
        'mbti_result': mbti_result,
        'voice_input': text
    })
    
    # Convert response to speech
    voice_processor.text_to_speech(response)

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
        'mbti_result': mbti_result,
        'voice_input': None
    })
    
    # Convert response to speech
    voice_processor.text_to_speech(response)

@socketio.on('start_voice')
def handle_start_voice():
    """Start voice recognition."""
    success = voice_processor.start_listening(handle_voice_input)
    emit('voice_status', {'status': 'started' if success else 'error'})

@socketio.on('stop_voice')
def handle_stop_voice():
    """Stop voice recognition."""
    voice_processor.stop_listening()
    emit('voice_status', {'status': 'stopped'})

@socketio.on('disconnect')
def handle_disconnect():
    """Clean up resources on client disconnect."""
    voice_processor.cleanup()

if __name__ == '__main__':
    try:
        socketio.run(app, debug=True)
    finally:
        voice_processor.cleanup() 