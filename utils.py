"""
utils.py - Import, Export, Broken Link Checker, and Sample Data Generator for LinkVault
"""

import csv
import io
import concurrent.futures
from typing import List, Dict, Any, Tuple
import requests

from database import add_bookmark, update_link_status, get_all_bookmarks
from analyzer import fetch_website_info, categorize_url, DEFAULT_HEADERS

# 30 Curated Sample Bookmarks across categories for Viva Demo
SAMPLE_BOOKMARKS = [
    {
        "url": "https://docs.python.org/3/",
        "title": "Python 3 Documentation",
        "domain": "docs.python.org",
        "category": "Education",
        "description": "Official Python programming language documentation, language reference, and standard library tutorial.",
        "is_favorite": True
    },
    {
        "url": "https://github.com",
        "title": "GitHub: Let's build from here",
        "domain": "github.com",
        "category": "Development",
        "description": "World's leading AI-powered developer platform to build, scale, and deliver software.",
        "is_favorite": True
    },
    {
        "url": "https://www.kaggle.com",
        "title": "Kaggle: Your Home for Data Science",
        "domain": "kaggle.com",
        "category": "Education",
        "description": "Inside Kaggle you'll find all the code and data you need for your data science project.",
        "is_favorite": True
    },
    {
        "url": "https://www.theverge.com",
        "title": "The Verge — Tech News, Reviews and Science",
        "domain": "theverge.com",
        "category": "News",
        "description": "Covering the intersection of technology, science, art, and culture.",
        "is_favorite": True
    },
    {
        "url": "https://stackoverflow.com",
        "title": "Stack Overflow - Where Developers Learn, Share, & Build",
        "domain": "stackoverflow.com",
        "category": "Development",
        "description": "The largest, most trusted online community for developers to learn, share programming knowledge.",
        "is_favorite": False
    },
    {
        "url": "https://w3schools.com",
        "title": "W3Schools Online Web Tutorials",
        "domain": "w3schools.com",
        "category": "Education",
        "description": "W3Schools offers free online tutorials, references and exercises in all major languages of the web.",
        "is_favorite": False
    },
    {
        "url": "https://pypi.org",
        "title": "PyPI · The Python Package Index",
        "domain": "pypi.org",
        "category": "Development",
        "description": "The Python Package Index (PyPI) is a repository of software for the Python programming language.",
        "is_favorite": False
    },
    {
        "url": "https://streamlit.io",
        "title": "Streamlit — A faster way to build data apps",
        "domain": "streamlit.io",
        "category": "Development",
        "description": "Streamlit turns data scripts into shareable web apps in minutes. All in pure Python.",
        "is_favorite": False
    },
    {
        "url": "https://geeksforgeeks.org",
        "title": "GeeksforGeeks | A computer science portal for geeks",
        "domain": "geeksforgeeks.org",
        "category": "Education",
        "description": "A Computer Science portal for geeks containing well written, well thought and well explained computer science articles.",
        "is_favorite": False
    },
    {
        "url": "https://techcrunch.com",
        "title": "TechCrunch — Startup and Technology News",
        "domain": "techcrunch.com",
        "category": "News",
        "description": "TechCrunch reports on the business of technology, startups, venture capital funding, and Silicon Valley.",
        "is_favorite": False
    },
    {
        "url": "https://arxiv.org",
        "title": "arXiv.org e-Print Archive",
        "domain": "arxiv.org",
        "category": "Education",
        "description": "Open-access archive for 2+ million scholarly articles in physics, mathematics, computer science, and AI.",
        "is_favorite": False
    },
    {
        "url": "https://leetcode.com",
        "title": "LeetCode - The World's Leading Online Technical Dev Platform",
        "domain": "leetcode.com",
        "category": "Education",
        "description": "Level up your coding skills and prepare for technical interviews with coding challenges.",
        "is_favorite": False
    },
    {
        "url": "https://bbc.com/news",
        "title": "BBC News - World & US News",
        "domain": "bbc.com",
        "category": "News",
        "description": "Visit BBC News for up-to-the-minute news, breaking news, video, audio and feature stories.",
        "is_favorite": False
    },
    {
        "url": "https://news.ycombinator.com",
        "title": "Hacker News",
        "domain": "news.ycombinator.com",
        "category": "News",
        "description": "Hacker News is a social news website focusing on computer science and entrepreneurship.",
        "is_favorite": False
    },
    {
        "url": "https://amazon.com",
        "title": "Amazon.com. Spend less. Smile more.",
        "domain": "amazon.com",
        "category": "Shopping",
        "description": "Free shipping on millions of items. Get the best of Shopping and Entertainment with Prime.",
        "is_favorite": False
    },
    {
        "url": "https://ebay.com",
        "title": "Electronics, Cars, Fashion, Collectibles & More | eBay",
        "domain": "ebay.com",
        "category": "Shopping",
        "description": "Buy and sell electronics, cars, fashion apparel, collectibles, sporting goods, digital cameras, and baby items.",
        "is_favorite": False
    },
    {
        "url": "https://investopedia.com",
        "title": "Investopedia: Sharpen Your Financial Knowledge",
        "domain": "investopedia.com",
        "category": "Finance",
        "description": "Investopedia is the world's leading source of financial content on the web, ranging from market news to dictionary terms.",
        "is_favorite": False
    },
    {
        "url": "https://coinmarketcap.com",
        "title": "Cryptocurrency Prices, Charts And Market Capitalizations | CoinMarketCap",
        "domain": "coinmarketcap.com",
        "category": "Finance",
        "description": "Top cryptocurrency prices and charts, listed by market capitalization.",
        "is_favorite": False
    },
    {
        "url": "https://youtube.com",
        "title": "YouTube",
        "domain": "youtube.com",
        "category": "Entertainment",
        "description": "Enjoy the videos and music you love, upload original content, and share it all with friends, family, and the world.",
        "is_favorite": False
    },
    {
        "url": "https://spotify.com",
        "title": "Spotify - Web Player: Music for everyone",
        "domain": "spotify.com",
        "category": "Entertainment",
        "description": "Spotify is a digital music service that gives you access to millions of songs.",
        "is_favorite": False
    },
    {
        "url": "https://reddit.com",
        "title": "Reddit - Dive into anything",
        "domain": "reddit.com",
        "category": "Social",
        "description": "Reddit is a network of communities where people can dive into their interests, hobbies and passions.",
        "is_favorite": False
    },
    {
        "url": "https://linkedin.com",
        "title": "LinkedIn: Log In or Sign Up",
        "domain": "linkedin.com",
        "category": "Social",
        "description": "Manage your professional identity. Build and engage with your professional network.",
        "is_favorite": False
    },
    {
        "url": "https://notion.so",
        "title": "Notion – One workspace. Every team.",
        "domain": "notion.so",
        "category": "Tools & Productivity",
        "description": "A new tool that blends your everyday work apps into one. It's the all-in-one workspace for you and your team.",
        "is_favorite": False
    },
    {
        "url": "https://figma.com",
        "title": "Figma: The Collaborative Interface Design Tool",
        "domain": "figma.com",
        "category": "Tools & Productivity",
        "description": "Figma is the leading collaborative design tool for building meaningful products.",
        "is_favorite": False
    },
    {
        "url": "https://canva.com",
        "title": "Canva: Visual Suite for Everyone",
        "domain": "canva.com",
        "category": "Tools & Productivity",
        "description": "Canva makes design amazingly simple and fun. Create stunning graphics with your photos and videos.",
        "is_favorite": False
    },
    {
        "url": "https://developer.mozilla.org",
        "title": "MDN Web Docs",
        "domain": "developer.mozilla.org",
        "category": "Education",
        "description": "The MDN Web Docs site provides information about Open Web technologies including HTML, CSS, and APIs.",
        "is_favorite": False
    },
    {
        "url": "https://dev.to",
        "title": "DEV Community",
        "domain": "dev.to",
        "category": "Development",
        "description": "A constructive and inclusive social network for software developers.",
        "is_favorite": False
    },
    {
        "url": "https://coursera.org",
        "title": "Coursera | Build Skills with Online Courses from Top Institutions",
        "domain": "coursera.org",
        "category": "Education",
        "description": "Join Coursera for free and learn online from world-class universities and industry leaders.",
        "is_favorite": False
    },
    {
        "url": "https://wired.com",
        "title": "WIRED - The Latest in Technology, Science, Culture and Business",
        "domain": "wired.com",
        "category": "News",
        "description": "WIRED is where tomorrow is realized. It is the essential source of information and ideas that make sense of a world in constant transformation.",
        "is_favorite": False
    },
    {
        "url": "https://invalid-nonexistent-domain-test12345.org",
        "title": "Broken Test Link (For Viva Demo)",
        "domain": "invalid-nonexistent-domain-test12345.org",
        "category": "Other",
        "description": "A test link to demonstrate the Broken Link Checker feature during viva presentation.",
        "is_favorite": False
    }
]

