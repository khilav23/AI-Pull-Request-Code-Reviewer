import redis
from dotenv import load_dotenv
import os 
load_dotenv()

REDIS_ENDPOINT = os.getenv("REDIS_ENDPOINT")
r = redis.StrictRedis(host=REDIS_ENDPOINT, port=6379, db=0)

try:
    response = r.ping()
    if response:
        print("Redis is running!")
except redis.ConnectionError:
    print("Redis is not running or cannot be reached.")
