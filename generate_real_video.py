"""
generate_real_video.py - Try to generate a real video!
"""

import os
import sys
import time
import json
import requests
from dotenv import load_dotenv

load_dotenv()

def generate_did_video(script_text):
    """Actually try to generate a video with D-ID"""
    
    print("[D-ID] Attempting video generation...")
    print(f"[D-ID] Script: {script_text[:100]}...")
    
    url = "https://api.d-id.com/talks"
    
    headers = {
        "Authorization": f"Basic {os.environ.get('DID_API_KEY')}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "script": {
            "type": "text",
            "input": script_text,
            "provider": {
                "type": "microsoft",
                "voice_id": "en-US-JennyNeural"
            }
        },
        "config": {
            "fluent": True,
            "pad_audio": 0.0
        },
        "source_url": "https://d-id-public-bucket.s3.us-west-2.amazonaws.com/alice.jpg"
    }
    
    try:
        # Create talk
        print("[D-ID] Sending request...")
        response = requests.post(url, json=payload, headers=headers)
        
        print(f"[D-ID] Response status: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            talk_id = data.get('id')
            print(f"[D-ID] Talk created! ID: {talk_id}")
            
            # Poll for completion
            print("[D-ID] Waiting for video generation...")
            max_attempts = 30
            for i in range(max_attempts):
                time.sleep(2)
                
                # Check status
                status_url = f"https://api.d-id.com/talks/{talk_id}"
                status_response = requests.get(status_url, headers=headers)
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    status = status_data.get('status')
                    
                    print(f"[D-ID] Status: {status}")
                    
                    if status == 'done':
                        video_url = status_data.get('result_url')
                        print(f"\n SUCCESS! Video generated!")
                        print(f"[VIDEO URL] {video_url}")
                        print(f"[Duration] {status_data.get('duration', 'unknown')} seconds")
                        return {
                            'success': True,
                            'video_url': video_url,
                            'talk_id': talk_id,
                            'duration': status_data.get('duration')
                        }
                    elif status == 'error':
                        print(f"[ERROR] Generation failed: {status_data.get('error', {}).get('message')}")
                        return {'success': False, 'error': status_data.get('error')}
                else:
                    print(f"[ERROR] Status check failed: {status_response.status_code}")
            
            print("[TIMEOUT] Video generation took too long")
            return {'success': False, 'error': 'Timeout'}
            
        elif response.status_code == 402:
            print("[ERROR] No credits remaining!")
            return {'success': False, 'error': 'No credits'}
        else:
            print(f"[ERROR] Request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return {'success': False, 'error': response.text}
            
    except Exception as e:
        print(f"[EXCEPTION] {str(e)}")
        return {'success': False, 'error': str(e)}

def main():
    print("=" * 60)
    print("VIDEOREACH AI - REAL VIDEO GENERATION TEST")
    print("=" * 60)
    
    # Create a short but valuable script
    script = """
    Hi Sarah from Shopify. I just analyzed your website and found something interesting.
    Your customer support team is manually handling over 5000 tickets per month,
    which is costing you approximately 50 thousand dollars in labor every month.
    I can show you how to automate 80 percent of these tickets using AI,
    saving you 480 thousand dollars per year.
    Let's discuss this opportunity. Book a 15 minute call at calendly.com/videoreach.
    """
    
    # Clean up script
    script = ' '.join(script.split())
    word_count = len(script.split())
    
    print(f"\nScript: {word_count} words")
    print("-" * 40)
    print(script)
    print("-" * 40)
    
    # Try to generate video
    result = generate_did_video(script)
    
    if result['success']:
        print("\n" + "=" * 60)
        print("VIDEO GENERATION SUCCESSFUL!")
        print("=" * 60)
        print(f"Video URL: {result['video_url']}")
        print(f"Duration: {result.get('duration', 'unknown')} seconds")
        print("\nYou can download or view this video in your browser!")
        
        # Save result
        with open('generated_video_result.json', 'w') as f:
            json.dump(result, f, indent=2)
        print("\nResult saved to: generated_video_result.json")
    else:
        print("\n" + "=" * 60)
        print("VIDEO GENERATION FAILED")
        print("=" * 60)
        print(f"Error: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()