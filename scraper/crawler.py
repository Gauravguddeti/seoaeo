"""
Web scraping module for extracting content from websites
"""
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse
import re
import config


class WebCrawler:
    """Crawls and extracts content from web pages"""
    
    def __init__(self, url: str):
        self.url = url
        self.base_domain = urlparse(url).netloc
        
    def fetch_page(self, url: str) -> Optional[requests.Response]:
        """Fetch a single page with proper headers and timeout"""
        try:
            headers = {
                'User-Agent': config.USER_AGENT,
                'Accept': 'text/html,application/xhtml+xml',
                'Accept-Language': 'en-US,en;q=0.9',
            }
            response = requests.get(
                url,
                headers=headers,
                timeout=config.REQUEST_TIMEOUT,
                allow_redirects=True
            )
            response.raise_for_status()
            
            # Check content length
            if len(response.content) > config.MAX_CONTENT_LENGTH:
                raise ValueError(f"Page too large: {len(response.content)} bytes")
            
            return response
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch {url}: {str(e)}")
    
    def extract_content(self, html: str, url: str) -> Dict:
        """Extract all relevant content from HTML"""
        soup = BeautifulSoup(html, 'lxml')
        
        # Remove script and style elements
        for element in soup(['script', 'style', 'nav', 'footer', 'header']):
            element.decompose()
        
        content = {
            'url': url,
            'title': self._extract_title(soup),
            'meta_description': self._extract_meta_description(soup),
            'headings': self._extract_headings(soup),
            'paragraphs': self._extract_paragraphs(soup),
            'lists': self._extract_lists(soup),
            'tables': self._extract_tables(soup),
            'faqs': self._extract_faqs(soup),
            'links': self._extract_links(soup, url),
            'html_size': len(html),
            'word_count': self._count_words(soup),
            'images': self._extract_images(soup),
            'open_graph': self._extract_open_graph(soup),
            'schema_markup': self._extract_schema(soup),
        }
        
        return content
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title"""
        title_tag = soup.find('title')
        return title_tag.get_text(strip=True) if title_tag else ""
    
    def _extract_meta_description(self, soup: BeautifulSoup) -> str:
        """Extract meta description"""
        meta = soup.find('meta', attrs={'name': 'description'})
        if not meta:
            meta = soup.find('meta', attrs={'property': 'og:description'})
        return meta.get('content', '').strip() if meta else ""
    
    def _extract_headings(self, soup: BeautifulSoup) -> Dict[str, List[str]]:
        """Extract all headings H1-H4"""
        headings = {
            'h1': [h.get_text(strip=True) for h in soup.find_all('h1')],
            'h2': [h.get_text(strip=True) for h in soup.find_all('h2')],
            'h3': [h.get_text(strip=True) for h in soup.find_all('h3')],
            'h4': [h.get_text(strip=True) for h in soup.find_all('h4')],
        }
        return headings
    
    def _extract_paragraphs(self, soup: BeautifulSoup) -> List[str]:
        """Extract all paragraph text"""
        paragraphs = []
        for p in soup.find_all('p'):
            text = p.get_text(strip=True)
            if len(text) > 20:  # Filter out very short paragraphs
                paragraphs.append(text)
        return paragraphs
    
    def _extract_lists(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract ordered and unordered lists"""
        lists = []
        for list_tag in soup.find_all(['ul', 'ol']):
            items = [li.get_text(strip=True) for li in list_tag.find_all('li', recursive=False)]
            if items:
                lists.append({
                    'type': list_tag.name,
                    'items': items
                })
        return lists
    
    def _extract_tables(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract table data"""
        tables = []
        for table in soup.find_all('table'):
            rows = []
            for tr in table.find_all('tr'):
                cells = [td.get_text(strip=True) for td in tr.find_all(['td', 'th'])]
                if cells:
                    rows.append(cells)
            if rows:
                tables.append({'rows': rows})
        return tables
    
    def _extract_faqs(self, soup: BeautifulSoup) -> List[Dict]:
        """Detect FAQ sections using various patterns"""
        faqs = []
        
        # Method 1: Look for FAQ schema markup
        faq_schemas = soup.find_all('div', attrs={'itemtype': re.compile(r'FAQPage|Question')})
        for schema in faq_schemas:
            question = schema.find(attrs={'itemprop': 'name'})
            answer = schema.find(attrs={'itemprop': 'text'})
            if question and answer:
                faqs.append({
                    'question': question.get_text(strip=True),
                    'answer': answer.get_text(strip=True)
                })
        
        # Method 2: Look for question headings followed by content
        for heading in soup.find_all(['h2', 'h3', 'h4']):
            heading_text = heading.get_text(strip=True)
            # Check if heading looks like a question
            if any(keyword in heading_text.lower() for keyword in ['?', 'what', 'how', 'why', 'when', 'where', 'who']):
                # Get next sibling content
                next_elem = heading.find_next_sibling(['p', 'div'])
                if next_elem:
                    faqs.append({
                        'question': heading_text,
                        'answer': next_elem.get_text(strip=True)
                    })
        
        return faqs
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> Dict:
        """Count internal and external links"""
        internal_links = []
        external_links = []
        
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            if not href or href.startswith('#') or href.startswith('javascript:'):
                continue
            
            absolute_url = urljoin(base_url, href)
            parsed = urlparse(absolute_url)
            
            if parsed.netloc == self.base_domain or not parsed.netloc:
                internal_links.append(absolute_url)
            else:
                external_links.append(absolute_url)
        
        return {
            'internal': list(set(internal_links)),
            'external': list(set(external_links)),
            'internal_count': len(set(internal_links)),
            'external_count': len(set(external_links)),
        }
    
    def _count_words(self, soup: BeautifulSoup) -> int:
        """Count total words in main content"""
        text = soup.get_text(separator=' ', strip=True)
        words = re.findall(r'\b\w+\b', text)
        return len(words)
    
    def _extract_images(self, soup: BeautifulSoup) -> Dict:
        """Extract image information"""
        images = soup.find_all('img')
        missing_alt = 0
        large_images = 0
        
        for img in images:
            if not img.get('alt'):
                missing_alt += 1
            # Note: Can't check actual file size without downloading
            # but we can warn about large dimensions
            width = img.get('width')
            if width and str(width).isdigit() and int(width) > 2000:
                large_images += 1
        
        return {
            'count': len(images),
            'missing_alt': missing_alt,
            'large_images': large_images,
            'has_lazy_loading': any(img.get('loading') == 'lazy' for img in images)
        }
    
    def _extract_open_graph(self, soup: BeautifulSoup) -> Dict:
        """Extract Open Graph meta tags"""
        og_data = {}
        
        og_title = soup.find('meta', property='og:title')
        og_desc = soup.find('meta', property='og:description')
        og_image = soup.find('meta', property='og:image')
        og_url = soup.find('meta', property='og:url')
        
        if og_title:
            og_data['title'] = og_title.get('content', '')
        if og_desc:
            og_data['description'] = og_desc.get('content', '')
        if og_image:
            og_data['image'] = og_image.get('content', '')
        if og_url:
            og_data['url'] = og_url.get('content', '')
        
        return og_data
    
    def _extract_schema(self, soup: BeautifulSoup) -> Dict:
        """Extract Schema.org structured data"""
        schema_scripts = soup.find_all('script', type='application/ld+json')
        
        if not schema_scripts:
            return {'found': False, 'types': []}
        
        schema_types = []
        for script in schema_scripts:
            try:
                import json
                data = json.loads(script.string)
                if isinstance(data, dict) and '@type' in data:
                    schema_types.append(data['@type'])
                elif isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and '@type' in item:
                            schema_types.append(item['@type'])
            except:
                pass
        
        return {
            'found': len(schema_scripts) > 0,
            'types': list(set(schema_types))
        }
    
    def find_content_page(self, soup: BeautifulSoup, homepage_url: str) -> Optional[str]:
        """Find the most promising content page to analyze"""
        # Look for blog posts, articles, or pages with substantial content
        candidates = []
        
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            if not href:
                continue
            
            absolute_url = urljoin(homepage_url, href)
            parsed = urlparse(absolute_url)
            
            # Must be same domain
            if parsed.netloc != self.base_domain:
                continue
            
            # Look for content indicators in URL
            content_indicators = ['blog', 'article', 'post', 'guide', 'tutorial', 'about', 'product']
            path_lower = parsed.path.lower()
            
            score = sum(indicator in path_lower for indicator in content_indicators)
            
            # Avoid navigation pages
            if any(x in path_lower for x in ['category', 'tag', 'archive', 'login', 'cart']):
                continue
            
            if score > 0 or len(parsed.path.split('/')) > 2:
                candidates.append((absolute_url, score))
        
        # Return highest scoring candidate
        if candidates:
            candidates.sort(key=lambda x: x[1], reverse=True)
            return candidates[0][0]
        
        return None
    
    def crawl(self) -> List[Dict]:
        """Crawl homepage and one content page"""
        pages = []
        
        # Crawl homepage
        try:
            response = self.fetch_page(self.url)
            content = self.extract_content(response.text, self.url)
            pages.append(content)
            
            # Find and crawl one content page
            soup = BeautifulSoup(response.text, 'lxml')
            content_url = self.find_content_page(soup, self.url)
            
            if content_url and content_url != self.url:
                try:
                    content_response = self.fetch_page(content_url)
                    content_page = self.extract_content(content_response.text, content_url)
                    pages.append(content_page)
                except Exception as e:
                    # If content page fails, continue with just homepage
                    print(f"Failed to fetch content page: {e}")
        
        except Exception as e:
            raise Exception(f"Crawling failed: {str(e)}")
        
        return pages
