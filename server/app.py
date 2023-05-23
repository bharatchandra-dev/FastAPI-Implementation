# load environment variables
from dotenv import load_dotenv
from pathlib import Path

env_path = Path('.') / '.setting_env'
load_dotenv(dotenv_path=env_path)

# Important libraries for FastAPI
import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.trustedhost import TrustedHostMiddleware

# Important libraries for MongoDB
from motor.motor_asyncio import AsyncIOMotorClient

# Define the allowed IP addresses for the specific API
allowed_ips = os.getenv("ALLOWED_IPS", "").split(",")

# MongoDB connection
MONGODB_URL = os.getenv("PROD_DB_URL", "")
client = AsyncIOMotorClient(MONGODB_URL)
db = client["prod_db"]
users_collection = db["users"]