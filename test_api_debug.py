"""
Debug API test to see what's happening
"""

import requests
import json

# Test the endpoint with debug
url = "http://localhost:5000/api/generate-video"

# Test 1: Send empty JSON
print("Test 1: Empty JSON")
response = requests.post(url, json={})
print(f"Response: {response.status_code}")
print(f"Body: {response.text}\n")

# Test 2: Send with mode=faceless
print("Test 2: Mode=faceless with minimal data")
response = requests.post(url, json={
    "mode": "faceless",
    "company": "Test Co",
    "website": "https://example.com",
    "industry": "HVAC"
})
print(f"Response: {response.status_code}")
print(f"Body: {response.text}\n")

# Test 3: Check what the API actually needs
print("Test 3: Mode=avatar with script")
response = requests.post(url, json={
    "mode": "avatar",
    "script": "Test script"
})
print(f"Response: {response.status_code}")
print(f"Body: {response.text}\n")