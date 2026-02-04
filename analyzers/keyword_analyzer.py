"""
Keyword Analysis Module
Extracts and suggests keywords for better optimization
"""
from typing import Dict, List
from collections import Counter
import re


class KeywordAnalyzer:
    """Analyzes content for keyword usage and suggestions"""
    
    # Common stop words to ignore
    STOP_WORDS = {
        'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
        'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
        'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
        'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their',
        'what', 'so', 'up', 'out', 'if', 'about', 'who', 'get', 'which', 'go',
        'me', 'when', 'make', 'can', 'like', 'time', 'no', 'just', 'him', 'know',
        'take', 'people', 'into', 'year', 'your', 'good', 'some', 'could', 'them',
        'see', 'other', 'than', 'then', 'now', 'look', 'only', 'come', 'its', 'over',
        'think', 'also', 'back', 'after', 'use', 'two', 'how', 'our', 'work',
        'first', 'well', 'way', 'even', 'new', 'want', 'because', 'any', 'these',
        'give', 'day', 'most', 'us', 'is', 'was', 'are', 'been', 'has', 'had',
        'were', 'said', 'did', 'having', 'may', 'should', 'am', 'being', 'here',
        'more', 'through', 'very', 'much', 'where', 'too'
    }
    
    def __init__(self, content: Dict):
        self.content = content
    
    def analyze(self) -> Dict:
        """Analyze keywords in content"""
        # Extract text from various sources
        title = self.content.get('title', '')
        meta = self.content.get('meta_description', '')
        h1s = ' '.join(self.content.get('headings', {}).get('h1', []))
        h2s = ' '.join(self.content.get('headings', {}).get('h2', []))
        paragraphs = ' '.join(self.content.get('paragraphs', []))
        
        # Extract keywords
        all_keywords = self._extract_keywords(paragraphs)
        title_keywords = self._extract_keywords(title)
        h1_keywords = self._extract_keywords(h1s)
        
        # Get top keywords
        top_keywords = [word for word, count in all_keywords.most_common(10)]
        
        # Check keyword placement
        keyword_placement = self._check_keyword_placement(
            top_keywords[:3], title, h1s, paragraphs
        )
        
        # Suggest related keywords
        suggested_keywords = self._suggest_keywords(top_keywords, all_keywords)
        
        return {
            'top_keywords': top_keywords,
            'keyword_placement': keyword_placement,
            'suggested_keywords': suggested_keywords,
            'primary_focus': self._identify_primary_focus(all_keywords, title_keywords)
        }
    
    def _extract_keywords(self, text: str) -> Counter:
        """Extract keywords from text"""
        # Convert to lowercase
        text = text.lower()
        
        # Extract words (alphanumeric + hyphens)
        words = re.findall(r'\b[a-z]+(?:-[a-z]+)?\b', text)
        
        # Filter stop words and short words
        keywords = [w for w in words if w not in self.STOP_WORDS and len(w) > 3]
        
        return Counter(keywords)
    
    def _check_keyword_placement(self, top_keywords: List[str], title: str, h1: str, first_para: str) -> Dict:
        """Check if top keywords are in important locations"""
        placement = {}
        
        for keyword in top_keywords:
            placement[keyword] = {
                'in_title': keyword.lower() in title.lower(),
                'in_h1': keyword.lower() in h1.lower(),
                'in_first_paragraph': keyword.lower() in first_para[:500].lower()
            }
        
        return placement
    
    def _suggest_keywords(self, top_keywords: List[str], all_keywords: Counter) -> List[str]:
        """Suggest related keywords that could be added"""
        # Find medium-frequency keywords (mentioned but not in top 10)
        suggested = []
        
        for word, count in all_keywords.most_common(30):
            if word not in top_keywords[:10] and count >= 2:
                suggested.append(word)
        
        return suggested[:10]
    
    def _identify_primary_focus(self, all_keywords: Counter, title_keywords: Counter) -> str:
        """Identify the primary focus keyword"""
        # Keywords in title that also appear frequently in content
        common = set(title_keywords.keys()) & set(all_keywords.keys())
        
        if common:
            # Return the most frequent one that's also in title
            for word, _ in all_keywords.most_common():
                if word in common:
                    return word
        
        # Fallback to most common keyword
        if all_keywords:
            return all_keywords.most_common(1)[0][0]
        
        return "unknown"
