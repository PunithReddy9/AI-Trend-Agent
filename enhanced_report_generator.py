# enhanced_report_generator.py
#!/usr/bin/env python3
"""
Enhanced Report Generator - Create reports with actionable takeaways
"""

import time
from datetime import datetime
from typing import List, Dict, Any

def generate_detailed_insights(article: Dict[str, Any], llm_manager) -> Dict[str, Any]:
    """
    Generate detailed insights and takeaways from article using LLM.
    Uses pre-fetched content for efficiency.
    """
    title = article.get('title', '')
    # Use full content if available, otherwise fall back to summary
    article_text = article.get('content', article.get('summary', ''))
    
    # Enhanced prompt for detailed analysis
    prompt = f"""Analyze this AI news article and provide detailed insights:

Title: {title}
Content: {article_text[:2000]}

Please provide:

1. KEY TAKEAWAYS (3-4 bullet points of main insights)
2. BUSINESS IMPACT (How this affects companies/professionals)
3. TECHNICAL DETAILS (Key technical aspects explained simply)
4. ACTION ITEMS (What readers should do about this)

Format your response as:
TAKEAWAYS:
• [Key insight 1]
• [Key insight 2]
• [Key insight 3]

BUSINESS IMPACT:
[2-3 sentences about business implications]

TECHNICAL DETAILS:
[2-3 sentences explaining the technology]

ACTION ITEMS:
• [Action 1]
• [Action 2]

END_ANALYSIS"""
    
    try:
        response = llm_manager.generate_response(prompt, temperature=0.3)
        
        if response:
            return parse_detailed_insights(response)
        else:
            return generate_fallback_insights(title, article.get('summary', ''))
            
    except Exception as e:
        print(f"⚠️ Error generating insights: {e}")
        return generate_fallback_insights(title, article.get('summary', ''))

def parse_detailed_insights(response: str) -> Dict[str, Any]:
    """
    Parse LLM response into structured insights
    """
    insights = {
        'takeaways': [],
        'business_impact': '',
        'technical_details': '',
        'action_items': [],
        'raw_response': response
    }
    
    try:
        current_section = None
        
        for line in response.split('\n'):
            line = line.strip()
            
            if 'TAKEAWAYS:' in line.upper():
                current_section = 'takeaways'
            elif 'BUSINESS IMPACT:' in line.upper():
                current_section = 'business_impact'
            elif 'TECHNICAL DETAILS:' in line.upper():
                current_section = 'technical_details'
            elif 'ACTION ITEMS:' in line.upper():
                current_section = 'action_items'
            elif line.startswith(('•', '-')):
                bullet_text = line[1:].strip()
                if current_section == 'takeaways':
                    insights['takeaways'].append(bullet_text)
                elif current_section == 'action_items':
                    insights['action_items'].append(bullet_text)
            elif line and current_section in ['business_impact', 'technical_details']:
                if current_section == 'business_impact':
                    insights['business_impact'] += line + ' '
                elif current_section == 'technical_details':
                    insights['technical_details'] += line + ' '
        
        # Clean up text sections
        insights['business_impact'] = insights['business_impact'].strip()
        insights['technical_details'] = insights['technical_details'].strip()
        
    except Exception as e:
        print(f"⚠️ Error parsing insights: {e}")
    
    return insights

def generate_fallback_insights(title: str, summary: str) -> Dict[str, Any]:
    """
    Generate basic insights when LLM fails
    """
    return {
        'takeaways': [
            f"AI development: {title}",
            "Industry advancement in artificial intelligence",
            "Potential impact on business and technology"
        ],
        'business_impact': f"This development in AI technology may affect how businesses approach {title.lower()}. Companies should monitor these changes for potential opportunities.",
        'technical_details': f"Technical advancement related to {title}. See article for specific implementation details.",
        'action_items': [
            "Monitor this development for business impact",
            "Consider implications for your AI strategy",
            "Stay updated on similar advancements"
        ],
        'raw_response': 'Fallback analysis due to LLM unavailability'
    }

def generate_enhanced_report(articles: List[Dict[str, Any]], llm_manager) -> str:
    """
    Generate comprehensive report with real takeaways
    """
    print("📋 Generating enhanced report with detailed insights...")
    
    # Analyze each article for detailed insights
    enhanced_articles = []
    
    # Limit to top 5 for detailed analysis to keep report concise
    articles_to_analyze = articles[:5]
    
    for i, article in enumerate(articles_to_analyze, 1):
        print(f"🔍 Analyzing article {i}/{len(articles_to_analyze)}: {article['title'][:50]}...")
        
        # Generate detailed insights
        insights = generate_detailed_insights(article, llm_manager)
        
        # Add insights to article
        article['detailed_insights'] = insights
        enhanced_articles.append(article)
        
        # Small delay to prevent overwhelming LLM
        time.sleep(1)
    
    # Generate overall trends summary
    trend_summary = llm_manager.summarize_trends(articles)
    
    # Build comprehensive report
    report = f"""
AI NEWS INTELLIGENCE REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

=== EXECUTIVE SUMMARY ===
This report analyzes the latest AI developments and provides actionable insights for technology professionals and business leaders.

Total Articles Analyzed: {len(articles)}
High-Quality Articles: {len([a for a in articles if a.get('final_score', 0) >= 7.0])}

=== KEY TRENDS OVERVIEW ===
{trend_summary}

=== TOP INSIGHTS & TAKEAWAYS ===
"""
    
    # Add detailed analysis for each top article
    for i, article in enumerate(enhanced_articles, 1):
        insights = article.get('detailed_insights', {})
        score = article.get('final_score', 0)
        
        report += f"""
{i}. {article['title']}
   Source: {article['source']} | Quality Score: {score:.1f}/10
   URL: {article.get('url', 'N/A')}

   KEY TAKEAWAYS:
"""
        
        for takeaway in insights.get('takeaways', []):
            report += f"   • {takeaway}\n"
        
        report += f"""
   BUSINESS IMPACT:
   {insights.get('business_impact', 'See article for business implications.')}

   TECHNICAL DETAILS:
   {insights.get('technical_details', 'See article for technical information.')}

   ACTION ITEMS:
"""
        
        for action in insights.get('action_items', []):
            report += f"   • {action}\n"
        
        report += "\n" + "="*80 + "\n"
    
    # Add quick summaries for remaining articles
    if len(articles) > 5:
        report += f"\n=== ADDITIONAL NOTABLE ARTICLES ===\n"
        
        for article in articles[5:10]:  # Next 5 articles
            score = article.get('final_score', 0)
            report += f"""
• {article['title']} (Score: {score:.1f}/10)
  Source: {article.get('source')}
  Summary: {article.get('summary', 'No summary available')[:200]}...
  URL: {article.get('url', 'N/A')}
"""
    
    report += f"""

=== RECOMMENDATIONS ===
Based on this analysis, we recommend:

1. MONITOR: Keep track of developments in AI models and infrastructure
2. EVALUATE: Assess how these technologies could impact your business
3. EXPERIMENT: Consider pilot projects with relevant AI technologies
4. PREPARE: Update AI strategies based on emerging trends

Report generated by AI News Aggregation Pipeline
"""
    
    return report

def save_enhanced_report(articles: List[Dict[str, Any]], llm_manager, filename: str = None) -> str:
    """
    Generate and save enhanced report
    """
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"outputs/enhanced_report_{timestamp}.txt"
    
    # Generate the enhanced report
    report_content = generate_enhanced_report(articles, llm_manager)
    
    # Save to file
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"📄 Enhanced report saved to: {filename}")
    return filename