"""
api.py - VideoReach AI API Wrapper with Multi-Mode Support
Following ZAD Core-First Mandate: Phase 2 - API Wrapper

This API exposes video generation with multiple modes:
- Avatar videos (D-ID/HeyGen)
- Faceless videos (Screenshots + Voiceover)

Endpoints:
- POST /api/generate-video (avatar or faceless)
- POST /api/generate-report
- GET /api/health

Requirements:
- Flask for minimal API
- Supports both avatar and faceless videos
- No authentication yet (per VRA-004)
- Returns video URL and metadata
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import time
import asyncio
from typing import Dict, Optional
from dotenv import load_dotenv

# Import the proven core function
from core_test import generate_video_did

# Import faceless video generator
from faceless_video_generator import FacelessVideoGenerator
from faceless_pipeline_integration import FacelessVideoPipeline

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
    Generate video - supports both avatar and faceless modes.
    
    Expected JSON payload:
    {
        "mode": "avatar" or "faceless" (default: "faceless"),
        "script": "Video script text" (for avatar mode),
        "company": "Company name" (for faceless mode),
        "website": "https://company.com" (for faceless mode),
        "industry": "HVAC/Plumbing/etc",
        "painPoints": ["no online booking", "manual processes"],
        "monthlyLoss": 10000,
        "solutionCost": 497,
        "competitor": "Competitor name",
        "avatarId": "optional_avatar_id",
        "voiceId": "optional_voice_id"
    }
    
    Returns:
    {
        "success": true/false,
        "videoUrl": "https://...",
        "duration": 45,
        "cost": 0.04 or 0.20,
        "provider": "Faceless" or "D-ID",
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
        
        # Determine mode (default to faceless as it's cheaper)
        mode = data.get('mode', 'faceless').lower()
        
        # Log request
        print(f"📥 Video generation request received")
        print(f"🎬 Mode: {mode}")
        
        # Start timing
        start_time = time.time()
        
        if mode == 'avatar':
            # Avatar mode - use existing D-ID implementation
            script = data.get('script')
            
            if not script:
                return jsonify({
                    'success': False,
                    'error': 'Script is required for avatar mode'
                }), 400
            
            # Validate script length (45 seconds max ~ 250 words)
            word_count = len(script.split())
            if word_count > 250:
                return jsonify({
                    'success': False,
                    'error': f'Script too long: {word_count} words (max 250)'
                }), 400
            
            print(f"📝 Script length: {word_count} words")
            
            # Generate avatar video
            result = generate_video_did(script)
            
            # Calculate generation time
            generation_time = time.time() - start_time
            
            if result and result.get('success'):
                return jsonify({
                    'success': True,
                    'videoUrl': result['video_url'],
                    'duration': result['duration'],
                    'cost': 0.20,  # Avatar cost
                    'provider': result.get('provider', 'D-ID'),
                    'generationTime': round(generation_time, 2),
                    'videoId': result.get('video_id')
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'error': 'Avatar video generation failed',
                    'details': 'Check server logs for details',
                    'generationTime': round(generation_time, 2)
                }), 500
                
        else:  # faceless mode
            # Validate required fields for faceless video
            required_fields = ['company', 'website', 'industry']
            missing_fields = [f for f in required_fields if not data.get(f)]
            
            if missing_fields:
                return jsonify({
                    'success': False,
                    'error': f'Missing required fields: {", ".join(missing_fields)}'
                }), 400
            
            # Prepare company data for faceless video
            company_data = {
                'company': data.get('company'),
                'website': data.get('website'),
                'industry': data.get('industry'),
                'pain_points': data.get('painPoints', ['manual processes', 'no automation']),
                'monthly_loss': data.get('monthlyLoss', 10000),
                'solution_cost': data.get('solutionCost', 497),
                'competitor': data.get('competitor', 'leading competitors'),
                'calendar_link': data.get('calendarLink', 'calendly.com/demo')
            }
            
            print(f"🏢 Company: {company_data['company']}")
            print(f"🌐 Website: {company_data['website']}")
            
            # Generate faceless video
            generator = FacelessVideoGenerator()
            
            # Run async function in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            video_path = loop.run_until_complete(
                generator.generate_faceless_video(company_data)
            )
            loop.close()
            
            # Calculate generation time
            generation_time = time.time() - start_time
            
            if video_path:
                return jsonify({
                    'success': True,
                    'videoUrl': video_path,
                    'duration': 45,  # Typical faceless video duration
                    'cost': 0.04,  # Faceless cost (80% cheaper!)
                    'provider': 'Faceless',
                    'generationTime': round(generation_time, 2),
                    'mode': 'faceless'
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'error': 'Faceless video generation failed',
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

@app.route('/api/video-modes', methods=['GET'])
def get_video_modes():
    """
    Get available video generation modes and their comparison.
    
    Returns information about avatar vs faceless videos.
    """
    return jsonify({
        'modes': {
            'faceless': {
                'name': 'Faceless Video',
                'description': 'Data-driven video with screenshots, charts, and AI voiceover',
                'cost': 0.04,
                'processingTime': '10-15 seconds',
                'advantages': [
                    '80% cheaper than avatar videos',
                    '66% faster processing',
                    'No uncanny valley effect',
                    'Shows actual website problems',
                    'Data visualizations included',
                    'No API rate limits'
                ],
                'bestFor': [
                    'B2B prospecting',
                    'Technical audiences', 
                    'Data-driven presentations',
                    'High-volume campaigns'
                ],
                'components': [
                    'Website screenshots with annotations',
                    'Revenue loss charts',
                    'ROI calculators',
                    'Professional voiceover',
                    'Call-to-action screens'
                ]
            },
            'avatar': {
                'name': 'Avatar Video',
                'description': 'AI-generated spokesperson video with realistic avatar',
                'cost': 0.20,
                'processingTime': '30-45 seconds',
                'advantages': [
                    'Personal connection',
                    'Eye contact with viewer',
                    'Good for relationship building',
                    'Familiar video format'
                ],
                'bestFor': [
                    'Personal introductions',
                    'Relationship-focused sales',
                    'Service businesses',
                    'Lower volume, high-touch'
                ],
                'components': [
                    'AI avatar spokesperson',
                    'Lip-synced speech',
                    'Professional background',
                    'Natural gestures'
                ]
            }
        },
        'recommendation': 'Start with faceless videos - they are cheaper, faster, and often convert better for B2B',
        'comparison': {
            'costSavings': '80% reduction with faceless',
            'speedImprovement': '66% faster with faceless',
            'scaleCapability': {
                'faceless': '1000+ videos/day',
                'avatar': '500 videos/day (API limits)'
            }
        }
    }), 200

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint (VRA-005).
    Returns basic API status.
    """
    return jsonify({
        'status': 'healthy',
        'service': 'VideoReach AI API',
        'version': '2.0.0',  # Updated version with faceless support
        'features': ['avatar', 'faceless'],
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
        'version': '2.0.0',
        'endpoints': {
            'POST /api/generate-video': 'Generate AI avatar or faceless video',
            'GET /api/video-modes': 'Get video mode comparison',
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