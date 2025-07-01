import httpx
from typing import Dict, Any, Optional, List
import os
from dotenv import load_dotenv
from token_manager import TokenManager

# Load environment variables
load_dotenv()

class RedditClient:
    """
    Client for interacting with Reddit API
    """
    def __init__(self):
        self.base_url = "https://oauth.reddit.com"
        self.user_agent = os.getenv("REDDIT_USER_AGENT", "FastAPI:RedditApp:v0.1.0")
        self.token_manager = TokenManager()
        
    async def _make_request(self, method: str, endpoint: str, params: Optional[Dict[str, Any]] = None, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make an authenticated request to Reddit API
        """
        token = self.token_manager.get_token()
        if not token:
            raise ValueError("No valid token available")
            
        headers = {
            "Authorization": f"Bearer {token}",
            "User-Agent": self.user_agent
        }
        
        url = f"{self.base_url}{endpoint}"
        
        async with httpx.AsyncClient() as client:
            if method.lower() == "get":
                response = await client.get(url, headers=headers, params=params)
            elif method.lower() == "post":
                response = await client.post(url, headers=headers, json=params if data is None else None, data=data)
            elif method.lower() == "put":
                response = await client.put(url, headers=headers, json=params)
            elif method.lower() == "delete":
                response = await client.delete(url, headers=headers, params=params)
            elif method.lower() == "patch":
                response = await client.patch(url, headers=headers, json=params)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
            if response.status_code in [200, 201, 202, 204]:
                if response.status_code == 204 or not response.content:
                    return {"status": "success"}
                return response.json()
            else:
                raise Exception(f"API request failed: {response.status_code} - {response.text}")
    
    # User Identity Endpoints
    async def get_me(self) -> Dict[str, Any]:
        """
        Get information about the authenticated user
        """
        return await self._make_request("GET", "/api/v1/me")
    
    async def get_karma(self) -> Dict[str, Any]:
        """
        Get user's karma breakdown by subreddit
        """
        return await self._make_request("GET", "/api/v1/me/karma")
    
    async def get_trophies(self) -> Dict[str, Any]:
        """
        Get user's trophies
        """
        return await self._make_request("GET", "/api/v1/me/trophies")
    
    # Subreddit Endpoints
    async def get_subscribed_subreddits(self, limit: int = 25) -> Dict[str, Any]:
        """
        Get user's subscribed subreddits
        """
        return await self._make_request("GET", "/subreddits/mine/subscriber", {"limit": limit})
    
    async def get_subreddit_info(self, subreddit: str) -> Dict[str, Any]:
        """
        Get information about a specific subreddit
        """
        return await self._make_request("GET", f"/r/{subreddit}/about")
    
    async def get_subreddit_rules(self, subreddit: str) -> Dict[str, Any]:
        """
        Get rules for a subreddit
        """
        return await self._make_request("GET", f"/r/{subreddit}/about/rules")
    
    async def get_subreddit_moderators(self, subreddit: str) -> Dict[str, Any]:
        """
        Get moderators of a subreddit
        """
        return await self._make_request("GET", f"/r/{subreddit}/about/moderators")
    
    # Post Endpoints
    async def get_posts(self, sort: str = "hot", limit: int = 25) -> Dict[str, Any]:
        """
        Get posts from subscribed subreddits
        """
        return await self._make_request("GET", f"/{sort}", {"limit": limit})
    
    async def get_subreddit_posts(self, subreddit: str, sort: str = "hot", limit: int = 25) -> Dict[str, Any]:
        """
        Get posts from a specific subreddit
        """
        return await self._make_request("GET", f"/r/{subreddit}/{sort}", {"limit": limit})
    
    async def get_post_details(self, post_id: str) -> Dict[str, Any]:
        """
        Get details of a specific post
        """
        # Remove 't3_' prefix if present
        if post_id.startswith('t3_'):
            post_id = post_id[3:]
            
        return await self._make_request("GET", f"/comments/{post_id}")
    
    async def get_post_duplicates(self, post_id: str) -> Dict[str, Any]:
        """
        Get duplicates of a post
        """
        # Remove 't3_' prefix if present
        if post_id.startswith('t3_'):
            post_id = post_id[3:]
            
        return await self._make_request("GET", f"/duplicates/{post_id}")
    
    # User Content Endpoints
    async def get_user_saved(self, limit: int = 25) -> Dict[str, Any]:
        """
        Get user's saved posts and comments
        """
        return await self._make_request("GET", "/user/me/saved", {"limit": limit})
    
    async def get_user_hidden(self, limit: int = 25) -> Dict[str, Any]:
        """
        Get user's hidden posts
        """
        return await self._make_request("GET", "/user/me/hidden", {"limit": limit})
    
    async def get_user_upvoted(self, limit: int = 25) -> Dict[str, Any]:
        """
        Get user's upvoted posts
        """
        return await self._make_request("GET", "/user/me/upvoted", {"limit": limit})
    
    async def get_user_downvoted(self, limit: int = 25) -> Dict[str, Any]:
        """
        Get user's downvoted posts
        """
        return await self._make_request("GET", "/user/me/downvoted", {"limit": limit})
    
    # User Profile Endpoints
    async def get_user_profile(self, username: str) -> Dict[str, Any]:
        """
        Get information about a specific user
        """
        return await self._make_request("GET", f"/user/{username}/about")
    
    async def get_user_posts(self, username: str, limit: int = 25) -> Dict[str, Any]:
        """
        Get posts submitted by a user
        """
        return await self._make_request("GET", f"/user/{username}/submitted", {"limit": limit})
    
    async def get_user_comments(self, username: str, limit: int = 25) -> Dict[str, Any]:
        """
        Get comments by a user
        """
        return await self._make_request("GET", f"/user/{username}/comments", {"limit": limit})
    
    # Search Endpoints
    async def search(self, query: str, subreddit: Optional[str] = None, sort: str = "relevance", limit: int = 25) -> Dict[str, Any]:
        """
        Search Reddit
        """
        params = {
            "q": query,
            "sort": sort,
            "limit": limit
        }
        
        endpoint = f"/r/{subreddit}/search" if subreddit else "/search"
        return await self._make_request("GET", endpoint, params)
    
    # Multireddit Endpoints
    async def get_user_multireddits(self, username: str = "me") -> Dict[str, Any]:
        """
        Get multireddits of a user
        """
        return await self._make_request("GET", f"/api/multi/user/{username}")
    
    async def get_multireddit(self, username: str, multi_name: str) -> Dict[str, Any]:
        """
        Get a specific multireddit
        """
        return await self._make_request("GET", f"/user/{username}/m/{multi_name}")
    
    # Misc Endpoints
    async def get_trending_subreddits(self) -> Dict[str, Any]:
        """
        Get trending subreddits
        """
        return await self._make_request("GET", "/api/trending_subreddits")
    
    async def get_subreddits_by_category(self, category: str = "popular", limit: int = 25) -> Dict[str, Any]:
        """
        Get subreddits by category
        """
        return await self._make_request("GET", f"/subreddits/{category}", {"limit": limit})
    
    async def get_wiki_pages(self, subreddit: str) -> Dict[str, Any]:
        """
        Get wiki pages of a subreddit
        """
        return await self._make_request("GET", f"/r/{subreddit}/wiki/pages")
    
    async def get_wiki_page(self, subreddit: str, page: str) -> Dict[str, Any]:
        """
        Get a specific wiki page
        """
        return await self._make_request("GET", f"/r/{subreddit}/wiki/{page}")
    
    async def get_traffic_stats(self, subreddit: str) -> Dict[str, Any]:
        """
        Get traffic statistics of a subreddit
        """
        return await self._make_request("GET", f"/r/{subreddit}/about/traffic")
    
    async def get_by_ids(self, ids: List[str]) -> Dict[str, Any]:
        """
        Get information about multiple posts/comments by IDs
        """
        # Ensure all IDs have proper prefix
        formatted_ids = []
        for id in ids:
            if not id.startswith('t1_') and not id.startswith('t3_'):
                # Assume it's a post if no prefix
                id = f"t3_{id}"
            formatted_ids.append(id)
            
        id_param = ",".join(formatted_ids)
        return await self._make_request("GET", f"/by_id/{id_param}")
    
    async def get_subreddit_flairs(self, subreddit: str) -> Dict[str, Any]:
        """
        Get available post flairs in a subreddit
        """
        return await self._make_request("GET", f"/r/{subreddit}/api/link_flair")
        
    # Additional Endpoints
    
    # Voting
    async def vote(self, id: str, direction: int) -> Dict[str, Any]:
        """
        Vote on a post or comment
        direction: 1 (upvote), -1 (downvote), 0 (remove vote)
        """
        return await self._make_request("POST", "/api/vote", {"id": id, "dir": direction})
    
    # Saving/Unsaving
    async def save(self, id: str, category: Optional[str] = None) -> Dict[str, Any]:
        """
        Save a post or comment
        """
        params = {"id": id}
        if category:
            params["category"] = category
        return await self._make_request("POST", "/api/save", params)
    
    async def unsave(self, id: str) -> Dict[str, Any]:
        """
        Unsave a post or comment
        """
        return await self._make_request("POST", "/api/unsave", {"id": id})
    
    # Hide/Unhide
    async def hide(self, id: str) -> Dict[str, Any]:
        """
        Hide a post
        """
        return await self._make_request("POST", "/api/hide", {"id": id})
    
    async def unhide(self, id: str) -> Dict[str, Any]:
        """
        Unhide a post
        """
        return await self._make_request("POST", "/api/unhide", {"id": id})
    
    # Comments
    async def add_comment(self, parent_id: str, text: str) -> Dict[str, Any]:
        """
        Add a comment to a post or comment
        """
        return await self._make_request("POST", "/api/comment", {"parent": parent_id, "text": text})
    
    async def edit_comment(self, comment_id: str, text: str) -> Dict[str, Any]:
        """
        Edit a comment
        """
        return await self._make_request("POST", "/api/editusertext", {"thing_id": comment_id, "text": text})
    
    async def delete_comment(self, comment_id: str) -> Dict[str, Any]:
        """
        Delete a comment
        """
        return await self._make_request("POST", "/api/del", {"id": comment_id})
    
    # Submissions
    async def submit_post(self, subreddit: str, title: str, kind: str, text: Optional[str] = None, url: Optional[str] = None) -> Dict[str, Any]:
        """
        Submit a post to a subreddit
        kind: 'self' for text post, 'link' for link post
        """
        params = {
            "sr": subreddit,
            "title": title,
            "kind": kind
        }
        
        if kind == "self" and text:
            params["text"] = text
        elif kind == "link" and url:
            params["url"] = url
            
        return await self._make_request("POST", "/api/submit", params)
    
    # Subreddit Management
    async def subscribe(self, subreddit_id: str, action: str = "sub") -> Dict[str, Any]:
        """
        Subscribe or unsubscribe from a subreddit
        action: 'sub' to subscribe, 'unsub' to unsubscribe
        """
        return await self._make_request("POST", "/api/subscribe", {"sr": subreddit_id, "action": action})
    
    # Flair
    async def select_flair(self, subreddit: str, link_id: Optional[str] = None, flair_template_id: str = None, text: Optional[str] = None) -> Dict[str, Any]:
        """
        Select a flair for a post or user
        """
        params = {"r": subreddit}
        
        if link_id:
            params["link"] = link_id
            
        if flair_template_id:
            params["flair_template_id"] = flair_template_id
            
        if text:
            params["text"] = text
            
        return await self._make_request("POST", "/api/selectflair", params)
    
    # Private Messages
    async def get_messages(self, where: str = "inbox", limit: int = 25) -> Dict[str, Any]:
        """
        Get private messages
        where: 'inbox', 'unread', 'sent'
        """
        return await self._make_request("GET", f"/message/{where}", {"limit": limit})
    
    async def send_message(self, to: str, subject: str, text: str) -> Dict[str, Any]:
        """
        Send a private message
        """
        return await self._make_request("POST", "/api/compose", {"to": to, "subject": subject, "text": text})
    
    async def mark_messages_read(self, ids: List[str]) -> Dict[str, Any]:
        """
        Mark messages as read
        """
        return await self._make_request("POST", "/api/read_message", {"id": ",".join(ids)})
    
    async def mark_messages_unread(self, ids: List[str]) -> Dict[str, Any]:
        """
        Mark messages as unread
        """
        return await self._make_request("POST", "/api/unread_message", {"id": ",".join(ids)})
    
    # Reporting
    async def report(self, id: str, reason: str) -> Dict[str, Any]:
        """
        Report a post or comment
        """
        return await self._make_request("POST", "/api/report", {"thing_id": id, "reason": reason})
    
    # User Blocking
    async def block_user(self, account_id: str) -> Dict[str, Any]:
        """
        Block a user
        """
        return await self._make_request("POST", "/api/block_user", {"account_id": account_id})
    
    # Friends
    async def get_friends(self) -> Dict[str, Any]:
        """
        Get list of friends
        """
        return await self._make_request("GET", "/api/v1/me/friends")
    
    async def add_friend(self, username: str, note: Optional[str] = None) -> Dict[str, Any]:
        """
        Add a user as friend
        """
        data = {}
        if note:
            data["note"] = note
        return await self._make_request("PUT", f"/api/v1/me/friends/{username}", data)
    
    async def remove_friend(self, username: str) -> Dict[str, Any]:
        """
        Remove a user from friends
        """
        return await self._make_request("DELETE", f"/api/v1/me/friends/{username}")
    
    # User Preferences
    async def get_preferences(self) -> Dict[str, Any]:
        """
        Get user preferences
        """
        return await self._make_request("GET", "/api/v1/me/prefs")
    
    async def update_preferences(self, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update user preferences
        """
        return await self._make_request("PATCH", "/api/v1/me/prefs", preferences) 