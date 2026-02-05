"""
Visual Analyzer - Captures screenshots and annotates them with SEO/AEO issues
"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image, ImageDraw, ImageFont
from typing import Dict, List, Tuple
import time
import os


class VisualAnalyzer:
    """Captures webpage screenshots and annotates them with issues"""
    
    def __init__(self):
        self.driver = None
        
    def setup_driver(self):
        """Initialize headless Chrome driver"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
    
    def capture_screenshot(self, url: str, output_path: str) -> str:
        """Capture full-page screenshot"""
        if not self.driver:
            self.setup_driver()
        
        self.driver.get(url)
        time.sleep(3)  # Wait for page load
        
        # Take screenshot
        self.driver.save_screenshot(output_path)
        return output_path
    
    def annotate_issues(self, screenshot_path: str, issues: List[Dict], output_path: str):
        """Annotate screenshot with visual markers for issues"""
        img = Image.open(screenshot_path)
        draw = ImageDraw.Draw(img)
        
        # Try to load font, fallback to default
        try:
            font = ImageFont.truetype("arial.ttf", 24)
            font_small = ImageFont.truetype("arial.ttf", 18)
        except:
            font = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Color coding by issue severity
        colors = {
            'fail': (255, 0, 0, 200),      # Red
            'warning': (255, 165, 0, 200),  # Orange
            'pass': (0, 200, 0, 200)        # Green
        }
        
        y_offset = 50
        annotation_number = 1
        
        for issue in issues:
            status = issue.get('status', 'warning')
            name = issue.get('name', 'Unknown')
            color = colors.get(status, colors['warning'])
            
            # Determine position based on issue type
            position = self._map_issue_to_position(name, img.size)
            
            # Draw circle marker
            self._draw_marker(draw, position, annotation_number, color)
            
            # Draw annotation box on the right side
            box_x = img.width - 500
            box_y = y_offset
            self._draw_annotation_box(
                draw, 
                (box_x, box_y), 
                f"{annotation_number}. {name}", 
                issue.get('explanation', '')[:80],
                color,
                font_small
            )
            
            y_offset += 100
            annotation_number += 1
        
        img.save(output_path)
        return output_path
    
    def _map_issue_to_position(self, issue_name: str, img_size: Tuple[int, int]) -> Tuple[int, int]:
        """Map issue type to approximate screen position"""
        width, height = img_size
        
        # Position mapping based on typical webpage structure
        position_map = {
            'Page Title': (100, 50),
            'Meta Description': (100, 50),
            'H1 Heading': (200, 200),
            'Heading Hierarchy': (200, 300),
            'Content Length': (width // 2, height // 2),
            'Readability': (width // 2, height // 2),
            'Internal Links': (300, height - 200),
            'External Links': (300, height - 300),
            'Image Optimization': (width - 300, height // 2),
            'Social Media (Open Graph)': (100, 80),
            'Structured Data (Schema)': (100, 100),
            'HTTPS & Security Headers': (50, 30),
            'Mobile-Friendliness': (width - 100, 50),
            'Canonical Tag': (100, 70),
        }
        
        return position_map.get(issue_name, (width // 2, 150))
    
    def _draw_marker(self, draw, position: Tuple[int, int], number: int, color: Tuple):
        """Draw numbered circle marker"""
        x, y = position
        radius = 30
        
        # Draw circle
        draw.ellipse(
            [(x - radius, y - radius), (x + radius, y + radius)],
            fill=color,
            outline=(255, 255, 255, 255),
            width=3
        )
        
        # Draw number
        try:
            font = ImageFont.truetype("arial.ttf", 28)
        except:
            font = ImageFont.load_default()
        
        text = str(number)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        draw.text(
            (x - text_width // 2, y - text_height // 2),
            text,
            fill=(255, 255, 255, 255),
            font=font
        )
    
    def _draw_annotation_box(self, draw, position: Tuple[int, int], title: str, description: str, color: Tuple, font):
        """Draw annotation box with issue details"""
        x, y = position
        box_width = 480
        box_height = 90
        
        # Draw background box
        draw.rectangle(
            [(x, y), (x + box_width, y + box_height)],
            fill=(255, 255, 255, 230),
            outline=color,
            width=3
        )
        
        # Draw title
        draw.text((x + 10, y + 10), title, fill=color, font=font)
        
        # Draw description
        draw.text((x + 10, y + 40), description, fill=(50, 50, 50, 255), font=font)
    
    def cleanup(self):
        """Close browser driver"""
        if self.driver:
            self.driver.quit()
