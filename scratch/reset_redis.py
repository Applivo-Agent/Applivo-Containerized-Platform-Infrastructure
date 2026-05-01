import redis
from app.core.config import settings

def reset_rate_limits():
    try:
        # Try WITHOUT password if the previous one failed
        url_no_pass = "redis://127.0.0.1:6379/0"
        r = redis.from_url(url_no_pass, decode_responses=True)
        print(f"Connecting to Redis (No Auth) at {url_no_pass}...")
        
        keys_to_delete = []
        for key in r.scan_iter(match="auth_rate:*"):
            keys_to_delete.append(key)
        for key in r.scan_iter(match="rate:*"):
            keys_to_delete.append(key)
            
        if keys_to_delete:
            print(f"Found {len(keys_to_delete)} keys to delete: {keys_to_delete}")
            r.delete(*keys_to_delete)
            print("Successfully deleted all rate limit keys!")
        else:
            print("No rate limit keys found.")
            
    except Exception as e:
        print(f"Error resetting rate limits: {e}")

if __name__ == "__main__":
    reset_rate_limits()