def seed_sample_bookmarks() -> Tuple[int, int]:
    """
    Seed the SQLite database with 30 pre-configured sample bookmarks.
    Returns (added_count, skipped_count).
    """
    added = 0
    skipped = 0
    for item in SAMPLE_BOOKMARKS:
        success, _, _ = add_bookmark(
            url=item["url"],
            title=item["title"],
            domain=item["domain"],
            category=item["category"],
            description=item["description"],
            is_favorite=item.get("is_favorite", False)
        )
        if success:
            added += 1
        else:
            skipped += 1
    return added, skipped

def export_bookmarks_to_csv() -> str:
    """Export all saved bookmarks to CSV string format."""
    bookmarks = get_all_bookmarks()
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write CSV Header
    writer.writerow(["ID", "URL", "Title", "Domain", "Category", "Description", "Favorite", "Status Code", "Is Broken", "Created At"])
    
    for bm in bookmarks:
        writer.writerow([
            bm["id"],
            bm["url"],
            bm["title"],
            bm["domain"],
            bm["category"],
            bm["description"],
            "Yes" if bm["is_favorite"] else "No",
            bm["status_code"],
            "Yes" if bm["is_broken"] else "No",
            bm["created_at"]
        ])
        
    return output.getvalue()

def process_bulk_file(file_content: str, filename: str, auto_scrape: bool = True) -> Dict[str, Any]:
    """
    Process uploaded CSV or TXT file containing URLs.
    Supports simple TXT (1 URL per line) or CSV format.
    """
    urls_to_process = []
    
    if filename.lower().endswith(".csv"):
        reader = csv.reader(io.StringIO(file_content))
        header = next(reader, None) # Check header
        
        # Check if header contains url column
        url_idx = 0
        title_idx = None
        cat_idx = None
        desc_idx = None
        
        if header:
            lower_header = [h.strip().lower() for h in header]
            if "url" in lower_header:
                url_idx = lower_header.index("url")
            if "title" in lower_header:
                title_idx = lower_header.index("title")
            if "category" in lower_header:
                cat_idx = lower_header.index("category")
            if "description" in lower_header:
                desc_idx = lower_header.index("description")
                
        for row in reader:
            if not row or len(row) <= url_idx:
                continue
            u = row[url_idx].strip()
            if u.startswith(("http://", "https://", "www.")):
                urls_to_process.append({
                    "url": u,
                    "title": row[title_idx].strip() if title_idx is not None and len(row) > title_idx else "",
                    "category": row[cat_idx].strip() if cat_idx is not None and len(row) > cat_idx else "",
                    "description": row[desc_idx].strip() if desc_idx is not None and len(row) > desc_idx else ""
                })
    else:
        # Plain text file with URLs
        lines = file_content.splitlines()
        for line in lines:
            line = line.strip()
            if line.startswith(("http://", "https://", "www.")):
                urls_to_process.append({"url": line, "title": "", "category": "", "description": ""})
                
    added = 0
    duplicates = 0
    errors = 0
    
    for item in urls_to_process:
        url = item["url"]
        title = item["title"]
        category = item["category"]
        description = item["description"]
        
        # Auto extract info if missing
        if auto_scrape and (not title or not category):
            info = fetch_website_info(url)
            title = title or info["title"]
            category = category or info["category"]
            description = description or info["description"]
        else:
            if not category:
                category = categorize_url(url, title, description)
            if not title:
                title = url
                
        domain = urllib.parse.urlparse(url if url.startswith("http") else f"https://{url}").netloc.replace("www.", "")
        success, _, _ = add_bookmark(url, title, domain, category, description)
        
        if success:
            added += 1
        else:
            duplicates += 1
            
    return {
        "total_found": len(urls_to_process),
        "added": added,
        "duplicates": duplicates,
        "errors": errors
    }

