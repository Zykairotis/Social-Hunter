from fastapi import FastAPI, Depends, HTTPException, status, Request, Query, Body
from fastapi.responses import JSONResponse, RedirectResponse
import httpx
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from reddit_auth import RedditAuth
from reddit_client import RedditClient
from token_manager import TokenManager

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Reddit API",
    description="A FastAPI application for interacting with Reddit API",
    version="0.1.0"
)

# Initialize Reddit Auth
reddit_auth = RedditAuth()
token_manager = TokenManager()

# Initialize Reddit Client
reddit_client = RedditClient()

class HealthResponse(BaseModel):
    status: str
    version: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: Optional[str] = None
    scope: str

class VoteRequest(BaseModel):
    id: str
    direction: int

class SaveRequest(BaseModel):
    id: str
    category: Optional[str] = None

class CommentRequest(BaseModel):
    parent_id: str
    text: str

class EditCommentRequest(BaseModel):
    comment_id: str
    text: str

class SubmitPostRequest(BaseModel):
    subreddit: str
    title: str
    kind: str
    text: Optional[str] = None
    url: Optional[str] = None

class SubscribeRequest(BaseModel):
    subreddit_id: str
    action: str = "sub"

class FlairRequest(BaseModel):
    subreddit: str
    link_id: Optional[str] = None
    flair_template_id: Optional[str] = None
    text: Optional[str] = None

class MessageRequest(BaseModel):
    to: str
    subject: str
    text: str

class ReportRequest(BaseModel):
    id: str
    reason: str

class BlockUserRequest(BaseModel):
    account_id: str

class FriendNoteRequest(BaseModel):
    note: Optional[str] = None

@app.get("/healthcheck", response_model=HealthResponse)
async def healthcheck():
    """
    Check if the API is running properly
    """
    return HealthResponse(status="ok", version="0.1.0")

@app.get("/login")
async def login():
    """
    Generate Reddit authorization URL
    """
    auth_url = reddit_auth.get_auth_url()
    return {"auth_url": auth_url}

@app.get("/")
async def callback(code: Optional[str] = None, state: Optional[str] = None, error: Optional[str] = None):
    """
    Handle the callback from Reddit OAuth
    """
    if error:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": error}
        )
        
    if not code:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "No authorization code provided"}
        )
        
    try:
        token_data = await reddit_auth.get_token(code)
        # Save token for future use
        token_manager.save_token(token_data)
        return token_data
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": f"Failed to authenticate: {str(e)}"}
        )

@app.get("/auth/check")
async def check_auth():
    """
    Check if the authentication token is valid
    """
    if token_manager.is_token_valid():
        return {"status": "authenticated", "valid": True}
    return {"status": "not authenticated", "valid": False}

@app.get("/auth/token")
async def get_token():
    """
    Get the current access token
    """
    token = token_manager.get_token()
    if token:
        return {"access_token": token}
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"error": "No valid token found"}
    )

@app.post("/auth/token")
async def save_token(token_data: TokenResponse):
    """
    Save a token manually
    """
    token_manager.save_token(token_data.dict())
    return {"status": "success", "message": "Token saved successfully"}

@app.delete("/auth/token")
async def clear_token():
    """
    Clear the stored token
    """
    token_manager.clear_tokens()
    return {"status": "success", "message": "Token cleared successfully"}

# User Identity Endpoints
@app.get("/api/me")
async def get_me():
    """
    Get information about the authenticated user
    """
    try:
        return await reddit_client.get_me()
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": str(e)}
        )

@app.get("/api/me/karma")
async def get_karma():
    """
    Get user's karma breakdown by subreddit
    """
    try:
        return await reddit_client.get_karma()
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": str(e)}
        )

@app.get("/api/me/trophies")
async def get_trophies():
    """
    Get user's trophies
    """
    try:
        return await reddit_client.get_trophies()
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": str(e)}
        )

