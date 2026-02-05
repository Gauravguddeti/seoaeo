"""
PDF Report Generator - Creates downloadable PDF reports with annotated images
"""
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
from typing import Dict
import os


class PDFReportGenerator:
    """Generates comprehensive PDF reports with visual analysis"""
    
    def __init__(self, output_path: str):
        self.output_path = output_path
        self.doc = SimpleDocTemplate(output_path, pagesize=A4)
        self.styles = getSampleStyleSheet()
        self.story = []
        
        # Custom styles
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2C3E50'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#34495E'),
            spaceAfter=12,
            spaceBefore=12
        )
    
    def add_cover_page(self, url: str, analysis_date: str):
        """Add cover page"""
        self.story.append(Spacer(1, 2*inch))
        
        title = Paragraph("SEO & AEO Analysis Report", self.title_style)
        self.story.append(title)
        self.story.append(Spacer(1, 0.5*inch))
        
        url_text = Paragraph(f"<b>Website:</b> {url}", self.styles['Normal'])
        self.story.append(url_text)
        self.story.append(Spacer(1, 0.2*inch))
        
        date_text = Paragraph(f"<b>Analysis Date:</b> {analysis_date}", self.styles['Normal'])
        self.story.append(date_text)
        
        self.story.append(PageBreak())
    
    def add_score_summary(self, seo_score: float, aeo_score: float, crawlability_score: float):
        """Add score summary page"""
        heading = Paragraph("Executive Summary", self.heading_style)
        self.story.append(heading)
        self.story.append(Spacer(1, 0.3*inch))
        
        # Create score table
        data = [
            ['Metric', 'Score', 'Grade'],
            ['SEO Score', f'{seo_score}/100', self._score_to_grade(seo_score)],
            ['AEO Score', f'{aeo_score}/100', self._score_to_grade(aeo_score)],
            ['Crawlability', f'{crawlability_score}/100', self._score_to_grade(crawlability_score)],
        ]
        
        table = Table(data, colWidths=[2*inch, 1.5*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498DB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 0.5*inch))
    
    def add_annotated_screenshot(self, image_path: str, caption: str = "Visual Analysis"):
        """Add annotated screenshot to report"""
        heading = Paragraph("Visual Analysis", self.heading_style)
        self.story.append(heading)
        self.story.append(Spacer(1, 0.2*inch))
        
        caption_text = Paragraph(caption, self.styles['Normal'])
        self.story.append(caption_text)
        self.story.append(Spacer(1, 0.2*inch))
        
        # Add image (scale to fit page)
        img = RLImage(image_path, width=7*inch, height=4.5*inch)
        self.story.append(img)
        self.story.append(PageBreak())
    
    def add_detailed_checks(self, checks: list, section_title: str):
        """Add detailed check results"""
        heading = Paragraph(section_title, self.heading_style)
        self.story.append(heading)
        self.story.append(Spacer(1, 0.2*inch))
        
        for check in checks:
            status_color = {
                'pass': colors.green,
                'warning': colors.orange,
                'fail': colors.red
            }.get(check.get('status', 'warning'), colors.orange)
            
            check_title = Paragraph(
                f"<b>{check.get('name', 'Check')}</b> - "
                f"<font color='{status_color.hexval()}'>{check.get('status', 'N/A').upper()}</font>",
                self.styles['Normal']
            )
            self.story.append(check_title)
            self.story.append(Spacer(1, 0.1*inch))
            
            explanation = Paragraph(f"<i>{check.get('explanation', '')}</i>", self.styles['Normal'])
            self.story.append(explanation)
            self.story.append(Spacer(1, 0.05*inch))
            
            recommendation = Paragraph(f"→ {check.get('recommendation', '')}", self.styles['Normal'])
            self.story.append(recommendation)
            self.story.append(Spacer(1, 0.2*inch))
        
        self.story.append(PageBreak())
    
    def generate(self):
        """Generate the PDF file"""
        self.doc.build(self.story)
        return self.output_path
    
    @staticmethod
    def _score_to_grade(score: float) -> str:
        """Convert score to letter grade"""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'
