"""Test actual signup via HTTP request"""
import sys
sys.path.insert(0, '.')

import httpx

# Test signup
response = httpx.post('http://localhost:8000/api/auth/signup', json={
    'email': 'faizaqureshi883@gmail.com',
    'password': 'password123'
})

print(f"Status: {response.status_code}")
print(f"Content: {response.text}")