# Subreddit Endpoints
@app.get("/api/subreddits/mine")
async def get_subscribed_subreddits(limit: int = Query(25, ge=1, le=100)):
    """
    Get user's subscribed subreddits
    """
    try:
        return await reddit_client.get_subscribed_subreddits(limit)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": str(e)}
        )

@app.get("/api/subreddit/{subreddit}")
async def get_subreddit_info(subreddit: str):
    """
    Get information about a specific subreddit
    """
    try:
        return await reddit_client.get_subreddit_info(subreddit)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": str(e)}
        )

@app.get("/api/subreddit/{subreddit}/rules")
async def get_subreddit_rules(subreddit: str):
    """
    Get rules for a subreddit
    """
    try:
        return await reddit_client.get_subreddit_rules(subreddit)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": str(e)}
        )

@app.get("/api/subreddit/{subreddit}/moderators")
async def get_subreddit_moderators(subreddit: str):
    """
    Get moderators of a subreddit
    """
    try:
        return await reddit_client.get_subreddit_moderators(subreddit)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": str(e)}
        )

# Post Endpoints
@app.get("/api/posts/{sort}")
async def get_posts(sort: str = "hot", limit: int = Query(25, ge=1, le=100)):
    """
    Get posts from subscribed subreddits
    """
    try:
        return await reddit_client.get_posts(sort, limit)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": str(e)}
        )

@app.get("/api/subreddit/{subreddit}/posts/{sort}")
async def get_subreddit_posts(subreddit: str, sort: str = "hot", limit: int = Query(25, ge=1, le=100)):
    """
    Get posts from a specific subreddit
    """
    try:
        return await reddit_client.get_subreddit_posts(subreddit, sort, limit)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": str(e)}
        )

@app.get("/api/post/{post_id}")
async def get_post_details(post_id: str):
    """
    Get details of a specific post
    """
    try:
        return await reddit_client.get_post_details(post_id)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": str(e)}
        )

@app.get("/api/post/{post_id}/duplicates")
async def get_post_duplicates(post_id: str):
    """
    Get duplicates of a post
    """
    try:
        return await reddit_client.get_post_duplicates(post_id)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": str(e)}
        )

# User Content Endpoints
@app.get("/api/me/saved")
async def get_user_saved(limit: int = Query(25, ge=1, le=100)):
    """
    Get user's saved posts and comments
    """
    try:
        return await reddit_client.get_user_saved(limit)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": str(e)}
        )

@app.get("/api/me/hidden")
async def get_user_hidden(limit: int = Query(25, ge=1, le=100)):
    """
    Get user's hidden posts
    """
    try:
        return await reddit_client.get_user_hidden(limit)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": str(e)}
        )

@app.get("/api/me/upvoted")
async def get_user_upvoted(limit: int = Query(25, ge=1, le=100)):
    """
    Get user's upvoted posts
    """
    try:
        return await reddit_client.get_user_upvoted(limit)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": str(e)}
        )

@app.get("/api/me/downvoted")
async def get_user_downvoted(limit: int = Query(25, ge=1, le=100)):
    """
    Get user's downvoted posts
    """
    try:
        return await reddit_client.get_user_downvoted(limit)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": str(e)}
        )

# User Profile Endpoints
@app.get("/api/user/{username}")
async def get_user_profile(username: str):
    """
    Get information about a specific user
    """
    try:
        return await reddit_client.get_user_profile(username)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": str(e)}
        )

@app.get("/api/user/{username}/posts")
async def get_user_posts(username: str, limit: int = Query(25, ge=1, le=100)):
    """
    Get posts submitted by a user
    """
    try:
        return await reddit_client.get_user_posts(username, limit)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": str(e)}
        )

@app.get("/api/user/{username}/comments")
async def get_user_comments(username: str, limit: int = Query(25, ge=1, le=100)):
    """
    Get comments by a user
    """
    try:
        return await reddit_client.get_user_comments(username, limit)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": str(e)}
        )

