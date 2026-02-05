# Visual Analysis Feature - Documentation

## Overview

The visual analysis feature captures screenshots of analyzed websites, annotates them with detected SEO/AEO issues, and generates comprehensive PDF reports. Issues are marked directly on the webpage screenshot with numbered markers and explanations.

## Features

✅ **Screenshot Capture** - Automated webpage screenshots using Selenium  
✅ **Visual Annotation** - Issues marked with colored circles and numbers  
✅ **Color Coding** - Red (fail), Orange (warning), Green (pass)  
✅ **Position Mapping** - Issues placed at relevant screen locations  
✅ **Annotation Boxes** - Side panel with issue explanations  
✅ **PDF Reports** - Professional reports with scores, annotated images, and detailed checks  
✅ **Download Endpoints** - Separate endpoints for PDF and annotated images  

## API Endpoints

### 1. Start Visual Analysis
```http
POST /api/analyze-visual
Content-Type: application/json

{
  "url": "https://example.com"
}
```

**Response:**
```json
{
  "analysis_id": "abc123-def456-...",
  "message": "Visual analysis started",
  "status_url": "/api/status/abc123-def456-...",
  "report_url": "/api/report/abc123-def456-..."
}
```

### 2. Check Analysis Status
```http
GET /api/status/{analysis_id}
```

**Response:**
```json
{
  "status": "completed",
  "progress": "Visual analysis complete!",
  "result": {
    "seo": { "score": 85.5, ... },
    "aeo": { "score": 78.2, ... },
    "crawlability": { "score": 95.0, ... },
    "visual_report": {
      "screenshot": "reports/abc123_original.png",
      "annotated_screenshot": "reports/abc123_annotated.png",
      "pdf_report": "reports/abc123_report.pdf"
    }
  }
}
```

### 3. Download PDF Report
```http
GET /api/report/{analysis_id}/pdf
```

Returns PDF file with:
- Cover page with URL and analysis date
- Executive summary with scores table
- Annotated screenshot showing issues
- Detailed SEO check results
- Detailed AEO check results
- Crawlability analysis results

### 4. Get Annotated Image
```http
GET /api/report/{analysis_id}/image
```

Returns PNG image with visual annotations showing where issues are on the webpage.

## Usage Examples

### Using cURL

```bash
# Start visual analysis
curl -X POST http://localhost:8000/api/analyze-visual \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'

# Check status
curl http://localhost:8000/api/status/YOUR_ANALYSIS_ID

# Download PDF
curl http://localhost:8000/api/report/YOUR_ANALYSIS_ID/pdf \
  -o report.pdf

# Download annotated image
curl http://localhost:8000/api/report/YOUR_ANALYSIS_ID/image \
  -o annotated.png
```

### Using Python

```python
import requests
import time

# Start analysis
response = requests.post(
    "http://localhost:8000/api/analyze-visual",
    json={"url": "https://example.com"}
)
analysis_id = response.json()["analysis_id"]

# Wait for completion
while True:
    status = requests.get(f"http://localhost:8000/api/status/{analysis_id}").json()
    if status["status"] == "completed":
        break
    print(f"Progress: {status['progress']}")
    time.sleep(2)

# Download PDF report
pdf_response = requests.get(f"http://localhost:8000/api/report/{analysis_id}/pdf")
with open("report.pdf", "wb") as f:
    f.write(pdf_response.content)

# Download annotated image
img_response = requests.get(f"http://localhost:8000/api/report/{analysis_id}/image")
with open("annotated.png", "wb") as f:
    f.write(img_response.content)
```

### Using JavaScript/Fetch

```javascript
// Start analysis
const response = await fetch('http://localhost:8000/api/analyze-visual', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ url: 'https://example.com' })
});
const { analysis_id } = await response.json();

// Poll for completion
let status = { status: 'processing' };
while (status.status !== 'completed') {
  await new Promise(resolve => setTimeout(resolve, 2000));
  const statusResponse = await fetch(`http://localhost:8000/api/status/${analysis_id}`);
  status = await statusResponse.json();
  console.log('Progress:', status.progress);
}

// Download PDF
window.open(`http://localhost:8000/api/report/${analysis_id}/pdf`);

