"""
Configuration for SEO + AEO Analyzer
All scoring weights and thresholds are defined here for easy adjustment
"""
import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = "llama-3.3-70b-versatile"  # Updated model (Feb 2026)

# Scraping Configuration
REQUEST_TIMEOUT = 10  # seconds
MAX_CONTENT_LENGTH = 5_000_000  # 5MB
USER_AGENT = "SEO-AEO-Analyzer/1.0 (Educational Tool)"

# SEO Scoring Weights (must sum to 100)
SEO_WEIGHTS = {
    "title": 10,
    "meta_description": 6,
    "h1_count": 5,
    "heading_hierarchy": 5,
    "content_length": 10,
    "internal_links": 5,
    "external_links": 5,
    "readability": 8,
    "html_size": 3,
    "keyword_density": 3,
    "images": 6,
    "open_graph": 4,
    "schema_markup": 6,
    "https_security": 10,  # NEW: Critical for modern SEO
    "mobile_friendly": 10,  # NEW: Mobile-first indexing
    "canonical_tag": 4,     # NEW: Duplicate content prevention
}

# SEO Thresholds
SEO_THRESHOLDS = {
    "title_min_length": 30,
    "title_max_length": 60,
    "meta_min_length": 120,
    "meta_max_length": 160,
    "content_min_words": 300,
    "content_ideal_words": 800,
    "h1_ideal_count": 1,
    "internal_links_min": 3,
    "external_links_min": 1,
    "html_max_size_kb": 100,
}

# AEO Scoring Weights (must sum to 100)
AEO_WEIGHTS = {
    "question_headings": 20,
    "direct_answers": 25,
    "answer_length": 15,
    "definition_clarity": 15,
    "structured_content": 15,
    "fluff_detection": 10,
}

# AEO Thresholds
AEO_THRESHOLDS = {
    "answer_min_words": 40,
    "answer_max_words": 80,
    "answer_ideal_words": 60,
    "question_keywords": ["what", "how", "why", "when", "where", "who", "benefits", "vs", "comparison"],
    "fluff_phrases": [
        "in today's world",
        "it goes without saying",
        "needless to say",
        "at the end of the day",
        "dive deep",
        "let's explore",
    ],
}

# Crawlability Scoring Weights (separate from SEO, displayed independently)
CRAWLABILITY_WEIGHTS = {
    "robots_txt": 50,
    "sitemap": 50,
}

# Analysis Configuration
MAX_PAGES_TO_CRAWL = 2  # Homepage + 1 content page for MVP
ANALYSIS_TIMEOUT = 15  # seconds