# Search Endpoints
@app.get("/api/search")
async def search(
    query: str, 
    subreddit: Optional[str] = None, 
    sort: str = "relevance", 
    limit: int = Query(25, ge=1, le=100)
):
    """
    Search Reddit
    """
    try:
        return await reddit_client.search(query, subreddit, sort, limit)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": str(e)}
        )

# Multireddit Endpoints
@app.get("/api/multireddits/{username}")
async def get_user_multireddits(username: str = "me"):
    """
    Get multireddits of a user
    """
    try:
        return await reddit_client.get_user_multireddits(username)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": str(e)}
        )

@app.get("/api/multireddit/{username}/{multi_name}")
async def get_multireddit(username: str, multi_name: str):
    """
    Get a specific multireddit
    """
    try:
        return await reddit_client.get_multireddit(username, multi_name)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": str(e)}
        )

# Misc Endpoints
@app.get("/api/trending")
async def get_trending_subreddits():
    """
    Get trending subreddits
    """
    try:
        return await reddit_client.get_trending_subreddits()
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": str(e)}
        )

@app.get("/api/subreddits/{category}")
async def get_subreddits_by_category(category: str = "popular", limit: int = Query(25, ge=1, le=100)):
    """
    Get subreddits by category
    """
    try:
        return await reddit_client.get_subreddits_by_category(category, limit)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": str(e)}
        )

@app.get("/api/subreddit/{subreddit}/wiki")
async def get_wiki_pages(subreddit: str):
    """
    Get wiki pages of a subreddit
    """
    try:
        return await reddit_client.get_wiki_pages(subreddit)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": str(e)}
        )

@app.get("/api/subreddit/{subreddit}/wiki/{page}")
async def get_wiki_page(subreddit: str, page: str):
    """
    Get a specific wiki page
    """
    try:
        return await reddit_client.get_wiki_page(subreddit, page)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": str(e)}
        )

@app.get("/api/subreddit/{subreddit}/traffic")
async def get_traffic_stats(subreddit: str):
    """
    Get traffic statistics of a subreddit
    """
    try:
        return await reddit_client.get_traffic_stats(subreddit)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": str(e)}
        )

@app.get("/api/by_ids")
async def get_by_ids(ids: str):
    """
    Get information about multiple posts/comments by IDs (comma-separated)
    """
    try:
        id_list = ids.split(",")
        return await reddit_client.get_by_ids(id_list)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": str(e)}
        )

@app.get("/api/subreddit/{subreddit}/flairs")
async def get_subreddit_flairs(subreddit: str):
    """
    Get available post flairs in a subreddit
    """
    try:
        return await reddit_client.get_subreddit_flairs(subreddit)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": str(e)}
        )

# Additional Endpoints

# Voting
@app.post("/api/vote")
async def vote(request: VoteRequest):
    """
    Vote on a post or comment
    direction: 1 (upvote), -1 (downvote), 0 (remove vote)
    """
    try:
        return await reddit_client.vote(request.id, request.direction)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": str(e)}
        )

# Saving/Unsaving
@app.post("/api/save")
async def save(request: SaveRequest):
    """
    Save a post or comment
    """
    try:
        return await reddit_client.save(request.id, request.category)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": str(e)}
        )

@app.post("/api/unsave")
async def unsave(id: str = Body(..., embed=True)):
    """
    Unsave a post or comment
    """
    try:
        return await reddit_client.unsave(id)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": str(e)}
        )

# Hide/Unhide
@app.post("/api/hide")
async def hide(id: str = Body(..., embed=True)):
    """
    Hide a post
    """
    try:
        return await reddit_client.hide(id)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": str(e)}
        )

@app.post("/api/unhide")
async def unhide(id: str = Body(..., embed=True)):
    """
    Unhide a post
    """
    try:
        return await reddit_client.unhide(id)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": str(e)}
        )

