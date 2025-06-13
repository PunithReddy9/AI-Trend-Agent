# cli.py
#!/usr/bin/env python3
"""
Command Line Interface for AI News Aggregation Pipeline
"""

import argparse
import sys
import os
from datetime import datetime

# Import our modules
from main_pipeline import NewsAggregationPipeline
from utils import print_system_status, print_health_report, create_backup
from config import Config

def run_full_pipeline(args):
    """Run the complete pipeline"""
    query = args.query or "latest AI trends and breakthroughs"
    
    print(f"🚀 Running full pipeline with query: '{query}'")
    
    pipeline = NewsAggregationPipeline()
    success = pipeline.run_complete_pipeline(query)
    
    if success:
        print("✅ Pipeline completed successfully!")
        return 0
    else:
        print("❌ Pipeline failed!")
        return 1

def run_extraction_only(args):
    """Run only the data extraction part"""
    print("📰 Running data extraction only...")
    
    pipeline = NewsAggregationPipeline()
    results = pipeline.extract_news_data()
    
    if results:
        total_articles = sum(
            r.get('article_count', 0) for r in results.values() 
            if r.get('success')
        )
        print(f"✅ Extracted {total_articles} articles from {len(results)} sources")
        return 0
    else:
        print("❌ Extraction failed!")
        return 1

def interactive_mode(args):
    """Start interactive query mode"""
    print("🔍 Starting interactive query mode...")
    
    pipeline = NewsAggregationPipeline()
    pipeline.interactive_query()
    return 0

def system_check(args):
    """Perform system health check"""
    print("🔍 Performing system check...")
    
    # Basic system requirements
    all_good = print_system_status()
    
    # Detailed health report
    print_health_report()
    
    # Configuration validation
    print("\n🔧 Configuration Validation:")
    print("="*35)
    
    issues = Config.validate_config()
    if issues:
        for issue in issues:
            print(f"❌ {issue}")
        return 1
    else:
        print("✅ All configuration valid!")
        Config.print_config()
        return 0 if all_good else 1

def create_data_backup(args):
    """Create backup of data"""
    print("💾 Creating data backup...")
    
    backup_path = create_backup()
    if backup_path:
        print(f"✅ Backup created successfully: {backup_path}")
        return 0
    else:
        print("❌ Backup failed!")
        return 1

def list_recent_data(args):
    """List recent data files"""
    print("📋 Recent data files:")
    
    directories = ['data', 'outputs', 'logs']
    
    for directory in directories:
        if os.path.exists(directory):
            print(f"\n📁 {directory}/")
            files = sorted(os.listdir(directory), reverse=True)
            for file in files[:5]:  # Show latest 5 files
                filepath = os.path.join(directory, file)
                size = os.path.getsize(filepath)
                mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                print(f"   📄 {file} ({size} bytes, {mtime.strftime('%Y-%m-%d %H:%M')})")
        else:
            print(f"\n📁 {directory}/ - Not found")
    
    return 0

def quick_search(args):
    """Quick search in vector database"""
    if not args.query:
        print("❌ Please provide a search query with --query")
        return 1
    
    print(f"🔍 Searching for: '{args.query}'")
    
    try:
        from chroma_db import ChromaDBManager
        
        db_manager = ChromaDBManager()
        results = db_manager.search_similar(args.query, n_results=args.count or 5)
        
        if results:
            print(f"\n📋 Found {len(results)} relevant articles:")
            for i, article in enumerate(results, 1):
                print(f"\n{i}. {article['title']}")
                print(f"   Source: {article['source']}")
                print(f"   Similarity: {article['similarity_score']:.3f}")
                print(f"   URL: {article['url']}")
        else:
            print("❌ No relevant articles found")
        
        return 0
        
    except Exception as e:
        print(f"❌ Search failed: {str(e)}")
        return 1

def configure_sources(args):
    """Configure news sources"""
    print("⚙️ News Sources Configuration:")
    print("="*35)
    
    for name, config in Config.NEWS_SOURCES.items():
        status = "✅ Enabled" if config.get('enabled') else "❌ Disabled"
        print(f"{name}: {status}")
        print(f"   URL: {config['url']}")
        print()
    
    print("💡 To enable/disable sources, edit config.py")
    return 0

def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="AI News Aggregation Pipeline - Command Line Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s run --query "GPT-4 developments"     # Run full pipeline
  %(prog)s extract                              # Extract news only
  %(prog)s search --query "machine learning"    # Search vector DB
  %(prog)s interactive                          # Interactive mode
  %(prog)s check                                # System health check
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Run full pipeline
    run_parser = subparsers.add_parser('run', help='Run complete pipeline')
    run_parser.add_argument('--query', '-q', type=str, 
                           help='Search query for news filtering')
    run_parser.set_defaults(func=run_full_pipeline)
    
    # Extract only
    extract_parser = subparsers.add_parser('extract', help='Extract news data only')
    extract_parser.set_defaults(func=run_extraction_only)
    
    # Interactive mode
    interactive_parser = subparsers.add_parser('interactive', help='Interactive query mode')
    interactive_parser.set_defaults(func=interactive_mode)
    
    # System check
    check_parser = subparsers.add_parser('check', help='System health check')
    check_parser.set_defaults(func=system_check)
    
    # Search vector DB
    search_parser = subparsers.add_parser('search', help='Search vector database')
    search_parser.add_argument('--query', '-q', type=str, required=True,
                              help='Search query')
    search_parser.add_argument('--count', '-n', type=int, default=5,
                              help='Number of results to return')
    search_parser.set_defaults(func=quick_search)
    
    # Backup data
    backup_parser = subparsers.add_parser('backup', help='Create data backup')
    backup_parser.set_defaults(func=create_data_backup)
    
    # List files
    list_parser = subparsers.add_parser('list', help='List recent data files')
    list_parser.set_defaults(func=list_recent_data)
    
    # Configure sources
    config_parser = subparsers.add_parser('config', help='Show configuration')
    config_parser.set_defaults(func=configure_sources)
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Check basic requirements for most commands
    if args.command in ['run', 'extract', 'search', 'interactive']:
        print("🔍 Quick system check...")
        from utils import check_system_requirements
        
        requirements = check_system_requirements()
        critical_missing = []
        
        if not requirements['ollama_available'] and args.command in ['run', 'interactive']:
            critical_missing.append("Ollama not available")
        
        if not requirements['selenium_available'] or not requirements['chrome_driver_available']:
            critical_missing.append("Selenium or ChromeDriver not properly installed")

        if not requirements['required_packages']:
            critical_missing.append("Required packages not installed")
        
        if critical_missing:
            print("❌ Critical requirements missing:")
            for missing in critical_missing:
                print(f"   • {missing}")
            print("\n💡 Run 'python cli.py check' for detailed information")
            return 1
    
    # Execute command
    try:
        return args.func(args)
    except KeyboardInterrupt:
        print("\n⏹️ Operation interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main())