"""
analyzer.py - Website Metadata Extractor and Smart Categorizer for LinkVault
"""

import re
import urllib.parse
from typing import Dict, Any, Tuple
import requests
from bs4 import BeautifulSoup

# Standard HTTP headers to avoid being blocked by anti-bot measures
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# Categorization rules based on domains and keywords
CATEGORY_RULES = {
    "Education": {
        "domains": [
            "docs.python.org", "python.org", "kaggle.com", "coursera.org", "edx.org",
            "khanacademy.org", "udemy.com", "wikipedia.org", "w3schools.com",
            "geeksforgeeks.org", "sciencedirect.com", "arxiv.org", "scholar.google.com",
            "mit.edu", "stanford.edu", "harvard.edu", "duolingo.com", "brilliant.org",
            "codecademy.com", "freecodecamp.org", "leetcode.com"
        ],
        "keywords": [
            "tutorial", "course", "education", "learn", "academy", "study", "university",
            "school", "documentation", "guide", "syllabus", "lecture", "textbook",
            "algorithm", "exercise", "practice", "cheat sheet", "reference", "viva"
        ]
    },
    "Development": {
        "domains": [
            "github.com", "gitlab.com", "stackoverflow.com", "dev.to", "npmjs.com",
            "pypi.org", "codepen.io", "replit.com", "huggingface.co", "hashnode.com",
            "docker.com", "kubernetes.io", "developer.mozilla.org", "fastapi.tiangolo.com",
            "react.dev", "vuejs.org", "nextjs.org", "streamlit.io"
        ],
        "keywords": [
            "github", "git", "code", "repository", "api", "framework", "library",
            "developer", "programming", "script", "python", "javascript", "react",
            "css", "html", "backend", "frontend", "compiler", "npm", "pip", "pypi",
            "stack overflow", "bug", "deploy", "repo", "terminal", "sdk"
        ]
    },
    "News": {
        "domains": [
            "theverge.com", "techcrunch.com", "bbc.com", "cnn.com", "nytimes.com",
            "reuters.com", "bloomberg.com", "theguardian.com", "wired.com",
            "news.ycombinator.com", "engadget.com", "arstechnica.com", "ndtv.com",
            "indiatimes.com", "washingtonpost.com"
        ],
        "keywords": [
            "news", "breaking", "headline", "article", "report", "press", "journalism",
            "verge", "tech news", "daily", "politics", "world", "opinion", "coverage"
        ]
    },
    "Shopping": {
        "domains": [
            "amazon.com", "amazon.in", "ebay.com", "flipkart.com", "walmart.com",
            "bestbuy.com", "aliexpress.com", "etsy.com", "target.com", "myntra.com"
        ],
        "keywords": [
            "shop", "shopping", "store", "buy", "deal", "cart", "discount", "price",
            "ecommerce", "product", "checkout", "fashion", "order", "sale"
        ]
    },
    "Finance": {
        "domains": [
            "moneycontrol.com", "yahoo.com/finance", "marketwatch.com", "investopedia.com",
            "coinmarketcap.com", "binance.com", "tradingview.com", "zerodha.com",
            "mint.com", "stripe.com"
        ],
        "keywords": [
            "finance", "money", "stock", "crypto", "trading", "investment", "bank",
            "market", "portfolio", "currency", "bitcoin", "shares", "dividend", "mutual fund"
        ]
    },
    "Entertainment": {
        "domains": [
            "youtube.com", "youtu.be", "netflix.com", "spotify.com", "twitch.tv",
            "imdb.com", "hulu.com", "disneyplus.com", "primevideo.com", "soundcloud.com",
            "ign.com", "gameinformer.com"
        ],
        "keywords": [
            "video", "movie", "music", "song", "streaming", "game", "gaming", "watch",
            "play", "podcast", "trailer", "episode", "cinema", "entertainment", "stream"
        ]
    },
    "Social": {
        "domains": [
            "twitter.com", "x.com", "linkedin.com", "reddit.com", "facebook.com",
            "instagram.com", "pinterest.com", "discord.com", "medium.com", "threads.net"
        ],
        "keywords": [
            "social", "community", "post", "tweet", "profile", "network", "forum",
            "discussion", "sub-reddit", "feed", "connect", "chat"
        ]
    },
    "Tools & Productivity": {
        "domains": [
            "notion.so", "figma.com", "canva.com", "trello.com", "miro.com",
            "docs.google.com", "drive.google.com", "slack.com", "zoom.us", "linear.app"
        ],
        "keywords": [
            "tool", "app", "productivity", "workspace", "task", "design", "note",
            "dashboard", "calculator", "convert", "utility", "organizer", "generator"
        ]
    }
}

