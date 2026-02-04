# SEO + AEO Website Analyzer (MVP)

A web application that analyzes websites for both traditional SEO and modern AEO (Answer Engine Optimization).

## Features

- **SEO Analysis**: Rule-based checks for title, meta, headings, content structure, and linking
- **AEO Analysis**: Evaluates answer-readiness for AI search engines
- **AI-Powered Recommendations**: Uses Groq API for content rewriting examples
- **Transparent Scoring**: Every score is explainable and reproducible
- **Fast Analysis**: Results in under 20 seconds

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your Groq API key:
   ```
   GROQ_API_KEY=your_key_here
   ```

4. Run the application:
   ```bash
   uvicorn main:app --reload
   ```

5. Open your browser to `http://localhost:8000`

## Architecture

- **Backend**: FastAPI (Python)
- **Scraping**: requests + BeautifulSoup
- **AI**: Groq API (for explanations and rewrites only)
- **Frontend**: HTML/CSS/JavaScript

## Philosophy

- **Rules over hype**: Scoring is deterministic, not AI-generated
- **Clarity over cleverness**: Every recommendation has a clear reason
- **AI as helper**: AI rewrites and explains, but doesn't decide scores

## Project Structure

```
seoaeo/
├── main.py                 # FastAPI application entry point
├── config.py              # Configuration and settings
├── scraper/
│   └── crawler.py         # Web scraping logic
├── analyzers/
│   ├── seo_analyzer.py    # SEO analysis engine
│   ├── aeo_analyzer.py    # AEO analysis engine
│   └── scoring.py         # Scoring system
├── ai/
│   └── groq_client.py     # Groq API integration
├── static/
│   ├── css/
│   ├── js/
│   └── index.html         # Frontend UI
└── requirements.txt
```
