"""
The Beast — Social Content Trend Scout
=======================================
Scans trending dog/pet content on Instagram & TikTok using Perplexity Sonar API,
then generates a daily actionable content suggestion for Blue the Pitbull.

Usage:
    python trend_scout.py                  # Full scout (requires PERPLEXITY_API_KEY)
    python trend_scout.py --dry-run        # Simulate with mock data (no API calls)
    python trend_scout.py --save           # Save suggestion to JSON file

Environment Variables:
    PERPLEXITY_API_KEY   - Perplexity Sonar API key (https://docs.perplexity.ai)
    RAPIDAPI_KEY         - Optional fallback for direct Instagram/TikTok scraping
"""

import os
import sys
import json
import random
import argparse
import requests
from datetime import datetime, date

# Load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # Falls back to system environment variables

# ──────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────

PERPLEXITY_API_KEY = os.environ.get("PERPLEXITY_API_KEY", "")
PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"

BLUE_PROFILE = {
    "name": "Blue",
    "breed": "Pitbull",
    "traits": ["high energy", "muscular", "photogenic", "loyal", "goofy", "loves water", "great jumper"],
    "strengths": ["jumping", "beach runs", "trick shots", "intense stares", "costume tolerance"]
}

CONTENT_PILLARS = [
    "outdoor adventures (beach, hiking, park, lake)",
    "trick and training clips",
    "costume and dress-up shoots",
    "reaction and comedy clips",
    "aesthetic golden hour photography",
    "seasonal and holiday themed content"
]

EVERGREEN_HASHTAGS = [
    "#dogsofinstagram", "#pitbull", "#pitbullsofinstagram", "#bluenosepitbull",
    "#doglife", "#pitbulllove", "#doglover", "#bully", "#petsofinstagram",
    "#dogstagram", "#pitbullnation", "#pitbullworld", "#dogsofig",
    "#bullybreed", "#pitbullmom", "#pitbulldad", "#instadog", "#dogoftheday"
]

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "content_suggestions")


# ──────────────────────────────────────────────
# Perplexity Sonar API — Trend Discovery
# ──────────────────────────────────────────────

