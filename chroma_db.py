import chromadb
from chromadb.utils import embedding_functions
import os
from datetime import datetime
import json
from typing import List, Dict, Any

class ChromaDBManager:
    def __init__(self, db_path="./vectordb"):
        """Initialize ChromaDB with persistent storage"""
        self.db_path = db_path
        
        # Create directory if it doesn't exist
        os.makedirs(db_path, exist_ok=True)
        
        # Initialize persistent client
        self.client = chromadb.PersistentClient(path=db_path)
        
        # Setup embedding function (all-MiniLM-L6-v2)
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        # Create or get collection
        self.collection_name = "ai_news_articles"
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_function,
            metadata={"description": "AI News Articles for Newsletter Curation"}
        )
        
        print(f"✅ ChromaDB initialized at: {db_path}")
        print(f"📚 Collection: {self.collection_name}")
        print(f"🔤 Embedding model: all-MiniLM-L6-v2")
    
    def add_articles(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Add articles to the vector database"""
        if not articles:
            return {"success": False, "message": "No articles provided"}
        
        documents = []
        metadatas = []
        ids = []
        
        added_count = 0
        skipped_count = 0
        
        for i, article in enumerate(articles):
            # Create document text for embedding
            title = article.get('title', '')
            summary = article.get('summary', '')
            
            if not title:  # Skip articles without titles
                skipped_count += 1
                continue
            
            # Combine title and summary for better embedding
            doc_text = f"{title}. {summary}".strip()
            
            # Create unique ID
            article_id = f"{article.get('source', 'unknown')}_{datetime.now().strftime('%Y%m%d')}_{i}"
            
            # Prepare metadata
            metadata = {
                'title': title,
                'source': article.get('source', ''),
                'author': article.get('author', ''),
                'date': article.get('date', ''),
                'url': article.get('url', ''),
                'category': article.get('category', 'AI/ML'),
                'added_at': datetime.now().isoformat()
            }
            
            documents.append(doc_text)
            metadatas.append(metadata)
            ids.append(article_id)
            added_count += 1
        
        if documents:
            try:
                # Add to ChromaDB
                self.collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
                
                print(f"✅ Added {added_count} articles to vector database")
                if skipped_count > 0:
                    print(f"⚠️ Skipped {skipped_count} articles (missing title)")
                
                return {
                    "success": True,
                    "added": added_count,
                    "skipped": skipped_count,
                    "total_in_db": self.collection.count()
                }
                
            except Exception as e:
                print(f"❌ Error adding articles to database: {str(e)}")
                return {"success": False, "error": str(e)}
        else:
            return {"success": False, "message": "No valid articles to add"}
    
    def search_similar(self, query_text: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search for similar articles"""
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results,
                include=['documents', 'metadatas', 'distances']
            )
            
            similar_articles = []
            if results['documents'] and results['documents'][0]:
                for doc, metadata, distance in zip(
                    results['documents'][0], 
                    results['metadatas'][0], 
                    results['distances'][0]
                ):
                    similar_articles.append({
                        'title': metadata['title'],
                        'source': metadata['source'],
                        'url': metadata['url'],
                        'similarity_score': 1 - distance,  # Convert distance to similarity
                        'document': doc
                    })
            
            return similar_articles
            
        except Exception as e:
            print(f"❌ Error searching database: {str(e)}")
            return []
    
    def get_article_insights(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """Get insights about an article using vector search"""
        title = article.get('title', '')
        summary = article.get('summary', '')
        
        if not title:
            return {}
        
        # Search for similar articles
        query_text = f"{title} {summary}"
        similar_articles = self.search_similar(query_text, n_results=3)
        
        # Filter out very low similarity matches
        relevant_similar = [
            art for art in similar_articles 
            if art['similarity_score'] > 0.7 and art['title'] != title
        ]
        
        return {
            'article_title': title,
            'related_articles': relevant_similar,
            'related_count': len(relevant_similar)
        }
    
    def detect_trends(self, articles: List[Dict[str, Any]]) -> List[str]:
        """Simple trend detection based on content similarity"""
        if not articles:
            return []
        
        trends = []
        
        # Common AI terms to look for
        ai_terms = [
            'GPT', 'LLM', 'Large Language Model', 'ChatGPT', 'OpenAI',
            'machine learning', 'deep learning', 'neural network',
            'transformer', 'AI model', 'artificial intelligence',
            'computer vision', 'natural language processing', 'NLP'
        ]
        
        # Count term occurrences across all articles
        term_counts = {}
        total_text = ""
        
        for article in articles:
            article_text = f"{article.get('title', '')} {article.get('summary', '')}".lower()
            total_text += article_text + " "
        
        for term in ai_terms:
            count = total_text.lower().count(term.lower())
            if count >= 2:  # Term appears in multiple articles
                term_counts[term] = count
        
        # Create trend descriptions
        for term, count in sorted(term_counts.items(), key=lambda x: x[1], reverse=True)[:3]:
            trends.append(f"{term} developments (mentioned {count} times)")
        
        return trends
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            count = self.collection.count()
            return {
                "total_articles": count,
                "collection_name": self.collection_name,
                "embedding_model": "all-MiniLM-L6-v2",
                "db_path": self.db_path
            }
        except Exception as e:
            return {"error": str(e)}
    
    def reset_database(self):
        """Reset the database (useful for testing)"""
        try:
            self.client.delete_collection(self.collection_name)
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function
            )
            print("🔄 Database reset successfully")
        except Exception as e:
            print(f"❌ Error resetting database: {str(e)}")

def test_chromadb():
    """Test ChromaDB functionality"""
    print("🧪 Testing ChromaDB setup...")
    
    # Initialize manager
    db_manager = ChromaDBManager()
    
    # Test data
    test_articles = [
        {
            'title': 'OpenAI Releases GPT-4.5 with Enhanced Capabilities',
            'summary': 'OpenAI announces new language model with improved reasoning and efficiency.',
            'source': 'test',
            'category': 'AI Research'
        },
        {
            'title': 'Google DeepMind Advances in Computer Vision',
            'summary': 'New breakthrough in image recognition technology using transformer architecture.',
            'source': 'test',
            'category': 'Computer Vision'
        }
    ]
    
    # Add test articles
    result = db_manager.add_articles(test_articles)
    print(f"📊 Add result: {result}")
    
    # Search for similar content
    similar = db_manager.search_similar("OpenAI language model", n_results=2)
    print(f"🔍 Similar articles found: {len(similar)}")
    
    # Get insights
    insights = db_manager.get_article_insights(test_articles[0])
    print(f"💡 Insights: {insights}")
    
    # Get stats
    stats = db_manager.get_stats()
    print(f"📈 Database stats: {stats}")
    
    print("✅ ChromaDB test completed!")

if __name__ == "__main__":
    test_chromadb()