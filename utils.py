"""
Error handling and validation utilities
"""
from typing import Optional
from urllib.parse import urlparse
import re


class ValidationError(Exception):
    """Custom validation error"""
    pass


class URLValidator:
    """Validates and normalizes URLs"""
    
    @staticmethod
    def validate(url: str) -> str:
        """
        Validate URL and return normalized version
        Raises ValidationError if invalid
        """
        if not url:
            raise ValidationError("URL cannot be empty")
        
        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Parse URL
        try:
            parsed = urlparse(url)
        except Exception:
            raise ValidationError("Invalid URL format")
        
        # Check scheme
        if parsed.scheme not in ('http', 'https'):
            raise ValidationError("URL must use HTTP or HTTPS protocol")
        
        # Check domain
        if not parsed.netloc:
            raise ValidationError("URL must have a valid domain")
        
        # Check for localhost/private IPs (optional security measure)
        # Commented out for local testing - uncomment in production
        # if URLValidator._is_private_url(parsed.netloc):
        #     raise ValidationError("Cannot analyze localhost or private network URLs")
        
        return url
    
    @staticmethod
    def _is_private_url(netloc: str) -> bool:
        """Check if URL points to localhost or private network"""
        private_patterns = [
            r'^localhost',
            r'^127\.',
            r'^192\.168\.',
            r'^10\.',
            r'^172\.(1[6-9]|2[0-9]|3[0-1])\.',
            r'^0\.0\.0\.0',
        ]
        
        netloc_lower = netloc.lower().split(':')[0]  # Remove port
        
        for pattern in private_patterns:
            if re.match(pattern, netloc_lower):
                return True
        
        return False


class ContentValidator:
    """Validates extracted content"""
    
    @staticmethod
    def has_minimum_content(content: dict) -> tuple[bool, Optional[str]]:
        """
        Check if content meets minimum requirements
        Returns (is_valid, error_message)
        """
        if not content:
            return False, "No content could be extracted from the page"
        
        # Check for basic HTML elements
        if not content.get('title') and not content.get('paragraphs'):
            return False, "Page appears to be empty or could not be parsed"
        
        # Check word count
        word_count = content.get('word_count', 0)
        if word_count < 50:
            return False, f"Page has insufficient content ({word_count} words). Minimum 50 words required."
        
        return True, None
    
    @staticmethod
    def detect_unsupported_content(content: dict) -> Optional[str]:
        """
        Detect if page is a type we can't properly analyze
        Returns error message if unsupported, None otherwise
        """
        title = content.get('title', '').lower()
        
        # Check for common unsupported page types
        unsupported_indicators = {
            'Page Not Found': 'This appears to be a 404 error page',
            '404': 'This appears to be a 404 error page',
            'Access Denied': 'Access to this page was denied',
            'Login': 'This appears to be a login page',
            'Sign In': 'This appears to be a login page',
            'Maintenance': 'This page appears to be under maintenance',
        }
        
        for indicator, message in unsupported_indicators.items():
            if indicator.lower() in title:
                return message
        
        return None


def handle_crawl_errors(error: Exception) -> str:
    """
    Convert crawling errors to user-friendly messages
    """
    error_str = str(error).lower()
    
    if 'timeout' in error_str:
        return "The website took too long to respond. Please try again or check if the site is accessible."
    
    if 'connection' in error_str or 'refused' in error_str:
        return "Could not connect to the website. Please check the URL and try again."
    
    if 'ssl' in error_str or 'certificate' in error_str:
        return "SSL certificate error. The website may have security issues."
    
    if '404' in error_str:
        return "Page not found (404). Please check the URL."
    
    if '403' in error_str or 'forbidden' in error_str:
        return "Access forbidden (403). The website is blocking automated access."
    
    if '500' in error_str or '502' in error_str or '503' in error_str:
        return "The website is experiencing server errors. Please try again later."
    
    if 'too large' in error_str:
        return "The page is too large to analyze. Maximum size is 5MB."
    
    # Generic error
    return f"Failed to analyze website: {str(error)}"


def handle_ai_errors(error: Exception, feature: str) -> str:
    """
    Convert AI errors to user-friendly messages
    """
    error_str = str(error).lower()
    
    if 'api key' in error_str or 'authentication' in error_str:
        return f"AI feature unavailable: API key not configured. {feature} will be skipped."
    
    if 'rate limit' in error_str:
        return f"AI rate limit reached. {feature} temporarily unavailable."
    
    if 'timeout' in error_str:
        return f"AI service timed out. {feature} will be skipped."
    
    # Non-critical AI errors should not fail the analysis
    return f"AI enhancement unavailable for {feature}. Analysis continues with rule-based results."