// Display annotated image
const imageUrl = `http://localhost:8000/api/report/${analysis_id}/image`;
document.getElementById('result').innerHTML = `<img src="${imageUrl}" alt="Annotated Screenshot">`;
```

## Visual Annotation Details

### Issue Positioning

Issues are mapped to approximate screen positions based on their type:

| Issue Type | Screen Position |
|------------|----------------|
| Page Title, Meta Description | Top left (header area) |
| H1 Heading | Upper content area |
| Content Length, Readability | Center page |
| Links | Lower content area |
| Images | Right side |
| Security Headers | Top bar |
| Mobile-Friendliness | Top right |

### Color Coding

- **🔴 Red (Fail)**: Critical issues that must be fixed
- **🟠 Orange (Warning)**: Important improvements recommended
- **🟢 Green (Pass)**: No issues detected (not shown on annotations)

### Annotation Components

1. **Numbered Circles**: Placed on the screenshot at issue locations
2. **Annotation Boxes**: Right side panel with:
   - Issue number and name
   - Brief explanation (first 80 characters)

### PDF Report Structure

1. **Cover Page**
   - Report title
   - Analyzed URL
   - Analysis date

2. **Executive Summary**
   - Score table with SEO, AEO, and Crawlability scores
   - Letter grades (A, B, C, D, F)

3. **Visual Analysis Page**
   - Full annotated screenshot
   - Caption explaining the annotations

4. **Detailed Checks** (3 sections)
   - SEO Analysis Details (16 checks)
   - AEO Analysis Details (6 checks)
   - Crawlability Analysis (2 checks)

Each check includes:
- Check name with color-coded status
- Explanation in italics
- Actionable recommendation with arrow

## Requirements

### System Requirements

- **Chrome Browser**: Required for screenshot capture
- **Python 3.8+**: For running the application
- **4GB RAM minimum**: For browser automation

### Python Dependencies

```txt
selenium==4.17.2          # Browser automation
Pillow==10.2.0            # Image manipulation
reportlab==4.0.9          # PDF generation
webdriver-manager==4.0.1  # ChromeDriver management
```

All dependencies are automatically installed via requirements.txt.

## File Structure

```
d:\seoaeo\
├── visual_analyzer.py       # Screenshot capture & annotation
├── pdf_generator.py          # PDF report generation
├── main.py                   # API endpoints (updated)
├── requirements.txt          # Dependencies (updated)
├── test_visual.py            # Test script
└── reports/                  # Generated reports (auto-created)
    ├── {id}_original.png     # Original screenshot
    ├── {id}_annotated.png    # Annotated screenshot
    └── {id}_report.pdf        # PDF report
```

## Troubleshooting

### Chrome/ChromeDriver Issues

**Error**: "ChromeDriver not found"
```bash
# WebDriver Manager automatically downloads ChromeDriver
# Ensure Chrome browser is installed
```

**Error**: "Chrome failed to start"
```python
# Add these options to visual_analyzer.py if needed:
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--disable-dev-shm-usage')
```

### PDF Generation Issues

**Error**: "Cannot find font"
```python
# Fonts fallback to default if system fonts unavailable
# This is handled automatically in the code
```

### Screenshot Size Issues

Default size: 1920x1080. To change:
```python
# In visual_analyzer.py, modify:
chrome_options.add_argument('--window-size=1920,1080')
```

## Performance Considerations

| Operation | Time | Notes |
|-----------|------|-------|
| Standard Analysis | 5-10s | Without visual features |
| Visual Analysis | 15-25s | Includes screenshot + PDF |
| Screenshot Capture | 3-5s | Depends on page load time |
| Image Annotation | 1-2s | In-memory processing |
| PDF Generation | 2-3s | Including all sections |

**Optimization Tips:**
- Use standard `/api/analyze` for quick checks
- Use `/api/analyze-visual` when presentation matters
- Screenshots are cached in `reports/` directory
- Clean up old reports periodically

## Limitations

1. **Screenshot Accuracy**: Positioning is approximate based on typical layouts
2. **Dynamic Content**: JavaScript-heavy sites may need longer load times
3. **Mobile View**: Screenshots are desktop view (1920x1080)
4. **File Storage**: Reports stored on disk (consider cloud storage for production)
5. **Chrome Dependency**: Requires Chrome browser installed on server

## Future Enhancements

- [ ] Mobile viewport screenshots
- [ ] Multiple screenshot sizes
- [ ] Comparison reports (before/after)
- [ ] Custom annotation positions
- [ ] Batch analysis with merged PDF
- [ ] HTML report format
- [ ] Email delivery of reports
- [ ] Report history/archive

## Testing

Run the test script to verify setup:

```bash
cd d:\seoaeo
python test_visual.py
```

Expected output:
```
Testing Visual Analysis Components...
============================================================

1. Testing VisualAnalyzer initialization...
   [OK] VisualAnalyzer created successfully

2. Testing PDFReportGenerator initialization...
   [OK] PDFReportGenerator created successfully

3. Generating sample PDF report...
   [OK] PDF report generated: reports\test_report.pdf
   [OK] File size: 3.18 KB

============================================================
Visual analysis components are ready!
```

## Support

For issues or questions:
1. Check this documentation
2. Review error messages in terminal
3. Verify Chrome browser is installed
4. Check Python dependencies are installed
5. Ensure reports directory has write permissions
