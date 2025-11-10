#!/usr/bin/env python3
"""Simple test to check API basics."""
import requests
import sys

# Test health endpoint
print("Testing health endpoint...")
try:
    response = requests.get("http://localhost:8000/health", timeout=5)
    print(f"✅ Health: {response.status_code} - {response.json()}")
except Exception as e:
    print(f"❌ Health check failed: {e}")
    sys.exit(1)

# Test ranking job creation with minimal data
print("\nTesting ranking job creation...")
try:
    files = [
        ('cv_files', ('test.pdf', open('data/resumes/00782d2a-6c8d-41e6-ab7b-d26bce182086.pdf', 'rb'), 'application/pdf'))
    ]
    data = {
        'job_description': 'Looking for a Python developer',
        'job_title': 'Python Developer',
        'company': 'Test Company'
    }
    
    response = requests.post(
        "http://localhost:8000/api/v1/ranking_jobs/create",
        data=data,
        files=files,
        timeout=30
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:500]}")
    
    if response.status_code == 200:
        print("✅ Job created successfully!")
    else:
        print(f"❌ Job creation failed")
        
except Exception as e:
    print(f"❌ Request failed: {e}")
    import traceback
    traceback.print_exc()

