import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
import sys

load_dotenv()
MONGODB_URL = os.getenv("MONGODB_URL")

async def test_connection():
    try:
        client = AsyncIOMotorClient(MONGODB_URL, serverSelectionTimeoutMS=5000)
        # Attempt to get server info to force a connection
        info = await client.server_info()
        print("Successfully connected to MongoDB!")
    except Exception as e:
        print(f"Connection failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test_connection())