# Comments
@app.post("/api/comment")
async def add_comment(request: CommentRequest):
    """
    Add a comment to a post or comment
    """
    try:
        return await reddit_client.add_comment(request.parent_id, request.text)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": str(e)}
        )

@app.put("/api/comment")
async def edit_comment(request: EditCommentRequest):
    """
    Edit a comment
    """
    try:
        return await reddit_client.edit_comment(request.comment_id, request.text)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": str(e)}
        )

@app.delete("/api/comment/{comment_id}")
async def delete_comment(comment_id: str):
    """
    Delete a comment
    """
    try:
        return await reddit_client.delete_comment(comment_id)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": str(e)}
        )

# Submissions
@app.post("/api/submit")
async def submit_post(request: SubmitPostRequest):
    """
    Submit a post to a subreddit
    """
    try:
        return await reddit_client.submit_post(
            request.subreddit, 
            request.title, 
            request.kind, 
            request.text, 
            request.url
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": str(e)}
        )

# Subreddit Management
@app.post("/api/subscribe")
async def subscribe(request: SubscribeRequest):
    """
    Subscribe or unsubscribe from a subreddit
    """
    try:
        return await reddit_client.subscribe(request.subreddit_id, request.action)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": str(e)}
        )

# Flair
@app.post("/api/flair")
async def select_flair(request: FlairRequest):
    """
    Select a flair for a post or user
    """
    try:
        return await reddit_client.select_flair(
            request.subreddit,
            request.link_id,
            request.flair_template_id,
            request.text
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": str(e)}
        )

# Private Messages
@app.get("/api/messages/{where}")
async def get_messages(where: str = "inbox", limit: int = Query(25, ge=1, le=100)):
    """
    Get private messages
    """
    try:
        return await reddit_client.get_messages(where, limit)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": str(e)}
        )

@app.post("/api/message")
async def send_message(request: MessageRequest):
    """
    Send a private message
    """
    try:
        return await reddit_client.send_message(request.to, request.subject, request.text)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": str(e)}
        )

@app.post("/api/message/read")
async def mark_messages_read(ids: List[str] = Body(..., embed=True)):
    """
    Mark messages as read
    """
    try:
        return await reddit_client.mark_messages_read(ids)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": str(e)}
        )

@app.post("/api/message/unread")
async def mark_messages_unread(ids: List[str] = Body(..., embed=True)):
    """
    Mark messages as unread
    """
    try:
        return await reddit_client.mark_messages_unread(ids)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": str(e)}
        )

# Reporting
@app.post("/api/report")
async def report(request: ReportRequest):
    """
    Report a post or comment
    """
    try:
        return await reddit_client.report(request.id, request.reason)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": str(e)}
        )

# User Blocking
@app.post("/api/block")
async def block_user(request: BlockUserRequest):
    """
    Block a user
    """
    try:
        return await reddit_client.block_user(request.account_id)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": str(e)}
        )

# Friends
@app.get("/api/friends")
async def get_friends():
    """
    Get list of friends
    """
    try:
        return await reddit_client.get_friends()
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": str(e)}
        )

@app.put("/api/friends/{username}")
async def add_friend(username: str, request: FriendNoteRequest = Body(...)):
    """
    Add a user as friend
    """
    try:
        return await reddit_client.add_friend(username, request.note)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": str(e)}
        )

@app.delete("/api/friends/{username}")
async def remove_friend(username: str):
    """
    Remove a user from friends
    """
    try:
        return await reddit_client.remove_friend(username)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": str(e)}
        )

# User Preferences
@app.get("/api/preferences")
async def get_preferences():
    """
    Get user preferences
    """
    try:
        return await reddit_client.get_preferences()
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": str(e)}
        )

@app.patch("/api/preferences")
async def update_preferences(preferences: Dict[str, Any] = Body(...)):
    """
    Update user preferences
    """
    try:
        return await reddit_client.update_preferences(preferences)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": str(e)}
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8550, reload=True) 