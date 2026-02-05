"""
FastAPI main application
Handles URL analysis requests and serves frontend
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from pydantic import BaseModel, HttpUrl
from typing import Dict, Optional
import uuid
import time
from datetime import datetime
from pathlib import Path
import os

from scraper.crawler import WebCrawler
from analyzers.seo_analyzer import SEOAnalyzer
from analyzers.aeo_analyzer import AEOAnalyzer
from analyzers.keyword_analyzer import KeywordAnalyzer
from analyzers.scoring import ScoringEngine
from analyzers.crawlability_analyzer import CrawlabilityAnalyzer
from ai.groq_client import GroqClient
from utils import URLValidator, ContentValidator, handle_crawl_errors, handle_ai_errors, ValidationError
from history_storage import HistoryStorage
from visual_analyzer import VisualAnalyzer
from pdf_generator import PDFReportGenerator

app = FastAPI(
    title="SEO + AEO Analyzer",
    description="Analyze websites for SEO and Answer Engine Optimization",
    version="1.0.0"
)

# Create reports directory
REPORTS_DIR = Path("reports")
REPORTS_DIR.mkdir(exist_ok=True)

# In-memory storage for analysis results (in production, use a database)
analysis_results = {}

# History storage
history_storage = HistoryStorage()


class AnalyzeRequest(BaseModel):
    """Request model for URL analysis"""
    url: HttpUrl


class AnalysisStatus(BaseModel):
    """Status of an ongoing analysis"""
    status: str  # "processing", "completed", "failed"
    progress: str
    result: Optional[Dict] = None
    error: Optional[str] = None


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main HTML page"""
    with open("static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.post("/api/analyze")
async def analyze_url(request: AnalyzeRequest, background_tasks: BackgroundTasks):
    """
    Start analysis of a URL
    Returns an analysis ID to check status
    """
    url = str(request.url)
    
    # Validate URL
    try:
        url = URLValidator.validate(url)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    analysis_id = str(uuid.uuid4())
    
    # Initialize status
    analysis_results[analysis_id] = {
        "status": "processing",
        "progress": "Starting analysis...",
        "started_at": datetime.now().isoformat()
    }
    
    # Run analysis in background
    background_tasks.add_task(run_analysis, analysis_id, url)
    
    return {
        "analysis_id": analysis_id,
        "message": "Analysis started",
        "status_url": f"/api/status/{analysis_id}"
    }


@app.post("/api/analyze-visual")
async def analyze_url_visual(request: AnalyzeRequest, background_tasks: BackgroundTasks):
    """
    Start visual analysis with screenshot annotation
    Returns an analysis ID to check status
    """
    url = str(request.url)
    
    # Validate URL
    try:
        url = URLValidator.validate(url)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    analysis_id = str(uuid.uuid4())
    
    # Initialize status
    analysis_results[analysis_id] = {
        "status": "processing",
        "progress": "Starting visual analysis...",
        "started_at": datetime.now().isoformat()
    }
    
    # Run analysis in background
    background_tasks.add_task(run_visual_analysis, analysis_id, url)
    
    return {
        "analysis_id": analysis_id,
        "message": "Visual analysis started",
        "status_url": f"/api/status/{analysis_id}",
        "report_url": f"/api/report/{analysis_id}"
    }


@app.get("/api/status/{analysis_id}")
async def get_analysis_status(analysis_id: str):
    """Get the status of an analysis"""
    if analysis_id not in analysis_results:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    return analysis_results[analysis_id]


async def run_analysis(analysis_id: str, url: str):
    """
    Run the complete analysis pipeline
    This runs in the background
    """
    try:
        # Update progress
        analysis_results[analysis_id]["progress"] = "Crawling website..."
        
        # Step 1: Crawl website
        try:
            crawler = WebCrawler(url)
            pages = crawler.crawl()
        except Exception as e:
            # Log the actual error for debugging
            import traceback
            print(f"\n[CRAWLER ERROR] Type: {type(e).__name__}")
            print(f"[CRAWLER ERROR] Message: {str(e)}")
            print(f"[CRAWLER ERROR] URL: {url}")
            print(f"[CRAWLER ERROR] Traceback:")
            traceback.print_exc()
            print("=" * 80)
            raise Exception(handle_crawl_errors(e))
        
        if not pages:
            raise Exception("No content could be extracted from the website")
        
        # Use the first page (homepage) for analysis
        content = pages[0]
        
        # Validate content
        is_valid, error_msg = ContentValidator.has_minimum_content(content)
        if not is_valid:
            raise Exception(error_msg)
        
        unsupported_msg = ContentValidator.detect_unsupported_content(content)
        if unsupported_msg:
            raise Exception(unsupported_msg)
        
        # Step 2: SEO Analysis
        analysis_results[analysis_id]["progress"] = "Running SEO analysis..."
        seo_analyzer = SEOAnalyzer(content)
        seo_results = seo_analyzer.analyze()
        
        # Step 3: AEO Analysis
        analysis_results[analysis_id]["progress"] = "Running AEO analysis..."
        aeo_analyzer = AEOAnalyzer(content)
        aeo_results = aeo_analyzer.analyze()
        
        # Step 3.5: Crawlability Analysis
        analysis_results[analysis_id]["progress"] = "Checking crawlability..."
        crawlability_analyzer = CrawlabilityAnalyzer(url)
        crawlability_results = crawlability_analyzer.analyze()
        
        # Step 3.7: Keyword Analysis
        analysis_results[analysis_id]["progress"] = "Analyzing keywords..."
        keyword_analyzer = KeywordAnalyzer(content)
        keyword_results = keyword_analyzer.analyze()
        
        # Step 4: Calculate Scores
        analysis_results[analysis_id]["progress"] = "Calculating scores..."
        seo_score = ScoringEngine.calculate_seo_score(seo_results['checks'])
        aeo_score = ScoringEngine.calculate_aeo_score(aeo_results['checks'])
        crawlability_score = ScoringEngine.calculate_crawlability_score(crawlability_results['checks'])
        
        # Step 5: Generate Recommendations
        recommendations = ScoringEngine.generate_priority_recommendations(
            seo_results['checks'],
            aeo_results['checks'],
            seo_score['score'],
            aeo_score['score']
        )
        
        action_checklist = ScoringEngine.generate_action_checklist(recommendations)
        
        # Step 6: AI Enhancement (optional, gracefully degrade if fails)
        analysis_results[analysis_id]["progress"] = "Generating AI insights..."
        ai_content = None
        ai_explanation_seo = None
        ai_explanation_aeo = None
        
        try:
            groq_client = GroqClient()
            
            # Generate before/after example if there's a top issue
            if recommendations:
                try:
                    ai_content = groq_client.generate_before_after_example(
                        content, 
                        recommendations[0]
                    )
                except Exception as e:
                    print(handle_ai_errors(e, "Content rewrite example"))
            
            # Generate explanations
            try:
                ai_explanation_seo = groq_client.explain_recommendations(
                    [r for r in recommendations if r['type'] == 'SEO'][:3],
                    seo_score['score'],
                    'SEO'
                )
            except Exception as e:
                print(handle_ai_errors(e, "SEO explanation"))
            
            try:
                ai_explanation_aeo = groq_client.explain_recommendations(
                    [r for r in recommendations if r['type'] == 'AEO'][:3],
                    aeo_score['score'],
                    'AEO'
                )
            except Exception as e:
                print(handle_ai_errors(e, "AEO explanation"))
        
        except Exception as e:
            # Groq client initialization failed
            print(handle_ai_errors(e, "AI features"))
            # Continue without AI enhancements
        
        # Compile final result
        result = {
            "url": url,
            "analyzed_at": datetime.now().isoformat(),
            "metadata": {
                "title": content.get('title', ''),
                "word_count": content.get('word_count', 0),
                "url": content.get('url', url)
            },
            "seo": {
                "score": seo_score['score'],
                "grade": seo_score['grade'],
                "explanation": ai_explanation_seo or seo_score['explanation'],
                "checks": seo_results['checks'],
                "breakdown": seo_score['breakdown']
            },
            "aeo": {
                "score": aeo_score['score'],
                "grade": aeo_score['grade'],
                "explanation": ai_explanation_aeo or aeo_score['explanation'],
                "checks": aeo_results['checks'],
                "breakdown": aeo_score['breakdown'],
                "top_issues": aeo_results.get('top_issues', [])
            },
            "crawlability": {
                "score": crawlability_score['score'],
                "grade": crawlability_score['grade'],
                "explanation": crawlability_score['explanation'],
                "checks": crawlability_results['checks'],
                "breakdown": crawlability_score['breakdown']
            },
            "keywords": keyword_results,
            "recommendations": recommendations,
            "action_checklist": action_checklist,
            "before_after_example": ai_content
        }
        
        # Mark as completed
        analysis_results[analysis_id]["status"] = "completed"
        analysis_results[analysis_id]["progress"] = "Analysis complete!"
        analysis_results[analysis_id]["result"] = result
        
        # Save to history
        try:
            history_storage.save_analysis(url, result)
        except Exception as e:
            print(f"Failed to save to history: {e}")
    
    except Exception as e:
        # Mark as failed
        analysis_results[analysis_id]["status"] = "failed"
        analysis_results[analysis_id]["error"] = str(e)
        analysis_results[analysis_id]["progress"] = f"Analysis failed: {str(e)}"


async def run_visual_analysis(analysis_id: str, url: str):
    """
    Run the complete analysis pipeline with visual annotation
    This runs in the background
    """
    visual_analyzer = None
    
    try:
        # Run standard analysis first
        await run_analysis(analysis_id, url)
        
        if analysis_results[analysis_id]["status"] == "failed":
            return
        
        # Get analysis results
        result = analysis_results[analysis_id]["result"]
        
        # Visual annotation
        analysis_results[analysis_id]["progress"] = "Capturing screenshot..."
        
        visual_analyzer = VisualAnalyzer()
        
        # Capture screenshot
        screenshot_path = REPORTS_DIR / f"{analysis_id}_original.png"
        visual_analyzer.capture_screenshot(url, str(screenshot_path))
        
        # Annotate with issues
        analysis_results[analysis_id]["progress"] = "Annotating issues..."
        
        # Collect all issues (fail + warning only)
        issues_to_annotate = []
        for check in result['seo']['checks']:
            if check['status'] in ['fail', 'warning']:
                issues_to_annotate.append(check)
        
        annotated_path = REPORTS_DIR / f"{analysis_id}_annotated.png"
        visual_analyzer.annotate_issues(
            str(screenshot_path),
            issues_to_annotate[:10],  # Limit to top 10 issues
            str(annotated_path)
        )
        
        # Generate PDF
        analysis_results[analysis_id]["progress"] = "Generating PDF report..."
        
        pdf_path = REPORTS_DIR / f"{analysis_id}_report.pdf"
        pdf_gen = PDFReportGenerator(str(pdf_path))
        
        pdf_gen.add_cover_page(url, result['analyzed_at'])
        pdf_gen.add_score_summary(
            result['seo']['score'],
            result['aeo']['score'],
            result['crawlability']['score']
        )
        pdf_gen.add_annotated_screenshot(str(annotated_path), "Issues highlighted on the webpage")
        pdf_gen.add_detailed_checks(result['seo']['checks'], "SEO Analysis Details")
        pdf_gen.add_detailed_checks(result['aeo']['checks'], "AEO Analysis Details")
        pdf_gen.add_detailed_checks(result['crawlability']['checks'], "Crawlability Analysis")
        
        pdf_gen.generate()
        
        # Update result with visual report paths
        result['visual_report'] = {
            'screenshot': str(screenshot_path),
            'annotated_screenshot': str(annotated_path),
            'pdf_report': str(pdf_path)
        }
        
        analysis_results[analysis_id]["result"] = result
        analysis_results[analysis_id]["progress"] = "Visual analysis complete!"
        
    except Exception as e:
        analysis_results[analysis_id]["status"] = "failed"
        analysis_results[analysis_id]["error"] = f"Visual analysis failed: {str(e)}"
        analysis_results[analysis_id]["progress"] = f"Visual analysis failed: {str(e)}"
    finally:
        if visual_analyzer:
            visual_analyzer.cleanup()


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/report/{analysis_id}/pdf")
async def download_pdf_report(analysis_id: str):
    """Download PDF report"""
    if analysis_id not in analysis_results:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    result = analysis_results[analysis_id].get("result")
    if not result or 'visual_report' not in result:
        raise HTTPException(status_code=404, detail="Visual report not available. Use /api/analyze-visual endpoint")
    
    pdf_path = result['visual_report']['pdf_report']
    
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="PDF report file not found")
    
    return FileResponse(
        pdf_path,
        media_type='application/pdf',
        filename=f"seo_report_{analysis_id}.pdf"
    )


