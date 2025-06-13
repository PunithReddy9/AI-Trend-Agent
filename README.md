# AI News Aggregation Pipeline 🤖📰

An intelligent news aggregation system that automatically discovers, processes, and analyzes AI-related news articles from multiple sources. The pipeline uses advanced natural language processing and vector search capabilities to identify trending topics, generate insights, and create comprehensive reports.

## 🌟 Features

### Core Functionality
- **Multi-source News Extraction**: Automatically scrapes articles from configurable news sources (KDnuggets, AI News, The New Stack, etc.)
- **Intelligent Content Processing**: Uses LLM models (Ollama) to analyze and filter articles for quality and relevance
- **Vector Database Storage**: Implements ChromaDB for semantic search and similarity matching
- **Comprehensive Reporting**: Generates detailed reports with insights, trends, and actionable takeaways
- **Interactive Query Mode**: Allows real-time search and analysis of stored articles

### Advanced Features
- **Quality Scoring**: Multi-criteria quality assessment for article filtering
- **Trend Detection**: Identifies emerging patterns and themes in AI news
- **Semantic Search**: Find relevant articles using natural language queries
- **Backup & Recovery**: Built-in data backup and restoration capabilities
- **CLI Interface**: Comprehensive command-line interface for all operations
- **Health Monitoring**: System status checks and configuration validation

## 🏗️ Architecture

The pipeline consists of several interconnected components:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   News Sources  │────│   Web Scraper    │────│  Raw Articles   │
│   • KDnuggets   │    │   • Selenium     │    │   • JSON Data   │
│   • AI News     │    │   • BeautifulSoup│    │   • Metadata    │
│   • The New     │    │   • Newspaper3k  │    │                 │
│     Stack       │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Vector DB     │────│   LLM Processing │────│ Article Filtering│
│   • ChromaDB    │    │   • Ollama       │    │ • Quality Score │
│   • Embeddings  │    │   • Analysis     │    │ • Relevance     │
│   • Similarity  │    │   • Summarization│    │ • Deduplication │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Reports &     │────│   Insights       │────│   Trend         │
│   Outputs       │    │   Generation     │    │   Analysis      │
│   • Text Files  │    │   • Summaries    │    │   • Patterns    │
│   • JSON Data   │    │   • Key Points   │    │   • Themes      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🔧 Installation

### Prerequisites

- **Python 3.8+**: Ensure you have Python 3.8 or later installed
- **Ollama**: Install and configure Ollama for LLM processing
  ```bash
  # Install Ollama (macOS/Linux)
  curl https://ollama.ai/install.sh | sh
  
  # Pull the required model
  ollama pull llama3.1:8b
  ```

### Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd ai-trend-agent
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv myenv
   source myenv/bin/activate  # On Windows: myenv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify installation:**
   ```bash
   python main.py check
   ```

### Environment Setup

Create a `.env` file in the project root for environment-specific configurations:

```env
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b

# Optional: Custom configurations
VECTOR_DB_PATH=./vectordb
MAX_ARTICLES_TO_PROCESS=50
MIN_QUALITY_SCORE=4.0
```

## 🚀 Usage

### Command Line Interface

The pipeline provides a comprehensive CLI for all operations:

#### Run Complete Pipeline
```bash
# Run with default AI trends query
python main.py run

# Run with custom query
python main.py run --query "GPT-4 developments and applications"
```

#### Extract News Only
```bash
# Extract articles without processing
python main.py extract
```

#### Interactive Mode
```bash
# Start interactive query session
python main.py interactive
```

#### Search Existing Articles
```bash
# Search vector database
python main.py search --query "machine learning" --count 10
```

#### System Health Check
```bash
# Perform comprehensive system check
python main.py check
```

#### List Recent Data
```bash
# Show recent data files
python main.py list
```

#### Configure Sources
```bash
# View and configure news sources
python main.py sources
```

#### Create Backup
```bash
# Create data backup
python main.py backup
```

### Python API Usage

You can also use the pipeline programmatically:

```python
from main_pipeline import NewsAggregationPipeline

# Initialize pipeline
pipeline = NewsAggregationPipeline()

# Run complete pipeline
success = pipeline.run_complete_pipeline("AI ethics and safety")

# Or run individual steps
extraction_results = pipeline.extract_news_data()
processed_articles = pipeline.process_and_filter_articles(extraction_results)
pipeline.store_in_vector_db(processed_articles)
insights = pipeline.get_relevant_insights("AI ethics")
```

## ⚙️ Configuration

### News Sources Configuration

Edit `config.py` to customize news sources:

```python
NEWS_SOURCES = {
    'kdnuggets': {
        'url': 'https://www.kdnuggets.com/',
        'enabled': True
    },
    'ai_news': {
        'url': 'https://artificialintelligence-news.com/',
        'enabled': True
    },
    'custom_source': {
        'url': 'https://your-custom-source.com/',
        'enabled': False
    }
}
```

