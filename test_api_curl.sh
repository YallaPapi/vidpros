#!/bin/bash

echo "Testing API endpoints with curl..."
echo "================================="

# Test health endpoint
echo -e "\n1. Testing /health endpoint:"
curl -s http://localhost:5000/health | python -m json.tool

# Test video modes endpoint
echo -e "\n2. Testing /api/video-modes endpoint:"
curl -s http://localhost:5000/api/video-modes | python -m json.tool | head -20

# Test faceless video generation
echo -e "\n3. Testing faceless video generation:"
curl -X POST http://localhost:5000/api/generate-video \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "faceless",
    "company": "Test HVAC Company",
    "website": "https://example.com",
    "industry": "HVAC",
    "painPoints": ["no online booking", "manual scheduling"],
    "monthlyLoss": 12000,
    "solutionCost": 497
  }' \
  -s | python -m json.tool

echo -e "\nDone!"