@app.get("/api/report/{analysis_id}/image")
async def get_annotated_image(analysis_id: str):
    """Get annotated screenshot"""
    if analysis_id not in analysis_results:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    result = analysis_results[analysis_id].get("result")
    if not result or 'visual_report' not in result:
        raise HTTPException(status_code=404, detail="Visual report not available. Use /api/analyze-visual endpoint")
    
    image_path = result['visual_report']['annotated_screenshot']
    
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Annotated image not found")
    
    return FileResponse(
        image_path,
        media_type='image/png',
        filename=f"annotated_{analysis_id}.png"
    )


@app.get("/api/export/{analysis_id}")
async def export_report(analysis_id: str, format: str = "json"):
    """
    Export analysis report in JSON or text format
    """
    if analysis_id not in analysis_results:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    analysis = analysis_results[analysis_id]
    
    if analysis["status"] != "completed":
        raise HTTPException(status_code=400, detail="Analysis not completed yet")
    
    result = analysis["result"]
    
    if format == "json":
        return JSONResponse(content=result)
    
    elif format == "txt":
        # Generate plain text report
        from fastapi.responses import PlainTextResponse
        report = generate_text_report(result)
        return PlainTextResponse(
            content=report,
            headers={"Content-Disposition": f"attachment; filename=seo-aeo-report-{analysis_id[:8]}.txt"}
        )
    
    else:
        raise HTTPException(status_code=400, detail="Invalid format. Use 'json' or 'txt'")


