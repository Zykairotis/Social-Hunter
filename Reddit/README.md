# Reddit API Application

A FastAPI application for interacting with the Reddit API.

## Features

- OAuth authentication with Reddit
- Token management (storage and refresh)
- 50+ API endpoints for accessing Reddit data
- Comprehensive error handling
- Support for both read and write operations

## Setup

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file based on the example:
   ```
   REDDIT_CLIENT_ID=your_client_id_here
   REDDIT_CLIENT_SECRET=your_client_secret_here
   REDDIT_USER_AGENT=FastAPI:RedditApp:v0.1.0
   REDDIT_REDIRECT_URI=http://localhost:8550
   ```

## How to get Reddit API credentials

1. Go to https://www.reddit.com/prefs/apps
2. Click "Create App" or "Create Another App" button
3. Fill in the required fields:
   - Name: Your app name
   - App type: Choose "web app"
   - Description: Brief description of your app
   - About URL: Your website URL (optional)
   - Redirect URI: http://localhost:8550
4. Click "Create app" button
5. Copy the client ID (the string under the app name) and client secret

## Running the application

Start the server with uvicorn:

```
uvicorn main:app --host 0.0.0.0 --port 8550 --reload
```

Or run directly:

```
python main.py
```

## API Endpoints

### Authentication Endpoints

- `GET /healthcheck`: Check if the API is running properly
- `GET /login`: Generate Reddit authorization URL
- `GET /`: Handle the callback from Reddit OAuth (root endpoint)
- `GET /auth/check`: Check if the authentication token is valid
- `GET /auth/token`: Get the current access token
- `POST /auth/token`: Save a token manually
- `DELETE /auth/token`: Clear the stored token

### User Identity Endpoints

- `GET /api/me`: Get information about the authenticated user
- `GET /api/me/karma`: Get user's karma breakdown by subreddit
- `GET /api/me/trophies`: Get user's trophies
- `GET /api/preferences`: Get user preferences
- `PATCH /api/preferences`: Update user preferences

### Subreddit Endpoints

- `GET /api/subreddits/mine`: Get user's subscribed subreddits
- `GET /api/subreddit/{subreddit}`: Get information about a specific subreddit
- `GET /api/subreddit/{subreddit}/rules`: Get rules for a subreddit
- `GET /api/subreddit/{subreddit}/moderators`: Get moderators of a subreddit
- `GET /api/subreddits/{category}`: Get subreddits by category (popular, new, etc.)
- `GET /api/subreddit/{subreddit}/flairs`: Get available post flairs in a subreddit
- `GET /api/subreddit/{subreddit}/traffic`: Get traffic statistics of a subreddit
- `POST /api/subscribe`: Subscribe or unsubscribe from a subreddit

### Post Endpoints

- `GET /api/posts/{sort}`: Get posts from subscribed subreddits (hot, new, rising, top)
- `GET /api/subreddit/{subreddit}/posts/{sort}`: Get posts from a specific subreddit
- `GET /api/post/{post_id}`: Get details of a specific post
- `GET /api/post/{post_id}/duplicates`: Get duplicates of a post
- `GET /api/by_ids`: Get information about multiple posts/comments by IDs
- `POST /api/submit`: Submit a new post to a subreddit
- `POST /api/vote`: Vote on a post or comment
- `POST /api/save`: Save a post or comment
- `POST /api/unsave`: Unsave a post or comment
- `POST /api/hide`: Hide a post
- `POST /api/unhide`: Unhide a post
- `POST /api/flair`: Select a flair for a post
- `POST /api/report`: Report a post or comment

### Comment Endpoints

- `POST /api/comment`: Add a comment to a post or comment
- `PUT /api/comment`: Edit a comment
- `DELETE /api/comment/{comment_id}`: Delete a comment

### User Content Endpoints

- `GET /api/me/saved`: Get user's saved posts and comments
- `GET /api/me/hidden`: Get user's hidden posts
- `GET /api/me/upvoted`: Get user's upvoted posts
- `GET /api/me/downvoted`: Get user's downvoted posts

### User Profile Endpoints

- `GET /api/user/{username}`: Get information about a specific user
- `GET /api/user/{username}/posts`: Get posts submitted by a user
- `GET /api/user/{username}/comments`: Get comments by a user
- `POST /api/block`: Block a user

### Friends Endpoints

- `GET /api/friends`: Get list of friends
- `PUT /api/friends/{username}`: Add a user as friend
- `DELETE /api/friends/{username}`: Remove a user from friends

### Message Endpoints

- `GET /api/messages/{where}`: Get private messages (inbox, unread, sent)
- `POST /api/message`: Send a private message
- `POST /api/message/read`: Mark messages as read
- `POST /api/message/unread`: Mark messages as unread

### Search Endpoints

- `GET /api/search`: Search Reddit

### Multireddit Endpoints

- `GET /api/multireddits/{username}`: Get multireddits of a user
- `GET /api/multireddit/{username}/{multi_name}`: Get a specific multireddit

### Wiki Endpoints

- `GET /api/subreddit/{subreddit}/wiki`: Get wiki pages of a subreddit
- `GET /api/subreddit/{subreddit}/wiki/{page}`: Get a specific wiki page

### Misc Endpoints

- `GET /api/trending`: Get trending subreddits

## Authentication Flow

1. Call `/login` to get the Reddit authorization URL
2. Redirect the user to the authorization URL
3. Reddit will redirect back to your application's root endpoint (`/`)
4. The application will exchange the authorization code for an access token
5. The token will be automatically stored for future API requests
6. Use the token to make API requests to the Reddit API

## Token Management

The application includes a token manager that:
- Stores tokens securely in a JSON file
- Automatically checks token validity
- Handles token expiration

## Documentation

API documentation is available at:
- Swagger UI: http://localhost:8550/docs
- ReDoc: http://localhost:8550/redoc

## Required OAuth Scopes

Different endpoints require different OAuth scopes. Here are the main ones:

- `identity`: Access your username and identity
- `read`: Access posts and comments
- `vote`: Vote on posts and comments
- `save`: Save/unsave posts and comments
- `edit`: Edit your posts and comments
- `submit`: Submit posts and comments
- `subscribe`: Manage your subscriptions
- `history`: Access your voting history
- `flair`: Manage your flair
- `privatemessages`: Access your private messages
- `report`: Report content
- `modconfig`, `modflair`, `modlog`, `modposts`, `modwiki`: Moderator actions
- `wikiedit`, `wikiread`: Wiki actions

Make sure to request the appropriate scopes when generating the authorization URL. 