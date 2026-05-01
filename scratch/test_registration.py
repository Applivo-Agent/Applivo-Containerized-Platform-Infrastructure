import asyncio
import httpx
import json

async def test_register():
    url = "http://localhost:8000/api/auth/register/initiate"
    data = {
        "email": "ss0856@srmist.edu.in",
        "password": "Password123!",
        "full_name": "test"
    }
    print(f"Sending POST to {url}...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data, timeout=10.0)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_register())
