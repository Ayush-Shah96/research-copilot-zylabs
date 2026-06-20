"""Search service abstraction for company research."""
import logging
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
from datetime import datetime
import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from app.config import settings

logger = logging.getLogger(__name__)


class SearchResult:
    """Represents a single search result."""
    
    def __init__(
        self,
        title: str,
        url: str,
        snippet: str,
        source: str = "unknown",
        date: Optional[str] = None,
        relevance_score: float = 1.0,
    ):
        """
        Initialize a search result.
        
        Args:
            title: Result title
            url: Result URL
            snippet: Content snippet
            source: Source identifier
            date: Publication date if available
            relevance_score: Relevance score (0-1)
        """
        self.title = title
        self.url = url
        self.snippet = snippet
        self.source = source
        self.date = date
        self.relevance_score = relevance_score

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "title": self.title,
            "url": self.url,
            "snippet": self.snippet,
            "source": self.source,
            "date": self.date,
            "relevance_score": self.relevance_score,
        }


class SearchProvider(ABC):
    """Abstract base class for search providers."""
    
    @abstractmethod
    def search(self, query: str, limit: int = 10) -> List[SearchResult]:
        """
        Execute a search query.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of search results
        """
        pass


class TavilySearchProvider(SearchProvider):
    """Tavily Search provider implementation."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Tavily search provider.
        
        Args:
            api_key: Tavily API key (uses settings if not provided)
        """
        self.api_key = api_key or settings.SEARCH_API_KEY
        self.base_url = "https://api.tavily.com/search"
        
        if not self.api_key:
            logger.warning("Tavily API key not configured")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.HTTPError,)),
        reraise=True,
    )
    def search(self, query: str, limit: int = 10) -> List[SearchResult]:
        """
        Search using Tavily API.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of search results
        """
        logger.info(f"Searching Tavily for: {query}")
        
        try:
            payload = {
                "api_key": self.api_key,
                "query": query,
                "max_results": limit,
                "include_answer": True,
            }
            
            with httpx.Client(timeout=10.0) as client:
                response = client.post(self.base_url, json=payload)
                response.raise_for_status()
            
            data = response.json()
            results = []
            
            for result in data.get("results", []):
                search_result = SearchResult(
                    title=result.get("title", ""),
                    url=result.get("url", ""),
                    snippet=result.get("content", ""),
                    source="tavily",
                    date=result.get("published_date"),
                )
                results.append(search_result)
            
            logger.info(f"Found {len(results)} results from Tavily")
            return results
            
        except httpx.HTTPError as e:
            logger.error(f"Tavily search error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in Tavily search: {str(e)}")
            return []


class BraveSearchProvider(SearchProvider):
    """Brave Search provider implementation."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Brave search provider.
        
        Args:
            api_key: Brave API key (uses settings if not provided)
        """
        self.api_key = api_key or settings.SEARCH_API_KEY
        self.base_url = "https://api.search.brave.com/res/v1/web/search"
        
        if not self.api_key:
            logger.warning("Brave API key not configured")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.HTTPError,)),
        reraise=True,
    )
    def search(self, query: str, limit: int = 10) -> List[SearchResult]:
        """
        Search using Brave Search API.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of search results
        """
        logger.info(f"Searching Brave for: {query}")
        
        try:
            headers = {"Accept": "application/json", "X-Subscription-Token": self.api_key}
            params = {"q": query, "count": limit}
            
            with httpx.Client(timeout=10.0) as client:
                response = client.get(
                    self.base_url,
                    headers=headers,
                    params=params,
                )
                response.raise_for_status()
            
            data = response.json()
            results = []
            
            for result in data.get("web", {}).get("results", []):
                search_result = SearchResult(
                    title=result.get("title", ""),
                    url=result.get("url", ""),
                    snippet=result.get("description", ""),
                    source="brave",
                )
                results.append(search_result)
            
            logger.info(f"Found {len(results)} results from Brave")
            return results
            
        except httpx.HTTPError as e:
            logger.error(f"Brave search error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in Brave search: {str(e)}")
            return []


class MockSearchProvider(SearchProvider):
    """Mock search provider for testing."""
    
    def search(self, query: str, limit: int = 10) -> List[SearchResult]:
        """
        Return mock search results.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of mock search results
        """
        logger.info(f"Mock search for: {query}")
        
        mock_results = [
            SearchResult(
                title=f"Result 1 for {query}",
                url=f"https://example.com/result1",
                snippet=f"This is a mock result about {query}",
                source="mock",
            ),
            SearchResult(
                title=f"Result 2 for {query}",
                url=f"https://example.com/result2",
                snippet=f"Another mock result related to {query}",
                source="mock",
            ),
        ]
        
        return mock_results[:limit]


