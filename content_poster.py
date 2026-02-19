"""
The Beast — Content Poster
===========================
Takes Georg's photos/videos of Blue and posts them to Instagram and TikTok
with auto-generated captions and trending hashtags.

Usage:
    python content_poster.py --media ./blue_beach.jpg --platform instagram
    python content_poster.py --media ./blue_trick.mp4 --platform tiktok
    python content_poster.py --media ./blue.jpg --platform all
    python content_poster.py --dry-run --media ./test.jpg
    python content_poster.py --from-suggestion        # Uses today's saved suggestion

Environment Variables:
    INSTAGRAM_ACCESS_TOKEN  - Instagram Graph API access token
    INSTAGRAM_ACCOUNT_ID    - Instagram Business Account ID
    TIKTOK_ACCESS_TOKEN     - TikTok Content Posting API token
    PERPLEXITY_API_KEY      - For generating fresh captions if no suggestion file exists
"""

import os
import sys
import json
import argparse
import requests
import mimetypes
from datetime import date, datetime

# ──────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────

INSTAGRAM_ACCESS_TOKEN = os.environ.get("INSTAGRAM_ACCESS_TOKEN", "")
INSTAGRAM_ACCOUNT_ID = os.environ.get("INSTAGRAM_ACCOUNT_ID", "")
TIKTOK_ACCESS_TOKEN = os.environ.get("TIKTOK_ACCESS_TOKEN", "")

SUGGESTION_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "content_suggestions")

EVERGREEN_HASHTAGS = [
    "#dogsofinstagram", "#pitbull", "#pitbullsofinstagram", "#bluenosepitbull",
    "#doglife", "#pitbulllove", "#doglover", "#bully", "#petsofinstagram",
    "#dogstagram", "#pitbullnation", "#pitbullworld", "#dogsofig",
    "#bullybreed", "#instadog", "#dogoftheday"
]


# ──────────────────────────────────────────────
# Suggestion Loader
# ──────────────────────────────────────────────

def load_todays_suggestion():
    """Load today's suggestion from the trend scout output."""
    filename = f"suggestion_{date.today().strftime('%Y-%m-%d')}.json"
    filepath = os.path.join(SUGGESTION_DIR, filename)

    if not os.path.exists(filepath):
        print(f"[WARN] No suggestion file found for today: {filepath}")
        print("       Run trend_scout.py first, or provide a --caption manually.")
        return None

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data.get("suggestion", {})


def build_caption(suggestion=None, custom_caption=None):
    """Build the final caption with hashtags."""
    if custom_caption:
        caption = custom_caption
        hashtags = EVERGREEN_HASHTAGS
    elif suggestion:
        caption = suggestion.get("sample_caption", "Blue being Blue. 💪🐾")
        hashtags = suggestion.get("all_hashtags", EVERGREEN_HASHTAGS)
    else:
        caption = "Blue being Blue. 💪🐾"
        hashtags = EVERGREEN_HASHTAGS

    # Ensure hashtags are formatted
    formatted_tags = []
    for tag in hashtags:
        if not tag.startswith("#"):
            tag = f"#{tag}"
        formatted_tags.append(tag)

    # Build the final caption: caption + line break + hashtags
    hashtag_block = " ".join(formatted_tags)
    full_caption = f"{caption}\n.\n.\n.\n{hashtag_block}"

    return full_caption, formatted_tags


# ──────────────────────────────────────────────
# Instagram Posting (Graph API)
# ──────────────────────────────────────────────

