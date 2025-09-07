import requests
from bs4 import BeautifulSoup
from newspaper import Article
from readability import Document
import re
from datetime import datetime
from urllib.parse import urlparse
import json
from typing import Dict, List, Optional, Tuple
import time

class ContentExtractor:
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def extract_content(self, url: str, max_length: int = 5000) -> Dict:

        try:
            newspaper_result = self._extract_with_newspaper(url)
            if newspaper_result and newspaper_result.get('content'):
                return self._format_result(newspaper_result, url, max_length)
            
            readability_result = self._extract_with_readability(url)
            if readability_result and readability_result.get('content'):
                return self._format_result(readability_result, url, max_length)
            
            bs_result = self._extract_with_beautifulsoup(url)
            return self._format_result(bs_result, url, max_length)
            
        except Exception as e:
            return {
                'url': url,
                'title': 'Content Extraction Failed',
                'summary': f'Could not extract content: {str(e)}',
                'content': '',
                'metadata': {
                    'author': 'Unknown',
                    'publish_date': None,
                    'domain': urlparse(url).netloc,
                    'extraction_method': 'failed',
                    'error': str(e)
                },
                'source_info': {
                    'link': url,
                    'website': urlparse(url).netloc,
                    'extraction_timestamp': datetime.now().isoformat()
                }
            }
    
    def _extract_with_newspaper(self, url: str) -> Optional[Dict]:
        try:
            article = Article(url)
            article.download()
            article.parse()
            
            return {
                'title': article.title or 'No title found',
                'summary': article.summary or '',
                'content': article.text or '',
                'metadata': {
                    'author': ', '.join(article.authors) if article.authors else 'Unknown',
                    'publish_date': article.publish_date.isoformat() if article.publish_date else None,
                    'domain': urlparse(url).netloc,
                    'extraction_method': 'newspaper3k'
                }
            }
        except Exception as e:
            print(f"Newspaper3k extraction failed for {url}: {e}")
            return None
    
    def _extract_with_readability(self, url: str) -> Optional[Dict]:
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            doc = Document(response.text)
            title = doc.title() or 'No title found'
            content = doc.summary()
            
            soup = BeautifulSoup(content, 'html.parser')
            clean_content = soup.get_text()
            
            metadata = self._extract_metadata_from_html(response.text, url)
            
            return {
                'title': title,
                'summary': self._generate_summary(clean_content),
                'content': clean_content,
                'metadata': {
                    **metadata,
                    'extraction_method': 'readability-lxml'
                }
            }
        except Exception as e:
            print(f"Readability extraction failed for {url}: {e}")
            return None
    
    def _extract_with_beautifulsoup(self, url: str) -> Dict:
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            for script in soup(["script", "style"]):
                script.decompose()
            
            title_tag = soup.find('title')
            title = title_tag.get_text().strip() if title_tag else 'No title found'
            
            content_selectors = [
                'article', 'main', '.content', '.post-content', 
                '.article-content', '.entry-content', 'div[role="main"]'
            ]
            
            content = ''
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    content = content_elem.get_text()
                    break
            
            if not content:
                body = soup.find('body')
                content = body.get_text() if body else soup.get_text()
            
            content = self._clean_text(content)
            
            metadata = self._extract_metadata_from_html(response.text, url)
            
            return {
                'title': title,
                'summary': self._generate_summary(content),
                'content': content,
                'metadata': {
                    **metadata,
                    'extraction_method': 'beautifulsoup'
                }
            }
        except Exception as e:
            print(f"BeautifulSoup extraction failed for {url}: {e}")
            return {
                'title': 'Extraction Failed',
                'summary': f'Could not extract content: {str(e)}',
                'content': '',
                'metadata': {
                    'author': 'Unknown',
                    'publish_date': None,
                    'domain': urlparse(url).netloc,
                    'extraction_method': 'beautifulsoup_failed',
                    'error': str(e)
                }
            }
    
    def _extract_metadata_from_html(self, html_content: str, url: str) -> Dict:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        metadata = {
            'author': 'Unknown',
            'publish_date': None,
            'domain': urlparse(url).netloc
        }
        
        author_selectors = [
            'meta[name="author"]',
            'meta[property="article:author"]',
            '.author',
            '.byline',
            '[rel="author"]'
        ]
        
        for selector in author_selectors:
            elem = soup.select_one(selector)
            if elem:
                if elem.name == 'meta':
                    metadata['author'] = elem.get('content', 'Unknown')
                else:
                    metadata['author'] = elem.get_text().strip()
                break
        
        date_selectors = [
            'meta[property="article:published_time"]',
            'meta[name="date"]',
            'meta[name="pubdate"]',
            'time[datetime]',
            '.date',
            '.published'
        ]
        
        for selector in date_selectors:
            elem = soup.select_one(selector)
            if elem:
                if elem.name == 'meta':
                    date_str = elem.get('content', '')
                elif elem.name == 'time':
                    date_str = elem.get('datetime', '')
                else:
                    date_str = elem.get_text().strip()
                
                if date_str:
                    try:
                        from dateutil import parser
                        parsed_date = parser.parse(date_str)
                        metadata['publish_date'] = parsed_date.isoformat()
                    except:
                        metadata['publish_date'] = date_str
                break
        
        return metadata
    
    def _clean_text(self, text: str) -> str:
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n\s*\n', '\n', text)
        
        return text.strip()
    
    def _generate_summary(self, content: str, max_length: int = 300) -> str:
        if not content:
            return ''
        
        sentences = re.split(r'[.!?]+', content)
        summary_sentences = []
        current_length = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and current_length + len(sentence) < max_length:
                summary_sentences.append(sentence)
                current_length += len(sentence)
            else:
                break
        
        summary = '. '.join(summary_sentences)
        if summary and not summary.endswith('.'):
            summary += '.'
        
        return summary
    
    def _format_result(self, result: Dict, url: str, max_length: int) -> Dict:
        content = result.get('content', '')
        
        if len(content) > max_length:
            content = content[:max_length]
            last_period = content.rfind('.')
            if last_period > max_length * 0.8:
                content = content[:last_period + 1]
            else:
                content = content + "..."
        
        return {
            'url': url,
            'title': result.get('title', 'No title found'),
            'summary': result.get('summary', ''),
            'content': content,
            'metadata': result.get('metadata', {}),
            'source_info': {
                'link': url,
                'website': urlparse(url).netloc,
                'extraction_timestamp': datetime.now().isoformat()
            }
        }
    
    def extract_multiple_urls(self, urls: List[str], max_length_per_url: int = 3000) -> Dict[str, Dict]:
        results = {}
        
        for url in urls:
            print(f"Extracting content from: {url}")
            results[url] = self.extract_content(url, max_length_per_url)
            time.sleep(1)
        
        return results

def extract_content_from_url(url: str, max_length: int = 5000) -> Dict:
    extractor = ContentExtractor()
    return extractor.extract_content(url, max_length)

def extract_content_from_urls(urls: List[str], max_length_per_url: int = 3000) -> Dict[str, Dict]:
    extractor = ContentExtractor()
    return extractor.extract_multiple_urls(urls, max_length_per_url)
