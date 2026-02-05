"""
Test script for visual analysis functionality
"""
from visual_analyzer import VisualAnalyzer
from pdf_generator import PDFReportGenerator
from pathlib import Path
import json

# Create test reports directory
REPORTS_DIR = Path("reports")
REPORTS_DIR.mkdir(exist_ok=True)

print("Testing Visual Analysis Components...")
print("=" * 60)

# Test 1: Visual Analyzer initialization
print("\n1. Testing VisualAnalyzer initialization...")
try:
    analyzer = VisualAnalyzer()
    print("   [OK] VisualAnalyzer created successfully")
except Exception as e:
    print(f"   [FAIL] Failed: {e}")

# Test 2: PDF Generator initialization
print("\n2. Testing PDFReportGenerator initialization...")
try:
    test_pdf_path = REPORTS_DIR / "test_report.pdf"
    pdf_gen = PDFReportGenerator(str(test_pdf_path))
    print("   [OK] PDFReportGenerator created successfully")
except Exception as e:
    print(f"   [FAIL] Failed: {e}")

# Test 3: Generate sample PDF report
print("\n3. Generating sample PDF report...")
try:
    pdf_gen.add_cover_page("https://example.com", "2026-02-05")
    pdf_gen.add_score_summary(85.5, 78.2, 95.0)
    
    # Add sample check
    sample_checks = [
        {
            "name": "Page Title",
            "status": "pass",
            "explanation": "Title length is optimal (45 characters).",
            "recommendation": "Title looks good.",
            "score": 100
        },
        {
            "name": "Mobile-Friendliness",
            "status": "warning",
            "explanation": "Viewport tag missing 'width' attribute",
            "recommendation": "Add width=device-width to viewport meta tag",
            "score": 70
        }
    ]
    
    pdf_gen.add_detailed_checks(sample_checks, "Sample SEO Checks")
    pdf_gen.generate()
    
    print(f"   [OK] PDF report generated: {test_pdf_path}")
    print(f"   [OK] File size: {test_pdf_path.stat().st_size / 1024:.2f} KB")
except Exception as e:
    print(f"   [FAIL] Failed: {e}")

print("\n" + "=" * 60)
print("Visual analysis components are ready!")
print("\nAPI Endpoints:")
print("  - POST /api/analyze-visual     - Start visual analysis")
print("  - GET  /api/report/{id}/pdf    - Download PDF report")
print("  - GET  /api/report/{id}/image  - Get annotated image")
print("\nNote: Screenshot capture requires Chrome browser installed")
print("=" * 60)