def generate_text_report(result: Dict) -> str:
    """Generate a plain text report"""
    lines = []
    lines.append("=" * 80)
    lines.append("SEO + AEO ANALYSIS REPORT")
    lines.append("=" * 80)
    lines.append("")
    lines.append(f"URL: {result['url']}")
    lines.append(f"Analyzed: {result['analyzed_at']}")
    lines.append(f"Page: {result['page_info']['title']}")
    lines.append(f"Word Count: {result['page_info']['word_count']}")
    lines.append("")
    
    # Scores
    lines.append("-" * 80)
    lines.append("SCORES")
    lines.append("-" * 80)
    lines.append(f"SEO Score: {result['seo']['score']}/100 (Grade: {result['seo']['grade']})")
    lines.append(f"  {result['seo']['explanation']}")
    lines.append("")
    lines.append(f"AEO Score: {result['aeo']['score']}/100 (Grade: {result['aeo']['grade']})")
    lines.append(f"  {result['aeo']['explanation']}")
    lines.append("")
    
    # Top Issues
    if result['aeo'].get('top_issues'):
        lines.append("-" * 80)
        lines.append("TOP REASONS AI WON'T PICK THIS PAGE")
        lines.append("-" * 80)
        for i, issue in enumerate(result['aeo']['top_issues'], 1):
            lines.append(f"{i}. {issue['name']}")
            lines.append(f"   {issue['reason']}")
            lines.append("")
    
    # SEO Checks
    lines.append("-" * 80)
    lines.append("SEO ANALYSIS DETAILS")
    lines.append("-" * 80)
    for check in result['seo']['checks']:
        status_symbol = "✓" if check['status'] == "pass" else ("⚠" if check['status'] == "warning" else "✗")
        lines.append(f"{status_symbol} {check['name']} [{check['status'].upper()}]")
        lines.append(f"  {check['explanation']}")
        lines.append(f"  → {check['recommendation']}")
        lines.append("")
    
    # AEO Checks
    lines.append("-" * 80)
    lines.append("AEO ANALYSIS DETAILS")
    lines.append("-" * 80)
    for check in result['aeo']['checks']:
        status_symbol = "✓" if check['status'] == "pass" else ("⚠" if check['status'] == "warning" else "✗")
        lines.append(f"{status_symbol} {check['name']} [{check['status'].upper()}]")
        lines.append(f"  {check['explanation']}")
        lines.append(f"  → {check['recommendation']}")
        lines.append("")
    
    # Action Checklist
    if result.get('action_checklist'):
        lines.append("-" * 80)
        lines.append("ACTION CHECKLIST")
        lines.append("-" * 80)
        for item in result['action_checklist']:
            lines.append(item)
        lines.append("")
    
    lines.append("=" * 80)
    lines.append("Generated by SEO + AEO Analyzer")
    lines.append("=" * 80)
    
    return "\n".join(lines)


@app.get("/api/history")
async def get_all_history():
    """Get all analyzed URLs with their latest results"""
    urls = history_storage.get_all_urls()
    return {"urls": urls}


@app.get("/api/history/{url:path}")
async def get_url_history(url: str, limit: int = 20):
    """Get analysis history for a specific URL"""
    history = history_storage.get_history_for_url(url, limit)
    return {"url": url, "history": history, "count": len(history)}


@app.get("/api/trends/{url:path}")
async def get_url_trends(url: str, limit: int = 10):
    """Get trend analysis for a URL"""
    trends = history_storage.compare_history(url, limit)
    return {"url": url, "trends": trends}


@app.delete("/api/history/{analysis_id}")
async def delete_analysis(analysis_id: str):
    """Delete a specific analysis from history"""
    success = history_storage.delete_history(analysis_id)
    
    if success:
        return {"message": "Analysis deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Analysis not found")


# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
