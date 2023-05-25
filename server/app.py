# load environment variables
from dotenv import load_dotenv
from pathlib import Path

env_path = Path('.') / '.setting_env'
load_dotenv(dotenv_path=env_path)

# Important libraries for FastAPI
import os
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import jwt, JWTError

# Important libraries for MongoDB
from motor.motor_asyncio import AsyncIOMotorClient

# Start the FastAPI app
app = FastAPI(
    title="FastAPI IP Filtering and JWT Authentication",
    description="This is a very fancy project, with auto docs for the API and everything",
    version="0.0.1",
    docs_url="/docs",
    redoc_url="/redoc",
    swagger_ui_oauth2_redirect_url="/docs/oauth2-redirect",
    contact={
        "name": "Bharat Chandra Sahu",
        # "email":"",
        # "url": ""
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    }
)

# Define the allowed IP addresses for the specific API
allowed_ips = os.getenv("ALLOWED_IPS", "")

# JWT configurations
SECRET_KEY = os.getenv("SECRET_KEY", "")
ALGORITHM = os.getenv("ALGORITHM", "")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 0))

# MongoDB connection
MONGODB_URL = os.getenv("PROD_DB_URL", "")
client = AsyncIOMotorClient(MONGODB_URL)
db = client["prod_db"]
users_collection = db["users"]

# Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Decorator to enforce IP filtering on a specific API route
def restrict_ip_addresses(func):
    async def wrapper(request: Request):
        client_host = request.client.host
        if client_host not in allowed_ips:
            raise HTTPException(status_code=403, detail="IP Address not allowed")
        return await func(request)
    return wrapper

# User Model
class User(BaseModel):
    username: str
    password: str

# JWT Token Model
class Token(BaseModel):
    access_token: str
    token_type: str

# Password Hashing and Verification
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

async def get_user(username: str):
    user = await users_collection.find_one({"username": username})
    return user

# Authentication
async def authenticate_user(username: str, password: str):
    user = await get_user(username)
    if not user:
        return False
    if not verify_password(password, user["password"]):
        return False
    return User(**user)

# Create Access Token
def create_access_token(data: dict):
    encoded_jwt = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# OAuth2 Password Bearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

# Token Validation and User Retrieval
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user = await get_user(token_data.username)
    if user is None:
        raise credentials_exception
    return User(**user)

# Token Data Model
class TokenData(BaseModel):
    username: str = None

# Token Route
@app.post("/token", response_model=Token)
async def login(form_data: User):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Create User Route
@app.post("/users")
async def create_user(user: User):
    hashed_password = pwd_context.hash(user.password)
    user_data = {
        "username": user.username,
        "password": hashed_password
    }
    result = await users_collection.insert_one(user_data)
    created_user = await users_collection.find_one({"_id": result.inserted_id})
    return User(**created_user)

# Protected Route
@app.get("/protected_route")
async def protected_route(user: User = Depends(get_current_user)):
    return {"message": "You have access to the protected route"}

# Your API routes
class RestrictedAPIResponse(BaseModel):
    message: str = "This API can only be accessed from allowed IP addresses."

@app.get("/")
async def root():
    return {"message": "Hello, World!"}

@app.get("/restricted_api", response_model=RestrictedAPIResponse, )
@restrict_ip_addresses
async def restricted_api(request: Request):
    return {"message": "This API can only be accessed from allowed IP addresses."}

# Add TrustedHostMiddleware to allow localhost access
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1"])

# Security requirement to include in Swagger documentation
security_requirements = [{"bearerAuth": []}]

# Include security requirements in Swagger documentation
@app.get("/docs", include_in_schema=False)
async def override_swagger_ui(request: Request):
    return await app.openapi_docs(request=request, security_requirements=security_requirements)

@app.get("/redoc", include_in_schema=False)
async def override_redoc(request: Request):
    return await app.openapi_redoc(request=request, security_requirements=security_requirements)