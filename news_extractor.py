# news_extractor.py
import requests
from bs4 import BeautifulSoup
import feedparser
import json
from datetime import datetime
from typing import List, Dict, Any
import time
import random
from urllib.parse import urljoin, urlparse
import re

# Selenium imports with error handling
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
    
    # Try to import webdriver-manager for automatic driver management
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        WEBDRIVER_MANAGER_AVAILABLE = True
    except ImportError:
        WEBDRIVER_MANAGER_AVAILABLE = False
        print("⚠️ webdriver-manager not available. For automatic driver updates, install with: pip install webdriver-manager")
    
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    WEBDRIVER_MANAGER_AVAILABLE = False
    print("⚠️ Selenium is not available. Install with: pip install selenium webdriver-manager")

from config import Config
from enhanced_content_fetcher import SmartContentFetcher

class SeleniumExtractor:
    def __init__(self):
        """Initialize Selenium WebDriver with optimal settings"""
        if not SELENIUM_AVAILABLE:
            raise ImportError("Selenium is required but not installed")
        
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """Setup Chrome WebDriver with optimized options"""
        try:
            chrome_options = Options()
            
            # Performance optimizations
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--blink-settings=imagesEnabled=false')
            
            # User agent to avoid detection
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # Create service
            service = None
            if WEBDRIVER_MANAGER_AVAILABLE:
                try:
                    service = Service(ChromeDriverManager().install())
                    print("✅ Using webdriver-manager for automatic ChromeDriver management")
                except Exception as e:
                    print(f"⚠️ webdriver-manager failed: {e}. Trying system ChromeDriver.")
                    service = Service()
            else:
                service = Service()
                print("📋 Using system ChromeDriver. Install webdriver-manager for automatic management.")
            
            # Create driver
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.set_page_load_timeout(30)
            
            print("✅ Selenium WebDriver initialized successfully")
            
        except WebDriverException as e:
            print(f"❌ Failed to initialize Selenium WebDriver: {e}")
            print("💡 Troubleshooting: Ensure Chrome browser is installed and ChromeDriver is in your PATH or use webdriver-manager.")
            self.driver = None
        except Exception as e:
            print(f"❌ An unexpected error occurred during WebDriver setup: {e}")
            self.driver = None
    
    def get_page_source(self, url: str, wait_for_element: str = "body") -> str:
        """Get page source using Selenium"""
        if not self.driver:
            raise Exception("WebDriver not initialized")
        
        try:
            print(f"🌐 Loading page with Selenium: {url}")
            self.driver.get(url)
            
            # Wait for a general element to be present
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, wait_for_element))
            )
            
            # Additional wait for dynamic content to settle
            time.sleep(3)
            
            return self.driver.page_source
            
        except TimeoutException:
            print(f"⏰ Timeout waiting for page to load: {url}")
            return self.driver.page_source if self.driver else ""
        except Exception as e:
            print(f"❌ Error loading page with Selenium: {e}")
            return ""
    
    def extract_articles_with_selenium(self, url: str, source_name: str) -> List[Dict[str, Any]]:
        """Extract articles using a generalized Selenium approach"""
        if not self.driver:
            print("❌ Selenium driver not available")
            return []
        
        try:
            # Generic configurations that work for many news sites
            generic_config = {
                'wait_element': 'article, .post, .entry, main',
                'article_selectors': [
                    'article', '.post', '.entry', '.news-item', '.story-item',
                    'div[class*="post"]', 'div[class*="article"]'
                ],
                'title_selectors': ['h1', 'h2', 'h3', '.title', '.headline'],
                'link_selectors': ['a'],
                'summary_selectors': ['.excerpt', '.summary', 'p']
            }
            
            page_source = self.get_page_source(url, generic_config['wait_element'])
            if not page_source:
                return []
            
            soup = BeautifulSoup(page_source, 'html.parser')
            articles = []
            
            # Find all article containers
            article_containers = []
            for selector in generic_config['article_selectors']:
                containers = soup.select(selector)
                if containers:
                    article_containers = containers
                    print(f"✅ Found {len(containers)} potential articles using selector: '{selector}'")
                    break
            
            if not article_containers:
                print(f"⚠️ No article containers found for {source_name} using generic selectors.")
                return []
            
            # Extract data from each container
            for container in article_containers[:20]:  # Limit to 20 articles
                article_data = self._extract_article_data(
                    container, generic_config, source_name, url
                )
                if article_data:
                    articles.append(article_data)
            
            print(f"✅ Extracted {len(articles)} articles from {source_name} using Selenium")
            return articles
            
        except Exception as e:
            print(f"❌ Selenium extraction failed for {source_name}: {e}")
            return []
    
    def _extract_article_data(self, container: Any, config: Dict, source_name: str, base_url: str) -> Dict[str, Any]:
        """Extract data from a single article container using generic selectors"""
        title = ""
        for selector in config['title_selectors']:
            title_elem = container.select_one(selector)
            if title_elem and len(title_elem.get_text(strip=True)) > 10:
                title = title_elem.get_text(strip=True)
                break
        
        if not title:
            return None # Skip containers without a clear title

        url = ""
        link_elem = container.find('a', href=True)
        if link_elem:
            url = urljoin(base_url, link_elem['href'])

        summary = ""
        for selector in config['summary_selectors']:
            summary_elem = container.select_one(selector)
            if summary_elem:
                text = summary_elem.get_text(strip=True)
                if len(text) > 20: # Ensure summary is substantial
                    summary = text
                    break
        
        return {
            'title': title,
            'summary': summary[:300],
            'url': url,
            'source': source_name,
            'category': 'AI/ML',
            'extracted_at': datetime.now().isoformat(),
            'extraction_method': 'selenium'
        }
    
    def close(self):
        """Close the WebDriver"""
        if self.driver:
            try:
                self.driver.quit()
                print("✅ Selenium WebDriver closed")
            except Exception as e:
                print(f"⚠️ Error closing WebDriver: {e}")

