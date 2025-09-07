from typing import Dict, List, Optional, Any
from datetime import datetime
from urllib.parse import urlparse
import re
from dataclasses import dataclass
from enum import Enum

class CitationStyle(Enum):
    APA = "apa"
    MLA = "mla"
    CHICAGO = "chicago"
    HARVARD = "harvard"
    IEEE = "ieee"

@dataclass
class SourceMetadata:
    url: str
    title: str
    author: str
    publish_date: Optional[str]
    domain: str
    access_date: str
    content_type: str = "webpage"
    
    def __post_init__(self):
        if not self.access_date:
            self.access_date = datetime.now().strftime("%Y-%m-%d")

@dataclass
class Citation:
    source: SourceMetadata
    quote: Optional[str] = None
    page_number: Optional[str] = None
    section: Optional[str] = None
    confidence: float = 1.0

class CitationManager:
    
    def __init__(self):
        self.sources: Dict[str, SourceMetadata] = {}
        self.citations: List[Citation] = []
    
    def add_source(self, url: str, title: str, author: str = "Unknown", 
                   publish_date: Optional[str] = None, content_type: str = "webpage") -> str:
        domain = urlparse(url).netloc
        source_id = self._generate_source_id(url, title)
        
        metadata = SourceMetadata(
            url=url,
            title=title,
            author=author,
            publish_date=publish_date,
            domain=domain,
            access_date=datetime.now().strftime("%Y-%m-%d"),
            content_type=content_type
        )
        
        self.sources[source_id] = metadata
        return source_id
    
    def add_citation(self, source_id: str, quote: Optional[str] = None, 
                    page_number: Optional[str] = None, section: Optional[str] = None,
                    confidence: float = 1.0) -> Citation:
        if source_id not in self.sources:
            raise ValueError(f"Source {source_id} not found")
        
        citation = Citation(
            source=self.sources[source_id],
            quote=quote,
            page_number=page_number,
            section=section,
            confidence=confidence
        )
        
        self.citations.append(citation)
        return citation
    
    def format_citation(self, source_id: str, style: CitationStyle = CitationStyle.APA) -> str:
        if source_id not in self.sources:
            return f"[Source not found: {source_id}]"
        
        source = self.sources[source_id]
        
        if style == CitationStyle.APA:
            return self._format_apa_citation(source)
        elif style == CitationStyle.MLA:
            return self._format_mla_citation(source)
        elif style == CitationStyle.CHICAGO:
            return self._format_chicago_citation(source)
        elif style == CitationStyle.HARVARD:
            return self._format_harvard_citation(source)
        elif style == CitationStyle.IEEE:
            return self._format_ieee_citation(source)
        else:
            return self._format_apa_citation(source)
    
    def format_in_text_citation(self, source_id: str, style: CitationStyle = CitationStyle.APA) -> str:
        if source_id not in self.sources:
            return f"[Source not found: {source_id}]"
        
        source = self.sources[source_id]
        
        if style == CitationStyle.APA:
            if source.author != "Unknown":
                return f"({source.author}, {self._extract_year(source.publish_date)})"
            else:
                return f"({source.title}, {self._extract_year(source.publish_date)})"
        elif style == CitationStyle.MLA:
            if source.author != "Unknown":
                return f"({source.author})"
            else:
                return f"({source.title})"
        elif style == CitationStyle.HARVARD:
            if source.author != "Unknown":
                return f"({source.author} {self._extract_year(source.publish_date)})"
            else:
                return f"({source.title} {self._extract_year(source.publish_date)})"
        else:
            return f"({source_id})"
    
    def generate_reference_list(self, style: CitationStyle = CitationStyle.APA) -> List[str]:
        references = []
        
        for source_id, source in self.sources.items():
            citation = self.format_citation(source_id, style)
            references.append(citation)
        
        return references
    
    def generate_bibliography(self, style: CitationStyle = CitationStyle.APA) -> str:
        references = self.generate_reference_list(style)
        
        if not references:
            return "No sources cited."
        
        bibliography = f"References ({style.value.upper()} Style):\n\n"
        
        for i, ref in enumerate(references, 1):
            bibliography += f"{i}. {ref}\n"
        
        return bibliography
    
    def get_source_statistics(self) -> Dict[str, Any]:
        total_sources = len(self.sources)
        total_citations = len(self.citations)
        
        domains = {}
        authors = {}
        years = {}
        
        for source in self.sources.values():
            domains[source.domain] = domains.get(source.domain, 0) + 1
            
            authors[source.author] = authors.get(source.author, 0) + 1
            
            year = self._extract_year(source.publish_date)
            if year:
                years[year] = years.get(year, 0) + 1
        
        return {
            "total_sources": total_sources,
            "total_citations": total_citations,
            "domains": domains,
            "authors": authors,
            "years": years,
            "most_common_domain": max(domains.items(), key=lambda x: x[1])[0] if domains else None,
            "most_common_author": max(authors.items(), key=lambda x: x[1])[0] if authors else None
        }
    
    def _generate_source_id(self, url: str, title: str) -> str: 
        domain = urlparse(url).netloc.replace("www.", "")
        title_words = re.sub(r'[^\w\s]', '', title.lower()).split()[:3]
        source_id = f"{domain}_{'_'.join(title_words)}"
        
        counter = 1
        original_id = source_id
        while source_id in self.sources:
            source_id = f"{original_id}_{counter}"
            counter += 1
        
        return source_id
    
    def _extract_year(self, date_string: Optional[str]) -> Optional[str]:
        if not date_string:
            return None
        
        year_match = re.search(r'\b(19|20)\d{2}\b', date_string)
        if year_match:
            return year_match.group()
        
        return None
    
    def _clean_title(self, title: str) -> str:
        if not title:
            return title
        
        title = re.sub(r'\.\w+[-\w]*\s*', '', title)
        
        title = re.sub(r'\b[A-Z][a-z]+-[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', '', title)

        title = re.sub(r'--[a-zA-Z-]+', '', title)
        
        title = re.sub(r'\b(Align|Display|Flex|Gap|Var|Font|Size|Weight|Line|Height|Media|Min|Width|Show|Seperator|Block)\b', '', title)
        
        title = re.sub(r'\s+', ' ', title)
        title = title.strip()

        if len(title) < 10:
            title_match = re.search(r'([A-Z][^.]*[.!?])', title)
            if title_match:
                title = title_match.group(1)
        
        return title
    
    def _format_apa_citation(self, source: SourceMetadata) -> str:
        citation_parts = []
        
        clean_title = self._clean_title(source.title)
        
        if source.author != "Unknown":
            citation_parts.append(source.author)
        else:
            citation_parts.append(clean_title)
        
        year = self._extract_year(source.publish_date)
        if year:
            citation_parts.append(f"({year})")
        else:
            citation_parts.append("(n.d.)")
        
        if source.author != "Unknown":
            citation_parts.append(f"{clean_title}.")
        else:
            citation_parts.append(f"Retrieved from {source.url}")
        
        if source.author != "Unknown":
            citation_parts.append(f"Retrieved {source.access_date} from {source.url}")
        
        return " ".join(citation_parts)
    
    def _format_mla_citation(self, source: SourceMetadata) -> str:
        citation_parts = []
        
        clean_title = self._clean_title(source.title)
        
        if source.author != "Unknown":
            citation_parts.append(source.author)
        
        citation_parts.append(f'"{clean_title}."')
        
        citation_parts.append(f"{source.domain},")
        
        year = self._extract_year(source.publish_date)
        if year:
            citation_parts.append(f"{year},")
        
        citation_parts.append(f"{source.access_date}, {source.url}.")
        
        return " ".join(citation_parts)
    
    def _format_chicago_citation(self, source: SourceMetadata) -> str:
        citation_parts = []
        
        clean_title = self._clean_title(source.title)
        
        if source.author != "Unknown":
            citation_parts.append(source.author)
        else:
            citation_parts.append(source.domain)
        
        citation_parts.append(f'"{clean_title}."')
        
        citation_parts.append(f"{source.domain}.")
        
        year = self._extract_year(source.publish_date)
        if year:
            citation_parts.append(f"Last modified {year}.")
        
        citation_parts.append(f"Accessed {source.access_date}. {source.url}.")
        
        return " ".join(citation_parts)
    
    def _format_harvard_citation(self, source: SourceMetadata) -> str:
        citation_parts = []
        
        clean_title = self._clean_title(source.title)
        
        if source.author != "Unknown":
            citation_parts.append(source.author)
        else:
            citation_parts.append(source.domain)
        
        year = self._extract_year(source.publish_date)
        if year:
            citation_parts.append(f"{year}")
        else:
            citation_parts.append("n.d.")

        citation_parts.append(f"{clean_title}.")
        
        citation_parts.append(f"Available at: {source.url} (Accessed: {source.access_date})")
        
        return " ".join(citation_parts)
    
    def _format_ieee_citation(self, source: SourceMetadata) -> str:
        citation_parts = []
        
        clean_title = self._clean_title(source.title)
        
        if source.author != "Unknown":
            citation_parts.append(source.author)
        else:
            citation_parts.append(source.domain)
        
        citation_parts.append(f'"{clean_title},"')
        
        citation_parts.append(f"{source.domain}.")
        
        year = self._extract_year(source.publish_date)
        if year:
            citation_parts.append(f"{year}.")
        
        citation_parts.append(f"[Online]. Available: {source.url}")
        
        return " ".join(citation_parts)

def create_citation_manager() -> CitationManager:
    return CitationManager()

def format_citation_from_content(content_data: Dict, style: CitationStyle = CitationStyle.APA) -> str:
    manager = CitationManager()
    
    source_id = manager.add_source(
        url=content_data.get('url', ''),
        title=content_data.get('title', 'Unknown Title'),
        author=content_data.get('metadata', {}).get('author', 'Unknown'),
        publish_date=content_data.get('metadata', {}).get('publish_date')
    )
    
    return manager.format_citation(source_id, style)

def generate_citations_for_sources(extracted_content: Dict[str, Dict], 
                                 style: CitationStyle = CitationStyle.APA) -> List[str]:
    manager = CitationManager()
    
    for url, content_data in extracted_content.items():
        manager.add_source(
            url=url,
            title=content_data.get('title', 'Unknown Title'),
            author=content_data.get('metadata', {}).get('author', 'Unknown'),
            publish_date=content_data.get('metadata', {}).get('publish_date')
        )
    
    return manager.generate_reference_list(style)