def post_to_instagram(media_path, caption):
    """Post a photo or video to Instagram via the Graph API."""
    if not INSTAGRAM_ACCESS_TOKEN or not INSTAGRAM_ACCOUNT_ID:
        print("[ERROR] Instagram credentials not set.")
        print("       Set INSTAGRAM_ACCESS_TOKEN and INSTAGRAM_ACCOUNT_ID environment variables.")
        return False

    mime_type, _ = mimetypes.guess_type(media_path)
    is_video = mime_type and mime_type.startswith("video")

    # Step 1: Create media container
    if is_video:
        # For video (Reels)
        container_url = f"https://graph.facebook.com/v18.0/{INSTAGRAM_ACCOUNT_ID}/media"
        container_params = {
            "media_type": "REELS",
            "video_url": media_path,  # Must be a public URL
            "caption": caption,
            "access_token": INSTAGRAM_ACCESS_TOKEN
        }
    else:
        # For photo
        container_url = f"https://graph.facebook.com/v18.0/{INSTAGRAM_ACCOUNT_ID}/media"
        container_params = {
            "image_url": media_path,  # Must be a public URL
            "caption": caption,
            "access_token": INSTAGRAM_ACCESS_TOKEN
        }

    try:
        print("[IG] Creating media container...")
        resp = requests.post(container_url, params=container_params, timeout=30)
        resp.raise_for_status()
        container_id = resp.json().get("id")

        if not container_id:
            print(f"[ERROR] Failed to create media container: {resp.json()}")
            return False

        # Step 2: Publish the container
        print("[IG] Publishing...")
        publish_url = f"https://graph.facebook.com/v18.0/{INSTAGRAM_ACCOUNT_ID}/media_publish"
        publish_params = {
            "creation_id": container_id,
            "access_token": INSTAGRAM_ACCESS_TOKEN
        }
        pub_resp = requests.post(publish_url, params=publish_params, timeout=30)
        pub_resp.raise_for_status()

        post_id = pub_resp.json().get("id")
        print(f"[IG] ✅ Posted successfully! Post ID: {post_id}")
        return True

    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Instagram posting failed: {e}")
        return False


# ──────────────────────────────────────────────
# TikTok Posting (Content Posting API)
# ──────────────────────────────────────────────

