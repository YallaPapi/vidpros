"""
api.py - VideoReach AI Minimal API Wrapper
Following ZAD Core-First Mandate: Phase 2 - API Wrapper

This minimal API exposes the proven core video generation function.
Single endpoint: POST /api/generate-video

Requirements:
- Flask for minimal API
- Uses proven core_test.py functions
- No authentication yet (per VRA-004)
- Returns video URL and metadata
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import time
from typing import Dict, Optional
from dotenv import load_dotenv

# Import the proven core function
from core_test import generate_video_did

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for browser testing

# Configuration
app.config['JSON_SORT_KEYS'] = False
app.config['DEBUG'] = os.environ.get('DEBUG', 'false').lower() == 'true'

@app.route('/api/generate-video', methods=['POST'])
def generate_video():
    """
    Single endpoint to generate video.
    
    Expected JSON payload:
    {
        "script": "Video script text",
        "avatarId": "optional_avatar_id",  # Not used yet for D-ID
        "voiceId": "optional_voice_id"      # Not used yet for D-ID
    }
    
    Returns:
    {
        "success": true/false,
        "videoUrl": "https://...",
        "duration": 19,
        "cost": 0.10,
        "provider": "D-ID",
        "generationTime": 15.5,
        "error": "error message if failed"
    }
    """
    try:
        # Get request data
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400
        
        # Extract script
        script = data.get('script')
        
        if not script:
            return jsonify({
                'success': False,
                'error': 'Script is required'
            }), 400
        
        # Validate script length (45 seconds max ~ 250 words)
        word_count = len(script.split())
        if word_count > 250:
            return jsonify({
                'success': False,
                'error': f'Script too long: {word_count} words (max 250)'
            }), 400
        
        # Log request
        print(f"📥 Video generation request received")
        print(f"📝 Script length: {word_count} words")
        
        # Start timing
        start_time = time.time()
        
        # Generate video using proven core function
        result = generate_video_did(script)
        
        # Calculate generation time
        generation_time = time.time() - start_time
        
        if result and result.get('success'):
            # Success response
            return jsonify({
                'success': True,
                'videoUrl': result['video_url'],
                'duration': result['duration'],
                'cost': 0.10,  # D-ID estimated cost
                'provider': result.get('provider', 'D-ID'),
                'generationTime': round(generation_time, 2),
                'videoId': result.get('video_id')
            }), 200
        else:
            # Failure response
            return jsonify({
                'success': False,
                'error': 'Video generation failed',
                'details': 'Check server logs for details',
                'generationTime': round(generation_time, 2)
            }), 500
            
    except Exception as e:
        print(f"❌ API Error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'details': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint (VRA-005).
    Returns basic API status.
    """
    return jsonify({
        'status': 'healthy',
        'service': 'VideoReach AI API',
        'version': '1.0.0',
        'timestamp': time.time()
    }), 200

@app.route('/status', methods=['GET'])
def status_check():
    """
    Status endpoint (VRA-005).
    Checks API connectivity to D-ID.
    """
    import requests
    
    status = {
        'api': 'running',
        'providers': {}
    }
    
    # Check D-ID API status
    try:
        did_key = os.environ.get('DID_API_KEY')
        if did_key:
            # Try to get D-ID credits/status
            headers = {"Authorization": f"Basic {did_key}"}
            # D-ID doesn't have a direct status endpoint, so we check talks endpoint
            response = requests.get(
                "https://api.d-id.com/talks",
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 200:
                status['providers']['did'] = {
                    'status': 'connected',
                    'available': True
                }
            elif response.status_code == 402:
                status['providers']['did'] = {
                    'status': 'connected',
                    'available': False,
                    'error': 'Trial credits exhausted'
                }
            else:
                status['providers']['did'] = {
                    'status': 'error',
                    'available': False,
                    'error': f'API returned {response.status_code}'
                }
        else:
            status['providers']['did'] = {
                'status': 'not_configured',
                'available': False
            }
    except Exception as e:
        status['providers']['did'] = {
            'status': 'error',
            'available': False,
            'error': str(e)
        }
    
    # Overall availability
    status['available'] = any(
        p.get('available', False) 
        for p in status['providers'].values()
    )
    
    return jsonify(status), 200

@app.route('/', methods=['GET'])
def index():
    """
    Root endpoint - basic API info.
    """
    return jsonify({
        'service': 'VideoReach AI API',
        'version': '1.0.0',
        'endpoints': {
            'POST /api/generate-video': 'Generate AI avatar video',
            'GET /health': 'Health check',
            'GET /status': 'Service status and availability'
        },
        'documentation': 'https://github.com/videoreach/api-docs'
    }), 200

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors."""
    return jsonify({
        'error': 'Endpoint not found',
        'available_endpoints': {
            'POST /api/generate-video': 'Generate video',
            'GET /health': 'Health check',
            'GET /status': 'Service status'
        }
    }), 404

@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors."""
    return jsonify({
        'error': 'Internal server error',
        'message': str(e)
    }), 500

def run_server(host='0.0.0.0', port=5000):
    """
    Run the Flask server.
    """
    print("=" * 60)
    print("🚀 VideoReach AI API Server")
    print("=" * 60)
    print(f"📡 Server starting on http://{host}:{port}")
    print(f"📍 Endpoints:")
    print(f"   POST /api/generate-video - Generate video")
    print(f"   GET  /health            - Health check")
    print(f"   GET  /status            - Service status")
    print("=" * 60)
    
    app.run(
        host=host,
        port=port,
        debug=app.config['DEBUG'],
        use_reloader=False  # Disable reloader for production
    )

if __name__ == '__main__':
    # Run server
    port = int(os.environ.get('PORT', 5000))
    run_server(port=port)