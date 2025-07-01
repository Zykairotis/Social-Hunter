#!/usr/bin/env python3
"""
Examples of using the InstagramClient for various Instagram interactions.
"""

from instagram_client import InstagramClient
import logging
import os
import time
import argparse
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("instagram_examples.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("instagram_examples")

def setup_client(args):
    """Set up and authenticate the Instagram client"""
    instagram = InstagramClient(
        username=args.username,
        password=args.password,
        session_file=args.session_file,
        use_proxy=args.proxy is not None,
        proxy=args.proxy
    )
    
    if not instagram.login():
        logger.error("Failed to login. Exiting.")
        return None
    
    return instagram

def example_account_info(instagram):
    """Example: Get account information"""
    logger.info("=== EXAMPLE: ACCOUNT INFO ===")
    
    account_info = instagram.get_account_info()
    if account_info:
        logger.info(f"Username: {account_info.username}")
        logger.info(f"Full name: {account_info.full_name}")
        logger.info(f"Media count: {account_info.media_count}")
        logger.info(f"Follower count: {account_info.follower_count}")
        logger.info(f"Following count: {account_info.following_count}")
        logger.info(f"Biography: {account_info.biography}")
        
        # Return the account info for use in other examples
        return account_info
    
    return None

def example_user_info(instagram, username):
    """Example: Get information about a user"""
    logger.info(f"=== EXAMPLE: USER INFO for {username} ===")
    
    user_info = instagram.get_user_info(username)
    if user_info:
        logger.info(f"User ID: {user_info.pk}")
        logger.info(f"Username: {user_info.username}")
        logger.info(f"Full name: {user_info.full_name}")
        logger.info(f"Biography: {user_info.biography}")
        logger.info(f"Media count: {user_info.media_count}")
        logger.info(f"Follower count: {user_info.follower_count}")
        logger.info(f"Following count: {user_info.following_count}")
        logger.info(f"Is private: {user_info.is_private}")
        logger.info(f"Is verified: {user_info.is_verified}")
        
        # Return the user info for use in other examples
        return user_info
    
    return None

def example_user_medias(instagram, username_or_id, amount=5):
    """Example: Get user's media posts"""
    logger.info(f"=== EXAMPLE: USER MEDIA for {username_or_id} ===")
    
    medias = instagram.get_user_medias(username_or_id, amount)
    logger.info(f"Retrieved {len(medias)} media posts")
    
    for i, media in enumerate(medias, 1):
        logger.info(f"Media {i}:")
        logger.info(f"  ID: {media.id}")
        logger.info(f"  Type: {media.media_type}")
        logger.info(f"  Code: {media.code}")
        logger.info(f"  Taken at: {media.taken_at}")
        logger.info(f"  Like count: {media.like_count}")
        logger.info(f"  Comment count: {media.comment_count}")
        if hasattr(media, 'caption_text') and media.caption_text:
            logger.info(f"  Caption: {media.caption_text[:50]}...")
    
    return medias

def example_download_media(instagram, media_list):
    """Example: Download media posts"""
    if not media_list or len(media_list) == 0:
        logger.warning("No media to download")
        return
    
    logger.info("=== EXAMPLE: DOWNLOAD MEDIA ===")
    
    download_dir = os.path.join("downloads", datetime.now().strftime("%Y%m%d_%H%M%S"))
    os.makedirs(download_dir, exist_ok=True)
    
    for i, media in enumerate(media_list[:2], 1):  # Just download the first 2 for example
        logger.info(f"Downloading media {i} (ID: {media.id})...")
        path = instagram.download_media(media.id, folder=download_dir)
        logger.info(f"  Saved to: {path}")
        time.sleep(1)  # Add delay between downloads

def example_hashtag_medias(instagram, hashtag, amount=5):
    """Example: Get media posts for a hashtag"""
    logger.info(f"=== EXAMPLE: HASHTAG MEDIA for #{hashtag} ===")
    
    medias = instagram.get_hashtag_medias(hashtag, amount)
    logger.info(f"Retrieved {len(medias)} media posts for #{hashtag}")
    
    for i, media in enumerate(medias, 1):
        logger.info(f"Media {i}:")
        logger.info(f"  ID: {media.id}")
        logger.info(f"  Type: {media.media_type}")
        logger.info(f"  User: {media.user.username}")
        logger.info(f"  Like count: {media.like_count}")
        logger.info(f"  Comment count: {media.comment_count}")
    
    return medias

def example_like_media(instagram, media_list):
    """Example: Like media posts"""
    if not media_list or len(media_list) == 0:
        logger.warning("No media to like")
        return
    
    logger.info("=== EXAMPLE: LIKE MEDIA ===")
    
    for i, media in enumerate(media_list[:1], 1):  # Just like the first one for example
        logger.info(f"Liking media {i} (ID: {media.id})...")
        result = instagram.like_media(media.id)
        logger.info(f"  Result: {'Success' if result else 'Failed'}")
        time.sleep(2)  # Add delay between likes

def example_comment_media(instagram, media_list):
    """Example: Comment on media posts"""
    if not media_list or len(media_list) == 0:
        logger.warning("No media to comment on")
        return
    
    logger.info("=== EXAMPLE: COMMENT MEDIA ===")
    
    for i, media in enumerate(media_list[:1], 1):  # Just comment on the first one for example
        logger.info(f"Commenting on media {i} (ID: {media.id})...")
        comment_text = f"Great post! Commented via instagrapi at {datetime.now().strftime('%H:%M:%S')}"
        result = instagram.post_comment(media.id, comment_text)
        if result:
            logger.info(f"  Comment posted: {comment_text}")
        else:
            logger.info("  Failed to post comment")
        time.sleep(2)  # Add delay between comments

def example_get_comments(instagram, media_list):
    """Example: Get comments on media posts"""
    if not media_list or len(media_list) == 0:
        logger.warning("No media to get comments from")
        return
    
    logger.info("=== EXAMPLE: GET COMMENTS ===")
    
    for i, media in enumerate(media_list[:1], 1):  # Just get comments from the first one for example
        logger.info(f"Getting comments for media {i} (ID: {media.id})...")
        comments = instagram.get_media_comments(media.id, 5)
        logger.info(f"  Retrieved {len(comments)} comments")
        
        for j, comment in enumerate(comments, 1):
            logger.info(f"  Comment {j}:")
            logger.info(f"    User: {comment.user.username}")
            logger.info(f"    Text: {comment.text}")
            logger.info(f"    Created at: {comment.created_at_utc}")

def example_direct_threads(instagram):
    """Example: Get direct message threads"""
    logger.info("=== EXAMPLE: DIRECT THREADS ===")
    
    threads = instagram.get_direct_threads(5)
    logger.info(f"Retrieved {len(threads)} direct message threads")
    
    for i, thread in enumerate(threads, 1):
        logger.info(f"Thread {i}:")
        logger.info(f"  ID: {thread.id}")
        logger.info(f"  Users: {[user.username for user in thread.users]}")
        
        if hasattr(thread, 'messages') and thread.messages:
            logger.info(f"  Last message: {thread.messages[0].text[:50]}...")

def example_follow_unfollow(instagram, username):
    """Example: Follow and unfollow a user"""
    logger.info(f"=== EXAMPLE: FOLLOW/UNFOLLOW {username} ===")
    
    # Follow
    logger.info(f"Following {username}...")
    result = instagram.follow_user(username)
    logger.info(f"  Result: {'Success' if result else 'Failed'}")
    
    time.sleep(5)  # Wait before unfollowing
    
    # Unfollow
    logger.info(f"Unfollowing {username}...")
    result = instagram.unfollow_user(username)
    logger.info(f"  Result: {'Success' if result else 'Failed'}")

def run_examples(args):
    """Run selected examples"""
    instagram = setup_client(args)
    if not instagram:
        return
    
    try:
        # Get account info (always run this first)
        account_info = example_account_info(instagram)
        
        # Run selected examples
        if args.all or args.user_info:
            user_info = example_user_info(instagram, args.target_user)
        
        if args.all or args.user_medias:
            target = args.target_user if args.target_user else account_info.username
            medias = example_user_medias(instagram, target, args.amount)
            
            if args.all or args.download:
                example_download_media(instagram, medias)
            
            if args.all or args.like:
                example_like_media(instagram, medias)
            
            if args.all or args.comment:
                example_comment_media(instagram, medias)
            
            if args.all or args.get_comments:
                example_get_comments(instagram, medias)
        
        if args.all or args.hashtag:
            hashtag_medias = example_hashtag_medias(instagram, args.hashtag_name, args.amount)
        
        if args.all or args.direct:
            example_direct_threads(instagram)
        
        if (args.all or args.follow) and args.target_user:
            example_follow_unfollow(instagram, args.target_user)
    
    finally:
        # Always logout
        logger.info("Logging out...")
        instagram.logout()

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Instagram API Examples")
    
    # Authentication
    parser.add_argument("-u", "--username", required=True, help="Instagram username")
    parser.add_argument("-p", "--password", required=True, help="Instagram password")
    parser.add_argument("-s", "--session-file", default="instagram_session.json", help="Session file path")
    parser.add_argument("--proxy", help="Proxy URL (e.g., http://user:pass@host:port)")
    
    # Examples selection
    parser.add_argument("--all", action="store_true", help="Run all examples")
    parser.add_argument("--user-info", action="store_true", help="Get user info")
    parser.add_argument("--user-medias", action="store_true", help="Get user media posts")
    parser.add_argument("--download", action="store_true", help="Download media")
    parser.add_argument("--like", action="store_true", help="Like media")
    parser.add_argument("--comment", action="store_true", help="Comment on media")
    parser.add_argument("--get-comments", action="store_true", help="Get comments on media")
    parser.add_argument("--hashtag", action="store_true", help="Get hashtag media")
    parser.add_argument("--direct", action="store_true", help="Get direct message threads")
    parser.add_argument("--follow", action="store_true", help="Follow and unfollow user")
    
    # Parameters
    parser.add_argument("--target-user", default="instagram", help="Target username for user-related examples")
    parser.add_argument("--hashtag-name", default="python", help="Hashtag name for hashtag examples")
    parser.add_argument("--amount", type=int, default=5, help="Number of items to retrieve")
    
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    run_examples(args) 