CATEGORIES_LIST = [
    "Education",
    "Development",
    "News",
    "Shopping",
    "Finance",
    "Entertainment",
    "Social",
    "Tools & Productivity",
    "Other"
]

def clean_title(raw_title: str) -> str:
    """Clean extracted HTML title by removing extra spaces and common site tags."""
    if not raw_title:
        return ""
    # Collapse multiple whitespace
    cleaned = re.sub(r'\s+', ' ', raw_title).strip()
    return cleaned

def extract_domain(url: str) -> str:
    """Extract clean domain name from URL (e.g. docs.python.org or github.com)."""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    parsed = urllib.parse.urlparse(url)
    domain = parsed.netloc.lower()
    if domain.startswith("www."):
        domain = domain[4:]
    return domain

def categorize_url(url: str, title: str = "", description: str = "") -> str:
    """
    Classify website category using keyword & domain rule engine.
    Fast, offline-friendly, deterministic, and accurate for viva demonstration.
    """
    domain = extract_domain(url).lower()
    full_text = f"{url} {domain} {title} {description}".lower()
    
    # Priority 1: Direct domain match
    for category, rules in CATEGORY_RULES.items():
        for dom in rules["domains"]:
            if dom in domain or domain.endswith("." + dom):
                return category
                
    # Priority 2: Keyword frequency score matching
    category_scores: Dict[str, int] = {cat: 0 for cat in CATEGORY_RULES}
    
    for category, rules in CATEGORY_RULES.items():
        for kw in rules["keywords"]:
            if kw in full_text:
                # Give higher weight if keyword is in domain or title
                weight = 3 if (kw in domain or kw in title.lower()) else 1
                category_scores[category] += weight

    best_category, max_score = max(category_scores.items(), key=lambda x: x[1])
    
    if max_score > 0:
        return best_category
        
    return "Other"

def fetch_website_info(url: str, timeout: int = 6) -> Dict[str, Any]:
    """
    Fetch website HTML and extract title, meta description, and category.
    Handles network errors, SSL errors, timeouts gracefully.
    """
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
        
    domain = extract_domain(url)
    result = {
        "url": url,
        "domain": domain,
        "title": domain.capitalize(), # Fallback title
        "description": "",
        "category": "Other",
        "status_code": 200,
        "is_broken": False,
        "error_message": None
    }
    
    try:
        response = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout, allow_redirects=True)
        result["status_code"] = response.status_code
        
        if response.status_code >= 400:
            result["is_broken"] = True
            result["title"] = f"{domain} (HTTP {response.status_code})"
            result["description"] = f"Failed to fetch content. Server returned status code {response.status_code}."
            result["category"] = categorize_url(url, result["title"], result["description"])
            return result
            
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Extract title
        title_tag = soup.find("title")
        if title_tag and title_tag.string:
            title_text = clean_title(title_tag.string)
            if title_text:
                result["title"] = title_text
        elif soup.find("h1"):
            h1_text = clean_title(soup.find("h1").get_text())
            if h1_text:
                result["title"] = h1_text
                
        # Extract meta description or og:description
        meta_desc = soup.find("meta", attrs={"name": "description"}) or \
                    soup.find("meta", attrs={"property": "og:description"}) or \
                    soup.find("meta", attrs={"name": "og:description"})
                    
        if meta_desc and meta_desc.get("content"):
            result["description"] = clean_title(meta_desc["content"])
        else:
            # Fallback snippet from first paragraph
            first_p = soup.find("p")
            if first_p:
                p_text = clean_title(first_p.get_text())
                if len(p_text) > 20:
                    result["description"] = p_text[:200] + ("..." if len(p_text) > 200 else "")
                    
    except requests.exceptions.SSLError:
        # Try fetching without SSL verify as a fallback for self-signed certificates
        try:
            response = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout, verify=False)
            result["status_code"] = response.status_code
            soup = BeautifulSoup(response.text, "html.parser")
            title_tag = soup.find("title")
            if title_tag and title_tag.string:
                result["title"] = clean_title(title_tag.string)
        except Exception as e:
            result["is_broken"] = True
            result["error_message"] = str(e)
            result["title"] = domain.capitalize()
            result["description"] = f"SSL/Connection error when connecting to {domain}."
    except requests.exceptions.Timeout:
        result["is_broken"] = True
        result["status_code"] = 408
        result["title"] = domain.capitalize()
        result["description"] = f"Request timed out while connecting to {domain}."
    except Exception as e:
        result["is_broken"] = True
        result["status_code"] = 0
        result["title"] = domain.capitalize()
        result["description"] = f"Could not connect to URL: {str(e)}"

    # Automatically compute category using rule engine
    result["category"] = categorize_url(url, result["title"], result["description"])
    return result
