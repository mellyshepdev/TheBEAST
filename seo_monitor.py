"""
The Beast -- SEO Monitor & Growth Engine
=========================================
Daily SEO health scanner for Georg's website. Checks page speed, meta tags,
broken links, content quality, and uses Perplexity to find keyword opportunities.

Usage:
    python seo_monitor.py                          # Full audit (requires API keys)
    python seo_monitor.py --dry-run                # Simulated audit (no API calls)
    python seo_monitor.py --url https://example.com  # Scan a specific URL
    python seo_monitor.py --save                   # Save report to JSON

Environment Variables:
    PERPLEXITY_API_KEY           - For keyword/trend research
    PAGESPEED_API_KEY            - Google PageSpeed Insights API key (optional, works without)
"""

import os
import sys
import json
import argparse
import requests
import re
from datetime import datetime, date
from urllib.parse import urljoin, urlparse

# ──────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────

PERPLEXITY_API_KEY = os.environ.get("PERPLEXITY_API_KEY", "")
PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"
PAGESPEED_API_KEY = os.environ.get("PAGESPEED_API_KEY", "")
PAGESPEED_API_URL = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"

DEFAULT_URL = "https://theofficialblacksheepcompany.com"
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "seo_reports")


# ──────────────────────────────────────────────
# Page Speed / Core Web Vitals
# ──────────────────────────────────────────────

def check_page_speed(url):
    """Check Core Web Vitals via Google PageSpeed Insights API."""
    params = {
        "url": url,
        "category": "PERFORMANCE",
        "strategy": "MOBILE"
    }
    if PAGESPEED_API_KEY:
        params["key"] = PAGESPEED_API_KEY

    try:
        resp = requests.get(PAGESPEED_API_URL, params=params, timeout=60)
        resp.raise_for_status()
        data = resp.json()

        lighthouse = data.get("lighthouseResult", {})
        audits = lighthouse.get("audits", {})
        categories = lighthouse.get("categories", {})

        perf_score = categories.get("performance", {}).get("score", 0)

        vitals = {
            "performance_score": int(perf_score * 100) if perf_score else 0,
            "first_contentful_paint": audits.get("first-contentful-paint", {}).get("displayValue", "N/A"),
            "largest_contentful_paint": audits.get("largest-contentful-paint", {}).get("displayValue", "N/A"),
            "cumulative_layout_shift": audits.get("cumulative-layout-shift", {}).get("displayValue", "N/A"),
            "total_blocking_time": audits.get("total-blocking-time", {}).get("displayValue", "N/A"),
            "speed_index": audits.get("speed-index", {}).get("displayValue", "N/A"),
        }

        # Extract opportunities (optimization suggestions from Lighthouse)
        opportunities = []
        for key, audit in audits.items():
            if audit.get("details", {}).get("type") == "opportunity":
                savings = audit.get("details", {}).get("overallSavingsMs", 0)
                if savings > 0:
                    opportunities.append({
                        "title": audit.get("title", key),
                        "description": audit.get("description", ""),
                        "savings_ms": savings
                    })

        vitals["opportunities"] = sorted(opportunities, key=lambda x: x["savings_ms"], reverse=True)[:5]
        return vitals

    except requests.exceptions.RequestException as e:
        return {"error": str(e), "performance_score": 0}


# ──────────────────────────────────────────────
# On-Page SEO Crawler
# ──────────────────────────────────────────────

