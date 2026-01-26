import wikipedia
import requests
from urllib.parse import urlparse
from typing import Dict, Optional
import re

from app.config import settings
from app.utils.exceptions import WikipediaServiceException, BadRequestException
from app.utils.logger import logger


class WikipediaService:

    def __init__(self):
       
        # Setup custom user agent as per Wikipedia API requirements
        session = requests.Session()
        session.headers.update({
            "User-Agent": settings.WIKIPEDIA_USER_AGENT
        })
        wikipedia.set_lang("fr")  # Default to French, can be changed
        
       
        self.session = session
    
    def extract_article_title_from_url(self, url: str) -> str:
       
        try:
            parsed = urlparse(url)
            
            # Validate Wikipedia domain
            if not parsed.netloc.endswith("wikipedia.org"):
                raise BadRequestException("URL must be from Wikipedia")
            
            # Extract path and get article identifier
            path = parsed.path
            
            # Remove /wiki/ prefix
            if "/wiki/" in path:
                article_id = path.split("/wiki/")[1]
            else:
                raise BadRequestException("Invalid Wikipedia URL format")
            
            # Replace underscores with spaces
            article_title = article_id.replace("_", " ")
            
            logger.info(f"Extracted article title from URL: {article_title}")
            
            return article_title
            
        except Exception as e:
            logger.error(f"Error extracting title from URL: {str(e)}")
            raise BadRequestException(f"Invalid Wikipedia URL: {str(e)}")
    
    def extract_article_content(self, url: str, language: str = "fr") -> Dict[str, any]:
        """
        Extract full article content from Wikipedia URL.
        
        Args:
            url: Wikipedia article URL
            language: Language code (default: fr)
        
        Returns:
            Dict containing title, summary, full_content, and sections
        
        Raises:
            WikipediaServiceException: If article extraction fails
        """
        try:
            # Set language
            wikipedia.set_lang(language)
            
            # Extract title from URL
            article_title = self.extract_article_title_from_url(url)
            
            logger.info(f"Fetching Wikipedia article: {article_title} ({language})")
            
            # Search for the article to get the exact title
            search_results = wikipedia.search(article_title, results=1)
            
            if not search_results:
                raise WikipediaServiceException(f"Article not found: {article_title}")
            
            # Get the article
            page = wikipedia.page(search_results[0], auto_suggest=False)
            
            # Get full content
            full_content = page.content
            
            # Parse sections
            sections = self._parse_sections(full_content)
            
            result = {
                "title": page.title,
                "url": page.url,
                "summary": page.summary,
                "full_content": full_content,
                "sections": sections,
                "language": language
            }
            
            logger.info(f"Successfully extracted article: {page.title} ({len(sections)} sections)")
            
            return result
            
        except wikipedia.exceptions.PageError as e:
            logger.error(f"Wikipedia page not found: {str(e)}")
            raise WikipediaServiceException(f"Article not found: {str(e)}")
        
        except wikipedia.exceptions.DisambiguationError as e:
            logger.error(f"Disambiguation page encountered: {str(e)}")
            raise WikipediaServiceException(
                f"Multiple articles found. Please be more specific. Options: {', '.join(e.options[:5])}"
            )
        
        except Exception as e:
            logger.error(f"Error extracting Wikipedia article: {str(e)}")
            raise WikipediaServiceException(f"Failed to extract article: {str(e)}")
    
    def _parse_sections(self, content: str) -> Dict[str, str]:
        """
        Parse article content into sections.
        
        Wikipedia sections are identified by === Section Name ===
        
        Args:
            content: Full article content
        
        Returns:
            Dict mapping section names to their content
        """
        sections = {}
        
        # Split by section markers (=== Section ===)
        # Pattern matches === Text === format
        section_pattern = r'===\s*(.+?)\s*==='
        
        # Find all section titles
        section_matches = list(re.finditer(section_pattern, content))
        
        if not section_matches:
            # No sections found, return full content as single section
            sections["Main Content"] = content
            return sections
        
        # Extract content for each section
        for i, match in enumerate(section_matches):
            section_name = match.group(1).strip()
            start_pos = match.end()
            
            # Find end position (start of next section or end of content)
            if i < len(section_matches) - 1:
                end_pos = section_matches[i + 1].start()
            else:
                end_pos = len(content)
            
            section_content = content[start_pos:end_pos].strip()
            
            if section_content:
                sections[section_name] = section_content
        
        # If there's content before the first section, add it as "Introduction"
        if section_matches:
            intro_content = content[:section_matches[0].start()].strip()
            if intro_content:
                sections = {"Introduction": intro_content, **sections}
        
        logger.info(f"Parsed {len(sections)} sections from article")
        
        return sections
    
    def get_article_summary(self, title: str, language: str = "fr", sentences: int = 5) -> str:
        """
        Get a quick summary of an article.
        
        Args:
            title: Article title
            language: Language code
            sentences: Number of sentences in summary
        
        Returns:
            str: Article summary
        """
        try:
            wikipedia.set_lang(language)
            summary = wikipedia.summary(title, sentences=sentences)
            
            logger.info(f"Retrieved summary for: {title}")
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting summary: {str(e)}")
            raise WikipediaServiceException(f"Failed to get summary: {str(e)}")


# Singleton instance
wikipedia_service = WikipediaService()