class SearchService:
    """Search service with provider abstraction."""
    
    def __init__(self, provider: Optional[SearchProvider] = None):
        """
        Initialize search service.
        
        Args:
            provider: Search provider instance (creates from settings if None)
        """
        if provider:
            self.provider = provider
        else:
            self.provider = self._create_provider(settings.SEARCH_PROVIDER)
    
    def _create_provider(self, provider_name: str) -> SearchProvider:
        """
        Create a search provider based on configuration.
        
        Args:
            provider_name: Name of the provider
            
        Returns:
            Configured search provider
        """
        provider_name = provider_name.lower() if provider_name else "tavily"
        
        if provider_name == "tavily":
            return TavilySearchProvider()
        elif provider_name == "brave":
            return BraveSearchProvider()
        elif provider_name == "mock":
            return MockSearchProvider()
        else:
            logger.warning(f"Unknown provider '{provider_name}', using mock")
            return MockSearchProvider()
    
    def search_company(self, company_name: str, limit: int = 5) -> List[SearchResult]:
        """
        Search for company information.
        
        Args:
            company_name: Name of the company
            limit: Maximum number of results
            
        Returns:
            List of search results
        """
        logger.info(f"Searching company info for: {company_name}")
        query = f"{company_name} company information about products services"
        
        try:
            return self.provider.search(query, limit)
        except Exception as e:
            logger.error(f"Error searching company info: {str(e)}")
            return []
    
    def search_news(self, company_name: str, limit: int = 5) -> List[SearchResult]:
        """
        Search for recent news about company.
        
        Args:
            company_name: Name of the company
            limit: Maximum number of results
            
        Returns:
            List of news articles
        """
        logger.info(f"Searching news for: {company_name}")
        query = f"{company_name} news recent 2024"
        
        try:
            return self.provider.search(query, limit)
        except Exception as e:
            logger.error(f"Error searching news: {str(e)}")
            return []
    
    def search_products(self, company_name: str, limit: int = 5) -> List[SearchResult]:
        """
        Search for company products and services.
        
        Args:
            company_name: Name of the company
            limit: Maximum number of results
            
        Returns:
            List of search results
        """
        logger.info(f"Searching products for: {company_name}")
        query = f"{company_name} products services features"
        
        try:
            return self.provider.search(query, limit)
        except Exception as e:
            logger.error(f"Error searching products: {str(e)}")
            return []
    
    def search_competitors(self, company_name: str, industry: Optional[str] = None, limit: int = 5) -> List[SearchResult]:
        """
        Search for competitors.
        
        Args:
            company_name: Name of the company
            industry: Industry name if known
            limit: Maximum number of results
            
        Returns:
            List of search results
        """
        logger.info(f"Searching competitors for: {company_name}")
        
        if industry:
            query = f"{industry} competitors alternatives to {company_name}"
        else:
            query = f"competitors alternatives to {company_name}"
        
        try:
            return self.provider.search(query, limit)
        except Exception as e:
            logger.error(f"Error searching competitors: {str(e)}")
            return []
    
    def search_financials(self, company_name: str, limit: int = 5) -> List[SearchResult]:
        """
        Search for financial information.
        
        Args:
            company_name: Name of the company
            limit: Maximum number of results
            
        Returns:
            List of search results
        """
        logger.info(f"Searching financials for: {company_name}")
        query = f"{company_name} funding revenue financial performance Series"
        
        try:
            return self.provider.search(query, limit)
        except Exception as e:
            logger.error(f"Error searching financials: {str(e)}")
            return []
    
    def search_custom(self, query: str, limit: int = 10) -> List[SearchResult]:
        """
        Execute a custom search query.
        
        Args:
            query: Custom search query
            limit: Maximum number of results
            
        Returns:
            List of search results
        """
        logger.info(f"Custom search: {query}")
        
        try:
            return self.provider.search(query, limit)
        except Exception as e:
            logger.error(f"Error in custom search: {str(e)}")
            return []


# Global instance
_search_service: Optional[SearchService] = None


def get_search_service() -> SearchService:
    """Get or create the global search service instance."""
    global _search_service
    
    if _search_service is None:
        _search_service = SearchService()
    
    return _search_service