"""
Test the API endpoint for faceless video generation
"""

import requests
import json
import time

def test_video_modes():
    """Test the video modes endpoint"""
    print("Testing /api/video-modes endpoint...")
    
    try:
        response = requests.get("http://localhost:5000/api/video-modes")
        if response.status_code == 200:
            data = response.json()
            print("SUCCESS: Video modes retrieved")
            print(f"  Faceless cost: ${data['modes']['faceless']['cost']}")
            print(f"  Avatar cost: ${data['modes']['avatar']['cost']}")
            print(f"  Recommendation: {data['recommendation']}")
            return True
    except requests.exceptions.ConnectionError:
        print("ERROR: API server not running on port 5000")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def test_faceless_generation():
    """Test faceless video generation via API"""
    print("\nTesting faceless video generation...")
    
    # Test data
    payload = {
        "mode": "faceless",
        "company": "Bob's HVAC Services",
        "website": "https://example.com",
        "industry": "HVAC",
        "painPoints": [
            "no online booking",
            "manual scheduling", 
            "phone-only support"
        ],
        "monthlyLoss": 15000,
        "solutionCost": 497,
        "competitor": "TechHVAC Pro",
        "calendarLink": "calendly.com/bobshvac-demo"
    }
    
    try:
        print(f"  Company: {payload['company']}")
        print(f"  Industry: {payload['industry']}")
        print(f"  Pain points: {', '.join(payload['painPoints'])}")
        print(f"  Sending request...")
        
        response = requests.post(
            "http://localhost:5000/api/generate-video",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("SUCCESS: Video generated!")
            print(f"  Video URL: {data.get('videoUrl', 'N/A')}")
            print(f"  Cost: ${data.get('cost', 'N/A')}")
            print(f"  Generation time: {data.get('generationTime', 'N/A')} seconds")
            print(f"  Provider: {data.get('provider', 'N/A')}")
            return True
        else:
            print(f"ERROR: Status code {response.status_code}")
            print(f"  Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to API server")
        print("  Make sure to run: python api.py")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def test_health_check():
    """Test health endpoint"""
    print("Testing /health endpoint...")
    
    try:
        response = requests.get("http://localhost:5000/health")
        if response.status_code == 200:
            data = response.json()
            print("SUCCESS: API is healthy")
            print(f"  Version: {data.get('version', 'N/A')}")
            print(f"  Features: {', '.join(data.get('features', []))}")
            return True
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def main():
    print("=" * 60)
    print("API FACELESS VIDEO TEST")
    print("=" * 60)
    print("\nMake sure the API server is running:")
    print("  python api.py")
    print("\n" + "=" * 60 + "\n")
    
    results = []
    
    # Test 1: Health check
    results.append(("Health Check", test_health_check()))
    
    # Test 2: Video modes
    results.append(("Video Modes", test_video_modes()))
    
    # Test 3: Faceless generation
    results.append(("Faceless Generation", test_faceless_generation()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "PASSED" if passed else "FAILED"
        print(f"{test_name}: {status}")
    
    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)
    
    print(f"\nTotal: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("\nAll tests passed! API is working correctly.")
    else:
        print(f"\n{total_tests - total_passed} test(s) failed.")
        print("Check if the API server is running: python api.py")

if __name__ == "__main__":
    main()