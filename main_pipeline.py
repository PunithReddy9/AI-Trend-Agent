# main_pipeline.py
#!/usr/bin/env python3
"""
AI News Aggregation Pipeline - Main Orchestrator with Enhanced Reporting
Handles the complete workflow from data extraction to detailed insights
"""

import os
import json
import sys
from datetime import datetime
from typing import Dict, List, Any
from dotenv import load_dotenv

# Import our custom modules
from news_extractor import EnhancedNewsExtractor as AINewsExtractor
from chroma_db import ChromaDBManager
from llm_test import OllamaManager
from enhanced_report_generator import save_enhanced_report

# Load environment variables
load_dotenv()

class NewsAggregationPipeline:
    def __init__(self):
        """Initialize the complete pipeline"""
        print("🚀 Initializing AI News Aggregation Pipeline...")
        
        # Initialize components
        self.scraper = AINewsExtractor()
        self.vector_db = ChromaDBManager()
        self.llm_manager = OllamaManager()
        
        # Create output directories
        self.create_directories()
        
        print("✅ Pipeline initialized successfully!")
    
    def create_directories(self):
        """Create necessary directories"""
        directories = ['data', 'outputs', 'logs']
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def extract_news_data(self) -> Dict[str, Any]:
        """Step 1: Extract news data from sources"""
        print("\n" + "="*50)
        print("📰 STEP 1: EXTRACTING NEWS DATA")
        print("="*50)
        
        try:
            # Extract from multiple sources
            results = self.scraper.extract_multiple_sources()
            
            # Save raw results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"data/raw_extraction_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Raw data saved to: {filename}")
            
            return results
            
        except Exception as e:
            print(f"❌ Error in data extraction: {str(e)}")
            return {}
    
    def process_and_filter_articles(self, extraction_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Step 2: Process and filter articles using LLM"""
        print("\n" + "="*50)
        print("🤖 STEP 2: PROCESSING & FILTERING ARTICLES")
        print("="*50)
        
        # Collect all articles from all sources
        all_articles = []
        
        for source_name, result in extraction_results.items():
            if result.get('success') and result.get('articles'):
                articles = result['articles']
                print(f"📋 Found {len(articles)} articles from {source_name}")
                all_articles.extend(articles)
        
        print(f"📊 Total articles collected: {len(all_articles)}")
        
        if not all_articles:
            print("⚠️ No articles found to process")
            return []
        
        # Use LLM to analyze and filter articles
        try:
            # Select top articles using LLM analysis
            top_articles = self.llm_manager.select_top_articles(all_articles, count=15)
            
            print(f"✅ Selected {len(top_articles)} high-quality articles")
            
            # Save processed articles
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"data/processed_articles_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(top_articles, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Processed articles saved to: {filename}")
            
            return top_articles
            
        except Exception as e:
            print(f"❌ Error in article processing: {str(e)}")
            return all_articles[:10]  # Fallback: return first 10 articles
    
    def store_in_vector_db(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Step 3: Generate embeddings and store in vector database"""
        print("\n" + "="*50)
        print("🧠 STEP 3: STORING IN VECTOR DATABASE")
        print("="*50)
        
        if not articles:
            print("⚠️ No articles to store in vector database")
            return {"success": False, "message": "No articles provided"}
        
        try:
            # Add articles to vector database
            result = self.vector_db.add_articles(articles)
            
            if result['success']:
                print(f"✅ Successfully stored {result['added']} articles in vector database")
                print(f"📊 Total articles in database: {result['total_in_db']}")
            else:
                print(f"❌ Failed to store articles: {result.get('error', 'Unknown error')}")
            
            return result
            
        except Exception as e:
            print(f"❌ Error storing in vector database: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_relevant_insights(self, query: str = "AI trends and developments", top_k: int = 5) -> List[Dict[str, Any]]:
        """Step 4: Get relevant information using vector search"""
        print("\n" + "="*50)
        print("🔍 STEP 4: RETRIEVING RELEVANT INSIGHTS")
        print("="*50)
        
        try:
            # Search for relevant articles
            similar_articles = self.vector_db.search_similar(query, n_results=top_k)
            
            print(f"🎯 Found {len(similar_articles)} relevant articles for query: '{query}'")
            
            # Generate insights using LLM
            if similar_articles:
                insights_summary = self.llm_manager.summarize_trends([
                    {
                        'title': art['title'],
                        'summary': art['document']
                    } for art in similar_articles
                ])
                
                print("💡 Generated insights summary:")
                print(insights_summary)
                
                # Save insights
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                insights_data = {
                    'query': query,
                    'relevant_articles': similar_articles,
                    'insights_summary': insights_summary,
                    'generated_at': timestamp
                }
                
                filename = f"outputs/insights_{timestamp}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(insights_data, f, indent=2, ensure_ascii=False)
                
                print(f"💾 Insights saved to: {filename}")
                
                return similar_articles
            else:
                print("⚠️ No relevant articles found")
                return []
            
        except Exception as e:
            print(f"❌ Error retrieving insights: {str(e)}")
            return []
    
    def generate_comprehensive_report(self, articles: List[Dict[str, Any]]) -> str:
        """Generate comprehensive report with detailed insights and takeaways"""
        print("\n" + "="*50)
        print("📋 STEP 5: GENERATING COMPREHENSIVE REPORT")
        print("="*50)
        
        if not articles:
            print("⚠️ No articles to generate a report from.")
            return ""

        try:
            # Generate enhanced report with detailed insights
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"outputs/comprehensive_report_{timestamp}.txt"
            
            print("🔍 Analyzing articles for detailed insights...")
            print("   This may take a few minutes...")
            
            # Generate and save the enhanced report
            save_enhanced_report(articles, self.llm_manager, filename)
            
            print(f"📄 Comprehensive report saved to: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ Error generating comprehensive report: {str(e)}")
            return ""
    
    def run_complete_pipeline(self, query: str = "latest AI trends and breakthroughs"):
        """Run the complete pipeline with enhanced reporting"""
        print("🌟 STARTING COMPLETE AI NEWS AGGREGATION PIPELINE")
        print("="*60)
        
        try:
            # Step 1: Extract news data
            extraction_results = self.extract_news_data()
            
            if not extraction_results:
                print("❌ Pipeline failed at data extraction step")
                return False
            
            # Step 2: Process and filter articles
            filtered_articles = self.process_and_filter_articles(extraction_results)
            
            if not filtered_articles:
                print("❌ Pipeline failed at article processing step")
                return False
            
            # Step 3: Store in vector database
            storage_result = self.store_in_vector_db(filtered_articles)
            
            if not storage_result.get('success'):
                print("⚠️ Vector database storage failed, but continuing...")
            
            # Step 4: Get relevant insights
            self.get_relevant_insights(query)
            
            # Step 5: Generate comprehensive report with detailed insights
            report_file = self.generate_comprehensive_report(filtered_articles)
            
            print("\n" + "="*60)
            print("🎉 PIPELINE COMPLETED SUCCESSFULLY!")
            print("="*60)
            
            article_count = len(filtered_articles)
            stored_count = storage_result.get('added', 0)

            print(f"📊 Results Summary:")
            print(f"   • Processed: {article_count} high-quality articles")
            print(f"   • Stored in Vector DB: {stored_count} articles")
            if report_file:
                print(f"   • Comprehensive report: {report_file}")
            
            print(f"\n💡 Next Steps:")
            print(f"   • Review the comprehensive report in the 'outputs' folder.")
            print(f"   • Use the insights to inform your AI strategy.")
            
            return True
            
        except Exception as e:
            print(f"❌ Pipeline failed with error: {str(e)}")
            return False
        
        finally:
            # Cleanup
            self.scraper.close()
    
    def interactive_query(self):
        """Interactive mode for querying the vector database"""
        print("\n🔍 INTERACTIVE QUERY MODE")
        print("="*40)
        print("Enter queries to search the vector database. Type 'quit' to exit.")
        
        while True:
            try:
                query = input("\n🔎 Enter your query: ").strip()
                
                if query.lower() in ['quit', 'exit', 'q']:
                    break
                
                if not query:
                    continue
                
                # Search vector database
                results = self.vector_db.search_similar(query, n_results=3)
                
                if results:
                    print(f"\n📋 Found {len(results)} relevant articles:")
                    for i, article in enumerate(results, 1):
                        print(f"\n{i}. {article['title']}")
                        print(f"   Source: {article['source']}")
                        print(f"   Similarity: {article['similarity_score']:.2f}")
                        print(f"   URL: {article['url']}")
                else:
                    print("❌ No relevant articles found")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error: {str(e)}")
        
        print("\n👋 Exiting interactive mode")

def main():
    """Main function"""
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = "latest AI trends and breakthroughs"
    
    print(f"🎯 Query: {query}")
    
    # Initialize and run pipeline
    pipeline = NewsAggregationPipeline()
    
    # Run complete pipeline
    success = pipeline.run_complete_pipeline(query)
    
    if success:
        # Offer interactive mode
        response = input("\n🤔 Would you like to enter interactive query mode? (y/n): ")
        if response.lower().startswith('y'):
            pipeline.interactive_query()
    else:
        print("❌ Pipeline failed to complete")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())