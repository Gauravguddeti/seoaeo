# Setup and Usage Guide

## Quick Start

### 1. Install Dependencies

Open PowerShell in the project directory and run:

```powershell
pip install -r requirements.txt
```

### 2. Configure Groq API Key

Get your free API key from [Groq Console](https://console.groq.com/keys)

Create a `.env` file in the project root:

```powershell
Copy-Item .env.example .env
```

Edit `.env` and add your API key:

```
GROQ_API_KEY=your_actual_api_key_here
```

**Note**: The app works without an API key, but AI features (content rewrites and enhanced explanations) will be disabled.

### 3. Run the Application

```powershell
python main.py
```

Or using uvicorn directly:

```powershell
uvicorn main:app --reload
```

### 4. Access the Application

Open your browser to: **http://localhost:8000**

---

## Project Structure

```
seoaeo/
├── main.py                 # FastAPI app and endpoints
├── config.py              # Configuration and scoring weights
├── utils.py               # Error handling and validation
├── requirements.txt       # Python dependencies
├── .env                   # API keys (not in git)
├── README.md             # Project documentation
│
├── scraper/
│   ├── __init__.py
│   └── crawler.py         # Web scraping and content extraction
│
├── analyzers/
│   ├── __init__.py
│   ├── seo_analyzer.py    # Rule-based SEO checks
│   ├── aeo_analyzer.py    # AEO analysis engine
│   └── scoring.py         # Scoring system
│
├── ai/
│   ├── __init__.py
│   └── groq_client.py     # AI integration (content rewrites)
│
└── static/
    ├── index.html         # Frontend UI
    ├── css/
    │   └── style.css      # Styling
    └── js/
        └── app.js         # Frontend logic
```

---

## How It Works

### 1. URL Submission
- User enters a website URL
- Frontend validates the URL format
- POST request sent to `/api/analyze`

### 2. Crawling Phase
- Fetches homepage HTML
- Attempts to find one content-rich page
- Extracts: title, meta, headings, paragraphs, lists, tables, FAQs, links

### 3. SEO Analysis (Rule-Based)
- Checks 10 SEO factors using deterministic rules
- Each check returns: pass/warning/fail + explanation + recommendation
- No AI involved in scoring decisions

### 4. AEO Analysis (Rule-Based)
- Evaluates 6 AEO factors for answer-readiness
- Looks for question headings, direct answers, optimal length, structure
- Detects fluff and weak definitions

### 5. Scoring
- Weighted scoring system (configurable in config.py)
- SEO score: 0-100 with letter grade
- AEO score: 0-100 with letter grade
- Fully transparent breakdown

### 6. AI Enhancement (Optional)
- Groq API generates content rewrite examples
- AI explains recommendations in natural language
- **If AI fails**: analysis completes without AI features

### 7. Report Generation
- Displays both scores with explanations
- Shows top issues preventing AI extraction
- Provides before/after content example
- Lists all checks with recommendations
- Gives prioritized action checklist

---

## Configuration

### Adjusting Scoring Weights

Edit `config.py` to change how scores are calculated:

```python
# SEO Scoring Weights (must sum to 100)
SEO_WEIGHTS = {
    "title": 15,
    "meta_description": 10,
    "h1_count": 10,
    # ... adjust as needed
}

# AEO Scoring Weights (must sum to 100)
AEO_WEIGHTS = {
    "question_headings": 20,
    "direct_answers": 25,
    # ... adjust as needed
}
```

### Adjusting Thresholds

```python
SEO_THRESHOLDS = {
    "title_min_length": 30,
    "title_max_length": 60,
    "content_min_words": 300,
    # ... adjust as needed
}
```

---

## API Endpoints

### POST /api/analyze
Start analysis of a URL

**Request:**
```json
{
  "url": "https://example.com"
}
```

**Response:**
```json
{
  "analysis_id": "uuid",
  "message": "Analysis started",
  "status_url": "/api/status/{uuid}"
}
```

### GET /api/status/{analysis_id}
Check analysis status

**Response (Processing):**
```json
{
  "status": "processing",
  "progress": "Running SEO analysis..."
}
```

**Response (Complete):**
```json
{
  "status": "completed",
  "progress": "Analysis complete!",
  "result": { /* full analysis */ }
}
```

### GET /api/health
Health check endpoint

---

## Troubleshooting

### "GROQ_API_KEY not set"
- Create a `.env` file with your API key
- Or run without AI features (scores still work)

### "Could not connect to website"
- Check if the URL is correct
- Website might be blocking automated access
- Try a different URL

### "Page has insufficient content"
- Page needs at least 50 words of content
- Try analyzing a blog post or article page instead

### Analysis takes too long
- Some websites load slowly
- JavaScript-heavy sites may not render properly (we use static HTML)
- Try the homepage or a simpler page

### Import errors
- Make sure you installed all dependencies: `pip install -r requirements.txt`
- Check Python version (3.10+ recommended)

---

## Testing

### Test with these example URLs:
1. **Your own blog**: Real results you can act on
2. **Competitor sites**: See what they're doing better/worse
3. **Wikipedia articles**: Usually have good SEO but weak AEO
4. **How-to blogs**: Often strong AEO signals

### What to look for:
- SEO scores should reflect traditional best practices
- AEO scores should highlight answer-readiness
- Recommendations should be specific and actionable
- Before/after examples should show clear improvements

---

## Customization Ideas

### Add More Checks
Edit `analyzers/seo_analyzer.py` or `analyzers/aeo_analyzer.py`:
- Add new check methods
- Update the `analyze()` method to include them
- Adjust weights in `config.py`

### Change UI Theme
Edit `static/css/style.css`:
- Modify CSS variables at the top
- Change colors, fonts, spacing

### Add Export Features
Modify `static/js/app.js` to add:
- PDF export
- JSON download
- Share link generation

---

## Performance Notes

- **Target**: Analysis completes in 15-20 seconds
- **Crawling**: 2-5 seconds
- **Analysis**: 1-2 seconds
- **AI Enhancement**: 8-12 seconds (optional)

To improve performance:
- Reduce AI calls
- Cache common site analyses
- Use async for AI calls
- Add database for results storage

---

## Production Deployment

### Before going live:

1. **Database**: Replace in-memory `analysis_results` dict with Redis/PostgreSQL
2. **Rate Limiting**: Add rate limiting to prevent abuse
3. **Authentication**: Add user accounts if needed
4. **Monitoring**: Add logging and error tracking
5. **HTTPS**: Use proper SSL certificates
6. **Environment**: Use production ASGI server (gunicorn + uvicorn)
7. **Scaling**: Consider background job queues (Celery)

### Example production command:
```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

---

## Philosophy Reminder

This tool is built on:

- **Rules over hype**: Scoring is deterministic
- **Clarity over cleverness**: Every score is explainable
- **AI as helper**: AI rewrites and explains, but doesn't decide

If something feels wrong, **fix it**. If something can be better, **improve it**.

Don't turn this into bloated SEO buzzword machine.

---

## Support

Questions? Issues? Improvements?

Check the code comments - they're extensive.
Most logic is self-explanatory with clear function names.

**Remember**: This is an MVP. It's meant to be extended, modified, and improved based on real usage.
