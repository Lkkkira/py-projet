"""
LinkVault Pro — Smart Bookmark Organizer
SaaS UX with Light Mode Default, Sidebar Custom Options & Smart Duplicate Resolution
"""

import streamlit as st
import pandas as pd
import time
from urllib.parse import urlparse

from database import (
    init_db,
    add_bookmark,
    get_all_bookmarks,
    search_and_filter_bookmarks,
    get_category_counts,
    get_dashboard_stats,
    toggle_favorite,
    update_bookmark,
    update_existing_bookmark,
    remove_all_duplicate_records,
    delete_bookmark,
    check_duplicate,
    clear_all_bookmarks
)
from analyzer import fetch_website_info, CATEGORIES_LIST, categorize_url
from utils import (
    seed_sample_bookmarks,
    export_bookmarks_to_csv,
    process_bulk_file,
    check_all_links_health
)

# Page Configuration - Collapsed Sidebar by Default (Opened via Hamburger ☰ button)
st.set_page_config(
    page_title="LinkVault Pro — Bookmark Organizer",
    page_icon="🔖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize Database Schema
init_db()

# Session State Initialization (Light Mode Default)
if "theme" not in st.session_state:
    st.session_state.theme = "Light"
if "current_nav" not in st.session_state:
    st.session_state.current_nav = "Vault"
if "edit_id" not in st.session_state:
    st.session_state.edit_id = None
if "selected_category" not in st.session_state:
    st.session_state.selected_category = "All"
if "search_query" not in st.session_state:
    st.session_state.search_query = ""
if "duplicate_found" not in st.session_state:
    st.session_state.duplicate_found = None
if "duplicate_new_info" not in st.session_state:
    st.session_state.duplicate_new_info = None

is_dark = (st.session_state.theme == "Dark")

# ---------------------------------------------------------
# Dynamic CSS Theme Engine (Light Mode Default & Dark Support)
# ---------------------------------------------------------
if is_dark:
    theme_css = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        .stApp {
            background-color: #0E0F12;
            color: #F5F5F3;
        }

        /* Sidebar Navigation Drawer */
        [data-testid="stSidebar"] {
            background-color: #13151A;
            border-right: 1px solid #22252E;
        }

        .top-navbar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: #16181F;
            border: 1px solid #262A35;
            padding: 1rem 1.6rem;
            border-radius: 12px;
            margin-bottom: 1.5rem;
        }

        .brand-logo {
            font-size: 1.4rem;
            font-weight: 800;
            color: #F5F5F3;
            display: flex;
            align-items: center;
            gap: 10px;
            letter-spacing: -0.02em;
        }

        .brand-logo span {
            color: #C5A059;
            font-size: 0.8rem;
            background: rgba(197, 160, 89, 0.15);
            padding: 2px 8px;
            border-radius: 4px;
            border: 1px solid rgba(197, 160, 89, 0.3);
            font-weight: 700;
        }

        .hero-card {
            background: #16181F;
            border: 1px solid #262A35;
            border-radius: 14px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
        }

        .hero-title {
            font-size: 1.15rem;
            font-weight: 700;
            color: #F5F5F3;
            margin-bottom: 4px;
        }

        .hero-subtitle {
            font-size: 0.88rem;
            color: #9E9EA0;
            margin-bottom: 1rem;
        }

        .bm-card {
            background: #16181F;
            border: 1px solid #262A35;
            border-radius: 12px;
            padding: 1.2rem;
            margin-bottom: 0.9rem;
            transition: all 0.2s ease;
        }

        .bm-card:hover {
            border-color: #C5A059;
            box-shadow: 0 4px 18px rgba(197, 160, 89, 0.08);
        }

        .bm-title {
            font-size: 1.08rem;
            font-weight: 700;
            color: #F5F5F3;
            text-decoration: none;
        }

        .bm-title:hover {
            color: #C5A059;
        }

        .domain-tag {
            font-size: 0.76rem;
            color: #9E9EA0;
            background: #101217;
            padding: 2px 8px;
            border-radius: 4px;
            border: 1px solid #22252E;
        }

        .bm-desc {
            color: #9E9EA0;
            font-size: 0.88rem;
            line-height: 1.45;
            margin: 8px 0 12px 0;
        }

        .cat-tag {
            font-size: 0.75rem;
            font-weight: 600;
            background: #1E222B;
            color: #D4AF37;
            padding: 2px 8px;
            border-radius: 4px;
            border: 1px solid rgba(197, 160, 89, 0.25);
        }

        div[data-baseweb="input"] > div {
            background-color: #121419 !important;
            border-color: #282C37 !important;
            color: #F5F5F3 !important;
            border-radius: 8px !important;
        }

        .stButton > button {
            white-space: normal !important;
            word-break: break-word !important;
            padding: 0.45rem 0.5rem !important;
            font-size: 0.84rem !important;
            min-height: 42px !important;
        }

        button[kind="primary"] {
            background-color: #C5A059 !important;
            color: #0E0F12 !important;
            border: none !important;
            font-weight: 700 !important;
            border-radius: 8px !important;
        }

        button[kind="secondary"] {
            background-color: #16181F !important;
            color: #F5F5F3 !important;
            border: 1px solid #2A2E39 !important;
            border-radius: 8px !important;
        }
    </style>
    """
else:
    theme_css = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        .stApp {
            background-color: #F8FAFC;
            color: #0F172A;
        }

        [data-testid="stSidebar"] {
            background-color: #FFFFFF;
            border-right: 1px solid #E2E8F0;
        }

        .top-navbar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            padding: 1rem 1.6rem;
            border-radius: 12px;
            margin-bottom: 1.5rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.03);
        }

        .brand-logo {
            font-size: 1.4rem;
            font-weight: 800;
            color: #0F172A;
            display: flex;
            align-items: center;
            gap: 10px;
            letter-spacing: -0.02em;
        }

        .brand-logo span {
            color: #B8860B;
            font-size: 0.8rem;
            background: #FEF3C7;
            padding: 2px 8px;
            border-radius: 4px;
            border: 1px solid #FCD34D;
            font-weight: 700;
        }

        .hero-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 14px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.03);
        }

        .hero-title {
            font-size: 1.15rem;
            font-weight: 700;
            color: #0F172A;
            margin-bottom: 4px;
        }

        .hero-subtitle {
            font-size: 0.88rem;
            color: #64748B;
            margin-bottom: 1rem;
        }

        .bm-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            padding: 1.2rem;
            margin-bottom: 0.9rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.03);
        }

        .bm-card:hover {
            border-color: #B8860B;
            box-shadow: 0 4px 18px rgba(184, 134, 11, 0.1);
        }

        .bm-title {
            font-size: 1.08rem;
            font-weight: 700;
            color: #0F172A;
            text-decoration: none;
        }

        .bm-title:hover {
            color: #B8860B;
        }

        .domain-tag {
            font-size: 0.76rem;
            color: #475569;
            background: #F1F5F9;
            padding: 2px 8px;
            border-radius: 4px;
            border: 1px solid #CBD5E1;
        }

        .bm-desc {
            color: #475569;
            font-size: 0.88rem;
            line-height: 1.45;
            margin: 8px 0 12px 0;
        }

        .cat-tag {
            font-size: 0.75rem;
            font-weight: 600;
            background: #FEF3C7;
            color: #92400E;
            padding: 2px 8px;
            border-radius: 4px;
            border: 1px solid #FCD34D;
        }

        div[data-baseweb="input"] > div {
            background-color: #FFFFFF !important;
            border-color: #CBD5E1 !important;
            color: #0F172A !important;
            border-radius: 8px !important;
        }

        .stButton > button {
            white-space: normal !important;
            word-break: break-word !important;
            padding: 0.45rem 0.5rem !important;
            font-size: 0.84rem !important;
            min-height: 42px !important;
        }

        button[kind="primary"] {
            background-color: #B8860B !important;
            color: #FFFFFF !important;
            border: none !important;
            font-weight: 700 !important;
            border-radius: 8px !important;
        }

        button[kind="secondary"] {
            background-color: #FFFFFF !important;
            color: #0F172A !important;
            border: 1px solid #CBD5E1 !important;
            border-radius: 8px !important;
        }
    </style>
    """

