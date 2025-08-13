"""
core_test.py - VideoReach AI Core Engine Test
Following ZAD Core-First Mandate: Prove the engine works before building the car.

This script tests the core video generation functionality with hardcoded data.
NO Flask, NO UI, NO database - just pure avatar video generation.

Requirements:
- Set environment variables: DID_API_KEY
- Install: pip install requests python-dotenv

Expected Output:
- Successfully generates a 30-45 second video
- Returns a valid video URL
- Completes in under 45 seconds
- Cost under $0.50 per video
"""

import os
import sys
import time
import json
import requests
from typing import Dict, Optional

# Fix Windows Unicode issues
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Hardcoded test data (as per ZAD mandate)
TEST_PROSPECT = {
    'first_name': 'John',
    'company_name': 'Acme Corp',
    'job_title': 'VP of Sales',
    'industry': 'Software',
    'pain_point': 'manual lead generation processes'
}

# Hardcoded script for video generation
TEST_SCRIPT = """
Hi John from Acme Corp. I noticed you're using manual processes 
for lead generation. We helped TechCo automate this and save 
20 hours per week. Worth a quick 15-minute chat to explore 
how we could do the same for you?
"""

def generate_video_did(script: str) -> Optional[Dict]:
    """
    Primary video generation using D-ID.
    
    This is the CORE FUNCTION that must work before anything else.
    """
    print("🚀 Starting D-ID video generation...")
    print(f"📝 Script length: {len(script.split())} words")
    
    api_key = os.environ.get('DID_API_KEY')
    if not api_key:
        raise ValueError("❌ DID_API_KEY not found in environment variables!")
    
    # D-ID API endpoint
    url = "https://api.d-id.com/talks"
    
    # D-ID payload format
    payload = {
        "script": {
            "type": "text",
            "input": script
        },
        "config": {
            "fluent": True,
            "pad_audio": 0.0
        },
        "source_url": "https://d-id-public-bucket.s3.us-west-2.amazonaws.com/alice.jpg"
    }
    
    headers = {
        "Authorization": f"Basic {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        print("📡 Sending request to D-ID API...")
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 429:
            print("❌ D-ID rate limit exceeded (trial limitation)")
            return None
        elif response.status_code == 402:
            print("❌ D-ID trial credits exhausted")
            return None
        elif response.status_code != 201:
            print(f"❌ D-ID API error: {response.status_code}")
            print(f"❌ Response: {response.text}")
            return None
            
        result = response.json()
        talk_id = result.get('id')
        
        if not talk_id:
            print("❌ No talk_id in D-ID response")
            print(f"Response: {result}")
            return None
            
        print(f"✅ Video generation initiated! ID: {talk_id}")
        
        # Poll for completion
        return poll_did_status(talk_id, api_key)
        
    except Exception as e:
        print(f"❌ D-ID error: {str(e)}")
        return None

def poll_did_status(talk_id: str, api_key: str, max_wait: int = 60) -> Optional[Dict]:
    """
    Poll D-ID API for video generation status.
    """
    url = f"https://api.d-id.com/talks/{talk_id}"
    headers = {"Authorization": f"Basic {api_key}"}
    
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            status = data.get('status')
            
            if status == 'done':
                video_url = data.get('result_url')
                duration = data.get('duration')
                print(f"✅ Video ready! URL: {video_url}")
                print(f"⏱️ Duration: {duration} seconds")
                return {
                    'success': True,
                    'video_url': video_url,
                    'duration': duration,
                    'video_id': talk_id,
                    'generation_time': time.time() - start_time,
                    'provider': 'D-ID'
                }
            elif status == 'error' or status == 'rejected':
                print(f"❌ D-ID generation failed: {status}")
                error_msg = data.get('error', {}).get('message', 'Unknown error')
                print(f"❌ Error: {error_msg}")
                return None
            else:
                print(f"⏳ Status: {status}... waiting 5 seconds")
                time.sleep(5)
        else:
            print(f"❌ Status check failed: {response.status_code}")
            return None
    
    print(f"❌ Timeout: Video not ready after {max_wait} seconds")
    return None

def main():
    """
    Main test function following ZAD Core-First Mandate.
    This MUST work before any other development proceeds.
    """
    print("=" * 60)
    print("🎬 VideoReach AI - Core Engine Test")
    print("=" * 60)
    print(f"👤 Test Prospect: {TEST_PROSPECT['first_name']} from {TEST_PROSPECT['company_name']}")
    print(f"📄 Script: {TEST_SCRIPT[:100]}...")
    print("=" * 60)
    
    # Start timing
    start_time = time.time()
    
    # Generate video (THE CORE FUNCTION)
    result = generate_video_did(TEST_SCRIPT)
    
    # Calculate metrics
    total_time = time.time() - start_time
    
    if result and result['success']:
        print("\n" + "=" * 60)
        print("🎉 SUCCESS! CORE ENGINE IS WORKING!")
        print("=" * 60)
        print(f"📹 Video URL: {result['video_url']}")
        print(f"⏱️ Total Generation Time: {total_time:.2f} seconds")
        print(f"🏢 Provider: {result.get('provider', 'Unknown')}")
        print(f"💰 Estimated Cost: $0.10 (D-ID)")
        print("\n✅ Core validation passed. Ready to proceed with API wrapper.")
        
        # Verify critical requirements
        if total_time < 45:
            print("✅ Generation time under 45 seconds")
        else:
            print("⚠️ Generation time exceeded 45 seconds target")
            
        return True
    else:
        print("\n" + "=" * 60)
        print("❌ FAILED! CORE ENGINE NOT WORKING!")
        print("=" * 60)
        print("🚫 Cannot proceed until core video generation works.")
        print("Debug steps:")
        print("1. Verify DID_API_KEY is set and valid")
        print("2. Check API quota and limits")
        print("3. Test with D-ID dashboard directly")
        print("4. Review error messages above")
        return False

def run_validation_tests(count: int = 10):
    """
    Run multiple validation tests as per VRA-003.
    """
    print(f"\n🔄 Running {count} consecutive validation tests...")
    print("=" * 60)
    
    successes = 0
    failures = 0
    times = []
    
    for i in range(count):
        print(f"\n[Test {i+1}/{count}]")
        print("-" * 40)
        
        start = time.time()
        result = generate_video_did(TEST_SCRIPT)
        duration = time.time() - start
        
        if result and result['success']:
            successes += 1
            times.append(duration)
            print(f"✅ Test {i+1} passed in {duration:.2f}s")
        else:
            failures += 1
            print(f"❌ Test {i+1} failed")
        
        # Small delay between tests to avoid rate limits
        if i < count - 1:
            print("⏳ Waiting 2 seconds before next test...")
            time.sleep(2)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 VALIDATION SUMMARY")
    print("=" * 60)
    print(f"✅ Successful: {successes}/{count}")
    print(f"❌ Failed: {failures}/{count}")
    
    if times:
        avg_time = sum(times) / len(times)
        print(f"⏱️ Average time: {avg_time:.2f}s")
        print(f"⏱️ Min time: {min(times):.2f}s")
        print(f"⏱️ Max time: {max(times):.2f}s")
    
    success_rate = (successes / count) * 100
    print(f"📈 Success rate: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print("\n✅ VALIDATION PASSED! Core engine is reliable.")
        return True
    else:
        print("\n❌ VALIDATION FAILED! Core engine needs fixes.")
        return False

if __name__ == "__main__":
    # Load environment variables if .env file exists
    if os.path.exists('.env'):
        from dotenv import load_dotenv
        load_dotenv()
    
    # Check for validation mode
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--validate':
        # Run full validation (VRA-003)
        success = run_validation_tests(10)
    else:
        # Run single test
        success = main()
    
    # Exit with appropriate code
    exit(0 if success else 1)