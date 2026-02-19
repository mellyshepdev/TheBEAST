---
name: Social Content Scout
description: Daily trend scout & content suggestion engine for Blue the Pitbull. Monitors Instagram & TikTok pet trends via Perplexity, generates actionable content ideas, and auto-posts with trending hashtags.
version: 1.0
owner: Georg
tags: [social, content, instagram, tiktok, trends, blue, pitbull]
allowed-tools: ["run_command", "write_to_file", "view_file"]
---

# Social Content Scout

## Mission
Every day, The Beast scans what's trending on dog/pet Instagram and TikTok, then tells Georg exactly what to do with **Blue** (his pitbull) to create viral-worthy content. When Georg shoots the content, The Beast posts it with all the right hashtags.

## Dog Profile
- **Name**: Blue
- **Breed**: Pitbull
- **Vibe**: High energy, muscular, photogenic, loyal, goofy
- **Strengths**: Jumping, beach runs, trick shots, intense stares, costume tolerance

## Daily Suggestion Rules
1. **Be specific**: Not "take a photo of Blue" → "Take Blue to the beach at golden hour, get a slow-mo of him jumping over a wave. Caption: 'Built different. 🌊'"
2. **Match trends**: If couples-with-dogs content is trending, suggest that. If costume content is hot, suggest a costume shoot.
3. **Rotate content pillars**:
   - 🏖️ Outdoor adventures (beach, hiking, park)
   - 🎬 Trick/training clips
   - 👔 Costume & dress-up
   - 😂 Reaction & comedy clips
   - 🌅 Aesthetic/golden hour shoots
   - 🎄 Seasonal & holiday themes
4. **Include a sample caption**: Write a draft caption in brand voice.
5. **Timing**: Suggest shooting time based on lighting needs (golden hour, etc.)

## Posting Rules
- **Hashtags**: Always include 20-30 trending + evergreen hashtags
- **Evergreen hashtags**: #dogsofinstagram #pitbull #pitbullsofinstagram #bluenosepitbull #doglife #pitbulllove #doglover #bully #petsofinstagram #dogstagram
- **Trending hashtags**: Pulled from current trend data
- **Optimal posting times**: 11AM–1PM or 7PM–9PM (highest engagement windows)
- **Location tag**: Always suggest a location if applicable

## How It Works
1. **Cron trigger** (n8n) or manual ask: "What should Blue do today?"
2. `trend_scout.py` runs → fetches trends via Perplexity Sonar API
3. Beast delivers the suggestion via OpenClaw (WhatsApp/Matrix/Slack)
4. Georg shoots the content and uploads it
5. `content_poster.py` runs → posts with caption + hashtags
6. Beast confirms with the live post link