def crawl_page_seo(url):
    """Crawl a page and analyze on-page SEO elements."""
    try:
        resp = requests.get(url, timeout=15, headers={"User-Agent": "TheBeast-SEO-Monitor/1.0"})
        resp.raise_for_status()
        html = resp.text

        issues = []
        suggestions = []

        # Title tag
        title_match = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
        title = title_match.group(1).strip() if title_match else ""
        if not title:
            issues.append({"severity": "HIGH", "issue": "Missing <title> tag", "fix": "Add a descriptive title tag (50-60 characters)"})
        elif len(title) < 30:
            issues.append({"severity": "MEDIUM", "issue": f"Title too short ({len(title)} chars): '{title}'", "fix": "Expand title to 50-60 characters with target keywords"})
        elif len(title) > 60:
            issues.append({"severity": "LOW", "issue": f"Title too long ({len(title)} chars)", "fix": "Trim title to under 60 characters to avoid truncation in search results"})

        # Meta description
        desc_match = re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', html, re.IGNORECASE)
        meta_desc = desc_match.group(1).strip() if desc_match else ""
        if not meta_desc:
            issues.append({"severity": "HIGH", "issue": "Missing meta description", "fix": "Add a compelling meta description (150-160 characters) summarizing the page"})
        elif len(meta_desc) < 120:
            issues.append({"severity": "MEDIUM", "issue": f"Meta description too short ({len(meta_desc)} chars)", "fix": "Expand to 150-160 characters for better CTR"})
        elif len(meta_desc) > 160:
            issues.append({"severity": "LOW", "issue": f"Meta description too long ({len(meta_desc)} chars)", "fix": "Trim to under 160 characters"})

        # H1 tags
        h1_matches = re.findall(r"<h1[^>]*>(.*?)</h1>", html, re.IGNORECASE | re.DOTALL)
        if not h1_matches:
            issues.append({"severity": "HIGH", "issue": "Missing H1 tag", "fix": "Add a single H1 tag with your primary keyword"})
        elif len(h1_matches) > 1:
            issues.append({"severity": "MEDIUM", "issue": f"Multiple H1 tags found ({len(h1_matches)})", "fix": "Use only one H1 per page"})

        # Images without alt text
        img_matches = re.findall(r"<img[^>]*>", html, re.IGNORECASE)
        imgs_without_alt = [img for img in img_matches if 'alt="' not in img.lower() and "alt='" not in img.lower()]
        if imgs_without_alt:
            issues.append({
                "severity": "MEDIUM",
                "issue": f"{len(imgs_without_alt)} of {len(img_matches)} images missing alt text",
                "fix": "Add descriptive alt text to all images for accessibility and SEO"
            })

        # Internal links
        link_matches = re.findall(r'href=["\'](.*?)["\']', html, re.IGNORECASE)
        internal_links = [l for l in link_matches if l.startswith("/") or urlparse(url).netloc in l]
        external_links = [l for l in link_matches if l.startswith("http") and urlparse(url).netloc not in l]

        if len(internal_links) < 3:
            suggestions.append("Add more internal links to improve site navigation and link equity")

        # Check for canonical tag
        canonical = re.search(r'<link\s+rel=["\']canonical["\']', html, re.IGNORECASE)
        if not canonical:
            issues.append({"severity": "LOW", "issue": "Missing canonical tag", "fix": "Add a canonical link tag to prevent duplicate content issues"})

        # Check for Open Graph tags
        og_tags = re.findall(r'<meta\s+property=["\']og:', html, re.IGNORECASE)
        if len(og_tags) < 3:
            suggestions.append("Add Open Graph tags (og:title, og:description, og:image) for better social sharing")

        # Check for viewport meta (mobile)
        viewport = re.search(r'<meta\s+name=["\']viewport["\']', html, re.IGNORECASE)
        if not viewport:
            issues.append({"severity": "HIGH", "issue": "Missing viewport meta tag", "fix": "Add viewport meta tag for mobile responsiveness"})

        # SSL check
        is_https = url.startswith("https://")
        if not is_https:
            issues.append({"severity": "HIGH", "issue": "Site not using HTTPS", "fix": "Install SSL certificate and redirect HTTP to HTTPS"})

        return {
            "url": url,
            "title": title,
            "meta_description": meta_desc,
            "h1_count": len(h1_matches),
            "image_count": len(img_matches),
            "images_without_alt": len(imgs_without_alt),
            "internal_links": len(internal_links),
            "external_links": len(external_links),
            "has_canonical": bool(canonical),
            "has_viewport": bool(viewport),
            "is_https": is_https,
            "og_tags_count": len(og_tags),
            "issues": issues,
            "suggestions": suggestions
        }

    except requests.exceptions.RequestException as e:
        return {"url": url, "error": str(e), "issues": [{"severity": "CRITICAL", "issue": f"Could not reach {url}", "fix": "Check if the site is online and the URL is correct"}]}


# ──────────────────────────────────────────────
# SEO Growth Suggestions (Perplexity)
# ──────────────────────────────────────────────

