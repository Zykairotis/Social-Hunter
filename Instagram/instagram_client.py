from instagrapi import Client
from instagrapi.exceptions import (
    ChallengeRequired, 
    TwoFactorRequired, 
    ClientError, 
    ClientLoginRequired,
    ClientConnectionError
)
import logging
import json
import os
import time
import random
from pathlib import Path
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("instagram_api.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("instagram")

class InstagramClient:
    """A wrapper class for instagrapi Client with enhanced functionality"""
    
    def __init__(self, username=None, password=None, session_file="instagram_session.json", use_proxy=False, proxy=None):
        self.username = username
        self.password = password
        self.session_file = session_file
        self.use_proxy = use_proxy
        self.proxy = proxy
        self.client = self._setup_client()
        self.logged_in = False
    
    def _setup_client(self):
        """Set up Instagram client with proper configuration"""
        cl = Client()
        
        # Set handlers for authentication challenges
        cl.challenge_code_handler = self._challenge_code_handler
        cl.challenge_resolver = self._challenge_resolver
        cl.two_factor_handler = self._two_factor_handler
        
        # Set reasonable delays between requests
        cl.delay_range = [1, 3]
        
        # Configure device (helps with login stability)
        cl.set_device({
            "app_version": "269.0.0.18.75",
            "android_version": 26,
            "android_release": "8.0.0",
            "dpi": "480dpi",
            "resolution": "1080x1920",
            "manufacturer": "OnePlus",
            "device": "OnePlus6T",
            "model": "ONEPLUS A6010",
            "cpu": "qcom",
            "version_code": "314665256"
        })
        
        # Set user agent (helps avoid detection)
        cl.user_agent = "Instagram 269.0.0.18.75 Android (26/8.0.0; 480dpi; 1080x1920; OnePlus; ONEPLUS A6010; OnePlus6T; qcom; en_US; 314665256)"
        
        # Configure proxy if needed
        if self.use_proxy and self.proxy:
            logger.info(f"Setting up proxy: {self.proxy}")
            cl.set_proxy(self.proxy)
        
        return cl
    
    def _challenge_code_handler(self, username, choice):
        """Handle challenge code verification"""
        logger.info(f"Challenge required for {username}. Options: {choice}")
        if choice == "0":
            logger.info("Sending verification code via SMS")
            return "0"  # SMS option
        elif choice == "1":
            logger.info("Sending verification code via Email")
            return "1"  # Email option
        else:
            logger.warning(f"Unknown challenge choice: {choice}")
            return "1"  # Default to email
    
    def _challenge_resolver(self, username, code):
        """Get verification code from user input"""
        logger.info(f"Enter verification code for {username}:")
        verification_code = input(f"Enter verification code for {username}: ")
        logger.info(f"Verification code entered: {verification_code}")
        return verification_code
    
    def _two_factor_handler(self):
        """Handle 2FA authentication"""
        logger.info("Two-factor authentication required")
        code = input("Enter 2FA code: ")
        logger.info(f"2FA code entered: {code}")
        return code
    
    def login(self):
        """Login to Instagram"""
        if not self.username or not self.password:
            logger.error("Username and password are required for login")
            return False
        
        # Try to load existing session
        if os.path.exists(self.session_file):
            logger.info(f"Loading session from {self.session_file}")
            try:
                self.client.load_settings(self.session_file)
                self.client.login(self.username, self.password)
                logger.info("Successfully logged in using session file")
                self.logged_in = True
                return True
            except Exception as e:
                logger.error(f"Failed to login with saved session: {e}")
                # If session loading fails, try fresh login
                return self._try_fresh_login()
        else:
            logger.info("No session file found, attempting fresh login")
            return self._try_fresh_login()
    
    def _try_fresh_login(self):
        """Attempt a fresh login and save session on success"""
        max_attempts = 3
        for attempt in range(1, max_attempts + 1):
            try:
                # Create a new client instance for each attempt after the first
                if attempt > 1:
                    logger.info("Creating a new client instance for fresh attempt")
                    self.client = self._setup_client()
                
                logger.info(f"Attempting fresh login for {self.username} (attempt {attempt}/{max_attempts})")
                self.client.login(self.username, self.password)
                logger.info("Login successful")
                self.client.dump_settings(self.session_file)
                logger.info(f"Session saved to {self.session_file}")
                self.logged_in = True
                return True
            except ChallengeRequired as e:
                logger.error(f"Challenge required: {e}")
                # Let the challenge_resolver handle this
                continue
            except TwoFactorRequired as e:
                logger.error(f"Two-factor authentication required: {e}")
                # Let the two_factor_handler handle this
                continue
            except ClientError as e:
                logger.error(f"Client error during login (attempt {attempt}/{max_attempts}): {e}")
                time.sleep(random.uniform(3, 5))  # Add delay between attempts
            except Exception as e:
                logger.error(f"Login failed (attempt {attempt}/{max_attempts}): {e}")
                time.sleep(random.uniform(3, 5))  # Add delay between attempts
        
        logger.error(f"All {max_attempts} login attempts failed")
        self.logged_in = False
        return False
    
    def check_login_status(self):
        """Check if the client is properly logged in"""
        if not self.logged_in:
            logger.warning("Not logged in yet")
            return False
            
        try:
            # Try to get account info as a simple check
            account_info = self.client.account_info()
            logger.info(f"Logged in as {account_info.username} (ID: {account_info.pk})")
            return True
        except ClientLoginRequired:
            logger.error("Not logged in or session expired")
            self.logged_in = False
            return False
        except ChallengeRequired as e:
            logger.error(f"Challenge required during status check: {e}")
            self.logged_in = False
            return False
        except Exception as e:
            logger.error(f"Error checking login status: {e}")
            self.logged_in = False
            return False
    
    def get_account_info(self):
        """Get information about the logged-in account"""
        if not self.check_login_status():
            return None
            
        try:
            return self.client.account_info()
        except Exception as e:
            logger.error(f"Failed to get account info: {e}")
            return None
    
    def get_user_info(self, username_or_id):
        """Get information about a user by username or user ID"""
        if not self.check_login_status():
            return None
            
        try:
            # Check if input is a username or user_id
            if isinstance(username_or_id, str) and not username_or_id.isdigit():
                user_id = self.client.user_id_from_username(username_or_id)
            else:
                user_id = username_or_id
                
            return self.client.user_info(user_id)
        except Exception as e:
            logger.error(f"Failed to get user info for {username_or_id}: {e}")
            return None
    
    def get_user_medias(self, username_or_id, amount=10):
        """Get user's media posts"""
        if not self.check_login_status():
            return []
            
        try:
            # Check if input is a username or user_id
            if isinstance(username_or_id, str) and not username_or_id.isdigit():
                user_id = self.client.user_id_from_username(username_or_id)
            else:
                user_id = username_or_id
                
            return self.client.user_medias(user_id, amount)
        except Exception as e:
            logger.error(f"Failed to get media for {username_or_id}: {e}")
            return []
    
    def download_media(self, media_pk, folder="downloads"):
        """Download a media by its primary key"""
        if not self.check_login_status():
            return None
            
        try:
            os.makedirs(folder, exist_ok=True)
            return self.client.media_download(media_pk, folder)
        except Exception as e:
            logger.error(f"Failed to download media {media_pk}: {e}")
            return None
    
    def get_media_comments(self, media_pk, amount=20):
        """Get comments for a media"""
        if not self.check_login_status():
            return []
            
        try:
            return self.client.media_comments(media_pk, amount)
        except Exception as e:
            logger.error(f"Failed to get comments for media {media_pk}: {e}")
            return []
    
    def post_comment(self, media_pk, text):
        """Post a comment on a media"""
        if not self.check_login_status():
            return None
            
        try:
            return self.client.media_comment(media_pk, text)
        except Exception as e:
            logger.error(f"Failed to post comment on media {media_pk}: {e}")
            return None
    
    def like_media(self, media_pk):
        """Like a media"""
        if not self.check_login_status():
            return False
            
        try:
            return self.client.media_like(media_pk)
        except Exception as e:
            logger.error(f"Failed to like media {media_pk}: {e}")
            return False
    
    def unlike_media(self, media_pk):
        """Unlike a media"""
        if not self.check_login_status():
            return False
            
        try:
            return self.client.media_unlike(media_pk)
        except Exception as e:
            logger.error(f"Failed to unlike media {media_pk}: {e}")
            return False
    
    def follow_user(self, username_or_id):
        """Follow a user"""
        if not self.check_login_status():
            return False
            
        try:
            # Check if input is a username or user_id
            if isinstance(username_or_id, str) and not username_or_id.isdigit():
                user_id = self.client.user_id_from_username(username_or_id)
            else:
                user_id = username_or_id
                
            return self.client.user_follow(user_id)
        except Exception as e:
            logger.error(f"Failed to follow user {username_or_id}: {e}")
            return False
    
    def unfollow_user(self, username_or_id):
        """Unfollow a user"""
        if not self.check_login_status():
            return False
            
        try:
            # Check if input is a username or user_id
            if isinstance(username_or_id, str) and not username_or_id.isdigit():
                user_id = self.client.user_id_from_username(username_or_id)
            else:
                user_id = username_or_id
                
            return self.client.user_unfollow(user_id)
        except Exception as e:
            logger.error(f"Failed to unfollow user {username_or_id}: {e}")
            return False
    
    def get_hashtag_medias(self, hashtag, amount=20):
        """Get media posts for a hashtag"""
        if not self.check_login_status():
            return []
            
        try:
            return self.client.hashtag_medias_recent(hashtag, amount)
        except Exception as e:
            logger.error(f"Failed to get media for hashtag {hashtag}: {e}")
            return []
    
    def get_direct_threads(self, amount=20):
        """Get direct message threads"""
        if not self.check_login_status():
            return []
            
        try:
            return self.client.direct_threads(amount)
        except Exception as e:
            logger.error(f"Failed to get direct threads: {e}")
            return []
    
    def send_direct_message(self, user_ids, text):
        """Send a direct message to users"""
        if not self.check_login_status():
            return None
            
        try:
            return self.client.direct_send(text, user_ids)
        except Exception as e:
            logger.error(f"Failed to send direct message: {e}")
            return None
    
    def logout(self):
        """Logout from Instagram"""
        if not self.logged_in:
            logger.warning("Not logged in")
            return True
            
        try:
            result = self.client.logout()
            self.logged_in = False
            return result
        except Exception as e:
            logger.error(f"Failed to logout: {e}")
            return False


# Example usage
def main():
    # Initialize the Instagram client
    username = 'enhidna'
    password = "Mytimeisprecious#012345"
    
    instagram = InstagramClient(username, password)
    
    # Login to Instagram
    if not instagram.login():
        logger.error("Failed to login. Exiting.")
        return
    
    # Get account information
    account_info = instagram.get_account_info()
    if account_info:
        logger.info(f"Logged in as: {account_info.username} ({account_info.full_name})")
        logger.info(f"Media count: {account_info.media_count}")
        logger.info(f"Follower count: {account_info.follower_count}")
        logger.info(f"Following count: {account_info.following_count}")
    
    # Example: Get user information
    # user_info = instagram.get_user_info("instagram")
    # if user_info:
    #     logger.info(f"User: {user_info.username}")
    #     logger.info(f"Full name: {user_info.full_name}")
    #     logger.info(f"Biography: {user_info.biography}")
    
    # Example: Get user media
    # medias = instagram.get_user_medias(account_info.pk, 5)
    # for i, media in enumerate(medias, 1):
    #     logger.info(f"Media {i}: {media.id} - {media.media_type} - Likes: {media.like_count}")
    #     
    #     # Download media
    #     instagram.download_media(media.id)
    
    # Example: Get hashtag media
    # hashtag_medias = instagram.get_hashtag_medias("python", 5)
    # for i, media in enumerate(hashtag_medias, 1):
    #     logger.info(f"Hashtag Media {i}: {media.id} - {media.media_type} - Likes: {media.like_count}")
    
    # Example: Get direct threads
    # threads = instagram.get_direct_threads(5)
    # for thread in threads:
    #     logger.info(f"Thread: {thread.id} - Users: {[user.username for user in thread.users]}")
    
    # Logout
    instagram.logout()
    logger.info("Logged out successfully")


if __name__ == "__main__":
    main() 