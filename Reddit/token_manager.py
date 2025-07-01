import json
import os
import time
from typing import Dict, Any, Optional

class TokenManager:
    """
    Class to manage Reddit OAuth tokens
    """
    def __init__(self, token_file: str = "tokens.json"):
        self.token_file = token_file
        self.tokens = self._load_tokens()
    
    def _load_tokens(self) -> Dict[str, Any]:
        """
        Load tokens from file
        """
        if os.path.exists(self.token_file):
            try:
                with open(self.token_file, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def _save_tokens(self) -> None:
        """
        Save tokens to file
        """
        with open(self.token_file, "w") as f:
            json.dump(self.tokens, f, indent=2)
    
    def save_token(self, token_data: Dict[str, Any]) -> None:
        """
        Save token data with expiration timestamp
        """
        # Calculate expiration timestamp
        expires_at = time.time() + token_data.get("expires_in", 3600)
        
        # Store token with expiration
        self.tokens = {
            "access_token": token_data.get("access_token"),
            "refresh_token": token_data.get("refresh_token"),
            "expires_at": expires_at,
            "scope": token_data.get("scope", "")
        }
        
        self._save_tokens()
    
    def get_token(self) -> Optional[str]:
        """
        Get current access token if valid
        """
        if not self.tokens:
            return None
            
        # Check if token is expired
        if time.time() > self.tokens.get("expires_at", 0):
            return None
            
        return self.tokens.get("access_token")
    
    def get_refresh_token(self) -> Optional[str]:
        """
        Get refresh token
        """
        return self.tokens.get("refresh_token")
    
    def is_token_valid(self) -> bool:
        """
        Check if token is valid
        """
        if not self.tokens:
            return False
            
        return time.time() < self.tokens.get("expires_at", 0)
    
    def clear_tokens(self) -> None:
        """
        Clear all tokens
        """
        self.tokens = {}
        self._save_tokens() 