def post_to_tiktok(media_path, caption):
    """Post a video to TikTok via the Content Posting API."""
    if not TIKTOK_ACCESS_TOKEN:
        print("[ERROR] TikTok credentials not set.")
        print("       Set TIKTOK_ACCESS_TOKEN environment variable.")
        return False

    mime_type, _ = mimetypes.guess_type(media_path)
    is_video = mime_type and mime_type.startswith("video")

    if not is_video:
        print("[WARN] TikTok only supports video content. Skipping photo.")
        return False

    try:
        # Step 1: Initialize upload
        print("[TT] Initializing video upload...")
        init_url = "https://open.tiktokapis.com/v2/post/publish/video/init/"
        headers = {
            "Authorization": f"Bearer {TIKTOK_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }

        file_size = os.path.getsize(media_path)
        init_payload = {
            "post_info": {
                "title": caption[:150],  # TikTok title limit
                "privacy_level": "PUBLIC_TO_EVERYONE",
                "disable_duet": False,
                "disable_comment": False,
                "disable_stitch": False
            },
            "source_info": {
                "source": "FILE_UPLOAD",
                "video_size": file_size
            }
        }

        resp = requests.post(init_url, headers=headers, json=init_payload, timeout=30)
        resp.raise_for_status()
        upload_url = resp.json().get("data", {}).get("upload_url")

        if not upload_url:
            print(f"[ERROR] Failed to get upload URL: {resp.json()}")
            return False

        # Step 2: Upload the video file
        print("[TT] Uploading video...")
        with open(media_path, "rb") as f:
            upload_resp = requests.put(
                upload_url,
                headers={
                    "Content-Type": "video/mp4",
                    "Content-Range": f"bytes 0-{file_size - 1}/{file_size}"
                },
                data=f,
                timeout=120
            )
            upload_resp.raise_for_status()

        print("[TT] ✅ Video uploaded and posted successfully!")
        return True

    except requests.exceptions.RequestException as e:
        print(f"[ERROR] TikTok posting failed: {e}")
        return False


# ──────────────────────────────────────────────
# Dry Run / Preview
# ──────────────────────────────────────────────

def preview_post(media_path, caption, hashtags, platform):
    """Show what would be posted without actually posting."""
    print("\n" + "=" * 60)
    print("🐾  THE BEAST — POST PREVIEW (DRY RUN)  🐾")
    print("=" * 60)
    print(f"\n📅  Date: {date.today().strftime('%A, %B %d, %Y')}")
    print(f"📁  Media: {media_path}")

    mime_type, _ = mimetypes.guess_type(media_path)
    media_type = "VIDEO" if mime_type and mime_type.startswith("video") else "PHOTO"
    print(f"🎬  Type: {media_type}")
    print(f"📱  Platform: {platform.upper()}")

    print(f"\n✍️   CAPTION:")
    # Show caption without the hashtag block for readability
    caption_lines = caption.split("\n.\n.\n.\n")
    print(f"   {caption_lines[0]}")

    print(f"\n#️⃣   HASHTAGS ({len(hashtags)}):")
    for i in range(0, len(hashtags), 5):
        chunk = hashtags[i:i+5]
        print(f"   {' '.join(chunk)}")

    print(f"\n📊  FULL CAPTION LENGTH: {len(caption)} characters")
    if len(caption) > 2200:
        print("   ⚠️  Warning: Caption exceeds Instagram's 2200 character limit!")

    print("\n" + "=" * 60)
    print("🔒  DRY RUN — Nothing was posted.")
    print("    Run without --dry-run to post for real.")
    print("=" * 60 + "\n")


# ──────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="The Beast — Content Poster")
    parser.add_argument("--media", type=str, help="Path to photo or video file")
    parser.add_argument("--platform", type=str, default="instagram",
                        choices=["instagram", "tiktok", "all"],
                        help="Target platform (default: instagram)")
    parser.add_argument("--caption", type=str, help="Custom caption (overrides suggestion)")
    parser.add_argument("--from-suggestion", action="store_true",
                        help="Use today's saved suggestion from trend_scout.py")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview the post without actually posting")
    args = parser.parse_args()

    print("\n🐾 The Beast Content Poster initializing...")

    # Validate media
    if not args.media:
        print("[ERROR] --media is required. Provide the path to your photo/video.")
        sys.exit(1)

    if not os.path.exists(args.media) and not args.dry_run:
        # In dry-run, we don't need the file to actually exist
        if not args.dry_run:
            print(f"[ERROR] Media file not found: {args.media}")
            sys.exit(1)

    # Load suggestion or use custom caption
    suggestion = None
    if args.from_suggestion or not args.caption:
        suggestion = load_todays_suggestion()

    caption, hashtags = build_caption(
        suggestion=suggestion,
        custom_caption=args.caption
    )

    # Dry run mode
    if args.dry_run:
        preview_post(args.media, caption, hashtags, args.platform)
        return

    # Post for real
    results = {}

    if args.platform in ("instagram", "all"):
        results["instagram"] = post_to_instagram(args.media, caption)

    if args.platform in ("tiktok", "all"):
        results["tiktok"] = post_to_tiktok(args.media, caption)

    # Summary
    print("\n" + "=" * 60)
    print("🐾  THE BEAST — POSTING RESULTS  🐾")
    print("=" * 60)
    for platform, success in results.items():
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"   {platform.upper()}: {status}")
    print("=" * 60 + "\n")

    # Save the posting record
    record = {
        "date": date.today().isoformat(),
        "media": args.media,
        "caption": caption,
        "hashtags": hashtags,
        "results": results,
        "posted_at": datetime.now().isoformat()
    }

    os.makedirs(SUGGESTION_DIR, exist_ok=True)
    record_path = os.path.join(SUGGESTION_DIR, f"post_record_{date.today().strftime('%Y-%m-%d')}.json")
    with open(record_path, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2, ensure_ascii=False)
    print(f"[SAVED] Post record: {record_path}")


if __name__ == "__main__":
    main()
