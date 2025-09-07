from typing import Dict, List, Optional, Any
from datetime import datetime
import json
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
import os

class KeyPoint(BaseModel):
    point: str
    source_url: str
    source_title: str
    confidence: float = 1.0

class Viewpoint(BaseModel):
    perspective: str
    supporting_evidence: List[str]
    source_urls: List[str]

class Trend(BaseModel):
    trend: str
    description: str
    supporting_data: List[str]
    source_urls: List[str]

class AnalysisResult(BaseModel):
    summary: str
    key_points: List[KeyPoint]
    trends: List[Trend]
    viewpoints: List[Viewpoint]
    gaps: List[str]
    pros_cons: Dict[str, List[str]]
    recommendations: List[str]
    sources_analyzed: int

class ContentAnalyzer:
    
    def __init__(self, model_name: str = "gemini-2.0-flash", temperature: float = 0.1):
        self.model_name = model_name
        self.temperature = temperature
        self.llm = None
        
        if os.getenv("GOOGLE_API_KEY"):
            self.llm = ChatGoogleGenerativeAI(
                model=model_name,
                temperature=temperature
            )
    
    def analyze_content(self, topic: str, extracted_content: Dict[str, Dict], 
                       analysis_type: str = "comprehensive") -> AnalysisResult:
        """
        
        Args:
            topic: Research topic
            extracted_content: Dictionary of URL -> extracted content
            analysis_type: Type of analysis (comprehensive, summary, trends, viewpoints)
            
        Returns:
            Structured analysis result
        """
        if not self.llm:
            return self._fallback_analysis(topic, extracted_content)
        
        content_text = self._prepare_content_for_analysis(extracted_content)
        
        if analysis_type == "comprehensive":
            return self._comprehensive_analysis(topic, content_text, extracted_content)
        elif analysis_type == "summary":
            return self._summary_analysis(topic, content_text, extracted_content)
        elif analysis_type == "trends":
            return self._trends_analysis(topic, content_text, extracted_content)
        elif analysis_type == "viewpoints":
            return self._viewpoints_analysis(topic, content_text, extracted_content)
        else:
            return self._comprehensive_analysis(topic, content_text, extracted_content)
    
    def _prepare_content_for_analysis(self, extracted_content: Dict[str, Dict]) -> str:
        content_parts = []
        
        for url, content_data in extracted_content.items():
            title = content_data.get('title', 'Unknown Title')
            summary = content_data.get('summary', '')
            content = content_data.get('content', '')
            metadata = content_data.get('metadata', {})
            
            source_info = f"Source: {title}\nURL: {url}\n"
            if metadata.get('author') and metadata['author'] != 'Unknown':
                source_info += f"Author: {metadata['author']}\n"
            if metadata.get('publish_date'):
                source_info += f"Date: {metadata['publish_date']}\n"
            
            source_info += f"Summary: {summary}\n"
            source_info += f"Content: {content[:2000]}...\n" if len(content) > 2000 else f"Content: {content}\n"
            source_info += "---\n"
            
            content_parts.append(source_info)
        
        return "\n".join(content_parts)
    
    def _comprehensive_analysis(self, topic: str, content_text: str, 
                              extracted_content: Dict[str, Dict]) -> AnalysisResult:
        
        parser = PydanticOutputParser(pydantic_object=AnalysisResult)
        
        prompt = ChatPromptTemplate.from_template("""
        Analyze the following research content about "{topic}" and provide a comprehensive analysis.

        Content to analyze:
        {content}

        Please provide a structured analysis including:
        1. A comprehensive summary
        2. Key points and facts with source attribution
        3. Identified trends and patterns
        4. Different viewpoints or perspectives
        5. Knowledge gaps or areas needing more research
        6. Pros and cons of different approaches
        7. Recommendations based on the findings

        For each key point, trend, and viewpoint, include the source URL and title for proper citation.

        {format_instructions}
        """)
        
        chain = prompt | self.llm | parser
        
        try:
            result = chain.invoke({
                "topic": topic,
                "content": content_text,
                "format_instructions": parser.get_format_instructions()
            })
            
            result.sources_analyzed = len(extracted_content)
            return result
            
        except Exception as e:
            print(f"Comprehensive analysis failed: {e}")
            return self._fallback_analysis(topic, extracted_content)
    
    def _summary_analysis(self, topic: str, content_text: str, 
                         extracted_content: Dict[str, Dict]) -> AnalysisResult:
        
        summary_prompt = f"""
        Based on the following research content about "{topic}", provide a structured summary:

        {content_text}

        Please provide:
        1. A clear, comprehensive summary
        2. Key points with source attribution
        3. Main findings and conclusions

        Focus on accuracy and proper source citation.
        """
        
        try:
            response = self.llm.invoke(summary_prompt)
            summary = response.content
            
            return AnalysisResult(
                summary=summary,
                key_points=[KeyPoint(
                    point="See summary for key points",
                    source_url="",
                    source_title=""
                )],
                trends=[],
                viewpoints=[],
                gaps=[],
                pros_cons={},
                recommendations=[],
                sources_analyzed=len(extracted_content)
            )
            
        except Exception as e:
            print(f"Summary analysis failed: {e}")
            return self._fallback_analysis(topic, extracted_content)
    
    def _trends_analysis(self, topic: str, content_text: str, 
                        extracted_content: Dict[str, Dict]) -> AnalysisResult:
        
        trends_prompt = f"""
        Analyze the following content about "{topic}" to identify trends, patterns, and developments:

        {content_text}

        Please identify:
        1. Current trends and patterns
        2. Emerging developments
        3. Historical progression
        4. Future projections mentioned in sources
        5. Statistical trends or data patterns

        For each trend, provide supporting evidence and source attribution.
        """
        
        try:
            response = self.llm.invoke(trends_prompt)
            trends_content = response.content
            
            return AnalysisResult(
                summary=f"Trend analysis for {topic}:\n{trends_content}",
                key_points=[],
                trends=[Trend(
                    trend="See summary for identified trends",
                    description=trends_content,
                    supporting_data=[],
                    source_urls=[]
                )],
                viewpoints=[],
                gaps=[],
                pros_cons={},
                recommendations=[],
                sources_analyzed=len(extracted_content)
            )
            
        except Exception as e:
            print(f"Trends analysis failed: {e}")
            return self._fallback_analysis(topic, extracted_content)
    
    def _viewpoints_analysis(self, topic: str, content_text: str, 
                           extracted_content: Dict[str, Dict]) -> AnalysisResult:
        
        viewpoints_prompt = f"""
        Analyze the following content about "{topic}" to identify different viewpoints, perspectives, and debates:

        {content_text}

        Please identify:
        1. Different perspectives or viewpoints
        2. Conflicting opinions or debates
        3. Pros and cons of different approaches
        4. Expert opinions and their positions
        5. Public vs. expert perspectives

        For each viewpoint, provide supporting evidence and source attribution.
        """
        
        try:
            response = self.llm.invoke(viewpoints_prompt)
            viewpoints_content = response.content
            
            return AnalysisResult(
                summary=f"Viewpoint analysis for {topic}:\n{viewpoints_content}",
                key_points=[],
                trends=[],
                viewpoints=[Viewpoint(
                    perspective="See summary for different viewpoints",
                    supporting_evidence=[],
                    source_urls=[]
                )],
                gaps=[],
                pros_cons={},
                recommendations=[],
                sources_analyzed=len(extracted_content)
            )
            
        except Exception as e:
            print(f"Viewpoints analysis failed: {e}")
            return self._fallback_analysis(topic, extracted_content)
    
    def _fallback_analysis(self, topic: str, extracted_content: Dict[str, Dict]) -> AnalysisResult:
        
        summaries = []
        sources = []
        
        for url, content_data in extracted_content.items():
            title = content_data.get('title', 'Unknown')
            summary = content_data.get('summary', '')
            summaries.append(f"• {title}: {summary}")
            sources.append(url)
        
        summary_text = f"Research Summary for '{topic}':\n\n" + "\n".join(summaries)
        
        return AnalysisResult(
            summary=summary_text,
            key_points=[KeyPoint(
                point="Content extracted from multiple sources",
                source_url="",
                source_title=""
            )],
            trends=[],
            viewpoints=[],
            gaps=["LLM analysis not available - API key required"],
            pros_cons={},
            recommendations=["Enable LLM analysis for detailed insights"],
            sources_analyzed=len(extracted_content)
        )
    
    def generate_formatted_output(self, analysis: AnalysisResult, 
                                format_type: str = "markdown") -> str:
        
        if format_type == "markdown":
            return self._generate_markdown_output(analysis)
        elif format_type == "html":
            return self._generate_html_output(analysis)
        elif format_type == "json":
            return analysis.model_dump_json(indent=2)
        else:
            return self._generate_markdown_output(analysis)
    
    def _generate_markdown_output(self, analysis: AnalysisResult) -> str:
        
        output = []
        output.append("# Research Analysis Report")
        output.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        output.append(f"**Sources Analyzed:** {analysis.sources_analyzed}")
        output.append("")
        
        output.append("## Summary")
        output.append(analysis.summary)
        output.append("")
        
        if analysis.key_points:
            output.append("## Key Points")
            for i, point in enumerate(analysis.key_points, 1):
                output.append(f"{i}. {point.point}")
                if point.source_url:
                    output.append(f"   - Source: [{point.source_title}]({point.source_url})")
            output.append("")
        
        if analysis.trends:
            output.append("## Trends and Patterns")
            for trend in analysis.trends:
                output.append(f"### {trend.trend}")
                output.append(trend.description)
                if trend.source_urls:
                    output.append("**Sources:**")
                    for url in trend.source_urls:
                        output.append(f"- {url}")
            output.append("")
        
        if analysis.viewpoints:
            output.append("## Different Viewpoints")
            for viewpoint in analysis.viewpoints:
                output.append(f"### {viewpoint.perspective}")
                for evidence in viewpoint.supporting_evidence:
                    output.append(f"- {evidence}")
                if viewpoint.source_urls:
                    output.append("**Sources:**")
                    for url in viewpoint.source_urls:
                        output.append(f"- {url}")
            output.append("")
        
        if analysis.pros_cons:
            output.append("## Pros and Cons")
            for category, items in analysis.pros_cons.items():
                output.append(f"### {category}")
                for item in items:
                    output.append(f"- {item}")
            output.append("")
        
        if analysis.gaps:
            output.append("## Knowledge Gaps")
            for gap in analysis.gaps:
                output.append(f"- {gap}")
            output.append("")
        
        if analysis.recommendations:
            output.append("## Recommendations")
            for rec in analysis.recommendations:
                output.append(f"- {rec}")
            output.append("")
        
        return "\n".join(output)
    
    def _generate_html_output(self, analysis: AnalysisResult) -> str:
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Research Analysis Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                h1 {{ color: #333; }}
                h2 {{ color: #666; border-bottom: 2px solid #eee; }}
                h3 {{ color: #888; }}
                .metadata {{ background: #f5f5f5; padding: 10px; border-radius: 5px; }}
                ul {{ line-height: 1.6; }}
                a {{ color: #0066cc; }}
            </style>
        </head>
        <body>
            <h1>Research Analysis Report</h1>
            <div class="metadata">
                <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>Sources Analyzed:</strong> {analysis.sources_analyzed}</p>
            </div>
            
            <h2>Summary</h2>
            <p>{analysis.summary.replace(chr(10), '<br>')}</p>
        """
        
        
        html += """
        </body>
        </html>
        """
        
        return html

def analyze_content(topic: str, extracted_content: Dict[str, Dict], 
                   analysis_type: str = "comprehensive") -> AnalysisResult:

    analyzer = ContentAnalyzer()
    return analyzer.analyze_content(topic, extracted_content, analysis_type)

def generate_report(analysis: AnalysisResult, format_type: str = "markdown") -> str:

    analyzer = ContentAnalyzer()
    return analyzer.generate_formatted_output(analysis, format_type)
