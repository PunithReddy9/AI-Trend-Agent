# utils.py
"""
Enhanced Utility functions for AI News Aggregation Pipeline with Selenium support
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import requests

def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """Setup logging configuration"""
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Create logger
    logger = logging.getLogger("ai_news_pipeline")
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # File handler
    file_handler = logging.FileHandler(
        f"logs/pipeline_{datetime.now().strftime('%Y%m%d')}.log"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

def save_json(data: Any, filename: str, directory: str = "data") -> str:
    """Save data to JSON file"""
    os.makedirs(directory, exist_ok=True)
    filepath = os.path.join(directory, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return filepath

def load_json(filepath: str) -> Optional[Any]:
    """Load data from JSON file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ File not found: {filepath}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Error decoding JSON: {e}")
        return None

def clean_text(text: str) -> str:
    """Clean and normalize text content"""
    if not text:
        return ""
    
    # Remove extra whitespace and normalize
    cleaned = str(text).strip()
    cleaned = cleaned.replace('\n', ' ').replace('\r', '')
    cleaned = ' '.join(cleaned.split())  # Remove multiple spaces
    
    return cleaned

def validate_article(article: Dict[str, Any]) -> bool:
    """Validate if article has required fields"""
    required_fields = ['title']
    optional_fields = ['summary', 'url', 'source', 'date']
    
    # Check required fields
    for field in required_fields:
        if not article.get(field):
            return False
    
    # Clean text fields
    for field in required_fields + optional_fields:
        if field in article and isinstance(article[field], str):
            article[field] = clean_text(article[field])
    
    return True

