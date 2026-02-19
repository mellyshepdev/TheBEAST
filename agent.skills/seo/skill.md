---
name: SEO Monitor & Growth
description: Daily SEO health monitoring, optimization suggestions, and engagement strategies for Georg's website. Tracks rankings, page speed, content gaps, and competitor activity.
version: 1.0
owner: Georg
tags: [seo, growth, analytics, engagement, optimization]
allowed-tools: ["run_command", "write_to_file", "view_file"]
---

# SEO Monitor & Growth

## Mission

The Beast monitors Georg's website daily, identifies SEO issues and opportunities, and delivers actionable suggestions to increase traffic, improve rankings, and boost engagement.

## Target Website

- **Domain**: `theofficialblacksheepcompany.com`
- **Industry**: Personal brand / creative services
- **Goal**: Higher organic traffic, better Google rankings, increased engagement

## Daily SEO Checks

1. **Technical Health**
   - Page load speed (Core Web Vitals: LCP, FID, CLS)
   - Mobile responsiveness
   - Broken links (404s)
   - SSL certificate status
   - Sitemap and robots.txt validity
   - Structured data / Schema markup

2. **Content & On-Page SEO**
   - Title tags and meta descriptions (missing, too short, too long, duplicate)
   - Heading structure (H1/H2/H3 hierarchy)
   - Image alt text coverage
   - Internal linking opportunities
   - Content freshness — pages that haven't been updated in 30+ days

3. **Rankings & Visibility**
   - Track keyword positions for target terms
   - New keyword opportunities from search trends
   - Pages losing ranking (position drops)
   - Featured snippet opportunities

4. **Engagement & Growth**
   - Bounce rate by page
   - Top exit pages (where are people leaving?)
   - Pages with high impressions but low clicks (CTR optimization)
   - Social sharing suggestions for top-performing content

## Suggestion Format

Each daily report should include:

- **Priority score** (1-10): How urgent is this fix?
- **What's wrong**: Clear, jargon-free description
- **What to do**: Step-by-step fix instructions
- **Expected impact**: What improvement to expect (traffic, ranking, speed)
- **Effort level**: Quick fix (5 min) / Medium (30 min) / Big project (hours+)

## Competitor Monitoring

- Track 3-5 competitor sites for content gaps
- Identify keywords competitors rank for that Georg doesn't
- Flag new content competitors publish in Georg's niche

## Tools & APIs

- **Perplexity Sonar**: Real-time search trend analysis and competitor research
- **Google PageSpeed Insights API**: Core Web Vitals and performance scores
- **Google Search Console API**: Rankings, impressions, clicks (when connected)
- **Lighthouse** (local): Full page audit scoring
- **Custom crawler**: Check links, meta tags, headings, alt text

## How It Works

1. **Cron trigger** (n8n, daily at 7 AM) or manual "How's my SEO?"
2. `seo_monitor.py` runs the full audit suite
3. Beast delivers the daily SEO briefing via OpenClaw
4. Georg applies fixes (or asks The Beast to auto-fix code-level issues)
5. Weekly trend comparison shows progress over time
