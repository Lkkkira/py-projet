"""
database.py - SQLite Database Management for LinkVault Pro
"""

import sqlite3
import os
from urllib.parse import urlparse
from typing import List, Dict, Any, Optional, Tuple

DB_PATH = "linkvault.db"

def get_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    """Create and return a database connection with Row factory."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path: str = DB_PATH) -> None:
    """Initialize SQLite database schema."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bookmarks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL UNIQUE,
                normalized_url TEXT NOT NULL UNIQUE,
                title TEXT NOT NULL,
                domain TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                is_favorite INTEGER DEFAULT 0,
                status_code INTEGER DEFAULT 200,
                is_broken INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for quick searching and filtering
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_category ON bookmarks(category)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_favorite ON bookmarks(is_favorite)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_normalized_url ON bookmarks(normalized_url)")
        conn.commit()

def normalize_url(url: str) -> str:
    """
    Normalize URL for consistent duplicate checking.
    Strips trailing slashes, converts scheme and netloc to lowercase, removes default ports.
    """
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
        
    parsed = urlparse(url)
    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()
    
    # Strip standard default ports if any
    if netloc.endswith(":80") and scheme == "http":
        netloc = netloc[:-3]
    elif netloc.endswith(":443") and scheme == "https":
        netloc = netloc[:-4]
        
    path = parsed.path.rstrip('/')
    query = parsed.query
    
    normalized = f"{scheme}://{netloc}{path}"
    if query:
        normalized += f"?{query}"
        
    return normalized

def check_duplicate(url: str, db_path: str = DB_PATH) -> Optional[Dict[str, Any]]:
    """Check if normalized URL already exists in database."""
    norm_url = normalize_url(url)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM bookmarks WHERE normalized_url = ?", (norm_url,))
        row = cursor.fetchone()
        return dict(row) if row else None

def update_existing_bookmark(
    bookmark_id: int,
    title: str,
    category: str,
    description: str,
    db_path: str = DB_PATH
) -> bool:
    """Update metadata for an existing bookmark."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE bookmarks
            SET title = ?, category = ?, description = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (title.strip(), category.strip(), description.strip(), bookmark_id))
        conn.commit()
        return cursor.rowcount > 0

def remove_all_duplicate_records(db_path: str = DB_PATH) -> int:
    """Scan DB for duplicate normalized URLs and remove older redundant entries."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM bookmarks
            WHERE id NOT IN (
                SELECT MAX(id)
                FROM bookmarks
                GROUP BY normalized_url
            )
        """)
        deleted_count = cursor.rowcount
        conn.commit()
        return deleted_count

def add_bookmark(
    url: str,
    title: str,
    domain: str,
    category: str,
    description: str = "",
    is_favorite: bool = False,
    db_path: str = DB_PATH
) -> Tuple[bool, str, Optional[int]]:
    """
    Add a new bookmark to SQLite.
    Returns tuple: (success: bool, message: str, new_id: Optional[int])
    """
    norm_url = normalize_url(url)
    existing = check_duplicate(url, db_path)
    if existing:
        return False, f"Bookmark already exists: '{existing['title']}'", existing['id']
        
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO bookmarks (url, normalized_url, title, domain, category, description, is_favorite)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (url.strip(), norm_url, title.strip(), domain.strip(), category.strip(), description.strip(), 1 if is_favorite else 0))
            conn.commit()
            return True, "Bookmark saved successfully!", cursor.lastrowid
        except sqlite3.IntegrityError as e:
            return False, f"Database integrity error: {e}", None

def get_all_bookmarks(db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    """Fetch all bookmarks ordered by creation time descending."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM bookmarks ORDER BY id DESC")
        return [dict(row) for row in cursor.fetchall()]

def search_and_filter_bookmarks(
    query: str = "",
    category: str = "All",
    favorites_only: bool = False,
    broken_only: bool = False,
    db_path: str = DB_PATH
) -> List[Dict[str, Any]]:
    """Search bookmarks by keyword across fields and filter by category or state."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        
        sql = "SELECT * FROM bookmarks WHERE 1=1"
        params = []
        
        if category and category != "All":
            sql += " AND category = ?"
            params.append(category)
            
        if favorites_only:
            sql += " AND is_favorite = 1"
            
        if broken_only:
            sql += " AND is_broken = 1"
            
        if query:
            search_pattern = f"%{query.strip()}%"
            sql += " AND (title LIKE ? OR url LIKE ? OR description LIKE ? OR domain LIKE ? OR category LIKE ?)"
            params.extend([search_pattern] * 5)
            
        sql += " ORDER BY is_favorite DESC, id DESC"
        cursor.execute(sql, params)
        return [dict(row) for row in cursor.fetchall()]

def get_category_counts(db_path: str = DB_PATH) -> Dict[str, int]:
    """Get count of bookmarks grouped by category."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT category, COUNT(*) as count FROM bookmarks GROUP BY category")
        counts = {row["category"]: row["count"] for row in cursor.fetchall()}
        cursor.execute("SELECT COUNT(*) as total FROM bookmarks")
        counts["All"] = cursor.fetchone()["total"]
        return counts

def get_dashboard_stats(db_path: str = DB_PATH) -> Dict[str, int]:
    """Get high level summary stats for the top bar."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM bookmarks")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT category) FROM bookmarks")
        categories = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM bookmarks WHERE is_favorite = 1")
        favorites = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM bookmarks WHERE is_broken = 1")
        broken = cursor.fetchone()[0]
        
        return {
            "total_bookmarks": total,
            "total_categories": categories,
            "total_favorites": favorites,
            "total_broken": broken
        }

def toggle_favorite(bookmark_id: int, db_path: str = DB_PATH) -> bool:
    """Toggle the favorite state of a bookmark."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE bookmarks SET is_favorite = NOT is_favorite, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (bookmark_id,))
        conn.commit()
        return cursor.rowcount > 0

def update_bookmark(
    bookmark_id: int,
    title: str,
    category: str,
    description: str,
    url: str,
    db_path: str = DB_PATH
) -> Tuple[bool, str]:
    """Update bookmark fields."""
    norm_url = normalize_url(url)
    domain = urlparse(norm_url).netloc.replace("www.", "")
    
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        # Check if new URL conflicts with another record
        cursor.execute("SELECT id FROM bookmarks WHERE normalized_url = ? AND id != ?", (norm_url, bookmark_id))
        if cursor.fetchone():
            return False, "Another bookmark with this URL already exists."
            
        cursor.execute("""
            UPDATE bookmarks 
            SET title = ?, category = ?, description = ?, url = ?, normalized_url = ?, domain = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (title.strip(), category.strip(), description.strip(), url.strip(), norm_url, domain, bookmark_id))
        conn.commit()
        return True, "Bookmark updated successfully!"

def update_link_status(bookmark_id: int, status_code: int, is_broken: bool, db_path: str = DB_PATH) -> None:
    """Update link accessibility status."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE bookmarks SET status_code = ?, is_broken = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?
        """, (status_code, 1 if is_broken else 0, bookmark_id))
        conn.commit()

def delete_bookmark(bookmark_id: int, db_path: str = DB_PATH) -> bool:
    """Delete bookmark by ID."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM bookmarks WHERE id = ?", (bookmark_id,))
        conn.commit()
        return cursor.rowcount > 0

def clear_all_bookmarks(db_path: str = DB_PATH) -> None:
    """Clear all records from bookmarks table."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM bookmarks")
        conn.commit()