def deduplicate_articles(articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Remove duplicate articles based on title similarity"""
    unique_articles = []
    seen_titles = set()
    
    for article in articles:
        title = article.get('title', '').lower().strip()
        
        # Simple deduplication based on title
        if title and title not in seen_titles:
            seen_titles.add(title)
            unique_articles.append(article)
    
    print(f"🔄 Deduplication: {len(articles)} → {len(unique_articles)} articles")
    return unique_articles

def calculate_relevance_score(article: Dict[str, Any], keywords: List[str]) -> float:
    """Calculate relevance score based on keyword presence"""
    text = f"{article.get('title', '')} {article.get('summary', '')}".lower()
    
    matches = 0
    total_keywords = len(keywords)
    
    for keyword in keywords:
        if keyword.lower() in text:
            matches += 1
    
    return matches / total_keywords if total_keywords > 0 else 0.0

def format_article_for_display(article: Dict[str, Any]) -> str:
    """Format article for console display"""
    title = article.get('title', 'No title')
    source = article.get('source', 'Unknown source')
    score = article.get('final_score', 'N/A')
    summary = article.get('summary', 'No summary')
    method = article.get('extraction_method', 'unknown')
    
    return f"""
📰 {title}
   Source: {source} | Score: {score} | Method: {method}
   Summary: {summary[:100]}{'...' if len(summary) > 100 else ''}
   URL: {article.get('url', 'No URL')}
"""

def check_selenium_installation() -> Dict[str, Any]:
    """Check Selenium installation and browser availability"""
    selenium_status = {
        'selenium_installed': False,
        'webdriver_manager_installed': False,
        'chrome_available': False,
        'chromedriver_available': False,
        'can_create_driver': False,
        'error_message': None
    }
    
    # Check Selenium installation
    try:
        import selenium
        selenium_status['selenium_installed'] = True
    except ImportError:
        selenium_status['error_message'] = "Selenium not installed. Run: pip install selenium"
        return selenium_status
    
    # Check webdriver-manager
    try:
        import webdriver_manager
        selenium_status['webdriver_manager_installed'] = True
    except ImportError:
        pass
    
    # Check Chrome availability
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        # Try to create a driver
        driver = None
        if selenium_status['webdriver_manager_installed']:
            try:
                from webdriver_manager.chrome import ChromeDriverManager
                from selenium.webdriver.chrome.service import Service
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=chrome_options)
                selenium_status['chromedriver_available'] = True
            except Exception as e:
                selenium_status['error_message'] = f"WebDriver Manager failed: {e}"
        
        if not driver:
            try:
                driver = webdriver.Chrome(options=chrome_options)
                selenium_status['chromedriver_available'] = True
            except Exception as e:
                selenium_status['error_message'] = f"ChromeDriver not found: {e}"
        
        if driver:
            selenium_status['can_create_driver'] = True
            selenium_status['chrome_available'] = True
            driver.quit()
            
    except Exception as e:
        selenium_status['error_message'] = f"Chrome/ChromeDriver test failed: {e}"
    
    return selenium_status

def check_system_requirements() -> Dict[str, bool]:
    """Check if all system requirements are met"""
    requirements = {
        'ollama_available': False,
        'required_packages': False,
        'selenium_available': False,
        'chrome_driver_available': False
    }
    
    # Check Ollama
    try:
        response = requests.get("http://localhost:11434/api/version", timeout=5)
        requirements['ollama_available'] = response.status_code == 200
    except:
        pass
    
    # Check required packages
    try:
        import chromadb
        import sentence_transformers
        requirements['required_packages'] = True
    except ImportError:
        pass
    
    # Check Selenium
    selenium_status = check_selenium_installation()
    requirements['selenium_available'] = selenium_status['selenium_installed']
    requirements['chrome_driver_available'] = selenium_status['can_create_driver']
    
    return requirements

def print_system_status():
    """Print comprehensive system status check"""
    print("🔍 System Status Check:")
    print("="*30)
    
    requirements = check_system_requirements()
    
    # Core requirements
    print("📋 Core Requirements:")
    core_requirements = ['ollama_available', 'required_packages', 'selenium_available', 'chrome_driver_available']
    for requirement in core_requirements:
        status = requirements.get(requirement, False)
        status_icon = "✅" if status else "❌"
        print(f"   {status_icon} {requirement.replace('_', ' ').title()}: {status}")
    
    # Selenium detailed status
    if requirements['selenium_available']:
        print("\n🔧 Selenium Details:")
        selenium_details = check_selenium_installation()
        
        details_to_show = [
            ('webdriver_manager_installed', 'WebDriver Manager'),
            ('chrome_available', 'Chrome Browser'),
            ('chromedriver_available', 'ChromeDriver'),
            ('can_create_driver', 'Can Create Driver')
        ]
        
        for key, label in details_to_show:
            status = selenium_details.get(key, False)
            status_icon = "✅" if status else "⚠️"
            print(f"   {status_icon} {label}: {status}")
        
        if selenium_details.get('error_message'):
            print(f"   ❌ Error: {selenium_details['error_message']}")
    
    # Overall assessment
    critical_missing = []
    if not requirements['ollama_available']:
        critical_missing.append("Ollama not running")
    if not requirements['required_packages']:
        critical_missing.append("Required packages missing")
    if not requirements['selenium_available'] or not requirements['chrome_driver_available']:
        critical_missing.append("Selenium/ChromeDriver not functional")

    print(f"\n🎯 Overall Status:")
    if not critical_missing:
        print("   ✅ All systems ready!")
    else:
        print("   ⚠️ Issues found:")
        for issue in critical_missing:
            print(f"      • {issue}")
    
    all_good = len(critical_missing) == 0
    return all_good

def create_summary_stats(articles: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create summary statistics for articles"""
    if not articles:
        return {}
    
    # Count by source
    sources = {}
    categories = {}
    extraction_methods = {}
    scores = []
    
    for article in articles:
        source = article.get('source', 'Unknown')
        category = article.get('category', 'Unknown')
        method = article.get('extraction_method', 'unknown')
        score = article.get('final_score')
        
        sources[source] = sources.get(source, 0) + 1
        categories[category] = categories.get(category, 0) + 1
        extraction_methods[method] = extraction_methods.get(method, 0) + 1
        
        if score is not None:
            scores.append(score)
    
    # Calculate score statistics
    avg_score = sum(scores) / len(scores) if scores else 0
    max_score = max(scores) if scores else 0
    min_score = min(scores) if scores else 0
    
    return {
        'total_articles': len(articles),
        'sources': sources,
        'categories': categories,
        'extraction_methods': extraction_methods,
        'score_stats': {
            'average': round(avg_score, 2),
            'maximum': round(max_score, 2),
            'minimum': round(min_score, 2)
        },
        'generated_at': datetime.now().isoformat()
    }

def monitor_pipeline_health() -> Dict[str, Any]:
    """Monitor pipeline health and performance including Selenium"""
    health_status = {
        'timestamp': datetime.now().isoformat(),
        'components': {},
        'overall_status': 'healthy'
    }
    
    # Check Ollama
    try:
        response = requests.get("http://localhost:11434/api/version", timeout=5)
        health_status['components']['ollama'] = {
            'status': 'healthy' if response.status_code == 200 else 'unhealthy',
            'response_time': response.elapsed.total_seconds()
        }
    except Exception as e:
        health_status['components']['ollama'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
    
    # Check ChromaDB
    try:
        import chromadb
        client = chromadb.Client()
        health_status['components']['chromadb'] = {'status': 'healthy'}
    except Exception as e:
        health_status['components']['chromadb'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
    
    # Check Selenium
    selenium_status = check_selenium_installation()
    health_status['components']['selenium'] = {
        'status': 'healthy' if selenium_status['can_create_driver'] else 'degraded',
        'selenium_installed': selenium_status['selenium_installed'],
        'chrome_available': selenium_status['chrome_available'],
        'can_create_driver': selenium_status['can_create_driver']
    }
    
    # Determine overall status
    critical_components = ['ollama', 'chromadb', 'selenium']
    
    critical_unhealthy = [
        name for name in critical_components
        if health_status['components'][name].get('status') != 'healthy'
    ]
    
    if critical_unhealthy:
        health_status['overall_status'] = 'unhealthy'
        health_status['critical_issues'] = critical_unhealthy
    
    return health_status

def print_health_report():
    """Print comprehensive system health report"""
    health = monitor_pipeline_health()
    
    print("\n🏥 System Health Report")
    print("="*30)
    
    # Core components
    print("🔧 Core Components:")
    components = ['ollama', 'chromadb', 'selenium']
    for component in components:
        if component in health['components']:
            status = health['components'][component]
            status_icon = "✅" if status['status'] == 'healthy' else "❌"
            print(f"   {status_icon} {component.title()}: {status['status']}")
            
            if 'error' in status:
                print(f"      Error: {status['error']}")
            if component == 'selenium':
                selenium_installed = status.get('selenium_installed', False)
                chrome_available = status.get('chrome_available', False)
                can_create = status.get('can_create_driver', False)
                print(f"      Selenium Lib: {'✅' if selenium_installed else '❌'}")
                print(f"      Chrome Browser: {'✅' if chrome_available else '❌'}")
                print(f"      Driver Functional: {'✅' if can_create else '❌'}")
    
    print(f"\n🎯 Overall Status: {health['overall_status'].upper()}")
    
    if 'critical_issues' in health:
        print(f"❌ Critical issues: {', '.join(health['critical_issues'])}")
    
    # Recommendations
    recommendations = []
    
    if health['components'].get('ollama', {}).get('status') != 'healthy':
        recommendations.append("Start Ollama server: ollama serve")
    if health['components'].get('selenium', {}).get('status') != 'healthy':
        recommendations.append("Install/update Selenium and WebDriver: pip install -U selenium webdriver-manager")
    
    if recommendations:
        print(f"\n💡 Recommendations:")
        for rec in recommendations:
            print(f"   • {rec}")

def create_backup(source_dir: str = "data", backup_dir: str = "backups") -> str:
    """Create backup of data directory"""
    import shutil
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{backup_dir}/backup_{timestamp}"
    
    os.makedirs(backup_dir, exist_ok=True)
    
    if os.path.exists(source_dir):
        shutil.copytree(source_dir, backup_path)
        print(f"💾 Backup created: {backup_path}")
        return backup_path
    else:
        print(f"⚠️ Source directory {source_dir} not found")
        return ""

if __name__ == "__main__":
    # Test utilities
    print("🧪 Testing enhanced utility functions...")
    
    # Test system requirements
    print_system_status()
    
    # Test health monitoring
    print_health_report()
    
    print("✅ Enhanced utility functions test completed!")