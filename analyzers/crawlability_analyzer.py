"""
Crawlability Analysis Engine
Checks robots.txt, sitemap, and crawl accessibility
"""
from typing import Dict, List
import requests
from urllib.parse import urljoin, urlparse
import config


class CrawlabilityCheck:
    """Represents a single crawlability check result"""
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


class CrawlabilityAnalyzer:
    """Analyzes website crawlability and indexability"""
    
    def __init__(self, url: str):
        self.url = url
        parsed = urlparse(url)
        self.base_url = f"{parsed.scheme}://{parsed.netloc}"
        self.checks: List[CrawlabilityCheck] = []
    
    def analyze(self) -> Dict:
        """Run all crawlability checks"""
        self.checks = []
        
        self.check_robots_txt()
        self.check_sitemap()
        
        return {
            'checks': [check.to_dict() for check in self.checks],
            'summary': self._generate_summary()
        }
    
    def check_robots_txt(self):
        """Check robots.txt file"""
        robots_url = urljoin(self.base_url, '/robots.txt')
        
        try:
            response = requests.get(
                robots_url, 
                timeout=config.REQUEST_TIMEOUT,
                headers={'User-Agent': config.USER_AGENT}
            )
            
            if response.status_code == 404:
                self.checks.append(CrawlabilityCheck(
                    name="Robots.txt File",
                    status="warning",
                    explanation="No robots.txt file found. Not critical but recommended.",
                    recommendation="Create a robots.txt file to guide search engine crawlers. Include sitemap location.",
                    score=70
                ))
                return
            
            if response.status_code != 200:
                self.checks.append(CrawlabilityCheck(
                    name="Robots.txt File",
                    status="warning",
                    explanation=f"Robots.txt returned status {response.status_code}.",
                    recommendation="Ensure robots.txt is accessible with a 200 status code.",
                    score=60
                ))
                return
            
            robots_content = response.text.lower()
            
            # Check for blocking rules
            blocks_all = 'disallow: /' in robots_content and 'user-agent: *' in robots_content
            has_sitemap = 'sitemap:' in robots_content
            
            issues = []
            score = 100
            
            if blocks_all:
                # Check if there's an allow rule that overrides
                if 'allow:' not in robots_content:
                    self.checks.append(CrawlabilityCheck(
                        name="Robots.txt File",
                        status="fail",
                        explanation="Robots.txt blocks all crawlers with 'Disallow: /' - site won't be indexed!",
                        recommendation="CRITICAL: Remove or modify the 'Disallow: /' rule to allow search engines to crawl your site.",
                        score=0
                    ))
                    return
                else:
                    issues.append("Has 'Disallow: /' but also 'Allow' rules")
                    score = 70
            
            if not has_sitemap:
                issues.append("No sitemap reference found")
                score -= 15
            
            status = "pass" if score >= 80 else "warning"
            explanation = "Robots.txt configured correctly." if score >= 80 else \
                         f"Robots.txt issues: {', '.join(issues)}" if issues else "Robots.txt accessible."
            recommendation = "Add 'Sitemap:' directive to robots.txt" if not has_sitemap else \
                           "Robots.txt configuration looks good."
            
            self.checks.append(CrawlabilityCheck(
                name="Robots.txt File",
                status=status,
                explanation=explanation,
                recommendation=recommendation,
                score=score
            ))
        
        except requests.RequestException as e:
            self.checks.append(CrawlabilityCheck(
                name="Robots.txt File",
                status="warning",
                explanation=f"Could not fetch robots.txt: {str(e)}",
                recommendation="Ensure robots.txt is accessible and server is responding properly.",
                score=50
            ))
    
    def check_sitemap(self):
        """Check for XML sitemap"""
        # Try common sitemap locations
        sitemap_urls = [
            urljoin(self.base_url, '/sitemap.xml'),
            urljoin(self.base_url, '/sitemap_index.xml'),
            urljoin(self.base_url, '/sitemap1.xml'),
        ]
        
        sitemap_found = False
        sitemap_location = None
        
        for sitemap_url in sitemap_urls:
            try:
                response = requests.get(
                    sitemap_url,
                    timeout=config.REQUEST_TIMEOUT,
                    headers={'User-Agent': config.USER_AGENT}
                )
                
                if response.status_code == 200:
                    # Check if it's actually XML
                    content_type = response.headers.get('content-type', '').lower()
                    is_xml = 'xml' in content_type or response.text.strip().startswith('<?xml')
                    
                    if is_xml:
                        sitemap_found = True
                        sitemap_location = sitemap_url
                        break
            except requests.RequestException:
                continue
        
        if sitemap_found:
            # Basic sitemap validation
            try:
                sitemap_content = response.text
                has_urlset = '<urlset' in sitemap_content or '<sitemapindex' in sitemap_content
                has_urls = '<loc>' in sitemap_content
                
                if has_urlset and has_urls:
                    self.checks.append(CrawlabilityCheck(
                        name="XML Sitemap",
                        status="pass",
                        explanation=f"XML sitemap found at {sitemap_location} with valid structure.",
                        recommendation="Ensure sitemap is regularly updated and submitted to Google Search Console.",
                        score=100
                    ))
                else:
                    self.checks.append(CrawlabilityCheck(
                        name="XML Sitemap",
                        status="warning",
                        explanation=f"Sitemap found but may be malformed (missing urlset or URLs).",
                        recommendation="Validate sitemap structure using Google Search Console or XML validators.",
                        score=70
                    ))
            except Exception:
                self.checks.append(CrawlabilityCheck(
                    name="XML Sitemap",
                    status="warning",
                    explanation="Sitemap found but could not be validated.",
                    recommendation="Check sitemap XML structure for errors.",
                    score=70
                ))
        else:
            self.checks.append(CrawlabilityCheck(
                name="XML Sitemap",
                status="warning",
                explanation="No XML sitemap found at common locations (sitemap.xml, sitemap_index.xml).",
                recommendation="Create an XML sitemap and submit it to search engines via Google Search Console and Bing Webmaster Tools.",
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
