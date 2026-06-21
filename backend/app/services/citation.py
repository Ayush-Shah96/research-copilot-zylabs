"""Citation service for managing research sources and references."""
import logging
from typing import List, Dict, Optional, Set
from datetime import datetime
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class Citation:
    """Represents a single citation/source."""
    
    def __init__(
        self,
        url: str,
        title: str = "",
        source_type: str = "web",
        date: Optional[str] = None,
        author: Optional[str] = None,
    ):
        """
        Initialize a citation.
        
        Args:
            url: Source URL
            title: Source title
            source_type: Type of source (web, news, academic, social_media)
            date: Publication date
            author: Author name if available
        """
        self.url = url
        self.title = title
        self.source_type = source_type
        self.date = date
        self.author = author
        self.added_at = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Optional[str]]:
        """Convert citation to dictionary."""
        return {
            "url": self.url,
            "title": self.title,
            "source_type": self.source_type,
            "date": self.date,
            "author": self.author,
        }
    
    def __repr__(self) -> str:
        return f"Citation(url={self.url[:50]}..., type={self.source_type})"


class CitationService:
    """Service for managing citations and sources."""
    
    def __init__(self):
        """Initialize citation service."""
        self.citations: Dict[str, Citation] = {}  # URL -> Citation mapping
        self.url_deduplication: Set[str] = set()
    
    def add_citation(
        self,
        url: str,
        title: str = "",
        source_type: str = "web",
        date: Optional[str] = None,
        author: Optional[str] = None,
    ) -> None:
        """
        Add a citation to the collection.
        
        Args:
            url: Source URL
            title: Source title
            source_type: Type of source
            date: Publication date
            author: Author name
        """
        if not url:
            return
        
        # Normalize URL for deduplication
        normalized_url = self._normalize_url(url)
        
        if normalized_url in self.url_deduplication:
            logger.debug(f"Citation already exists: {url}")
            return
        
        citation = Citation(
            url=url,
            title=title,
            source_type=source_type,
            date=date,
            author=author,
        )
        
        self.citations[normalized_url] = citation
        self.url_deduplication.add(normalized_url)
        
        logger.debug(f"Added citation: {title[:50] if title else 'Untitled'}")
    
    def add_citations_batch(self, citations: List[Dict[str, str]]) -> None:
        """
        Add multiple citations at once.
        
        Args:
            citations: List of citation dictionaries
        """
        for citation_data in citations:
            self.add_citation(
                url=citation_data.get("url", ""),
                title=citation_data.get("title", ""),
                source_type=citation_data.get("source_type", "web"),
                date=citation_data.get("date"),
                author=citation_data.get("author"),
            )
    
    def get_urls(self) -> List[str]:
        """
        Get list of all source URLs.
        
        Returns:
            List of URLs
        """
        return list(self.citations.keys())
    
    def get_citations(self) -> List[Citation]:
        """
        Get all citations.
        
        Returns:
            List of Citation objects
        """
        return list(self.citations.values())
    
    def get_citations_by_type(self, source_type: str) -> List[Citation]:
        """
        Get citations filtered by source type.
        
        Args:
            source_type: Type of source to filter by
            
        Returns:
            List of matching citations
        """
        return [
            citation for citation in self.citations.values()
            if citation.source_type == source_type
        ]
    
    def get_formatted_citations(self, style: str = "markdown") -> str:
        """
        Get formatted citations.
        
        Args:
            style: Citation style (markdown, html, apa, chicago)
            
        Returns:
            Formatted citations string
        """
        if not self.citations:
            return "No sources available."
        
        if style == "markdown":
            return self._format_markdown()
        elif style == "html":
            return self._format_html()
        elif style == "apa":
            return self._format_apa()
        else:
            return self._format_plain()
    
    def _format_markdown(self) -> str:
        """Format citations as markdown."""
        lines = ["## Sources\n"]
        
        for i, citation in enumerate(self.get_citations(), 1):
            line = f"{i}. [{citation.title or 'Untitled'}]({citation.url})"
            
            if citation.date:
                line += f" - {citation.date}"
            
            if citation.source_type != "web":
                line += f" ({citation.source_type})"
            
            lines.append(line)
        
        return "\n".join(lines)
    
    def _format_html(self) -> str:
        """Format citations as HTML."""
        lines = ["<div class='sources'><h3>Sources</h3><ol>"]
        
        for citation in self.get_citations():
            lines.append(
                f"<li><a href='{citation.url}' target='_blank'>"
                f"{citation.title or 'Untitled'}</a>"
            )
            
            if citation.date:
                lines.append(f" - {citation.date}")
            
            if citation.source_type != "web":
                lines.append(f" ({citation.source_type})")
            
            lines.append("</li>")
        
        lines.append("</ol></div>")
        return "".join(lines)
    
    def _format_apa(self) -> str:
        """Format citations as APA style."""
        lines = []
        
        for citation in self.get_citations():
            # Basic APA format: Author (Year). Title. Retrieved from URL
            author = citation.author or "Unknown Author"
            year = citation.date[:4] if citation.date else "n.d."
            title = citation.title or "Untitled"
            
            apa_citation = f"{author} ({year}). {title}. Retrieved from {citation.url}"
            lines.append(apa_citation)
        
        return "\n".join(lines)
    
    def _format_plain(self) -> str:
        """Format citations as plain text."""
        lines = ["Sources:\n"]
        
        for i, citation in enumerate(self.get_citations(), 1):
            lines.append(f"{i}. {citation.title or 'Untitled'}")
            lines.append(f"   URL: {citation.url}")
            
            if citation.date:
                lines.append(f"   Date: {citation.date}")
            
            if citation.source_type != "web":
                lines.append(f"   Type: {citation.source_type}")
            
            lines.append("")
        
        return "\n".join(lines)
    
    def _normalize_url(self, url: str) -> str:
        """
        Normalize URL for deduplication.
        
        Args:
            url: URL to normalize
            
        Returns:
            Normalized URL
        """
        # Remove trailing slashes and query parameters for comparison
        parsed = urlparse(url)
        normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        return normalized.rstrip("/").lower()
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get citation statistics.
        
        Returns:
            Dictionary with statistics
        """
        source_counts = {}
        for citation in self.citations.values():
            source_counts[citation.source_type] = source_counts.get(citation.source_type, 0) + 1
        
        return {
            "total_citations": len(self.citations),
            "unique_domains": len(set(
                urlparse(c.url).netloc for c in self.citations.values()
            )),
            "by_source_type": source_counts,
        }
    
    def clear(self) -> None:
        """Clear all citations."""
        self.citations.clear()
        self.url_deduplication.clear()
        logger.info("Citation service cleared")