st.markdown(theme_css, unsafe_allow_html=True)

# ---------------------------------------------------------
# Sidebar Navigation Drawer (Opens only via ☰ button)
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div style="padding: 0.5rem 0 1rem 0; border-bottom: 1px solid rgba(150,150,150,0.15); margin-bottom: 1.2rem;">
        <h2 style="font-size: 1.3rem; font-weight: 800; margin: 0; display: flex; align-items: center; gap: 8px;">
            🔖 LinkVault <span style="font-size:0.75rem; color:#B8860B; border:1px solid #B8860B; padding:2px 6px; border-radius:4px;">PRO</span>
        </h2>
    </div>
    """, unsafe_allow_html=True)

    # 1. MAIN NAVIGATION
    st.caption("MAIN NAVIGATION")
    nav_vault = st.button("🏠 Vault Collection", use_container_width=True, type="primary" if st.session_state.current_nav == "Vault" else "secondary")
    if nav_vault:
        st.session_state.current_nav = "Vault"
        st.rerun()

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # 2. WORKSPACE TOOLS
    st.caption("TOOLS & UTILITIES")
    nav_import = st.button("📥 Import & Export", use_container_width=True, type="primary" if st.session_state.current_nav == "ImportExport" else "secondary")
    if nav_import:
        st.session_state.current_nav = "ImportExport"
        st.rerun()

    nav_health = st.button("⚡ Health Diagnostic", use_container_width=True, type="primary" if st.session_state.current_nav == "HealthCheck" else "secondary")
    if nav_health:
        st.session_state.current_nav = "HealthCheck"
        st.rerun()

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # 3. MANUAL / CUSTOM ADD (Relocated from main page for progressive disclosure)
    with st.expander("🛠️ Custom / Manual Bookmark Add"):
        with st.form("sidebar_custom_form", clear_on_submit=True):
            s_url = st.text_input("Website URL", placeholder="https://example.com")
            s_title = st.text_input("Custom Title (Optional)")
            s_cat = st.selectbox("Category", ["Auto-Detect"] + CATEGORIES_LIST)
            s_desc = st.text_area("Custom Description", height=70)
            s_fav = st.checkbox("Mark as Favorite ⭐")
            
            s_submit = st.form_submit_button("Save Custom Link", type="primary", use_container_width=True)
            if s_submit:
                if not s_url.strip():
                    st.error("URL is required.")
                else:
                    with st.spinner("Saving custom link..."):
                        if not s_title or s_cat == "Auto-Detect":
                            scraped = fetch_website_info(s_url)
                            f_title = s_title.strip() or scraped["title"]
                            f_cat = s_cat if s_cat != "Auto-Detect" else scraped["category"]
                            f_desc = s_desc.strip() or scraped["description"]
                            dom = scraped["domain"]
                        else:
                            f_title = s_title.strip()
                            f_cat = s_cat
                            f_desc = s_desc.strip()
                            dom = urlparse(s_url if s_url.startswith("http") else f"https://{s_url}").netloc.replace("www.", "")
                            
                        ok, msg, _ = add_bookmark(s_url, f_title, dom, f_cat, f_desc, is_favorite=s_fav)
                        if ok:
                            st.success(msg)
                            time.sleep(0.5)
                            st.session_state.current_nav = "Vault"
                            st.rerun()
                        else:
                            st.warning(msg)

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # 4. DEMO & SYSTEM
    st.caption("PRESENTATION & PREFERENCES")
    nav_demo = st.button("🌱 Demo Dataset (30 Links)", use_container_width=True, type="primary" if st.session_state.current_nav == "Demo" else "secondary")
    if nav_demo:
        st.session_state.current_nav = "Demo"
        st.rerun()

    # Duplicate Audit Button
    if st.button("🧹 Clean Duplicate Links Audit", use_container_width=True):
        removed = remove_all_duplicate_records()
        if removed > 0:
            st.success(f"Removed {removed} duplicate link entries!")
        else:
            st.info("No duplicate entries found in database.")
        st.rerun()

    # Theme Switcher (Light Default)
    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    theme_choice = st.radio(
        "Theme Preference",
        ["☀️ Light Theme", "🌙 Dark Theme"],
        index=0 if not is_dark else 1,
        label_visibility="collapsed"
    )
    new_theme = "Light" if "Light" in theme_choice else "Dark"
    if new_theme != st.session_state.theme:
        st.session_state.theme = new_theme
        st.rerun()

# ---------------------------------------------------------
# Top Bar Header (Navbar)
# ---------------------------------------------------------
stats = get_dashboard_stats()

st.markdown(f"""
<div class="top-navbar">
    <div class="brand-logo">
        🔖 LinkVault <span>PRO</span>
    </div>
    <div style="font-size: 0.85rem; color: {'#9E9EA0' if is_dark else '#475569'};">
        Saved: <strong style="color:{'#C5A059' if is_dark else '#B8860B'};">{stats['total_bookmarks']}</strong> | Categories: <strong style="color:{'#C5A059' if is_dark else '#B8860B'};">{stats['total_categories']}</strong> | Favorites: <strong style="color:{'#C5A059' if is_dark else '#B8860B'};">{stats['total_favorites']}</strong>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# VIEW 1: MAIN VAULT COLLECTION (Laser Focused Workspace)
