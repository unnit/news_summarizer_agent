"""Flask Web Application for News Summarizer Agent."""

import os
import sys
import json
import asyncio
import threading
import uuid
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
from flask_cors import CORS
from werkzeug.utils import secure_filename

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from main import NewsSummarizerAgent
from tools.messenger_sender import MessengerSender, run_async

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')
CORS(app)

# Configuration
app.config['UPLOAD_FOLDER'] = Config.OUTPUT_DIR
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Increase timeout settings for long-running operations
app.config['PERMANENT_SESSION_LIFETIME'] = 300  # 5 minutes
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 300   # 5 minutes

# Initialize the news summarizer agent
try:
    agent = NewsSummarizerAgent()
    print("News Summarizer Agent initialized successfully")
except Exception as e:
    print(f"Error initializing agent: {e}")
    agent = None

# Initialize messenger sender
messenger_sender = MessengerSender()

# Task storage for async processing
task_storage = {}
task_lock = threading.Lock()

def process_news_task(task_id, mobile_number, news_category, country, voice_id):
    """Process news generation in background thread."""
    try:
        with task_lock:
            task_storage[task_id]['status'] = 'processing'
            task_storage[task_id]['progress'] = 10
            task_storage[task_id]['message'] = 'Starting news generation...'
        
        # Step 1: Fetch news
        with task_lock:
            task_storage[task_id]['progress'] = 25
            task_storage[task_id]['message'] = 'Fetching news articles...'
        
        results = agent.run_complete_workflow(
            news_category=news_category,
            country=country,
            voice_id=voice_id,
            send_messages=True
            #chat_id=mobile_number
        )
        
        with task_lock:
            if results['success']:
            #     task_storage[task_id]['progress'] = 80
            #     task_storage[task_id]['message'] = 'Sending messages...'
                
            #     # Priority 1: Send via Telegram (preferred)
            #     telegram_success = False
            #     telegram_message = 'Telegram not configured'
                
            #     if messenger_sender.telegram_bot:
            #         try:
            #             # Use the provided chat ID directly (could be username, chat ID, or phone number)
            #             telegram_chat_id = 
            #             message_text = f"Your daily news summary is ready!"
            #             # Send text message
            #             telegram_success = run_async(
            #                 messenger_sender.send_telegram_message(message_text, telegram_chat_id)
            #             )
                        
            #             # Send audio file if available
            #             audio_success = False
            #             if results.get('audio_path') and os.path.exists(results.get('audio_path')):
            #                 audio_success = run_async(
            #                     messenger_sender.send_telegram_audio(
            #                         results['audio_path'], 
            #                         "Your news summary audio",
            #                         telegram_chat_id
            #                     )
            #                 )
                        
            #             task_storage[task_id]['telegram_sent'] = telegram_success
            #             task_storage[task_id]['telegram_audio_sent'] = audio_success
            #             task_storage[task_id]['telegram_message'] = 'Telegram message sent successfully!' if telegram_success else 'Failed to send Telegram message'
                        
            #         except Exception as e:
            #             task_storage[task_id]['telegram_sent'] = False
            #             task_storage[task_id]['telegram_audio_sent'] = False
            #             task_storage[task_id]['telegram_message'] = f'Telegram error: {str(e)}'
            #     else:
                
                # Update final status
                task_storage[task_id]['status'] = 'completed'
                task_storage[task_id]['progress'] = 100
                task_storage[task_id]['message'] = 'News summary generated successfully!'
                task_storage[task_id]['result'] = {
                    'success': True,
                    'audio_url': f'/download/{os.path.basename(results.get("audio_path", ""))}',
                    'articles_count': results.get('articles_fetched', 0),
                    'summary_generated': results.get('summary_generated', False),
                    'audio_created': results.get('audio_created', False),
                    'timestamp': datetime.now().isoformat(),
                    'telegram_sent': True,
                    'telegram_audio_sent': True,
                    'telegram_message': 'Telegram message sent successfully!'
                }
            else:
                task_storage[task_id]['status'] = 'failed'
                task_storage[task_id]['message'] = f"Failed: {', '.join(results.get('errors', ['Unknown error']))}"
                task_storage[task_id]['result'] = {
                    'success': False,
                    'error': f"Failed to generate news summary: {', '.join(results.get('errors', ['Unknown error']))}"
                }
                
    except Exception as e:
        with task_lock:
            task_storage[task_id]['status'] = 'failed'
            task_storage[task_id]['message'] = f'Error: {str(e)}'
            task_storage[task_id]['result'] = {
                'success': False,
                'error': f'An error occurred: {str(e)}'
            }

