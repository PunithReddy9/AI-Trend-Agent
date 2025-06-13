import requests
import json
import time
from typing import Dict, List, Any, Optional

class OllamaManager:
    def __init__(self, base_url="http://localhost:11434"):
        """Initialize Ollama connection"""
        self.base_url = base_url
        self.model_name = "llama3.1:8b"
        
        # Verify connection
        if self.is_available():
            print(f"✅ Connected to Ollama at {base_url}")
        else:
            print(f"❌ Cannot connect to Ollama at {base_url}")
            print("Make sure Ollama is running: ollama serve")
    
    def is_available(self) -> bool:
        """Check if Ollama is running and accessible"""
        try:
            response = requests.get(f"{self.base_url}/api/version", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def list_models(self) -> List[str]:
        """List available models"""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                models = response.json().get('models', [])
                return [model['name'] for model in models]
            return []
        except Exception as e:
            print(f"Error listing models: {e}")
            return []
    
    def ensure_model_available(self, model_name: str = None) -> bool:
        """Ensure the required model is available"""
        model = model_name or self.model_name
        available_models = self.list_models()
        
        if model in available_models:
            print(f"✅ Model {model} is available")
            return True
        else:
            print(f"⚠️ Model {model} not found. Available models: {available_models}")
            print(f"Please run: ollama pull {model}")
            return False
    
    def generate_response(self, prompt: str, model: str = None, temperature: float = 0.3) -> Optional[str]:
        """Generate response using Ollama"""
        if not self.is_available():
            print("❌ Ollama is not available")
            return None
        
        model_name = model or self.model_name
        
        if not self.ensure_model_available(model_name):
            return None
        
        try:
            payload = {
                "model": model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": 1000,  # Limit response length
                    "stop": ["\n\n"]  # Stop at double newline
                }
            }
            
            print(f"🤖 Generating response with {model_name}...")
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error generating response: {e}")
            return None
    
    def analyze_article_quality(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze article quality using LLM"""
        title = article.get('title', '')
        summary = article.get('summary', '')
        source = article.get('source', '')
        
        prompt = f"""
Analyze this AI news article and provide a quality assessment:

Title: {title}
Summary: {summary}
Source: {source}

Please evaluate on a scale of 1-10 and provide:
1. Quality Score (1-10): Overall quality and value
2. Relevance Score (1-10): How relevant to AI professionals
3. Category: Research/Industry/Tools/Business/Tutorial
4. Key Insights: 2-3 main takeaways
5. Reason: Brief explanation of the scores

Format your response as:
Quality: X/10
Relevance: X/10
Category: [Category]
Insights: [Key insights]
Reason: [Brief explanation]
"""
        
        response = self.generate_response(prompt, temperature=0.1)
        
        if response:
            return self._parse_quality_analysis(response, article)
        else:
            # Fallback scoring
            return {
                'quality_score': 5,
                'relevance_score': 5,
                'category': 'AI/ML',
                'insights': ['Unable to analyze with LLM'],
                'reason': 'LLM analysis failed',
                'llm_analysis': False
            }
    
    def _parse_quality_analysis(self, response: str, article: Dict[str, Any]) -> Dict[str, Any]:
        """Parse LLM quality analysis response"""
        try:
            lines = response.strip().split('\n')
            result = {
                'quality_score': 5,
                'relevance_score': 5,
                'category': 'AI/ML',
                'insights': [],
                'reason': '',
                'llm_analysis': True,
                'raw_response': response
            }
            
            for line in lines:
                line = line.strip()
                if line.startswith('Quality:'):
                    try:
                        score = int(line.split(':')[1].split('/')[0].strip())
                        result['quality_score'] = max(1, min(10, score))
                    except:
                        pass
                elif line.startswith('Relevance:'):
                    try:
                        score = int(line.split(':')[1].split('/')[0].strip())
                        result['relevance_score'] = max(1, min(10, score))
                    except:
                        pass
                elif line.startswith('Category:'):
                    category = line.split(':', 1)[1].strip()
                    result['category'] = category
                elif line.startswith('Insights:'):
                    insights = line.split(':', 1)[1].strip()
                    result['insights'] = [insights]
                elif line.startswith('Reason:'):
                    reason = line.split(':', 1)[1].strip()
                    result['reason'] = reason
            
            return result
            
        except Exception as e:
            print(f"⚠️ Error parsing LLM response: {e}")
            return {
                'quality_score': 5,
                'relevance_score': 5,
                'category': 'AI/ML',
                'insights': ['Parsing error'],
                'reason': 'Failed to parse LLM response',
                'llm_analysis': False
            }
    
    def summarize_trends(self, articles: List[Dict[str, Any]]) -> str:
        """Generate trend summary from articles"""
        if not articles:
            return "No articles to analyze"
        
        # Prepare article summaries for LLM
        article_summaries = []
        for i, article in enumerate(articles[:10]):  # Limit to 10 articles
            summary = f"{i+1}. {article.get('title', '')} - {article.get('summary', '')}"
            article_summaries.append(summary)
        
        articles_text = '\n'.join(article_summaries)
        
        prompt = f"""
Analyze these AI news articles and identify the top 3 trends or themes:

{articles_text}

Please provide:
1. Top 3 trends or themes you see across these articles
2. Brief explanation of each trend
3. Which articles support each trend

Format as:
Trend 1: [Trend name] - [Brief explanation]
Trend 2: [Trend name] - [Brief explanation]  
Trend 3: [Trend name] - [Brief explanation]
"""
        
        response = self.generate_response(prompt, temperature=0.2)
        return response or "Unable to analyze trends"
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                models = response.json().get('models', [])
                current_model = None
                
                for model in models:
                    if model['name'] == self.model_name:
                        current_model = model
                        break
                
                return {
                    'model_name': self.model_name,
                    'available': current_model is not None,
                    'details': current_model,
                    'all_models': [m['name'] for m in models]
                }
            return {'error': 'Cannot fetch model info'}
        except Exception as e:
            return {'error': str(e)}
    
    def curate_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Curate and rank articles using LLM"""
        if not articles:
            return []
        
        curated_articles = []
        
        print(f"🤖 Analyzing {len(articles)} articles with LLM...")
        
        for i, article in enumerate(articles):
            print(f"Processing article {i+1}/{len(articles)}: {article.get('title', 'No title')[:50]}...")
            
            # Analyze each article
            analysis = self.analyze_article_quality(article)
            
            # Add analysis to article
            article['llm_analysis'] = analysis
            article['final_score'] = (analysis['quality_score'] + analysis['relevance_score']) / 2
            
            curated_articles.append(article)
        
        # Sort by final score
        curated_articles.sort(key=lambda x: x['final_score'], reverse=True)
        
        return curated_articles
    
    def select_top_articles(self, articles: List[Dict[str, Any]], count: int = 10) -> List[Dict[str, Any]]:
        """Select top articles based on LLM analysis"""
        curated = self.curate_articles(articles)
        
        # Filter articles with score >= 6 and take top 'count'
        high_quality = [art for art in curated if art['final_score'] >= 6.0]
        
        selected = high_quality[:count]
        
        print(f"📊 Selected {len(selected)} high-quality articles from {len(articles)} total")
        
        return selected
    
    def batch_analyze_articles(self, articles: List[Dict[str, Any]], batch_size: int = 5) -> List[Dict[str, Any]]:
        """Analyze articles in batches for better performance"""
        if not articles:
            return []
        
        print(f"🔄 Processing {len(articles)} articles in batches of {batch_size}...")
        
        all_analyzed = []
        
        for i in range(0, len(articles), batch_size):
            batch = articles[i:i + batch_size]
            print(f"📦 Processing batch {i//batch_size + 1}/{(len(articles) + batch_size - 1)//batch_size}")
            
            batch_analyzed = []
            for article in batch:
                analysis = self.analyze_article_quality(article)
                article['llm_analysis'] = analysis
                article['final_score'] = (analysis['quality_score'] + analysis['relevance_score']) / 2
                batch_analyzed.append(article)
            
            all_analyzed.extend(batch_analyzed)
            
            # Small delay between batches to prevent overwhelming the LLM
            if i + batch_size < len(articles):
                time.sleep(1)
        
        # Sort by final score
        all_analyzed.sort(key=lambda x: x['final_score'], reverse=True)
        
        return all_analyzed
    
    def generate_article_summary(self, article: Dict[str, Any]) -> str:
        """Generate an enhanced summary for an article"""
        title = article.get('title', '')
        summary = article.get('summary', '')
        
        prompt = f"""
Create an enhanced summary for this AI article:

Title: {title}
Original Summary: {summary}

Please provide:
1. A concise 2-sentence summary
2. Key technical points
3. Why this matters to AI professionals

Format your response as a cohesive paragraph that's engaging and informative.
"""
        
        response = self.generate_response(prompt, temperature=0.4)
        return response or summary
    
    def compare_articles(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compare multiple articles and find relationships"""
        if len(articles) < 2:
            return {'error': 'Need at least 2 articles to compare'}
        
        # Create comparison text
        comparison_text = ""
        for i, article in enumerate(articles[:5], 1):  # Limit to 5 articles
            comparison_text += f"Article {i}: {article.get('title', '')} - {article.get('summary', '')}\n"
        
        prompt = f"""
Compare these AI articles and identify:

{comparison_text}

Please provide:
1. Common themes or topics
2. Conflicting viewpoints (if any)
3. Complementary information
4. Overall narrative or story emerging

Be concise but insightful.
"""
        
        response = self.generate_response(prompt, temperature=0.3)
        
        return {
            'comparison_summary': response or "Unable to compare articles",
            'articles_compared': len(articles),
            'generated_at': time.time()
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on Ollama system"""
        health_status = {
            'timestamp': time.time(),
            'ollama_available': False,
            'model_available': False,
            'response_time': None,
            'test_successful': False
        }
        
        # Check if Ollama is available
        start_time = time.time()
        health_status['ollama_available'] = self.is_available()
        
        if health_status['ollama_available']:
            health_status['response_time'] = time.time() - start_time
            
            # Check if model is available
            health_status['model_available'] = self.ensure_model_available()
            
            # Test simple generation
            if health_status['model_available']:
                test_response = self.generate_response("Say 'OK' if you can read this.", temperature=0.1)
                health_status['test_successful'] = bool(test_response and 'OK' in test_response.upper())
        
        return health_status
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        try:
            # Test response time
            start_time = time.time()
            test_response = self.generate_response("Hello", temperature=0.1)
            response_time = time.time() - start_time
            
            # Get model info
            model_info = self.get_model_info()
            
            return {
                'response_time_seconds': round(response_time, 2),
                'model_loaded': model_info.get('available', False),
                'available_models': model_info.get('all_models', []),
                'current_model': self.model_name,
                'test_successful': bool(test_response),
                'timestamp': time.time()
            }
        except Exception as e:
            return {
                'error': str(e),
                'timestamp': time.time()
            }

def test_ollama_manager():
    """Test the complete Ollama functionality"""
    print("🧪 Testing Complete Ollama Manager...")
    
    # Initialize manager
    ollama = OllamaManager()
    
    if not ollama.is_available():
        print("❌ Ollama not available - skipping tests")
        return
    
    # Test model info
    info = ollama.get_model_info()
    print(f"📋 Model info: {info}")
    
    # Test performance stats
    stats = ollama.get_performance_stats()
    print(f"📊 Performance stats: {stats}")
    
    # Test health check
    health = ollama.health_check()
    print(f"🏥 Health check: {health}")
    
    # Test article analysis
    test_article = {
        'title': 'OpenAI Releases GPT-4.5 with Enhanced Reasoning',
        'summary': 'OpenAI announces significant improvements in their latest language model, featuring better reasoning capabilities and reduced hallucinations.',
        'source': 'test',
        'category': 'AI Research'
    }
    
    analysis = ollama.analyze_article_quality(test_article)
    print(f"📈 Article analysis: {analysis}")
    
    # Test enhanced summary
    enhanced_summary = ollama.generate_article_summary(test_article)
    print(f"📝 Enhanced summary: {enhanced_summary}")
    
    # Test curation
    test_articles = [
        test_article, 
        {
            'title': 'Google Introduces New AI Ethics Guidelines',
            'summary': 'Google releases comprehensive guidelines for responsible AI development.',
            'source': 'test',
            'category': 'AI Ethics'
        },
        {
            'title': 'Microsoft Copilot Gets Major Updates',
            'summary': 'Microsoft enhances Copilot with new features for enterprise users.',
            'source': 'test',
            'category': 'AI Tools'
        }
    ]
    
    curated = ollama.curate_articles(test_articles)
    print(f"✅ Curated {len(curated)} articles")
    
    # Test article comparison
    comparison = ollama.compare_articles(test_articles)
    print(f"🔍 Article comparison: {comparison}")
    
    # Test trend analysis
    trends = ollama.summarize_trends(test_articles)
    print(f"📈 Trends analysis: {trends}")
    
    print("✅ Ollama Manager test completed!")

if __name__ == "__main__":
    test_ollama_manager()