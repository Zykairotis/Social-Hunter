import os
import base64
import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from urllib.parse import urlencode

# Load environment variables
load_dotenv()

class RedditAuth:
    """
    Class to handle Reddit OAuth authentication
    """
    def __init__(self):
        self.client_id = os.getenv("REDDIT_CLIENT_ID")
        self.client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        self.user_agent = os.getenv("REDDIT_USER_AGENT", "FastAPI:RedditApp:v0.1.0")
        self.redirect_uri = os.getenv("REDDIT_REDIRECT_URI", "http://localhost:8550")
        self.oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)
        
        # Check if required environment variables are set
        if not self.client_id or not self.client_secret:
            raise ValueError("REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET must be set in environment variables")
    
    def get_auth_url(self) -> str:
        """
        Generate Reddit authorization URL
        """
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "state": "random_state",  # In production, use a secure random string
            "redirect_uri": self.redirect_uri,
            "duration": "permanent",
            "scope": "identity read"  # Add more scopes as needed
        }
        
        return f"https://www.reddit.com/api/v1/authorize?{urlencode(params)}"
    
    async def get_token(self, code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access token
        """
        auth_header = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
        
        headers = {
            "Authorization": f"Basic {auth_header}",
            "User-Agent": self.user_agent
        }
        
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://www.reddit.com/api/v1/access_token",
                headers=headers,
                data=data
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Token exchange failed: {response.text}"
                )
                
            return response.json()
    
    async def validate_token(self, token: Optional[str]) -> bool:
        """
        Validate if the token is still valid
        """
        if not token:
            return False
            
        headers = {
            "Authorization": f"Bearer {token}",
            "User-Agent": self.user_agent
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://oauth.reddit.com/api/v1/me",
                headers=headers
            )
            
            return response.status_code == 200 