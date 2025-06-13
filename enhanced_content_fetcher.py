# enhanced_content_fetcher.py - Smart article content extraction
import requests
from bs4 import BeautifulSoup
import time
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse
import json

class SmartContentFetcher:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
    
    def find_actual_article_urls(self, base_url: str, source_name: str) -> List[Dict[str, str]]:
        """
        Find actual article URLs from the main page instead of category links
        """
        try:
            print(f"🔍 Finding actual article URLs for {source_name}")
            
            response = self.session.get(base_url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Site-specific URL extraction strategies
            if 'artificialintelligence-news' in base_url:
                return self._extract_ai_news_urls(soup, base_url)
            elif 'kdnuggets' in base_url:
                return self._extract_kdnuggets_urls(soup, base_url)
            elif 'thenewstack' in base_url:
                return self._extract_newstack_urls(soup, base_url)
            else:
                return self._extract_generic_urls(soup, base_url)
                
        except Exception as e:
            print(f"❌ Error finding URLs for {source_name}: {e}")
            return []
    
    def _extract_ai_news_urls(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Extract actual article URLs from AI News homepage"""
        articles = []
        
        # Look for article links - AI News specific patterns
        selectors = [
            'article a[href]',
            '.post-title a[href]',
            '.entry-title a[href]',
            'h2 a[href]',
            'h3 a[href]',
            '.news-item a[href]',
            'a[href*="/news/"]',
            'a[href*="/article/"]',
            'a[href*="/2025/"]',
            'a[href*="/2024/"]'
        ]
        
        seen_urls = set()
        
        for selector in selectors:
            links = soup.select(selector)
            
            for link in links:
                href = link.get('href', '')
                title = link.get_text(strip=True)
                
                # Make URL absolute
                if href.startswith('/'):
                    full_url = urljoin(base_url, href)
                else:
                    full_url = href
                
                # Filter for actual articles (not categories)
                if (full_url and 
                    full_url not in seen_urls and
                    title and len(title) > 15 and
                    not any(skip in full_url.lower() for skip in ['/categories/', '/tags/', '/about', '/contact', 'javascript:', '#']) and
                    any(pattern in full_url.lower() for pattern in ['/news/', '/article/', '/2025/', '/2024/', full_url.count('/') >= 4])):
                    
                    articles.append({
                        'title': title,
                        'url': full_url
                    })
                    seen_urls.add(full_url)
                    
                    if len(articles) >= 15:  # Limit to 15 articles
                        break
            
            if len(articles) >= 15:
                break
        
        print(f"   Found {len(articles)} actual article URLs")
        return articles
    
    def _extract_kdnuggets_urls(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Extract actual article URLs from KDNuggets"""
        articles = []
        
        selectors = [
            'article a[href*="/"]',
            '.post-title a[href]',
            'h2 a[href]',
            'h3 a[href]',
            'a[href*="/2025/"]',
            'a[href*="/2024/"]'
        ]
        
        seen_urls = set()
        
        for selector in selectors:
            links = soup.select(selector)
            
            for link in links:
                href = link.get('href', '')
                title = link.get_text(strip=True)
                
                if href.startswith('/'):
                    full_url = 'https://www.kdnuggets.com' + href
                else:
                    full_url = href
                
                if (full_url and 
                    full_url not in seen_urls and
                    title and len(title) > 15 and
                    'kdnuggets.com' in full_url and
                    not any(skip in full_url.lower() for skip in ['/tag/', '/category/', '/about', 'javascript:', '#'])):
                    
                    articles.append({
                        'title': title,
                        'url': full_url
                    })
                    seen_urls.add(full_url)
                    
                    if len(articles) >= 15:
                        break
            
            if len(articles) >= 15:
                break
        
        return articles
    
    def _extract_newstack_urls(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Extract actual article URLs from The New Stack"""
        articles = []
        
        selectors = [
            'article a[href]',
            '.story-title a[href]',
            'h2 a[href]',
            'h3 a[href]'
        ]
        
        seen_urls = set()
        
        for selector in selectors:
            links = soup.select(selector)
            
            for link in links:
                href = link.get('href', '')
                title = link.get_text(strip=True)
                
                if href.startswith('/'):
                    full_url = 'https://thenewstack.io' + href
                else:
                    full_url = href
                
                if (full_url and 
                    full_url not in seen_urls and
                    title and len(title) > 15 and
                    'thenewstack.io' in full_url):
                    
                    articles.append({
                        'title': title,
                        'url': full_url
                    })
                    seen_urls.add(full_url)
                    
                    if len(articles) >= 15:
                        break
            
            if len(articles) >= 15:
                break
        
        return articles
    
    def _extract_generic_urls(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Generic URL extraction"""
        articles = []
        
        # Look for article-like links
        links = soup.find_all('a', href=True)
        seen_urls = set()
        
        for link in links:
            href = link.get('href', '')
            title = link.get_text(strip=True)
            
            if href.startswith('/'):
                full_url = urljoin(base_url, href)
            else:
                full_url = href
            
            # Basic filtering for article-like URLs
            if (full_url and 
                full_url not in seen_urls and
                title and len(title) > 15 and
                urlparse(full_url).netloc == urlparse(base_url).netloc and
                not any(skip in full_url.lower() for skip in ['/category', '/tag', '/about', 'javascript:', '#'])):
                
                articles.append({
                    'title': title,
                    'url': full_url
                })
                seen_urls.add(full_url)
                
                if len(articles) >= 15:
                    break
        
        return articles
    
    def extract_full_article_content(self, url: str, title: str = "") -> Dict[str, Any]:
        """
        Extract complete article content from URL
        """
        if not url or url == "":
            return {
                'success': False,
                'error': 'No URL provided',
                'content': '',
                'summary': '',
                'title': title
            }
        
        try:
            print(f"📄 Fetching: {title[:50]}...")
            
            response = self.session.get(url, timeout=20)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'iframe', 'advertisement', 'sidebar', 'menu']):
                element.decompose()
            
            # Extract article content with multiple strategies
            content = self._extract_article_text(soup)
            
            # Extract proper title if not provided
            if not title:
                title = self._extract_title(soup)
            
            # Extract metadata
            author = self._extract_author(soup)
            date = self._extract_date(soup)
            
            # Generate summary from content
            summary = self._generate_summary(content)
            
            # Clean content
            content = self._clean_text(content)
            
            return {
                'success': True,
                'title': title,
                'content': content,
                'summary': summary,
                'author': author,
                'date': date,
                'url': url,
                'word_count': len(content.split()),
                'extracted_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error extracting from {url}: {e}")
            return {
                'success': False,
                'error': str(e),
                'content': '',
                'summary': '',
                'title': title,
                'url': url
            }
    
    def _extract_article_text(self, soup: BeautifulSoup) -> str:
        """Extract main article text using multiple strategies"""
        
        # Strategy 1: Common article selectors
        content_selectors = [
            'article',
            '.article-content',
            '.post-content',
            '.entry-content',
            '.content',
            '.main-content',
            'main',
            '.story-body',
            '.article-body',
            '.post-body'
        ]
        
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                text = content_elem.get_text(separator=' ', strip=True)
                if len(text) > 200:  # Substantial content
                    return text
        
        # Strategy 2: Largest text block
        all_text_elements = soup.find_all(['p', 'div'])
        text_blocks = []
        
        for elem in all_text_elements:
            text = elem.get_text(strip=True)
            if len(text) > 50:  # Filter short text
                text_blocks.append(text)
        
        # Join substantial text blocks
        full_text = ' '.join(text_blocks)
        
        if len(full_text) > 200:
            return full_text
        
        # Strategy 3: All paragraphs
        paragraphs = soup.find_all('p')
        para_text = ' '.join([p.get_text(strip=True) for p in paragraphs])
        
        return para_text if para_text else "No content extracted"
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract article title"""
        title_selectors = [
            'h1',
            '.article-title',
            '.post-title',
            '.entry-title',
            'title'
        ]
        
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                title = title_elem.get_text(strip=True)
                if len(title) > 10:
                    return title
        
        return "No title found"
    
    def _extract_author(self, soup: BeautifulSoup) -> str:
        """Extract article author"""
        author_selectors = [
            '.author',
            '.byline',
            '.post-author',
            '[rel="author"]',
            '.article-author'
        ]
        
        for selector in author_selectors:
            author_elem = soup.select_one(selector)
            if author_elem:
                return author_elem.get_text(strip=True)
        
        return ""
    
    def _extract_date(self, soup: BeautifulSoup) -> str:
        """Extract publication date"""
        date_selectors = [
            'time',
            '.date',
            '.published',
            '.post-date',
            '.article-date'
        ]
        
        for selector in date_selectors:
            date_elem = soup.select_one(selector)
            if date_elem:
                # Try datetime attribute first
                datetime_attr = date_elem.get('datetime')
                if datetime_attr:
                    return datetime_attr
                
                # Otherwise get text
                date_text = date_elem.get_text(strip=True)
                if date_text:
                    return date_text
        
        return ""
    
    def _generate_summary(self, content: str) -> str:
        """Generate a meaningful summary from content"""
        if not content or len(content) < 100:
            return "No summary available"
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', content)
        
        # Filter meaningful sentences
        good_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if (len(sentence) > 30 and 
                len(sentence.split()) > 5 and
                not sentence.lower().startswith(('click', 'subscribe', 'follow', 'read more'))):
                good_sentences.append(sentence)
        
        # Take first 2-3 sentences for summary
        summary_sentences = good_sentences[:3]
        summary = '. '.join(summary_sentences)
        
        # Limit summary length
        if len(summary) > 300:
            summary = summary[:300] + "..."
        
        return summary if summary else content[:300] + "..."
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove common noise
        noise_patterns = [
            r'Advertisement\s*',
            r'Subscribe to.*?newsletter',
            r'Follow us on.*?',
            r'Click here to.*?',
            r'Read more.*?'
        ]
        
        for pattern in noise_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        return text.strip()
    
    def enhance_articles_with_content(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Enhance articles by fetching actual content from URLs
        """
        enhanced_articles = []
        
        print(f"🔄 Enhancing {len(articles)} articles with full content...")
        
        for i, article in enumerate(articles, 1):
            print(f"Processing {i}/{len(articles)}: {article.get('title', 'No title')[:50]}...")
            
            url = article.get('url', '')
            title = article.get('title', '')
            
            # If no URL or bad URL, try to find better one
            if not url or url == "" or '/categories/' in url:
                print(f"   ⚠️ No good URL found, keeping original data")
                enhanced_articles.append(article)
                continue
            
            # Fetch full content
            content_data = self.extract_full_article_content(url, title)
            
            if content_data['success']:
                # Update article with real content
                article.update({
                    'title': content_data['title'] or article['title'],
                    'summary': content_data['summary'],
                    'content': content_data['content'][:2000],  # First 2000 chars
                    'author': content_data['author'],
                    'date': content_data['date'],
                    'word_count': content_data['word_count'],
                    'content_extracted': True
                })
                print(f"   ✅ Enhanced with {content_data['word_count']} words")
            else:
                # Keep original but mark as failed
                article['content_extracted'] = False
                article['extraction_error'] = content_data['error']
                print(f"   ❌ Failed: {content_data['error']}")
            
            enhanced_articles.append(article)
            
            # Small delay to be respectful
            time.sleep(1)
        
        successful = len([a for a in enhanced_articles if a.get('content_extracted')])
        print(f"✅ Enhanced {successful}/{len(articles)} articles with real content")
        
        return enhanced_articles
    
    def get_articles_with_real_content(self, source_configs: Dict[str, Dict]) -> List[Dict[str, Any]]:
        """
        Get articles with actual content instead of just titles and tags
        """
        all_articles = []
        
        for source_name, config in source_configs.items():
            if not config.get('enabled', True):
                continue
            
            print(f"\n🔍 Processing {source_name} for real content...")
            
            # Step 1: Find actual article URLs
            article_urls = self.find_actual_article_urls(config['url'], source_name)
            
            if not article_urls:
                print(f"   ❌ No article URLs found for {source_name}")
                continue
            
            # Step 2: Extract content from each URL
            for url_data in article_urls:
                content = self.extract_full_article_content(url_data['url'], url_data['title'])
                
                if content['success']:
                    article = {
                        'title': content['title'],
                        'summary': content['summary'],
                        'content': content['content'][:1500],  # Limit for processing
                        'url': content['url'],
                        'author': content['author'],
                        'date': content['date'],
                        'source': source_name,
                        'category': 'AI/ML',
                        'extracted_at': content['extracted_at'],
                        'extraction_method': 'enhanced_content',
                        'word_count': content['word_count']
                    }
                    all_articles.append(article)
                
                # Respectful delay
                time.sleep(1)
        
        print(f"\n📊 Total articles with real content: {len(all_articles)}")
        return all_articles

def test_content_fetcher():
    """Test the enhanced content fetcher"""
    print("🧪 Testing Enhanced Content Fetcher...")
    
    fetcher = SmartContentFetcher()
    
    # Test with AI News
    sources = {
        'ai_news': {
            'url': 'https://artificialintelligence-news.com/',
            'enabled': True
        }
    }
    
    articles = fetcher.get_articles_with_real_content(sources)
    
    if articles:
        print(f"\n✅ Successfully extracted {len(articles)} articles with real content!")
        
        # Show sample
        for i, article in enumerate(articles[:2], 1):
            print(f"\nSample {i}:")
            print(f"Title: {article['title']}")
            print(f"Summary: {article['summary'][:100]}...")
            print(f"Content length: {len(article.get('content', ''))} chars")
            print(f"Word count: {article.get('word_count', 0)}")
    else:
        print("❌ No articles extracted")

if __name__ == "__main__":
    test_content_fetcher()