def fetch_trends_perplexity():
    """Use Perplexity Sonar to discover what's currently trending in pet/dog content."""
    if not PERPLEXITY_API_KEY:
        print("[ERROR] PERPLEXITY_API_KEY not set. Use --dry-run or set the key.")
        sys.exit(1)

    today = date.today().strftime("%B %d, %Y")

    prompt = f"""Today is {today}. I need to know what's currently trending on Instagram and TikTok 
for dog and pet content. Specifically:

1. What types of dog/pet photos and videos are going viral RIGHT NOW?
2. What hashtags are trending for dogs/pets this week?
3. What specific content themes or challenges are popular (e.g., beach dogs, costume trends, 
   trick videos, funny reactions)?
4. Are there any seasonal or current-event-related pet content trends?
5. What posting formats are performing best (reels, carousels, stories, TikToks)?

Focus on content that would work well for a muscular, photogenic pitbull.
Give me concrete, specific trends with example descriptions — not generic advice."""

    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "sonar",
        "messages": [
            {
                "role": "system",
                "content": "You are a social media trend analyst specializing in pet/dog content on Instagram and TikTok. Be specific and current."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.3
    }

    try:
        response = requests.post(PERPLEXITY_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        trend_report = data["choices"][0]["message"]["content"]

        # Extract citations if available
        citations = data.get("citations", [])

        return {
            "report": trend_report,
            "citations": citations,
            "fetched_at": datetime.now().isoformat(),
            "source": "perplexity_sonar"
        }
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Perplexity API call failed: {e}")
        sys.exit(1)


def generate_suggestion(trend_data):
    """Take trend data and generate a specific, actionable suggestion for Blue."""
    if not PERPLEXITY_API_KEY:
        print("[ERROR] PERPLEXITY_API_KEY not set.")
        sys.exit(1)

    today_pillar = CONTENT_PILLARS[date.today().timetuple().tm_yday % len(CONTENT_PILLARS)]

    prompt = f"""Based on these current pet/dog Instagram and TikTok trends:

{trend_data['report']}

Generate ONE specific, actionable content suggestion for my pitbull named Blue.
Blue is: {', '.join(BLUE_PROFILE['traits'])}. Good at: {', '.join(BLUE_PROFILE['strengths'])}.

Today's content pillar focus: {today_pillar}

Your response must be a valid JSON object with these exact keys:
{{
    "suggestion_title": "Short catchy title for the suggestion",
    "what_to_do": "Detailed, specific instructions on what to shoot. Include location, time of day, angles, props needed. Be VERY specific like a creative director.",
    "sample_caption": "A ready-to-post Instagram caption (fun, engaging, with emojis)",
    "trending_hashtags": ["list", "of", "20-30", "trending", "hashtags", "without #"],
    "best_time_to_shoot": "Recommended time of day and why",
    "best_time_to_post": "Recommended posting time window",
    "platform_priority": "instagram or tiktok — which platform this content would perform better on",
    "content_format": "reel, carousel, single photo, story, or tiktok",
    "trend_it_matches": "Which specific trend this suggestion is based on"
}}

Only return the JSON object, nothing else."""

    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "sonar",
        "messages": [
            {
                "role": "system",
                "content": "You are a creative director for pet social media content. Output valid JSON only."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7
    }

    try:
        response = requests.post(PERPLEXITY_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        raw_content = data["choices"][0]["message"]["content"]

        # Parse the JSON from response (handle markdown code blocks if present)
        json_str = raw_content.strip()
        if json_str.startswith("```"):
            json_str = json_str.split("\n", 1)[1]
            json_str = json_str.rsplit("```", 1)[0]

        suggestion = json.loads(json_str)

        # Add evergreen hashtags to trending ones
        all_hashtags = [f"#{h}" if not h.startswith("#") else h for h in suggestion.get("trending_hashtags", [])]
        for tag in EVERGREEN_HASHTAGS:
            if tag not in all_hashtags:
                all_hashtags.append(tag)
        suggestion["all_hashtags"] = all_hashtags

        return suggestion

    except (requests.exceptions.RequestException, json.JSONDecodeError, KeyError) as e:
        print(f"[ERROR] Suggestion generation failed: {e}")
        sys.exit(1)


# ──────────────────────────────────────────────
# Mock Data (for --dry-run)
# ──────────────────────────────────────────────

def get_mock_trends():
    """Return simulated trend data for testing without API calls."""
    mock_trends = [
        {
            "report": "Beach dog content is dominating Instagram this week. Videos of dogs jumping over waves and running on the sand are getting 3-5x normal engagement. TikTok is seeing a surge in 'my dog's reaction to...' videos. Carousels showing dogs in different outfits are performing well. Golden hour pitbull photography is trending with hashtags like #pitbullglow and #goldenhourpup.",
            "citations": ["https://example.com/trends"],
            "fetched_at": datetime.now().isoformat(),
            "source": "mock_data"
        },
        {
            "report": "Training and trick videos are viral this week. Dogs learning new tricks in under 60 seconds are blowing up on TikTok. Instagram Reels featuring 'before and after training' are trending. Pitbull positivity content is surging with creators posting muscular pitbulls being gentle with babies and small animals. Hashtag #pitbullsoftie has 2M+ views this week.",
            "citations": ["https://example.com/trends"],
            "fetched_at": datetime.now().isoformat(),
            "source": "mock_data"
        },
        {
            "report": "Costume and themed dog photoshoots are trending heavily. Valentine's Day aftermath content showing dogs in bow ties and 'date night' setups is performing. TikTok challenge: film your dog's reaction to wearing sunglasses. Story-style content '24 hours with my pitbull' is trending. Night photography of dogs with city lights is a new aesthetic trend.",
            "citations": ["https://example.com/trends"],
            "fetched_at": datetime.now().isoformat(),
            "source": "mock_data"
        }
    ]
    return random.choice(mock_trends)


def get_mock_suggestion(trend_data):
    """Generate a mock suggestion for dry-run mode."""
    mock_suggestions = [
        {
            "suggestion_title": "🌊 Beach Beast Mode",
            "what_to_do": "Hit the beach around 4:30 PM for golden hour. Get Blue running along the shoreline and capture a slow-mo video of him leaping over a small wave. Get low — shoot from ground level to make him look massive against the sunset. Bonus shot: Blue sitting stoically at the water's edge staring into the distance like a Greek god.",
            "sample_caption": "Built different. Born to run. 🌊💪\nBlue said the ocean ain't ready for this energy.\n\n#pitbull #beachdog #goldenhour",
            "trending_hashtags": ["beachdog", "dogsofthebeach", "pitbulllife", "beachvibes", "dogsonbeaches", "coastaldog", "sunsetdog", "beachpup", "oceandog", "pitbullglow", "goldenhourpup", "dogphotography", "beachbully", "pitbullpower", "saltlife", "dogbeachday", "bullybeach", "pitbullmuscle", "beachbeast", "coastaldogs"],
            "best_time_to_shoot": "4:30-5:30 PM — golden hour for dramatic lighting and warm tones",
            "best_time_to_post": "7:00-9:00 PM — peak evening scroll time",
            "platform_priority": "instagram",
            "content_format": "reel",
            "trend_it_matches": "Beach dog content with golden hour photography"
        },
        {
            "suggestion_title": "🎓 60-Second Trick Master",
            "what_to_do": "Film a quick trick compilation in the backyard or living room. Start with Blue doing 'sit', then 'shake', then a spin, then his best jump. Edit it as rapid-fire cuts with trending audio. Keep it under 30 seconds for maximum retention. End with Blue staring at the camera like 'yeah, I did that.'",
            "sample_caption": "IQ: Off the charts. Treats consumed: Also off the charts. 🧠🦴\nBlue just passed his finals with honors.\n\n#pitbulltricks #smartdog #dogtricks",
            "trending_hashtags": ["dogtricks", "smartdog", "pitbulltricks", "dogtraining", "trickdog", "cleverpup", "trainthedogs", "pitbulltraining", "60secondchallenge", "dogchallenge", "trickshot", "goodboy", "pitbullsmarts", "traineddog", "doggoals", "pitbullpride", "dogtricksofinstagram", "obedientdog", "trainyourdog", "tricksfordays"],
            "best_time_to_shoot": "Morning — dogs are most responsive to training after a walk",
            "best_time_to_post": "11:00 AM - 1:00 PM — lunch break scroll window",
            "platform_priority": "tiktok",
            "content_format": "tiktok",
            "trend_it_matches": "Training/trick compilation videos going viral on TikTok"
        },
        {
            "suggestion_title": "😎 Shades On, World Off",
            "what_to_do": "Put some cool sunglasses on Blue and film his reaction. Then do a 'transformation' style video: first shot = Blue looking normal, then transition with a flash effect to Blue wearing the sunglasses in a boss pose. Shoot against a clean background — plain wall or car hood works great. Portrait mode for the IG carousel version.",
            "sample_caption": "Management called. Said I'm too cool for the office. 😎🐕\nBlue with the shades = instant vibe upgrade.\n\n#pitbullswag #cooldog #sunglassesdog",
            "trending_hashtags": ["cooldog", "dogswag", "sunglassesdog", "pitbullstyle", "dogsinsunglasses", "bossdog", "vibecheck", "pitbullvibes", "swagdog", "drippydog", "fashiondog", "dripcheck", "coolesdog", "petfashion", "stylishdog", "dogdrip", "pitbullfashion", "ootddog", "dogwithstyle", "freshdog"],
            "best_time_to_shoot": "Anytime — indoor shoot with good lighting",
            "best_time_to_post": "7:00-9:00 PM — viral TikTok hours",
            "platform_priority": "tiktok",
            "content_format": "tiktok",
            "trend_it_matches": "Dog sunglasses reaction challenge trending on TikTok"
        }
    ]

    suggestion = random.choice(mock_suggestions)
    all_hashtags = [f"#{h}" for h in suggestion["trending_hashtags"]]
    for tag in EVERGREEN_HASHTAGS:
        if tag not in all_hashtags:
            all_hashtags.append(tag)
    suggestion["all_hashtags"] = all_hashtags

    return suggestion


# ──────────────────────────────────────────────
# Output & Display
# ──────────────────────────────────────────────

def display_suggestion(suggestion, trend_data=None):
    """Print the suggestion in Beast-branded format."""
    print("\n" + "=" * 60)
    print("🐾  THE BEAST — DAILY CONTENT SCOUT  🐾")
    print("=" * 60)
    print(f"\n📅  Date: {date.today().strftime('%A, %B %d, %Y')}")
    if trend_data:
        print(f"📡  Source: {trend_data.get('source', 'unknown')}")
    print(f"\n🎯  TODAY'S MISSION: {suggestion['suggestion_title']}")
    print("-" * 60)
    print(f"\n📸  WHAT TO DO:")
    print(f"   {suggestion['what_to_do']}")
    print(f"\n⏰  BEST TIME TO SHOOT: {suggestion['best_time_to_shoot']}")
    print(f"📤  BEST TIME TO POST:  {suggestion['best_time_to_post']}")
    print(f"📱  PLATFORM PRIORITY:  {suggestion['platform_priority'].upper()}")
    print(f"🎬  FORMAT:             {suggestion['content_format'].upper()}")
    print(f"🔥  TREND MATCH:        {suggestion['trend_it_matches']}")
    print(f"\n✍️   SAMPLE CAPTION:")
    print(f"   {suggestion['sample_caption']}")
    print(f"\n#️⃣   HASHTAGS ({len(suggestion['all_hashtags'])}):")
    # Print hashtags in rows of 5
    for i in range(0, len(suggestion['all_hashtags']), 5):
        chunk = suggestion['all_hashtags'][i:i+5]
        print(f"   {' '.join(chunk)}")
    print("\n" + "=" * 60)
    print("💪  Go get it, Georg. Blue is ready to break the internet.")
    print("=" * 60 + "\n")


def save_suggestion(suggestion, trend_data=None):
    """Save the suggestion to a JSON file for the content poster to use."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    filename = f"suggestion_{date.today().strftime('%Y-%m-%d')}.json"
    filepath = os.path.join(OUTPUT_DIR, filename)

    output = {
        "date": date.today().isoformat(),
        "suggestion": suggestion,
        "trend_data": trend_data,
        "generated_at": datetime.now().isoformat()
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"[SAVED] Suggestion saved to: {filepath}")
    return filepath


# ──────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="The Beast — Social Content Trend Scout")
    parser.add_argument("--dry-run", action="store_true", help="Simulate with mock data (no API calls)")
    parser.add_argument("--save", action="store_true", help="Save suggestion to JSON file")
    parser.add_argument("--json", action="store_true", help="Output raw JSON instead of formatted text")
    args = parser.parse_args()

    print("\n🐾 The Beast Content Scout initializing...")

    if args.dry_run:
        print("[DRY RUN] Using mock trend data — no API calls.\n")
        trend_data = get_mock_trends()
        suggestion = get_mock_suggestion(trend_data)
    else:
        print("[LIVE] Fetching real-time trends from Perplexity Sonar...\n")
        trend_data = fetch_trends_perplexity()
        print("[OK] Trends fetched. Generating suggestion for Blue...\n")
        suggestion = generate_suggestion(trend_data)

    if args.json:
        output = {"date": date.today().isoformat(), "suggestion": suggestion, "trend_data": trend_data}
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        display_suggestion(suggestion, trend_data)

    if args.save or not args.dry_run:
        save_suggestion(suggestion, trend_data)



if __name__ == "__main__":
    main()
