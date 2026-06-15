import aiohttp
from bs4 import BeautifulSoup
import logging
from typing import Optional, Dict, Any
import structlog

logger = structlog.get_logger(__name__)

class ScraperService:
    """Service for scraping content from URLs to populate the Knowledge Base."""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    async def scrape_url(self, url: str) -> Optional[Dict[str, str]]:
        """
        Scrape a URL and extract title and main content.
        
        Args:
            url: The URL to scrape
            
        Returns:
            Dictionary with 'title' and 'content' or None if failed
        """
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(url, timeout=15) as response:
                    if response.status != 200:
                        logger.error(f"Failed to fetch URL: {url}", status=response.status)
                        return None
                    
                    html = await response.text()
                    soup = BeautifulSoup(html, 'lxml')
                    
                    # Remove script and style elements
                    for script in soup(["script", "style"]):
                        script.decompose()

                    # Extract title
                    title = soup.title.string if soup.title else url
                    
                    # Basic content extraction - focusing on main tags
                    # In a more advanced version, we'd use something like 'readability'
                    content_parts = []
                    for tag in soup.find_all(['h1', 'h2', 'h3', 'p', 'li']):
                        text = tag.get_text().strip()
                        if text:
                            content_parts.append(text)
                    
                    content = "\n\n".join(content_parts)
                    
                    if not content:
                        logger.warning(f"No significant content found at URL: {url}")
                        return None
                        
                    return {
                        "title": title.strip(),
                        "content": content,
                        "url": url
                    }
                    
        except Exception as e:
            logger.error(f"Error scraping URL: {url}", error=str(e))
            return None

# Global instance
scraper = ScraperService()
