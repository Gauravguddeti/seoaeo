"""
SEO Analysis Engine - Rule-based, deterministic checks
"""
from typing import Dict, List, Tuple
import re
import config


class SEOCheck:
    """Represents a single SEO check result"""
    def __init__(self, name: str, status: str, explanation: str, recommendation: str, score: float):
        self.name = name
        self.status = status  # "pass", "warning", "fail"
        self.explanation = explanation
        self.recommendation = recommendation
        self.score = score  # 0-100 for this check
    
    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'status': self.status,
            'explanation': self.explanation,
            'recommendation': self.recommendation,
            'score': self.score
        }


class SEOAnalyzer:
    """Analyzes content for SEO best practices using deterministic rules"""
    
    def __init__(self, content: Dict):
        self.content = content
        self.checks: List[SEOCheck] = []
    
    def analyze(self) -> Dict:
        """Run all SEO checks"""
        self.checks = []
        
        self.check_title()
        self.check_meta_description()
        self.check_h1_count()
        self.check_heading_hierarchy()
        self.check_content_length()
        self.check_internal_links()
        self.check_external_links()
        self.check_readability()
        self.check_html_size()
        self.check_keyword_density()
        self.check_images()
        self.check_open_graph()
        self.check_schema_markup()
        
        return {
            'checks': [check.to_dict() for check in self.checks],
            'summary': self._generate_summary()
        }
    
    def check_title(self):
        """Check page title length and presence"""
        title = self.content.get('title', '')
        length = len(title)
        
        if not title:
            self.checks.append(SEOCheck(
                name="Page Title",
                status="fail",
                explanation="No title tag found on the page.",
                recommendation="Add a descriptive title tag between 30-60 characters that includes your target keyword.",
                score=0
            ))
        elif length < config.SEO_THRESHOLDS['title_min_length']:
            self.checks.append(SEOCheck(
                name="Page Title",
                status="warning",
                explanation=f"Title is too short ({length} characters). Search engines may not find it descriptive enough.",
                recommendation=f"Expand title to at least {config.SEO_THRESHOLDS['title_min_length']} characters while keeping it under {config.SEO_THRESHOLDS['title_max_length']}.",
                score=50
            ))
        elif length > config.SEO_THRESHOLDS['title_max_length']:
            self.checks.append(SEOCheck(
                name="Page Title",
                status="warning",
                explanation=f"Title is too long ({length} characters). It will be truncated in search results.",
                recommendation=f"Shorten title to {config.SEO_THRESHOLDS['title_max_length']} characters or less while keeping the most important keywords at the start.",
                score=70
            ))
        else:
            self.checks.append(SEOCheck(
                name="Page Title",
                status="pass",
                explanation=f"Title length is optimal ({length} characters).",
                recommendation="Title length is good. Ensure it accurately describes the page content and includes target keywords.",
                score=100
            ))
    
    def check_meta_description(self):
        """Check meta description presence and length"""
        meta = self.content.get('meta_description', '')
        length = len(meta)
        
        if not meta:
            self.checks.append(SEOCheck(
                name="Meta Description",
                status="fail",
                explanation="No meta description found.",
                recommendation="Add a compelling meta description between 120-160 characters that summarizes the page and encourages clicks.",
                score=0
            ))
        elif length < config.SEO_THRESHOLDS['meta_min_length']:
            self.checks.append(SEOCheck(
                name="Meta Description",
                status="warning",
                explanation=f"Meta description is too short ({length} characters).",
                recommendation=f"Expand to at least {config.SEO_THRESHOLDS['meta_min_length']} characters to maximize search snippet space.",
                score=50
            ))
        elif length > config.SEO_THRESHOLDS['meta_max_length']:
            self.checks.append(SEOCheck(
                name="Meta Description",
                status="warning",
                explanation=f"Meta description is too long ({length} characters) and will be cut off.",
                recommendation=f"Trim to {config.SEO_THRESHOLDS['meta_max_length']} characters, placing key information at the beginning.",
                score=70
            ))
        else:
            self.checks.append(SEOCheck(
                name="Meta Description",
                status="pass",
                explanation=f"Meta description length is optimal ({length} characters).",
                recommendation="Meta description length is good. Ensure it's compelling and includes a call-to-action.",
                score=100
            ))
    
    def check_h1_count(self):
        """Check H1 heading count"""
        h1s = self.content.get('headings', {}).get('h1', [])
        count = len(h1s)
        
        if count == 0:
            self.checks.append(SEOCheck(
                name="H1 Heading",
                status="fail",
                explanation="No H1 heading found on the page.",
                recommendation="Add exactly one H1 heading that clearly describes the page topic and includes your primary keyword.",
                score=0
            ))
        elif count == 1:
            self.checks.append(SEOCheck(
                name="H1 Heading",
                status="pass",
                explanation="Page has exactly one H1 heading (ideal).",
                recommendation="H1 count is perfect. Ensure it's descriptive and includes your primary keyword.",
                score=100
            ))
        else:
            self.checks.append(SEOCheck(
                name="H1 Heading",
                status="warning",
                explanation=f"Page has {count} H1 headings. Multiple H1s can dilute keyword focus.",
                recommendation="Reduce to one primary H1 heading. Convert other H1s to H2 or H3 headings based on content hierarchy.",
                score=60
            ))
    
    def check_heading_hierarchy(self):
        """Check if heading hierarchy is logical (H1 -> H2 -> H3 -> H4)"""
        headings = self.content.get('headings', {})
        h1_count = len(headings.get('h1', []))
        h2_count = len(headings.get('h2', []))
        h3_count = len(headings.get('h3', []))
        h4_count = len(headings.get('h4', []))
        
        issues = []
        
        if h1_count == 0 and (h2_count > 0 or h3_count > 0):
            issues.append("H2 or H3 headings exist without an H1")
        
        if h3_count > 0 and h2_count == 0:
            issues.append("H3 headings exist without any H2 headings")
        
        if h4_count > 0 and h3_count == 0:
            issues.append("H4 headings exist without any H3 headings")
        
        if issues:
            self.checks.append(SEOCheck(
                name="Heading Hierarchy",
                status="warning",
                explanation=f"Heading hierarchy issues detected: {', '.join(issues)}.",
                recommendation="Reorganize headings to follow proper hierarchy: H1 (page title) → H2 (main sections) → H3 (subsections) → H4 (minor sections).",
                score=50
            ))
        else:
            self.checks.append(SEOCheck(
                name="Heading Hierarchy",
                status="pass",
                explanation="Heading hierarchy follows proper structure.",
                recommendation="Heading structure is logical. Ensure each heading accurately describes the content below it.",
                score=100
            ))
    
    def check_content_length(self):
        """Check if content length is sufficient"""
        word_count = self.content.get('word_count', 0)
        
        if word_count < config.SEO_THRESHOLDS['content_min_words']:
            self.checks.append(SEOCheck(
                name="Content Length",
                status="fail",
                explanation=f"Content is too short ({word_count} words). Search engines prefer substantial content.",
                recommendation=f"Expand content to at least {config.SEO_THRESHOLDS['content_min_words']} words. Aim for {config.SEO_THRESHOLDS['content_ideal_words']}+ words for competitive topics.",
                score=30
            ))
        elif word_count < config.SEO_THRESHOLDS['content_ideal_words']:
            self.checks.append(SEOCheck(
                name="Content Length",
                status="warning",
                explanation=f"Content length ({word_count} words) is adequate but could be more comprehensive.",
                recommendation=f"Consider expanding to {config.SEO_THRESHOLDS['content_ideal_words']}+ words with more detailed information, examples, or use cases.",
                score=70
            ))
        else:
            self.checks.append(SEOCheck(
                name="Content Length",
                status="pass",
                explanation=f"Content length ({word_count} words) is substantial and comprehensive.",
                recommendation="Content length is good. Focus on maintaining quality and relevance throughout.",
                score=100
            ))
    
    def check_internal_links(self):
        """Check internal linking"""
        internal_count = self.content.get('links', {}).get('internal_count', 0)
        
        if internal_count < config.SEO_THRESHOLDS['internal_links_min']:
            self.checks.append(SEOCheck(
                name="Internal Links",
                status="warning",
                explanation=f"Only {internal_count} internal link(s) found. Internal linking helps SEO and user navigation.",
                recommendation=f"Add at least {config.SEO_THRESHOLDS['internal_links_min']} relevant internal links to related pages or resources on your site.",
                score=40
            ))
        else:
            self.checks.append(SEOCheck(
                name="Internal Links",
                status="pass",
                explanation=f"Good internal linking ({internal_count} links) helps distribute page authority.",
                recommendation="Internal linking is solid. Ensure anchor text is descriptive and links are contextually relevant.",
                score=100
            ))
    
    def check_external_links(self):
        """Check external linking"""
        external_count = self.content.get('links', {}).get('external_count', 0)
        
        if external_count < config.SEO_THRESHOLDS['external_links_min']:
            self.checks.append(SEOCheck(
                name="External Links",
                status="warning",
                explanation=f"Only {external_count} external link(s) found. Linking to authoritative sources builds trust.",
                recommendation="Add 1-3 links to relevant, authoritative external sources that support your content.",
                score=60
            ))
        else:
            self.checks.append(SEOCheck(
                name="External Links",
                status="pass",
                explanation=f"Page includes {external_count} external links to support claims.",
                recommendation="External linking is good. Ensure links go to reputable, relevant sources.",
                score=100
            ))
    
    def check_readability(self):
        """Basic readability check based on paragraph and sentence structure"""
        paragraphs = self.content.get('paragraphs', [])
        
        if not paragraphs:
            self.checks.append(SEOCheck(
                name="Readability",
                status="fail",
                explanation="No paragraph structure detected.",
                recommendation="Break content into clear paragraphs. Each paragraph should cover one main idea.",
                score=20
            ))
            return
        
        # Check average paragraph length
        avg_para_length = sum(len(p.split()) for p in paragraphs) / len(paragraphs)
        
        if avg_para_length > 100:
            self.checks.append(SEOCheck(
                name="Readability",
                status="warning",
                explanation=f"Average paragraph length is high ({avg_para_length:.0f} words). Long paragraphs reduce readability.",
                recommendation="Break long paragraphs into shorter ones (40-60 words ideal). Use bullet points and subheadings.",
                score=60
            ))
        else:
            self.checks.append(SEOCheck(
                name="Readability",
                status="pass",
                explanation="Paragraph structure supports good readability.",
                recommendation="Readability structure is good. Continue using short paragraphs, bullet points, and clear headings.",
                score=100
            ))
    
    def check_html_size(self):
        """Check HTML page size"""
        html_size_bytes = self.content.get('html_size', 0)
        html_size_kb = html_size_bytes / 1024
        
        if html_size_kb > config.SEO_THRESHOLDS['html_max_size_kb']:
            self.checks.append(SEOCheck(
                name="Page Size",
                status="warning",
                explanation=f"HTML size is {html_size_kb:.1f}KB. Large pages load slower.",
                recommendation="Optimize images, minify HTML/CSS/JS, and remove unnecessary elements to reduce page size.",
                score=60
            ))
        else:
            self.checks.append(SEOCheck(
                name="Page Size",
                status="pass",
                explanation=f"HTML size ({html_size_kb:.1f}KB) is reasonable.",
                recommendation="Page size is optimized. Continue monitoring as you add content.",
                score=100
            ))
    
    def check_keyword_density(self):
        """Check for keyword stuffing or over-optimization (basic heuristic)"""
        # Get all text content
        all_text = ' '.join(self.content.get('paragraphs', [])).lower()
        
        if not all_text:
            self.checks.append(SEOCheck(
                name="Keyword Balance",
                status="warning",
                explanation="Insufficient text content to evaluate keyword usage.",
                recommendation="Add more textual content with natural keyword usage.",
                score=50
            ))
            return
        
        # Simple check: Look for repeated 3-word phrases (potential keyword stuffing)
        words = re.findall(r'\b\w+\b', all_text)
        if len(words) < 50:
            self.checks.append(SEOCheck(
                name="Keyword Balance",
                status="pass",
                explanation="Content too short to evaluate keyword density.",
                recommendation="Focus on natural language and user value rather than keyword density.",
                score=100
            ))
            return
        
        # Check for repetitive phrases (simple heuristic)
        three_grams = [' '.join(words[i:i+3]) for i in range(len(words)-2)]
        if three_grams:
            max_repetition = max(three_grams.count(phrase) for phrase in set(three_grams))
            
            if max_repetition > 5:
                self.checks.append(SEOCheck(
                    name="Keyword Balance",
                    status="warning",
                    explanation=f"Detected repetitive phrases (up to {max_repetition} times). This may signal keyword stuffing.",
                    recommendation="Use natural language variations. Focus on semantic relevance rather than exact phrase repetition.",
                    score=60
                ))
            else:
                self.checks.append(SEOCheck(
                    name="Keyword Balance",
                    status="pass",
                    explanation="Keyword usage appears natural without over-optimization.",
                    recommendation="Continue using keywords naturally. Focus on topic coverage rather than density.",
                    score=100
                ))
        else:
            self.checks.append(SEOCheck(
                name="Keyword Balance",
                status="pass",
                explanation="Keyword usage appears balanced.",
                recommendation="Maintain natural keyword usage focused on user value.",
                score=100
            ))
    
    def check_images(self):
        """Check image optimization"""
        # Extract images from content (we'll need to get this from HTML)
        images_data = self.content.get('images', {})
        total_images = images_data.get('count', 0)
        missing_alt = images_data.get('missing_alt', 0)
        large_images = images_data.get('large_images', 0)
        
        if total_images == 0:
            self.checks.append(SEOCheck(
                name="Image Optimization",
                status="warning",
                explanation="No images detected on the page.",
                recommendation="Consider adding relevant images to enhance user experience and engagement.",
                score=70
            ))
            return
        
        if missing_alt == 0:
            self.checks.append(SEOCheck(
                name="Image Optimization",
                status="pass",
                explanation=f"All {total_images} images have alt text - excellent for accessibility and SEO.",
                recommendation="Continue adding descriptive alt text to all images.",
                score=100
            ))
        elif missing_alt < total_images / 2:
            self.checks.append(SEOCheck(
                name="Image Optimization",
                status="warning",
                explanation=f"{missing_alt} of {total_images} images are missing alt text.",
                recommendation="Add descriptive alt text to all images for accessibility and SEO. Describe what the image shows.",
                score=60
            ))
        else:
            self.checks.append(SEOCheck(
                name="Image Optimization",
                status="fail",
                explanation=f"{missing_alt} of {total_images} images are missing alt text (over 50%).",
                recommendation="Add alt text to all images. Use descriptive text that explains the image content.",
                score=30
            ))
    
    def check_open_graph(self):
        """Check Open Graph meta tags for social sharing"""
        og_data = self.content.get('open_graph', {})
        og_title = og_data.get('title')
        og_description = og_data.get('description')
        og_image = og_data.get('image')
        
        if og_title and og_description and og_image:
            self.checks.append(SEOCheck(
                name="Social Media (Open Graph)",
                status="pass",
                explanation="Open Graph tags are properly configured for social sharing.",
                recommendation="Ensure OG image is at least 1200x630px for best display on social platforms.",
                score=100
            ))
        elif og_title or og_description:
            self.checks.append(SEOCheck(
                name="Social Media (Open Graph)",
                status="warning",
                explanation="Some Open Graph tags present but incomplete.",
                recommendation="Add og:title, og:description, and og:image meta tags for better social media sharing.",
                score=60
            ))
        else:
            self.checks.append(SEOCheck(
                name="Social Media (Open Graph)",
                status="warning",
                explanation="No Open Graph tags found.",
                recommendation="Add Open Graph meta tags (og:title, og:description, og:image) to control how your page appears when shared on social media.",
                score=50
            ))
    
    def check_schema_markup(self):
        """Check for structured data (Schema.org)"""
        schema_data = self.content.get('schema_markup', {})
        has_schema = schema_data.get('found', False)
        schema_types = schema_data.get('types', [])
        
        if has_schema and schema_types:
            self.checks.append(SEOCheck(
                name="Structured Data (Schema)",
                status="pass",
                explanation=f"Schema markup detected: {', '.join(schema_types[:3])}.",
                recommendation="Validate your schema markup using Google's Rich Results Test tool.",
                score=100
            ))
        else:
            self.checks.append(SEOCheck(
                name="Structured Data (Schema)",
                status="warning",
                explanation="No structured data detected.",
                recommendation="Add Schema.org markup (JSON-LD) for better search result display. Consider Article, Organization, or FAQ schema based on your content type.",
                score=50
            ))
    
    def _generate_summary(self) -> Dict:
        """Generate summary statistics"""
        total_checks = len(self.checks)
        passed = sum(1 for c in self.checks if c.status == "pass")
        warnings = sum(1 for c in self.checks if c.status == "warning")
        failed = sum(1 for c in self.checks if c.status == "fail")
        
        return {
            'total_checks': total_checks,
            'passed': passed,
            'warnings': warnings,
            'failed': failed
        }