def check_single_link_health(bookmark: Dict[str, Any]) -> Tuple[int, int, bool]:
    """Helper to check link health status."""
    url = bookmark["url"]
    bm_id = bookmark["id"]
    try:
        res = requests.head(url, headers=DEFAULT_HEADERS, timeout=4, allow_redirects=True)
        status = res.status_code
        if status >= 400:
            # Re-check with GET if HEAD was rejected
            res_get = requests.get(url, headers=DEFAULT_HEADERS, timeout=4, stream=True)
            status = res_get.status_code
            
        is_broken = (status >= 400)
        update_link_status(bm_id, status, is_broken)
        return bm_id, status, is_broken
    except Exception:
        update_link_status(bm_id, 404, True)
        return bm_id, 404, True

def check_all_links_health(bookmarks: List[Dict[str, Any]]) -> Dict[str, int]:
    """Batch check health of all bookmarks concurrently using ThreadPoolExecutor."""
    broken_count = 0
    healthy_count = 0
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(check_single_link_health, bm) for bm in bookmarks]
        for future in concurrent.futures.as_completed(futures):
            try:
                _, status, is_broken = future.result()
                if is_broken:
                    broken_count += 1
                else:
                    healthy_count += 1
            except Exception:
                broken_count += 1
                
    return {"healthy": healthy_count, "broken": broken_count}