class EnhancedNewsExtractor:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        self.content_fetcher = SmartContentFetcher()
        self.selenium_extractor = None
        if SELENIUM_AVAILABLE:
            try:
                self.selenium_extractor = SeleniumExtractor()
            except Exception as e:
                print(f"⚠️ Selenium initialization failed: {e}")
    
    def extract_from_rss(self, rss_url: str, source_name: str, limit: int = 15) -> List[Dict[str, Any]]:
        """Extract articles from RSS feeds"""
        try:
            print(f"📡 Trying RSS feed for {source_name}...")
            feed = feedparser.parse(rss_url)
            articles = []
            
            for entry in feed.entries[:limit]:
                articles.append({
                    'title': entry.title if hasattr(entry, 'title') else 'No title',
                    'summary': entry.summary[:300] if hasattr(entry, 'summary') else 'No summary',
                    'url': entry.link,
                    'date': entry.published if hasattr(entry, 'published') else '',
                    'source': source_name,
                    'category': 'AI/ML',
                    'extracted_at': datetime.now().isoformat(),
                    'extraction_method': 'rss_basic'
                })
            
            print(f"✅ RSS extraction successful: {len(articles)} articles")
            return articles
            
        except Exception as e:
            print(f"❌ RSS extraction failed for {source_name}: {str(e)}")
            return []

    def extract_from_website_basic(self, url: str, source_name: str) -> List[Dict[str, Any]]:
        """Extract articles using basic requests + BeautifulSoup (fallback)"""
        try:
            print(f"🌐 Trying basic web scraping for {source_name}...")
            time.sleep(random.uniform(1, 3))
            
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Use the SmartContentFetcher's URL finding logic on the static HTML
            url_data_list = self.content_fetcher.find_actual_article_urls(url, source_name)
            
            articles = [
                {
                    'title': data['title'],
                    'summary': '',
                    'url': data['url'],
                    'source': source_name,
                    'category': 'AI/ML',
                    'extracted_at': datetime.now().isoformat(),
                    'extraction_method': 'basic'
                } for data in url_data_list
            ]
            
            print(f"✅ Basic extraction successful: {len(articles)} articles found")
            return articles
            
        except Exception as e:
            print(f"❌ Basic web extraction failed for {source_name}: {str(e)}")
            return []

    def extract_from_website_selenium(self, url: str, source_name: str) -> List[Dict[str, Any]]:
        """Extract articles using Selenium for JavaScript-heavy sites"""
        if not self.selenium_extractor:
            print(f"⚠️ Selenium not available for {source_name}")
            return []
        
        print(f"🔧 Trying Selenium extraction for {source_name}...")
        return self.selenium_extractor.extract_articles_with_selenium(url, source_name)
    
    def extract_from_website(self, url: str, source_name: str) -> List[Dict[str, Any]]:
        """Extract with cascading fallback: RSS -> Basic (BS4) -> Selenium"""
        articles = []
        
        # Method 1: Try RSS if available
        rss_urls = {
            'kdnuggets': 'https://www.kdnuggets.com/feed',
            'the_new_stack': 'https://thenewstack.io/blog/ai/feed/',
        }
        if source_name in rss_urls:
            articles = self.extract_from_rss(rss_urls[source_name], source_name)
        
        # Method 2: Try basic web scraping if RSS fails or is not enough
        if len(articles) < 5:
            basic_articles = self.extract_from_website_basic(url, source_name)
            articles.extend(basic_articles)
        
        # Method 3: Try Selenium as a last resort if other methods yield few results
        if len(articles) < 5:
            print(f"🚨 Previous methods found few articles for {source_name}, trying Selenium...")
            selenium_articles = self.extract_from_website_selenium(url, source_name)
            articles.extend(selenium_articles)

        # Final step: Enhance all found articles with full content
        if articles:
            # First, deduplicate based on URL
            seen_urls = set()
            unique_articles = []
            for article in articles:
                if article.get('url') and article['url'] not in seen_urls:
                    seen_urls.add(article['url'])
                    unique_articles.append(article)
            
            print(f"🔄 Enhancing {len(unique_articles)} unique articles with full content...")
            articles = self.content_fetcher.enhance_articles_with_content(unique_articles)

        return articles

    def extract_multiple_sources(self) -> Dict[str, Any]:
        """Extract from multiple sources using the robust fallback mechanism"""
        sources = Config.get_enabled_sources()
        
        all_results = {}
        total_articles = 0
        
        print(f"\n🚀 Starting extraction from {len(sources)} enabled sources...")
        print(f"📋 Fallback Strategy: RSS → Basic HTML → Selenium")
        
        for source_name, source_config in sources.items():
            print(f"\n🔍 Processing {source_name}...")
            
            articles = self.extract_from_website(source_config['url'], source_name)
            
            # Remove duplicates by title after content enhancement
            seen_titles = set()
            unique_articles = []
            for article in articles:
                title_lower = article['title'].lower()
                if title_lower not in seen_titles and len(title_lower) > 15:
                    seen_titles.add(title_lower)
                    unique_articles.append(article)
            
            result = {
                'source': source_name,
                'url': source_config['url'],
                'articles': unique_articles,
                'article_count': len(unique_articles),
                'extracted_at': datetime.now().isoformat(),
                'success': len(unique_articles) > 0
            }
            
            all_results[source_name] = result
            total_articles += len(unique_articles)
            
            print(f"✅ Extracted {len(unique_articles)} unique, content-rich articles from {source_name}")
        
        print(f"\n📊 Final Extraction Summary:")
        print(f"Total articles extracted: {total_articles}")
        print(f"Sources processed: {len(sources)}")
        
        return all_results

    def close(self):
        """Clean up resources"""
        if self.selenium_extractor:
            self.selenium_extractor.close()
        self.session.close()

def test_enhanced_extractor():
    """Test the enhanced news extractor"""
    print("🧪 Testing Enhanced News Extractor...")
    
    extractor = EnhancedNewsExtractor()
    
    try:
        results = extractor.extract_multiple_sources()
        
        for source, result in results.items():
            if result['success']:
                print(f"\n📰 {source}: {result['article_count']} articles")
                for i, article in enumerate(result['articles'][:2], 1):
                    content_len = len(article.get('content', ''))
                    print(f"  {i}. {article['title'][:60]}... (Content: {content_len} chars)")
            else:
                print(f"\n❌ {source}: Failed")
        
        print("\n✅ Enhanced extractor test completed!")
        
    finally:
        extractor.close()

if __name__ == "__main__":
    test_enhanced_extractor()