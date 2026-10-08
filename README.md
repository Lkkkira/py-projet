# 🔖 LinkVault Pro — Smart Bookmark Organizer

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Web%20App-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**LinkVault Pro** is an intelligent web application designed to help users save, organize, search, and manage website bookmarks automatically. Built using **Python**, **Streamlit**, and **SQLite**, it automatically extracts website metadata (titles, descriptions, domain tags) and categorizes web links using a keyword intelligence engine.

---

## ✨ Features

- ⚡ **Instant URL Quick Save**: Paste any web address and click *Save Link*. Title, domain, description, and category are scraped and assigned automatically.
- 🎨 **Progressive Disclosure Architecture**: Includes a collapsed sidebar navigation drawer (`☰`) keeping the main workspace clean and clutter-free.
- ☀️ **Dual Theme Support**: Light Mode (default) and Dark Mode themes with an instant toggle switch.
- 🏷️ **Smart Categorization Engine**: Classifies bookmarks into 9 categories (*Education*, *Development*, *News*, *Shopping*, *Finance*, *Entertainment*, *Social*, *Tools & Productivity*, *Other*).
- 🛡️ **Smart Duplicate Resolution**: Intercepts duplicate URLs automatically and offers 1-click metadata refresh or highlight options.
- 🔍 **Live Search & Category Navigation**: Filter bookmarks by keyword search across titles, URLs, descriptions, or click multi-row category pills.
- 📥 **Bulk Import & Export**: Import links from `.csv` or `.txt` files or export your entire collection to CSV.
- ⚡ **Link Health Diagnostics**: Multi-threaded scanner checking HTTP status codes (200 OK vs 404/broken links).
- 🌱 **1-Click Viva Demo Seeder**: Includes 30 pre-configured sample links for rapid project demonstration.

---

## 🛠️ Technology Stack

| Layer | Technology |
| :--- | :--- |
| **Language** | Python 3.10+ |
| **Frontend Framework** | Streamlit |
| **Database** | SQLite3 (`linkvault.db`) |
| **Web Scraping** | Requests, BeautifulSoup4, urllib.parse |
| **Data Processing** | Pandas, CSV |

---

## 🚀 Quick Start & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/zalaharpal/LinkVault-Pro.git
cd LinkVault-Pro
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Application
```bash
python -m streamlit run app.py
```

The web application will open in your browser at `http://localhost:8501`.

---

## 📂 Project Structure

```text
LinkVault-Pro/
├── app.py                 # Streamlit UI & Progressive Disclosure Layout
├── database.py            # SQLite schema, CRUD operations & duplicate handling
├── analyzer.py            # Web scraping, metadata extraction & keyword categorizer
├── utils.py               # Bulk import/export, link health checker & sample dataset
├── sample_bookmarks.csv   # 30 curated sample bookmarks for testing
├── requirements.txt       # Python package dependencies
├── .gitignore             # Files ignored by Git
└── README.md              # Project documentation
```

---

## 🎓 Core Python Concepts Demonstrated

- **Functions & Conditional Branching**: Keyword rule evaluation, domain matching, and URL normalization.
- **Lists, Dictionaries & Tuples**: Structured bookmark metadata representation and category mapping.
- **Regular Expressions (`re`)**: Title sanitization and URL parsing.
- **File Handling & Input/Output**: Reading/writing CSV and TXT files.
- **Exception & Error Handling**: Graceful handling of HTTP timeouts, SSL errors, and SQLite constraints.
- **Database Management (`sqlite3`)**: Schema creation, indexing, parameterized queries, and Row factories.
- **Multi-Threading (`concurrent.futures`)**: Parallel HTTP status validation for broken link diagnostics.

---

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.