@app.route('/')
def index():
    """Main page with the form."""
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_news():
    """Start news generation task and return task ID."""
    try:
        # Get form data
        mobile_number = request.form.get('mobile_number', '').strip()
        news_category = request.form.get('category', 'general')
        country = request.form.get('country', 'us')
        voice_id = request.form.get('voice', 'Joanna')
        
        # Validate inputs
        if not mobile_number:
            return jsonify({
                'success': False,
                'error': 'Chat ID is required'
            }), 400
        
        # Validate mobile number format (basic validation)
        # if not mobile_number.replace('+', '').replace('-', '').replace(' ', '').isdigit():
        #     return jsonify({
        #         'success': False,
        #         'error': 'Please enter a valid mobile number'
        #     }), 400
        
        # Check if agent is available
        if not agent:
            return jsonify({
                'success': False,
                'error': 'News summarizer agent is not available. Please check your configuration.'
            }), 500
        
        # Create unique task ID
        task_id = str(uuid.uuid4())
        
        # Initialize task status
        with task_lock:
            task_storage[task_id] = {
                'status': 'queued',
                'progress': 0,
                'message': 'Task queued for processing...',
                'created_at': datetime.now().isoformat(),
                'mobile_number': mobile_number
            }
        
        # Start background thread
        thread = threading.Thread(
            target=process_news_task,
            args=(task_id, mobile_number, news_category, country, voice_id)
        )
        thread.daemon = True
        thread.start()
        
        print(f"Started news generation task {task_id} for {mobile_number}")
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'message': 'News generation started. Use the task_id to check progress.',
            'status_url': f'/task/{task_id}'
        })
        
    except Exception as e:
        print(f"Error in generate_news: {e}")
        return jsonify({
            'success': False,
            'error': f'An error occurred: {str(e)}'
        }), 500

@app.route('/task/<task_id>')
def get_task_status(task_id):
    """Get the status of a news generation task."""
    try:
        with task_lock:
            if task_id not in task_storage:
                return jsonify({
                    'success': False,
                    'error': 'Task not found'
                }), 404
            
            task_data = task_storage[task_id].copy()
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'status': task_data['status'],
            'progress': task_data['progress'],
            'message': task_data['message'],
            'created_at': task_data['created_at'],
            'result': task_data.get('result')
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/download/<filename>')
def download_file(filename):
    """Download audio file."""
    try:
        # Secure the filename
        secure_name = secure_filename(filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_name)
        
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True, download_name=secure_name)
        else:
            return jsonify({'error': 'File not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/status')
def status():
    """Get application status."""
    try:
        if agent:
            agent_status = agent.get_status()
        else:
            agent_status = {'error': 'Agent not initialized'}
        
        return jsonify({
            'agent_available': agent is not None,
            'agent_status': agent_status,
            'messenger_platforms': messenger_sender.get_available_platforms(),
            'messenger_config': messenger_sender.validate_configuration(),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/voices')
def get_voices():
    """Get available Polly voices."""
    try:
        if agent and hasattr(agent, 'tts_converter'):
            voices = agent.tts_converter.get_available_voices()
            recommended = agent.tts_converter.get_recommended_voices()
            
            return jsonify({
                'success': True,
                'voices': [
                    {
                        'id': voice.get('Id'),
                        'name': voice.get('Name'),
                        'language': voice.get('LanguageCode'),
                        'gender': voice.get('Gender'),
                        'neural': 'neural' in voice.get('SupportedEngines', [])
                    }
                    for voice in voices
                ],
                'recommended': recommended
            })
        else:
            return jsonify({
                'success': False,
                'error': 'TTS converter not available'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Create output directory if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Run the Flask app with increased timeout
    print("Starting News Summarizer Web App...")
    print("Access the web interface at: http://localhost:8000")
    print("Async processing enabled - long operations won't timeout!")
    app.run(debug=True, host='0.0.0.0', port=8000, threaded=True)