# ---------------------------------------------------------
if st.session_state.current_nav == "Vault":

    # Hero Quick Input Card
    st.markdown("""
    <div class="hero-card">
        <div class="hero-title">✨ Save New Website</div>
        <div class="hero-subtitle">Paste any website link below to automatically extract title, domain, description, and category.</div>
    </div>
    """, unsafe_allow_html=True)

    url_col, btn_col = st.columns([4, 1])
    with url_col:
        input_url = st.text_input("URL Input", placeholder="https://docs.python.org/3/", label_visibility="collapsed", key="vault_url_input")
    with btn_col:
        save_click = st.button("⚡ Save Link", use_container_width=True, type="primary")

    # ---------------------------------------------------------
    # SMART DUPLICATE LINK PROGRAMmatic HANDLING
    # ---------------------------------------------------------
    if save_click:
        if not input_url.strip():
            st.error("Please enter a valid website address.")
        else:
            existing = check_duplicate(input_url)
            if existing:
                st.session_state.duplicate_found = existing
                st.session_state.duplicate_url = input_url
            else:
                st.session_state.duplicate_found = None
                with st.spinner("Analyzing web page..."):
                    info = fetch_website_info(input_url)
                    
                success, msg, _ = add_bookmark(
                    url=info["url"],
                    title=info["title"],
                    domain=info["domain"],
                    category=info["category"],
                    description=info["description"]
                )
                if success:
                    st.toast(f"Saved under '{info['category']}'!", icon="✅")
                    st.success(f"Saved **{info['title']}** under **{info['category']}**.")
                    time.sleep(0.4)
                    st.rerun()

    # Smart Duplicate Link Resolution Program Dialog
    if st.session_state.duplicate_found:
        dup = st.session_state.duplicate_found
        st.markdown(f"""
        <div style="background: {'rgba(234, 179, 8, 0.12)' if is_dark else '#FEF3C7'}; border: 1px solid {'#EAB308' if is_dark else '#FCD34D'}; border-radius: 10px; padding: 1.2rem; margin-bottom: 1.2rem;">
            <h4 style="margin: 0 0 6px 0; color: {'#FACC15' if is_dark else '#92400E'};">⚠️ Duplicate Bookmark Detected</h4>
            <p style="margin: 0 0 10px 0; font-size: 0.9rem; color: {'#E2E8F0' if is_dark else '#78350F'};">
                This URL is already saved as <strong>"{dup['title']}"</strong> in the <strong>{dup['category']}</strong> category.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        dup_c1, dup_c2, dup_c3 = st.columns([1.5, 1.5, 1])
        with dup_c1:
            if st.button("🔄 Refresh Metadata & Update", key="dup_update", type="primary", use_container_width=True):
                with st.spinner("Re-scraping website info..."):
                    fresh = fetch_website_info(st.session_state.duplicate_url)
                    update_existing_bookmark(dup['id'], fresh['title'], fresh['category'], fresh['description'])
                st.success("Updated bookmark metadata successfully!")
                st.session_state.duplicate_found = None
                time.sleep(0.5)
                st.rerun()
        with dup_c2:
            if st.button("🔍 Highlight Existing Bookmark", key="dup_search", use_container_width=True):
                st.session_state.search_query = dup['domain']
                st.session_state.duplicate_found = None
                st.rerun()
        with dup_c3:
            if st.button("Dismiss", key="dup_dismiss", use_container_width=True):
                st.session_state.duplicate_found = None
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Search & Filters
    sc1, sc2, sc3 = st.columns([3, 1, 1])
    with sc1:
        search_input_val = st.text_input(
            "Search",
            value=st.session_state.search_query,
            placeholder="Search by title, domain, URL, or category...",
            label_visibility="collapsed"
        )
        st.session_state.search_query = search_input_val
    with sc2:
        show_favs = st.checkbox("⭐ Favorites Only")
    with sc3:
        show_broken = st.checkbox("⚠️ Broken Only")

    # Category Pill Buttons — Multi-Row Layout (5 per row)
    cat_counts = get_category_counts()
    category_options = ["All"] + CATEGORIES_LIST

    row1_cats = category_options[:5]
    row2_cats = category_options[5:]

    row1_cols = st.columns(5)
    for idx, cat_name in enumerate(row1_cats):
        count = cat_counts.get(cat_name, 0)
        btn_label = f"{cat_name} ({count})"
        is_active = (st.session_state.selected_category == cat_name)
        with row1_cols[idx]:
            if st.button(
                btn_label,
                key=f"vault_cat_{cat_name}",
                use_container_width=True,
                type="primary" if is_active else "secondary"
            ):
                st.session_state.selected_category = cat_name
                st.rerun()

    st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)

    row2_cols = st.columns(5)
    for idx, cat_name in enumerate(row2_cats):
        count = cat_counts.get(cat_name, 0)
        btn_label = f"{cat_name} ({count})"
        is_active = (st.session_state.selected_category == cat_name)
        with row2_cols[idx]:
            if st.button(
                btn_label,
                key=f"vault_cat_{cat_name}",
                use_container_width=True,
                type="primary" if is_active else "secondary"
            ):
                st.session_state.selected_category = cat_name
                st.rerun()

    st.markdown("<hr style='margin-top: 0.8rem; margin-bottom: 1.2rem; opacity: 0.3;'>", unsafe_allow_html=True)

    # Bookmarks Grid Display
    active_cat = st.session_state.selected_category
    bookmarks = search_and_filter_bookmarks(
        query=st.session_state.search_query,
        category=active_cat,
        favorites_only=show_favs,
        broken_only=show_broken
    )

    if not bookmarks:
        st.markdown("""
        <div style="text-align: center; padding: 3rem 1.5rem; border-radius: 12px; border: 1px dashed rgba(150,150,150,0.3);">
            <h4 style="font-size: 1.1rem; margin-bottom: 6px;">No bookmarks match your criteria</h4>
            <p style="color: #9E9EA0; font-size: 0.9rem; margin-bottom: 1.2rem;">Try adjusting your search query, or click below to seed 30 sample bookmarks for demonstration.</p>
        </div>
        """, unsafe_allow_html=True)
        
        ec1, ec2, ec3 = st.columns([1, 2, 1])
        with ec2:
            if st.button("🌱 Load 30 Sample Bookmarks", use_container_width=True, type="primary"):
                added, skipped = seed_sample_bookmarks()
                st.success(f"Added {added} sample bookmarks!")
                st.rerun()
    else:
        st.caption(f"Displaying **{len(bookmarks)}** bookmark(s)")
        
        for bm in bookmarks:
            fav_star = "⭐" if bm['is_favorite'] else "☆"
            status_text = "🟢 200 OK" if not bm.get('is_broken') else f"⚠️ Unreachable ({bm['status_code']})"
            
            with st.container():
                c_main, c_actions = st.columns([5, 1.2])
                with c_main:
                    st.markdown(f"""
                    <div class="bm-card">
                        <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:4px;">
                            <a href="{bm['url']}" target="_blank" class="bm-title">{bm['title']}</a>
                            <span class="domain-tag">🌐 {bm['domain']}</span>
                        </div>
                        <div class="bm-desc">{bm['description'] if bm['description'] else 'No description available.'}</div>
                        <div style="display:flex; gap:10px; align-items:center;">
                            <span class="cat-tag">{bm['category']}</span>
                            <span style="font-size:0.75rem; color:#9E9EA0;">{status_text}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                with c_actions:
                    st.markdown("<div style='padding-top:6px;'></div>", unsafe_allow_html=True)
                    a1, a2, a3 = st.columns(3)
                    with a1:
                        if st.button(fav_star, key=f"fav_{bm['id']}", help="Toggle Favorite", use_container_width=True):
                            toggle_favorite(bm['id'])
                            st.rerun()
                    with a2:
                        if st.button("✏️", key=f"edit_btn_{bm['id']}", help="Edit Bookmark", use_container_width=True):
                            st.session_state.edit_id = bm['id'] if st.session_state.edit_id != bm['id'] else None
                            st.rerun()
                    with a3:
                        if st.button("🗑️", key=f"del_{bm['id']}", help="Delete Bookmark", use_container_width=True):
                            delete_bookmark(bm['id'])
                            st.toast("Bookmark removed!", icon="🗑️")
                            st.rerun()
                            
            # Inline Edit Form
            if st.session_state.edit_id == bm['id']:
                with st.form(key=f"edit_form_{bm['id']}"):
                    st.markdown(f"<h4>Edit: {bm['title']}</h4>", unsafe_allow_html=True)
                    e_title = st.text_input("Title", value=bm['title'])
                    e_url = st.text_input("URL", value=bm['url'])
                    
                    cat_idx = CATEGORIES_LIST.index(bm['category']) if bm['category'] in CATEGORIES_LIST else 0
                    e_cat = st.selectbox("Category", CATEGORIES_LIST, index=cat_idx)
                    e_desc = st.text_area("Description", value=bm['description'], height=70)
                    
                    es1, es2 = st.columns(2)
                    with es1:
                        if st.form_submit_button("Save Changes", type="primary", use_container_width=True):
                            ok, msg = update_bookmark(bm['id'], e_title, e_cat, e_desc, e_url)
                            if ok:
                                st.session_state.edit_id = None
                                st.success("Updated successfully!")
                                st.rerun()
                            else:
                                st.error(msg)
                    with es2:
                        if st.form_submit_button("Cancel", use_container_width=True):
                            st.session_state.edit_id = None
                            st.rerun()

# ---------------------------------------------------------
# VIEW 2: BULK IMPORT & EXPORT WORKSPACE
# ---------------------------------------------------------
elif st.session_state.current_nav == "ImportExport":
    st.markdown("<h3>📥 Bulk Import & Export Workspace</h3>", unsafe_allow_html=True)
    st.caption("Manage large bookmark collections using CSV or TXT files.")
    
    col_imp, col_exp = st.columns(2)
    
    with col_imp:
        st.subheader("Import Bookmarks")
        up_file = st.file_uploader("Upload CSV or TXT file", type=["csv", "txt"])
        auto_fetch = st.checkbox("Auto-extract web titles & categories", value=True)
        
        if up_file is not None:
            if st.button("Start Bulk Import", type="primary", use_container_width=True):
                content = up_file.getvalue().decode("utf-8")
                with st.spinner("Processing file..."):
                    res = process_bulk_file(content, up_file.name, auto_scrape=auto_fetch)
                st.success(f"Added {res['added']} bookmarks ({res['duplicates']} duplicates skipped).")
                time.sleep(1)
                st.session_state.current_nav = "Vault"
                st.rerun()
                
    with col_exp:
        st.subheader("Export Bookmarks")
        st.write("Download all currently saved bookmarks in structured CSV format.")
        csv_data = export_bookmarks_to_csv()
        st.download_button(
            label="📤 Download CSV Export File",
            data=csv_data,
            file_name="linkvault_bookmarks.csv",
            mime="text/csv",
            type="primary",
            use_container_width=True
        )

# ---------------------------------------------------------
# VIEW 3: LINK HEALTH DIAGNOSTICS WORKSPACE
# ---------------------------------------------------------
elif st.session_state.current_nav == "HealthCheck":
    st.markdown("<h3>⚡ Link Health Diagnostics</h3>", unsafe_allow_html=True)
    st.caption("Verify accessibility and detect broken or unreachable websites in your database.")
    
    all_bms = get_all_bookmarks()
    st.info(f"Database currently contains **{len(all_bms)}** saved bookmark(s).")
    
    if st.button("Run Diagnostic Health Scan", type="primary", use_container_width=True):
        if not all_bms:
            st.warning("No bookmarks saved to test.")
        else:
            with st.spinner("Testing HTTP connections..."):
                res = check_all_links_health(all_bms)
            st.success(f"Scan Complete! Healthy: {res['healthy']} | Unreachable / Broken: {res['broken']}")
            st.rerun()
            
    # Display Broken Links if any
    broken_list = [bm for bm in all_bms if bm.get('is_broken')]
    if broken_list:
        st.markdown("<h4>⚠️ Detected Broken Links</h4>", unsafe_allow_html=True)
        for bkm in broken_list:
            st.write(f"- **{bkm['title']}** (`{bkm['url']}`) — Status: HTTP {bkm['status_code']}")

# ---------------------------------------------------------
# VIEW 4: DEMO DATASET & VIVA PRESENTATION
# ---------------------------------------------------------
elif st.session_state.current_nav == "Demo":
    st.markdown("<h3>🌱 Viva Demo & Presentation Setup</h3>", unsafe_allow_html=True)
    st.caption("Pre-load 30 educational, technology, and news sample bookmarks for presentation.")
    
    dc1, dc2 = st.columns(2)
    with dc1:
        st.subheader("Load 30 Sample Links")
        if st.button("Load Sample Dataset Now", type="primary", use_container_width=True):
            with st.spinner("Seeding sample bookmarks..."):
                added, skipped = seed_sample_bookmarks()
            st.success(f"Loaded {added} bookmarks ({skipped} already existed)!")
            time.sleep(1)
            st.session_state.current_nav = "Vault"
            st.rerun()
            
    with dc2:
        st.subheader("Clear Database")
        st.write("Reset database back to empty state.")
        if st.button("Clear All Bookmarks", use_container_width=True):
            clear_all_bookmarks()
            st.toast("Database reset to 0 items.", icon="🗑️")
            st.rerun()

# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------
st.markdown("<br><hr style='opacity:0.2;'>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; color: #71717A; font-size: 0.8rem;">
    LinkVault Pro — Progressive Disclosure SaaS Architecture | Python, Streamlit & SQLite
</div>
""", unsafe_allow_html=True)