### Processing Parameters

Adjust processing behavior:

```python
# Quality and filtering settings
MIN_QUALITY_SCORE = 4.0          # Minimum quality score (1-10)
MAX_ARTICLES_TO_PROCESS = 50     # Maximum articles per run
TOP_ARTICLES_COUNT = 15          # Top articles to select
SIMILARITY_THRESHOLD = 0.7       # Similarity threshold for deduplication

# LLM settings
OLLAMA_MODEL = "llama3.1:8b"     # Ollama model to use
OLLAMA_TEMPERATURE = 0.3         # Model temperature (0-1)
```

### Vector Database Configuration

Configure ChromaDB settings:

```python
VECTOR_DB_PATH = "./vectordb"           # Database storage path
EMBEDDING_MODEL = "all-MiniLM-L6-v2"   # Embedding model
COLLECTION_NAME = "ai_news_articles"   # Collection name
```

## 📊 Output Structure

The pipeline generates organized outputs:

```
├── data/                           # Raw and processed data
│   ├── raw_extraction_*.json       # Raw scraped articles
│   └── processed_articles_*.json   # Filtered and processed articles
├── outputs/                        # Generated reports and insights
│   ├── comprehensive_report_*.txt  # Detailed analysis reports
│   ├── insights_*.json            # Structured insights data
│   └── summary_report_*.txt       # Concise summaries
├── logs/                          # System and error logs
└── vectordb/                      # ChromaDB vector database
```

### Report Types

1. **Comprehensive Reports**: Detailed analysis with insights, trends, and recommendations
2. **Summary Reports**: Concise overviews with key findings
3. **Insights JSON**: Structured data for programmatic access
4. **Raw Data**: Original scraped content for further processing

## 🔍 Quality Criteria

Articles are evaluated using multiple criteria:

- **Technical Accuracy** (25%): Factual correctness and technical depth
- **AI Relevance** (30%): Relevance to AI and machine learning topics
- **Content Freshness** (20%): Recency and timeliness of information
- **Source Credibility** (15%): Reputation and reliability of the source
- **Practical Value** (10%): Actionable insights and practical applications

## 🛠️ Development

### Adding New Data Sources

1. **Update configuration** in `config.py`:
   ```python
   'new_source': {
       'url': 'https://new-source.com/',
       'enabled': True
   }
   ```

2. **Implement extraction logic** in `news_extractor.py` if needed

3. **Test the new source**:
   ```bash
   python main.py extract
   ```

### Extending Analysis Capabilities

- **Custom quality criteria**: Modify `QUALITY_CRITERIA` in `config.py`
- **Additional keywords**: Update `AI_KEYWORDS` for better trend detection
- **New report formats**: Extend `enhanced_report_generator.py`

### Testing

Run the test suite:

```bash
# Run system tests
python utils/test_system.py

# Quick functionality test
python utils/quick_test_scrapegraph.py
```

## 🐛 Troubleshooting

### Common Issues

1. **Ollama Connection Error**:
   ```bash
   # Check if Ollama is running
   ollama list
   
   # Start Ollama if needed
   ollama serve
   ```

2. **ChromaDB Issues**:
   ```bash
   # Clear vector database
   rm -rf vectordb/
   
   # Restart pipeline
   python main.py run
   ```

3. **Web Scraping Failures**:
   - Check internet connectivity
   - Verify source URLs in `config.py`
   - Update web scraping logic if sites have changed

4. **Memory Issues**:
   - Reduce `MAX_ARTICLES_TO_PROCESS` in config
   - Process articles in smaller batches
   - Clear old data files regularly

### System Requirements

- **RAM**: Minimum 8GB (16GB recommended for large datasets)
- **Storage**: 5GB free space for databases and outputs
- **Network**: Stable internet connection for web scraping
- **CPU**: Multi-core processor recommended for parallel processing

## 📝 Dependencies

### Core Dependencies
- `requests>=2.31.0`: HTTP requests for web scraping
- `beautifulsoup4>=4.12.0`: HTML parsing
- `newspaper3k>=0.2.8`: Article extraction
- `selenium>=4.15.0`: Dynamic content scraping
- `chromadb>=0.4.0`: Vector database
- `sentence-transformers>=2.2.0`: Text embeddings

### Optional Dependencies
- `scrapegraph-py>=1.0.0`: Advanced scraping capabilities
- `pytest>=7.4.0`: Testing framework

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Run the test suite: `python utils/test_system.py`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [Ollama](https://ollama.ai/) for LLM processing
- Uses [ChromaDB](https://www.trychroma.com/) for vector storage
- Inspired by the need for intelligent news aggregation in the AI space

## 📞 Support

For issues, questions, or contributions:
- Create an issue on GitHub
- Check the troubleshooting section above
- Review the configuration documentation

---

**Happy News Aggregating!** 🚀📰🤖 