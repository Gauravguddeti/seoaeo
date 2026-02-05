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
        self.check_https_security()
        self.check_mobile_friendly()
        self.check_canonical_tag()
        
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
        """Check content readability using Flesch-Kincaid scores"""
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
        
        # Combine paragraphs for analysis
        full_text = ' '.join(paragraphs)
        
        if len(full_text) < 100:
            self.checks.append(SEOCheck(
                name="Readability",
                status="fail",
                explanation="Not enough text content to analyze readability.",
                recommendation="Add more detailed content to provide value to readers.",
                score=20
            ))
            return
        
        try:
            import textstat
            
            # Calculate readability scores
            flesch_score = textstat.flesch_reading_ease(full_text)
            grade_level = textstat.flesch_kincaid_grade(full_text)
            
            # Flesch Reading Ease interpretation:
            # 60-69: Standard (8th-9th grade) - IDEAL FOR WEB
            # 50-59: Fairly Difficult (10th-12th grade)
            # 30-49: Difficult (College)
            
            if flesch_score >= 60:
                status = "pass"
                score = 100
                explanation = f"Content is readable (Flesch: {flesch_score:.1f}, Grade: {grade_level:.1f}). Good for web audiences."
                recommendation = "Readability is good. Keep sentences clear and use simple language where possible."
            elif flesch_score >= 40:
                status = "warning"
                score = 70
                explanation = f"Content is somewhat difficult (Flesch: {flesch_score:.1f}, Grade: {grade_level:.1f})."
                recommendation = "Consider simplifying language. Break long sentences, use active voice, and avoid jargon."
            else:
                status = "warning"
                score = 50
                explanation = f"Content is difficult to read (Flesch: {flesch_score:.1f}, Grade: {grade_level:.1f})."
                recommendation = "Simplify content significantly. Use shorter sentences, simpler words, and break complex ideas into digestible pieces."
            
            self.checks.append(SEOCheck(
                name="Readability",
                status=status,
                explanation=explanation,
                recommendation=recommendation,
                score=score
            ))
        
        except ImportError:
            # Fallback to basic readability check if textstat not available
            avg_para_length = sum(len(p.split()) for p in paragraphs) / len(paragraphs)
            
            if avg_para_length > 100:
                score = 60
                status = "warning"
                explanation = f"Average paragraph length is high ({avg_para_length:.0f} words). Long paragraphs reduce readability."
                recommendation = "Break long paragraphs into shorter ones (40-60 words ideal). Use bullet points and subheadings."
            else:
                score = 100
                status = "pass"
                explanation = "Paragraph structure supports good readability."
                recommendation = "Readability structure is good. Continue using short paragraphs, bullet points, and clear headings."
            
            self.checks.append(SEOCheck(
                name="Readability",
                status=status,
                explanation=explanation,
                recommendation=recommendation,
                score=score
            ))
        except Exception as e:
            # Error in calculation
            self.checks.append(SEOCheck(
                name="Readability",
                status="warning",
                explanation=f"Could not calculate readability: {str(e)[:50]}",
                recommendation="Ensure content has proper sentence structure for analysis.",
                score=60
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
        """Check for structured data (Schema.org) with validation"""
        html_raw = self.content.get('html_raw', '')
        url = self.content.get('url', '')
        
        # Use extruct to extract and validate structured data
        try:
            import extruct
            
            metadata = extruct.extract(
                html_raw,
                base_url=url,
                syntaxes=['json-ld', 'microdata', 'rdfa']
            )
            
            # Check JSON-LD
            json_ld_items = metadata.get('json-ld', [])
            # Check Microdata
            microdata_items = metadata.get('microdata', [])
            # Check RDFa
            rdfa_items = metadata.get('rdfa', [])
            
            total_items = len(json_ld_items) + len(microdata_items) + len(rdfa_items)
            
            if total_items == 0:
                self.checks.append(SEOCheck(
                    name="Structured Data (Schema)",
                    status="warning",
                    explanation="No structured data detected.",
                    recommendation="Add Schema.org markup (JSON-LD) for better search result display. Consider Article, Organization, or FAQ schema based on your content type.",
                    score=50
                ))
                return
            
            # Extract schema types
            schema_types = []
            validation_issues = []
            
            for item in json_ld_items:
                if isinstance(item, dict):
                    item_type = item.get('@type', 'Unknown')
                    schema_types.append(f"{item_type} (JSON-LD)")
                    
                    # Basic validation: check for required @context
                    if '@context' not in item:
                        validation_issues.append(f"{item_type} missing @context")
                    
                    # Check for common required fields based on type
                    if item_type == 'Article' and 'headline' not in item:
                        validation_issues.append("Article missing 'headline'")
                    if item_type == 'Organization' and 'name' not in item:
                        validation_issues.append("Organization missing 'name'")
            
            for item in microdata_items:
                if isinstance(item, dict):
                    item_type = item.get('type', 'Unknown')
                    schema_types.append(f"{item_type} (Microdata)")
            
            for item in rdfa_items:
                if isinstance(item, dict):
                    item_type = item.get('@type', 'Unknown')
                    schema_types.append(f"{item_type} (RDFa)")
            
            # Determine score and status
            if validation_issues:
                status = "warning"
                score = 75
                explanation = f"Structured data found but has issues: {', '.join(validation_issues[:2])}"
                recommendation = "Fix schema validation errors. Use Google's Rich Results Test to identify all issues."
            else:
                status = "pass"
                score = 100
                explanation = f"Valid structured data found: {', '.join(schema_types[:3])}"
                recommendation = "Structured data looks good. Keep it updated and test regularly with Google's Rich Results Test."
            
            self.checks.append(SEOCheck(
                name="Structured Data (Schema)",
                status=status,
                explanation=explanation,
                recommendation=recommendation,
                score=score
            ))
        
        except ImportError:
            # Fallback if extruct not available (shouldn't happen)
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
        except Exception as e:
            # If extraction fails, fall back to basic check
            self.checks.append(SEOCheck(
                name="Structured Data (Schema)",
                status="warning",
                explanation=f"Could not validate structured data: {str(e)[:50]}",
                recommendation="Check schema markup syntax and validate with Google's Rich Results Test.",
                score=60
            ))

    
    def check_https_security(self):
        """Check HTTPS and security headers"""
        url = self.content.get('url', '')
        headers = self.content.get('headers', {})
        html_raw = self.content.get('html_raw', '')
        
        is_https = url.startswith('https://')
        has_hsts = 'strict-transport-security' in headers
        has_xframe = 'x-frame-options' in headers
        has_csp = 'content-security-policy' in headers
        
        # Check for mixed content (http:// resources on https:// page)
        mixed_content = False
        if is_https and html_raw:
            # Look for http:// in src, href attributes (excluding comments)
            import re
            http_pattern = r'(?:src|href)=["\']http://[^"\']*["\']'
            mixed_content = bool(re.search(http_pattern, html_raw, re.IGNORECASE))
        
        security_score = 0
        issues = []
        recommendations = []
        
        if not is_https:
            status = "fail"
            issues.append("Site does not use HTTPS")
            recommendations.append("Migrate to HTTPS immediately - it's a confirmed ranking signal")
            security_score = 0
        else:
            security_score = 50  # Base score for HTTPS
            
            if has_hsts:
                security_score += 20
            else:
                issues.append("Missing HSTS header")
                recommendations.append("Add Strict-Transport-Security header to enforce HTTPS")
            
            if has_xframe:
                security_score += 15
            else:
                issues.append("Missing X-Frame-Options header")
                recommendations.append("Add X-Frame-Options header to prevent clickjacking")
            
            if has_csp:
                security_score += 15
            else:
                issues.append("Missing Content-Security-Policy header")
                recommendations.append("Add CSP header to enhance security")
            
            if mixed_content:
                security_score -= 30
                issues.append("Mixed content detected (HTTP resources on HTTPS page)")
                recommendations.append("Update all resources to use HTTPS to avoid browser warnings")
            
            if security_score >= 90:
                status = "pass"
            elif security_score >= 50:
                status = "warning"
            else:
                status = "fail"
        
        explanation = "HTTPS with all security headers configured correctly." if security_score >= 90 else \
                      f"Security issues: {', '.join(issues)}" if issues else "Partial security configuration."
        recommendation = recommendations[0] if recommendations else "Security headers are well configured."
        
        self.checks.append(SEOCheck(
            name="HTTPS & Security Headers",
            status=status,
            explanation=explanation,
            recommendation=recommendation,
            score=security_score
        ))
    
    def check_mobile_friendly(self):
        """Check mobile-friendliness indicators"""
        viewport = self.content.get('viewport', {})
        html_raw = self.content.get('html_raw', '')
        
        has_viewport = viewport.get('exists', False)
        has_width = viewport.get('has_width', False)
        viewport_content = viewport.get('content', '')
        
        # Check for responsive CSS frameworks
        responsive_indicators = [
            'bootstrap', 'foundation', 'tailwind', 'bulma',
            '@media', 'viewport', 'responsive', 'mobile-first'
        ]
        has_responsive_css = any(indicator in html_raw.lower() for indicator in responsive_indicators)
        
        mobile_score = 0
        issues = []
        
        if not has_viewport:
            status = "fail"
            issues.append("No viewport meta tag")
            mobile_score = 0
        else:
            mobile_score = 40
            
            if has_width:
                mobile_score += 30
            else:
                issues.append("Viewport tag missing 'width' attribute")
            
            if 'width=device-width' in viewport_content.lower():
                mobile_score += 15
            else:
                issues.append("Viewport should use 'width=device-width'")
            
            if 'initial-scale' in viewport_content.lower():
                mobile_score += 10
            
            if has_responsive_css:
                mobile_score += 5
            else:
                issues.append("No clear responsive design indicators")
        
        if mobile_score >= 80:
            status = "pass"
        elif mobile_score >= 40:
            status = "warning"
        else:
            status = "fail"
        
        explanation = "Mobile-friendly configuration detected." if mobile_score >= 80 else \
                      f"Mobile issues: {', '.join(issues)}" if issues else "Partial mobile optimization."
        recommendation = "Add viewport meta tag: <meta name='viewport' content='width=device-width, initial-scale=1.0'>" if not has_viewport else \
                        "Ensure responsive design with CSS media queries and mobile testing."
        
        self.checks.append(SEOCheck(
            name="Mobile-Friendliness",
            status=status,
            explanation=explanation,
            recommendation=recommendation,
            score=mobile_score
        ))
    
    def check_canonical_tag(self):
        """Check for canonical URL tag"""
        # Note: Need to add canonical extraction to crawler
        # For now, check if it exists in raw HTML
        html_raw = self.content.get('html_raw', '')
        
        import re
        canonical_pattern = r'<link[^>]*rel=["\']canonical["\'][^>]*>'
        has_canonical = bool(re.search(canonical_pattern, html_raw, re.IGNORECASE))
        
        if has_canonical:
            self.checks.append(SEOCheck(
                name="Canonical Tag",
                status="pass",
                explanation="Canonical tag is present to prevent duplicate content issues.",
                recommendation="Ensure canonical URL points to the preferred version of this page.",
                score=100
            ))
        else:
            self.checks.append(SEOCheck(
                name="Canonical Tag",
                status="warning",
                explanation="No canonical tag found.",
                recommendation="Add a canonical link tag to specify the preferred URL version and prevent duplicate content penalties.",
                score=60
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
