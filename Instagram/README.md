# Instagram Client

A robust Instagram API client built using the `instagrapi` library with enhanced error handling, session management, and a comprehensive set of features.

## Features

- Robust login with session persistence
- Challenge resolver for handling Instagram security challenges
- Two-factor authentication support
- Proxy support
- Comprehensive error handling
- Rate limiting protection with automatic delays
- Support for most Instagram interactions:
  - User information retrieval
  - Media browsing and downloading
  - Commenting and liking
  - Following and unfollowing
  - Hashtag exploration
  - Direct messaging

## Setup

1. Install the required dependencies:

```bash
pip install instagrapi
```

2. Import and initialize the client:

```python
from instagram_client import InstagramClient

# Basic initialization
instagram = InstagramClient(username="your_username", password="your_password")

# With proxy
instagram = InstagramClient(
    username="your_username", 
    password="your_password",
    use_proxy=True,
    proxy="http://username:password@proxy_host:port"
)
```

## Usage Examples

### Authentication

```python
# Login to Instagram
instagram.login()

# Check login status
if instagram.check_login_status():
    print("Successfully logged in")

# Logout when done
instagram.logout()
```

### Account Information

```python
# Get your account info
account_info = instagram.get_account_info()
if account_info:
    print(f"Username: {account_info.username}")
    print(f"Full name: {account_info.full_name}")
    print(f"Media count: {account_info.media_count}")
    print(f"Follower count: {account_info.follower_count}")
    print(f"Following count: {account_info.following_count}")
```

### User Interactions

```python
# Get information about a user
user_info = instagram.get_user_info("instagram")
if user_info:
    print(f"User: {user_info.username}")
    print(f"Full name: {user_info.full_name}")
    print(f"Biography: {user_info.biography}")

# Follow a user
instagram.follow_user("instagram")

# Unfollow a user
instagram.unfollow_user("instagram")
```

### Media Interactions

```python
# Get user's media posts
medias = instagram.get_user_medias("instagram", 5)
for media in medias:
    print(f"Media ID: {media.id}")
    print(f"Media type: {media.media_type}")
    print(f"Like count: {media.like_count}")
    
    # Download the media
    instagram.download_media(media.id, folder="downloads")
    
    # Like the media
    instagram.like_media(media.id)
    
    # Get comments
    comments = instagram.get_media_comments(media.id, 10)
    for comment in comments:
        print(f"Comment by {comment.user.username}: {comment.text}")
    
    # Post a comment
    instagram.post_comment(media.id, "Great post!")
```

### Hashtag Exploration

```python
# Get media posts for a hashtag
hashtag_medias = instagram.get_hashtag_medias("python", 5)
for media in hashtag_medias:
    print(f"Media ID: {media.id}")
    print(f"Posted by: {media.user.username}")
    print(f"Like count: {media.like_count}")
```

### Direct Messaging

```python
# Get direct message threads
threads = instagram.get_direct_threads(5)
for thread in threads:
    print(f"Thread ID: {thread.id}")
    print(f"Users: {[user.username for user in thread.users]}")

# Send a direct message
user_id = instagram.get_user_info("instagram").pk
instagram.send_direct_message([user_id], "Hello from instagrapi!")
```

## Error Handling

The client includes comprehensive error handling for common Instagram API issues:

- Challenge verification (SMS/Email verification)
- Two-factor authentication
- Rate limiting
- Connection errors
- Login failures

## Session Management

The client automatically saves and loads session data to avoid repeated logins:

```python
# Custom session file
instagram = InstagramClient(
    username="your_username", 
    password="your_password",
    session_file="custom_session.json"
)
```

## Notes

- Be careful with the frequency and volume of your requests to avoid being flagged by Instagram
- Using proxies can help avoid IP-based restrictions
- Consider implementing additional delays between actions for a more human-like behavior
- Keep your credentials secure and never share your session files 