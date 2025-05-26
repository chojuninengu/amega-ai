"""
AMEGA-AI FastAPI Application

This module sets up the main FastAPI application instance with configuration
loading from environment variables, CORS middleware, and basic health check endpoint.
"""
from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic_settings import BaseSettings
import uvicorn
from typing import List
import logging
from datetime import datetime, timedelta

from .llm_manager import LLMManager, ChatMessage
from .auth import (
    User, Token, authenticate_user, create_access_token,
    get_current_active_user, get_password_hash, fake_users_db,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    APP_NAME: str = "AMEGA-AI"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    MODEL_NAME: str = "microsoft/DialoGPT-medium"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Load settings
settings = Settings()

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="A powerful AI-driven platform for intelligent automation and decision making.",
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize LLM Manager
llm_manager = LLMManager(model_name=settings.MODEL_NAME)

# Authentication endpoints
@app.post("/api/v1/auth/register", response_model=User)
async def register_user(user: User):
    """Register a new user."""
    if user.username in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Create a new user with hashed password
    hashed_password = get_password_hash("default-password")  # In production, get password from request
    user_dict = user.dict()
    user_dict["hashed_password"] = hashed_password
    fake_users_db[user.username] = user_dict
    
    return user

@app.post("/api/v1/auth/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login endpoint to get access token."""
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/v1/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Get current user information."""
    return current_user

# Protected chat endpoints
@app.post("/api/v1/chat", response_model=ChatMessage)
async def chat_completion(
    message: ChatMessage,
    current_user: User = Depends(get_current_active_user)
):
    """
    Chat completion endpoint.
    
    This endpoint processes a chat message and returns an AI-generated response.
    The conversation history is maintained for context-aware responses.
    """
    try:
        logger.info(f"Received chat message from user {current_user.username}: {message.content}")
        response = await llm_manager.chat(message)
        logger.info(f"Generated response: {response.content}")
        return response
    except Exception as e:
        logger.error(f"Error in chat completion: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request."
        )

@app.get("/api/v1/chat/history", response_model=List[ChatMessage])
async def get_chat_history(current_user: User = Depends(get_current_active_user)):
    """Retrieve the conversation history."""
    try:
        return llm_manager.get_conversation_history()
    except Exception as e:
        logger.error(f"Error retrieving chat history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the chat history."
        )

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Health check endpoint to verify API status."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.APP_VERSION,
        "service": settings.APP_NAME
    }

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": "Welcome to AMEGA-AI API",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }

if __name__ == "__main__":
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    uvicorn.run(
        "app:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