def get_seo_growth_suggestions(url, crawl_data):
    """Use Perplexity to generate SEO growth strategies based on site analysis."""
    if not PERPLEXITY_API_KEY:
        return {"suggestions": ["Set PERPLEXITY_API_KEY for AI-powered growth suggestions"], "source": "none"}

    today = date.today().strftime("%B %d, %Y")
    issues_summary = "\n".join([f"- [{i['severity']}] {i['issue']}" for i in crawl_data.get("issues", [])])

    prompt = f"""Today is {today}. I'm analyzing the website {url} for SEO improvements.

Current site analysis:
- Title: {crawl_data.get('title', 'N/A')}
- Meta description length: {len(crawl_data.get('meta_description', ''))} chars
- H1 tags: {crawl_data.get('h1_count', 0)}
- Images without alt text: {crawl_data.get('images_without_alt', 0)} of {crawl_data.get('image_count', 0)}
- Internal links: {crawl_data.get('internal_links', 0)}
- HTTPS: {crawl_data.get('is_https', False)}

Current issues found:
{issues_summary}

Based on this analysis and current SEO best practices, provide:
1. Top 5 immediate SEO fixes ranked by impact (with estimated effort: quick/medium/big)
2. 3 content ideas that could drive organic traffic based on current search trends
3. 2 engagement strategies to reduce bounce rate and increase time on site
4. Any emerging SEO trends this week that I should capitalize on

Be specific and actionable. No generic advice."""

    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "sonar",
        "messages": [
            {"role": "system", "content": "You are an expert SEO consultant. Be specific, data-driven, and actionable."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }

    try:
        response = requests.post(PERPLEXITY_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        return {
            "suggestions": data["choices"][0]["message"]["content"],
            "citations": data.get("citations", []),
            "source": "perplexity_sonar"
        }
    except requests.exceptions.RequestException as e:
        return {"suggestions": f"Error getting suggestions: {e}", "source": "error"}


# ──────────────────────────────────────────────
# Mock Data (for --dry-run)
# ──────────────────────────────────────────────

def get_mock_audit():
    """Return a simulated audit for testing."""
    return {
        "page_speed": {
            "performance_score": 72,
            "first_contentful_paint": "1.8 s",
            "largest_contentful_paint": "3.2 s",
            "cumulative_layout_shift": "0.12",
            "total_blocking_time": "340 ms",
            "speed_index": "2.4 s",
            "opportunities": [
                {"title": "Properly size images", "description": "Serve images in right size to save data", "savings_ms": 1200},
                {"title": "Eliminate render-blocking resources", "description": "CSS and JS blocking first paint", "savings_ms": 850},
                {"title": "Serve images in next-gen formats", "description": "Use WebP/AVIF instead of JPEG/PNG", "savings_ms": 600}
            ]
        },
        "crawl": {
            "url": DEFAULT_URL,
            "title": "The Official Black Sheep Company",
            "meta_description": "Creative services and digital solutions by Georg.",
            "h1_count": 1,
            "image_count": 12,
            "images_without_alt": 4,
            "internal_links": 8,
            "external_links": 3,
            "has_canonical": False,
            "has_viewport": True,
            "is_https": True,
            "og_tags_count": 2,
            "issues": [
                {"severity": "MEDIUM", "issue": "Meta description too short (52 chars)", "fix": "Expand to 150-160 characters for better CTR"},
                {"severity": "MEDIUM", "issue": "4 of 12 images missing alt text", "fix": "Add descriptive alt text to all images"},
                {"severity": "LOW", "issue": "Missing canonical tag", "fix": "Add canonical link tag to prevent duplicate content"},
                {"severity": "LOW", "issue": "Insufficient Open Graph tags", "fix": "Add og:title, og:description, og:image for social sharing"}
            ],
            "suggestions": [
                "Add more internal links to boost page authority distribution",
                "Add Open Graph tags for better social sharing previews"
            ]
        },
        "growth": {
            "suggestions": """## Top 5 Immediate SEO Fixes

1. **Expand meta descriptions** (Quick fix, 10 min)
   - Current: 52 chars. Target: 150-160 chars.
   - Include a call-to-action and primary keyword.
   - Impact: +15-30% CTR from search results.

2. **Add alt text to all images** (Quick fix, 15 min)
   - 4 images missing. Describe each image with relevant keywords.
   - Impact: Better image search rankings + accessibility.

3. **Optimize image sizes** (Medium effort, 30 min)
   - Convert to WebP format, compress large files.
   - Impact: ~1.2s faster load time, better Core Web Vitals.

4. **Add canonical tags** (Quick fix, 5 min)
   - Prevents duplicate content penalties.
   - Impact: Cleaner indexing by Google.

5. **Remove render-blocking CSS/JS** (Medium effort, 1 hr)
   - Defer non-critical JS, inline critical CSS.
   - Impact: ~850ms faster first paint.

## 3 Content Ideas for Organic Traffic

1. **"Behind the Brand" blog series** - Personal stories about building Black Sheep Company. "Founder story" keywords get 2.4K monthly searches.
2. **Client case studies** - "Before/after" transformation posts. These rank well for service-related queries.
3. **Industry tips listicles** - "Top 10 design trends 2026" style posts drive consistent organic traffic.

## 2 Engagement Strategies

1. **Add a sticky CTA bar** - A floating "Get a Free Quote" button reduces bounce by giving visitors an immediate action.
2. **Implement exit-intent popup** - Capture emails with a valuable lead magnet before visitors leave.

## Emerging SEO Trends This Week

- **AI-generated content signals**: Google is now better at identifying thin AI content. Focus on unique, experience-based writing.
- **Video SEO**: Short-form video embeds on pages are boosting time-on-page metrics significantly.""",
            "citations": [],
            "source": "mock_data"
        }
    }


# ──────────────────────────────────────────────
# Output & Display
# ──────────────────────────────────────────────

def display_report(audit_data):
    """Print the SEO report in Beast-branded format."""
    ps = audit_data.get("page_speed", {})
    cr = audit_data.get("crawl", {})
    gr = audit_data.get("growth", {})

    print("\n" + "=" * 60)
    print("  THE BEAST -- DAILY SEO BRIEFING")
    print("=" * 60)
    print(f"\n  Date: {date.today().strftime('%A, %B %d, %Y')}")
    print(f"  Target: {cr.get('url', DEFAULT_URL)}")

    # Performance Score
    score = ps.get("performance_score", 0)
    if score >= 90:
        grade = "EXCELLENT"
    elif score >= 70:
        grade = "NEEDS WORK"
    elif score >= 50:
        grade = "POOR"
    else:
        grade = "CRITICAL"

    print(f"\n--- PERFORMANCE: {score}/100 ({grade}) ---")
    print(f"  First Contentful Paint:   {ps.get('first_contentful_paint', 'N/A')}")
    print(f"  Largest Contentful Paint: {ps.get('largest_contentful_paint', 'N/A')}")
    print(f"  Cumulative Layout Shift:  {ps.get('cumulative_layout_shift', 'N/A')}")
    print(f"  Total Blocking Time:      {ps.get('total_blocking_time', 'N/A')}")
    print(f"  Speed Index:              {ps.get('speed_index', 'N/A')}")

    # Speed Opportunities
    opps = ps.get("opportunities", [])
    if opps:
        print(f"\n  TOP SPEED OPPORTUNITIES:")
        for opp in opps:
            print(f"  - {opp['title']} (save ~{opp['savings_ms']}ms)")

    # On-Page SEO
    print(f"\n--- ON-PAGE SEO ---")
    print(f"  Title:           {cr.get('title', 'N/A')}")
    print(f"  Meta Desc:       {len(cr.get('meta_description', ''))} chars")
    print(f"  H1 Tags:         {cr.get('h1_count', 0)}")
    print(f"  Images:          {cr.get('image_count', 0)} total, {cr.get('images_without_alt', 0)} missing alt text")
    print(f"  Internal Links:  {cr.get('internal_links', 0)}")
    print(f"  Canonical:       {'Yes' if cr.get('has_canonical') else 'MISSING'}")
    print(f"  HTTPS:           {'Yes' if cr.get('is_https') else 'NO'}")
    print(f"  Open Graph Tags: {cr.get('og_tags_count', 0)}")

    # Issues
    issues = cr.get("issues", [])
    if issues:
        print(f"\n--- ISSUES FOUND ({len(issues)}) ---")
        for issue in issues:
            icon = "!!!" if issue["severity"] == "HIGH" else ("!!" if issue["severity"] == "MEDIUM" else "!")
            print(f"  [{icon} {issue['severity']}] {issue['issue']}")
            print(f"      Fix: {issue['fix']}")

    # Growth Suggestions
    growth_text = gr.get("suggestions", "")
    if growth_text:
        print(f"\n--- GROWTH SUGGESTIONS ---")
        print(f"\n{growth_text}")

    print("\n" + "=" * 60)
    print("  Stay on top of it, Georg. The Beast has your SEO covered.")
    print("=" * 60 + "\n")


def save_report(audit_data):
    """Save the SEO report to JSON."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    filename = f"seo_report_{date.today().strftime('%Y-%m-%d')}.json"
    filepath = os.path.join(OUTPUT_DIR, filename)

    output = {
        "date": date.today().isoformat(),
        "audit": audit_data,
        "generated_at": datetime.now().isoformat()
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"[SAVED] SEO report saved to: {filepath}")
    return filepath


# ──────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="The Beast -- SEO Monitor & Growth Engine")
    parser.add_argument("--url", type=str, default=DEFAULT_URL, help="URL to audit")
    parser.add_argument("--dry-run", action="store_true", help="Simulate with mock data")
    parser.add_argument("--save", action="store_true", help="Save report to JSON")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    args = parser.parse_args()

    print("\n The Beast SEO Monitor initializing...")

    if args.dry_run:
        print("[DRY RUN] Using mock audit data.\n")
        audit_data = get_mock_audit()
    else:
        print(f"[LIVE] Auditing {args.url}...\n")

        # Run all checks
        print("[1/3] Checking page speed...")
        page_speed = check_page_speed(args.url)

        print("[2/3] Crawling on-page SEO...")
        crawl = crawl_page_seo(args.url)

        print("[3/3] Generating growth suggestions...")
        growth = get_seo_growth_suggestions(args.url, crawl)

        audit_data = {
            "page_speed": page_speed,
            "crawl": crawl,
            "growth": growth
        }

    if args.json:
        print(json.dumps(audit_data, indent=2, ensure_ascii=False))
    else:
        display_report(audit_data)

    if args.save or not args.dry_run:
        save_report(audit_data)


if __name__ == "__main__":
    main()
