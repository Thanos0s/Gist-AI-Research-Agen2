from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from tools import search_tool, wiki_tool, save_tool, multi_source_tool, scrape_multiple_urls_adaptive
from content_extractor import ContentExtractor
from content_analyzer import ContentAnalyzer, AnalysisResult
from citation_manager import CitationManager, CitationStyle
import json
import os
from datetime import datetime
from typing import Optional

load_dotenv()

class ResearchResponse(BaseModel):
    topic: str
    summary: str
    sources: list[str]
    source_urls: list[str]
    tools_used: list[str]
    analysis_result: Optional[AnalysisResult] = None
    citations: list[str] = []
    extraction_metadata: dict = {}

def research_topic(topic: str, time_filter: str = "Any time", tone: str = "Default", num_sources: int = 5) -> ResearchResponse:
    
    print(f"Researching: {topic}")
    print(f"Advanced options - Time filter: {time_filter}, Tone: {tone}, Sources: {num_sources}")
    
    
    response = ResearchResponse(
        topic=topic,
        summary="",
        sources=[],
        source_urls=[],
        tools_used=[],
        analysis_result=None,
        citations=[],
        extraction_metadata={}
    )
    
    
    
    print("Searching for multiple sources...")
    try:
        
        search_query = topic
        if time_filter == "Past year":
            search_query = f"{topic} after:2023"
        elif time_filter == "Past month":
            search_query = f"{topic} after:2024-11"
        
        
        from tools import search_multiple_sources
        search_results = search_multiple_sources(search_query, num_sources)
        response.tools_used.append("multi_source_search")
        
        
        response.sources.extend(search_results["sources"])
        response.source_urls.extend(search_results["urls"])
        
        print(f"Found {len(search_results['sources'])} sources")
        for i, (source, url) in enumerate(zip(search_results["sources"], search_results["urls"])):
            print(f"  {i+1}. {source} - {url}")
            
    except Exception as e:
        print(f"Multi-source search failed: {e}")
        
        try:
            search_results = search_tool.invoke(search_query)
            response.tools_used.append("search")
            response.sources.append(f"Web search results ({time_filter})")
            response.source_urls.append("https://search-results.com")
        except Exception as e2:
            print(f"Fallback search also failed: {e2}")
    
    
    if len(response.sources) < num_sources:
        print("Searching Wikipedia...")
        try:
            wiki_results = wiki_tool.invoke(topic)
            response.tools_used.append("wiki_tool")
            response.sources.append("Wikipedia")
            response.source_urls.append("https://en.wikipedia.org")
            print(f"Wikipedia results: {wiki_results[:200]}...")
        except Exception as e:
            print(f"Wikipedia search failed: {e}")
    else:
        print("Skipping Wikipedia - already have enough sources")
    
    
    
    
    
    # Advanced content extraction using new modules
    print("Extracting content with advanced methods...")
    extractor = ContentExtractor()
    extracted_content = extractor.extract_multiple_urls(response.source_urls, 3000)
    
    # Store extraction metadata
    response.extraction_metadata = {
        'total_urls': len(response.source_urls),
        'successful_extractions': len([url for url, data in extracted_content.items() if data.get('content')]),
        'extraction_methods': list(set([data.get('metadata', {}).get('extraction_method', 'unknown') for data in extracted_content.values()]))
    }
    
    # Add Wikipedia content if available
    if 'wiki_results' in locals():
        extracted_content['wikipedia'] = {
            'url': 'https://en.wikipedia.org',
            'title': f'Wikipedia: {topic}',
            'summary': wiki_results[:500] + "..." if len(wiki_results) > 500 else wiki_results,
            'content': wiki_results,
            'metadata': {
                'author': 'Wikipedia Contributors',
                'publish_date': None,
                'domain': 'en.wikipedia.org',
                'extraction_method': 'wikipedia_api'
            },
            'source_info': {
                'link': 'https://en.wikipedia.org',
                'website': 'en.wikipedia.org',
                'extraction_timestamp': datetime.now().isoformat()
            }
        }
    
    # Advanced content analysis
    print("Performing advanced content analysis...")
    analyzer = ContentAnalyzer()
    analysis_result = analyzer.analyze_content(topic, extracted_content, "comprehensive")
    response.analysis_result = analysis_result
    
    # Generate citations
    print("Generating citations...")
    citation_manager = CitationManager()
    for url, content_data in extracted_content.items():
        if url != 'wikipedia':  # Skip Wikipedia for now
            source_id = citation_manager.add_source(
                url=content_data.get('url', url),
                title=content_data.get('title', 'Unknown Title'),
                author=content_data.get('metadata', {}).get('author', 'Unknown'),
                publish_date=content_data.get('metadata', {}).get('publish_date')
            )
    
    # Generate citations in APA style
    response.citations = citation_manager.generate_reference_list(CitationStyle.APA)
    
    # Prepare content for summary generation
    content_for_summary = []
    for url, content_data in extracted_content.items():
        title = content_data.get('title', 'Unknown Title')
        summary = content_data.get('summary', '')
        content = content_data.get('content', '')
        metadata = content_data.get('metadata', {})
        
        source_info = f"Source: {title}\n"
        if metadata.get('author') and metadata['author'] != 'Unknown':
            source_info += f"Author: {metadata['author']}\n"
        if metadata.get('publish_date'):
            source_info += f"Date: {metadata['publish_date']}\n"
        source_info += f"URL: {url}\n"
        source_info += f"Summary: {summary}\n"
        source_info += f"Content: {content[:2000]}...\n" if len(content) > 2000 else f"Content: {content}\n"
        source_info += "---\n"
        
        content_for_summary.append(source_info)
    
    all_content = "\n".join(content_for_summary)
    
    # Use analysis result for summary if available, otherwise generate fallback
    if response.analysis_result and response.analysis_result.summary:
        response.summary = response.analysis_result.summary
    else:
        try:
            if not os.getenv("GOOGLE_API_KEY"):
                print("Warning: GOOGLE_API_KEY not found. Using fallback summary.")
                response.summary = f"Research on {topic} - information gathered from available sources using {tone.lower()} tone. (Note: AI summary generation requires GOOGLE_API_KEY)"
                return response
                
            llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash",
                temperature=0.1
            )
            
            tone_instructions = {
                "Academic": "Write in a formal, scholarly tone with precise language and academic terminology. Focus on evidence-based analysis and cite key findings.",
                "Casual": "Write in a friendly, conversational tone that's easy to understand. Use everyday language and make it engaging for general readers.",
                "Professional": "Write in a business-appropriate tone that's clear and authoritative. Focus on practical insights and actionable information.",
                "Creative": "Write in an engaging, creative tone with vivid descriptions and interesting perspectives. Make the content compelling and thought-provoking.",
                "Default": "Write in a balanced, informative tone that's accessible to a general audience while maintaining accuracy and depth."
            }
            
            tone_instruction = tone_instructions.get(tone, tone_instructions["Default"])
            
            summary_prompt = f"""
            Based on the following research about "{topic}":
            
            {all_content}
            
            Please provide a comprehensive summary of {topic} based on the scraped content from the sources above.
            {tone_instruction}
            
            IMPORTANT: Provide a complete, well-structured summary that includes:
            - Key facts and statistics from the sources
            - Important details and insights
            - A logical flow of information
            - Proper conclusion
            
            Make sure to write a complete summary without cutting off mid-sentence. The summary should be thorough and informative.
            """
            
            summary_response = llm.invoke(summary_prompt)
            response.summary = summary_response.content
            
        except Exception as e:
            print(f"Summary generation failed: {e}")
            response.summary = f"Research on {topic} - information gathered from available sources using {tone.lower()} tone. (Note: AI summary generation failed: {str(e)})"
    
    return response


if __name__ == "__main__":
    query = input("What can i help you research? ")
    result = research_topic(query, "Any time", "Default", 5)

    try:
        save_result = save_tool.invoke(str(result.model_dump()))
        print(f"\nSave result: {save_result}")
    except Exception as e:
        print(f"Save failed: {e}")