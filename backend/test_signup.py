"""Test signup."""
import httpx
import traceback

def test_signup():
    url = "http://localhost:8000/api/auth/signup"
    data = {"email": "test4@example.com", "password": "test123456"}

    try:
        response = httpx.post(url, json=data, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except httpx.HTTPStatusError as e:
        print(f"HTTP Error: {e.response.status_code}")
        print(f"Response: {e.response.text}")
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_signup()
