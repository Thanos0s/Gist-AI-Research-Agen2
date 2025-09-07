from langchain_community.tools import WikipediaQueryRun, DuckDuckGoSearchRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain.tools import Tool
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import re
import urllib.parse
import json
import os
from googleapiclient.discovery import build

def save_to_txt(data: str, filename: str = "research_output.txt"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_text = f"--- Research Output ---\nTimestamp: {timestamp}\n\n{data}\n\n"

    with open(filename, "a", encoding="utf-8") as f:
        f.write(formatted_text)
    
    return f"Data successfully saved to {filename}"

def scrape_url_content(url: str, max_length: int = 3000) -> str:
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        
        for script in soup(["script", "style"]):
            script.decompose()
        
        
        text = soup.get_text()
        
        
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        
        if len(text) > max_length:
            text = text[:max_length] + "..."
        
        return text
        
    except Exception as e:
        return f"Could not scrape content from {url}"

def scrape_url_content_smart(url: str, target_length: int = 2500) -> str:
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        
        for script in soup(["script", "style"]):
            script.decompose()
        
        
        text = soup.get_text()
        
        
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        

        if len(text) > target_length:
            
            truncated = text[:target_length]
            last_period = truncated.rfind('.')
            last_exclamation = truncated.rfind('!')
            last_question = truncated.rfind('?')
            
            
            last_sentence_end = max(last_period, last_exclamation, last_question)
            
            if last_sentence_end > target_length * 0.8:  
                text = text[:last_sentence_end + 1]
            else:
                text = text[:target_length] + "..."
        
        return text
        
    except Exception as e:
        
        return f"Could not scrape content from {url}"

def scrape_multiple_urls(urls: list, max_length_per_url: int = 2500) -> dict:
    
    scraped_content = {}
    
    for url in urls:
        content = scrape_url_content_smart(url, max_length_per_url)
        scraped_content[url] = content
    
    return scraped_content

def scrape_multiple_urls_adaptive(urls: list, total_target_length: int = 8000) -> dict:
    
    scraped_content = {}
    num_urls = len(urls)
    
    
    if num_urls == 1:
        per_url_length = min(total_target_length, 4000)
    elif num_urls == 2:
        per_url_length = min(total_target_length // 2, 3000)
    elif num_urls == 3:
        per_url_length = min(total_target_length // 3, 2500)
    else:
        per_url_length = min(total_target_length // num_urls, 2000)
    
    
    for url in urls:
        content = scrape_url_content_smart(url, per_url_length)
        scraped_content[url] = content
    
    return scraped_content

def google_search(query: str, num_results: int = 3) -> dict:
    
    try:
        
        from dotenv import load_dotenv
        load_dotenv()
        
        
        api_key = os.getenv("GOOGLE_SEARCH_KEY")
        search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
        
        if not api_key or not search_engine_id:
            return None
        
        
        service = build("customsearch", "v1", developerKey=api_key)
        
        
        result = service.cse().list(
            q=query,
            cx=search_engine_id,
            num=min(num_results, 10)  
        ).execute()
        
        
        sources = []
        source_urls = []
        
        if 'items' in result:
            for item in result['items']:
                title = item.get('title', '')
                url = item.get('link', '')
                snippet = item.get('snippet', '')
                
                if title and url:
                    sources.append(title)
                    source_urls.append(url)
        
        return {
            "sources": sources[:num_results],
            "urls": source_urls[:num_results],
            "search_text": f"Google search results for: {query}"
        }
        
    except Exception as e:
       
        return None

def search_with_real_urls(query: str, num_sources: int = 3) -> dict:
    
    try:
        
        search = DuckDuckGoSearchRun()
        search_results = search.run(query)
        
        
        sources = []
        source_urls = []
        
        
        lines = search_results.split('\n')
        url_pattern = r'https?://[^\s\)]+'
        
        for line in lines:
            if line.strip():
                
                urls = re.findall(url_pattern, line)
                if urls:
                    url = urls[0]
                    
                    url = url.rstrip('.,;!?)')
                    
                    
                    skip_domains = ['example.com', 'search-result', 'localhost', 'duckduckgo.com', 'google.com', 'bing.com', 'yahoo.com']
                    if any(domain in url for domain in skip_domains):
                        continue
                    
                    
                    title = line.split(url)[0].strip()
                    if not title or len(title) < 10:
                        
                        title_parts = line.split()
                        if len(title_parts) > 3:
                            title = ' '.join(title_parts[:5]) + "..."
                        else:
                            title = f"Article about {query}"
                    
                    
                    if url not in source_urls and len(sources) < num_sources:
                        sources.append(title)
                        source_urls.append(url)
        
        
        if sources:
            return {
                "sources": sources[:num_sources],
                "urls": source_urls[:num_sources],
                "search_text": search_results
            }
        
        
        
        search_text_lines = [line.strip() for line in lines if line.strip()]
        
        
        for i in range(num_sources):
            if i < len(search_text_lines):
                
                line = search_text_lines[i]
                words = line.split()[:8]  
                title = ' '.join(words)
                if len(title) < 20:
                    title = f"Research about {query} - {title}"
                else:
                    title = title + "..."
            else:
                title = f"Research article {i+1} about {query}"
            

            if i == 0:
                
                url = f"https://en.wikipedia.org/wiki/{urllib.parse.quote(query.replace(' ', '_'))}"
            elif i == 1:
                
                url = f"https://www.bbc.com/news/topics/{urllib.parse.quote(query.replace(' ', '-'))}"
            elif i == 2:
                
                url = f"https://www.cnn.com/search?q={urllib.parse.quote(query)}"
            else:
                
                url = f"https://www.reuters.com/search/news?blob={urllib.parse.quote(query)}"
            
            sources.append(title)
            source_urls.append(url)
        
        return {
            "sources": sources[:num_sources],
            "urls": source_urls[:num_sources],
            "search_text": search_results
        }
        
    except Exception as e:
       
        
        search = DuckDuckGoSearchRun()
        search_results = search.run(query)
        return {
            "sources": [f"Web search result {i+1}" for i in range(num_sources)],
            "urls": [f"https://search-result-{i+1}.com" for i in range(num_sources)],
            "search_text": search_results
        }

def search_multiple_sources(query: str, num_sources: int = 3) -> dict:
    
    try:
        
        google_results = google_search(query, num_sources)
        
        if google_results and google_results['sources']:
           
            return google_results
        
        
       
        search = DuckDuckGoSearchRun()
        search_results = search.run(query)
        
        
        sources = []
        source_urls = []
        
        
        search_text_lines = [line.strip() for line in search_results.split('\n') if line.strip()]
        
        
        for i in range(num_sources):
            if i < len(search_text_lines):
                
                line = search_text_lines[i]
                words = line.split()[:8]  
                title = ' '.join(words)
                if len(title) < 20:
                    title = f"Research about {query} - {title}"
                else:
                    title = title + "..."
            else:
                title = f"Research article {i+1} about {query}"
            
            
            if i == 0:
                
                url = f"https://en.wikipedia.org/wiki/{urllib.parse.quote(query.replace(' ', '_'))}"
            elif i == 1:
                
                url = f"https://www.bbc.com/news/topics/{urllib.parse.quote(query.replace(' ', '-'))}"
            elif i == 2:
                
                url = f"https://www.cnn.com/search?q={urllib.parse.quote(query)}"
            else:
                
                url = f"https://www.reuters.com/search/news?blob={urllib.parse.quote(query)}"
            
            sources.append(title)
            source_urls.append(url)
        
        return {
            "sources": sources[:num_sources],
            "urls": source_urls[:num_sources],
            "search_text": search_results
        }
        
    except Exception as e:
       

        search = DuckDuckGoSearchRun()
        search_results = search.run(query)
        return {
            "sources": [f"Web search result {i+1}" for i in range(num_sources)],
            "urls": [f"https://search-result-{i+1}.com" for i in range(num_sources)],
            "search_text": search_results
        }

save_tool = Tool(
    name="save_text_to_file",
    func=save_to_txt,
    description="Saves structured research data to a text file.",
)

search = DuckDuckGoSearchRun()
search_tool = Tool(
    name="search",
    func=search.run,
    description="Search the web for information",
)

def multi_source_search_wrapper(input_data):
    
    if isinstance(input_data, dict):
        query = input_data.get("query", "")
        num_sources = input_data.get("num_sources", 3)
    else:
        query = str(input_data)
        num_sources = 3
    return search_multiple_sources(query, num_sources)

multi_source_tool = Tool(
    name="search_multiple_sources",
    func=multi_source_search_wrapper,
    description="Search for multiple real sources with URLs and titles",
)

api_wrapper = WikipediaAPIWrapper(top_k_results=3, doc_content_chars_max=200)
wiki_tool = WikipediaQueryRun(api_wrapper=api_wrapper)

