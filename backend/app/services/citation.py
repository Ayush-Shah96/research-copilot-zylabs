"""Citation formatting service for research sources."""
import logging
from typing import List, Dict, Optional, Tuple
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class Citation:
    """Represents a research citation."""
    
    def __init__(
        self,
        title: str,
        url: str,
        date: Optional[str] = None,
        author: Optional[str] = None,
        source_type: str = "web",
    ):
        """
        Initialize a citation.
        
        Args:
            title: Citation title
            url: Source URL
            date: Publication date
            author: Author name
            source_type: Type of source (web, news, social, academic)
        """
        self.title = title
        self.url = url
        self.date = date
        self.author = author
        self.source_type = source_type

    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary."""
        return {
            "title": self.title,
            "url": self.url,
            "date": self.date,
            "author": self.author,
            "source_type": self.source_type,
        }

    def to_mla(self) -> str:
        """Format citation in MLA style."""
        if self.author:
            citation = f"{self.author}. \"{self.title}.\" "
        else:
            citation = f"\"{self.title}.\" "
        
        # Extract domain from URL
        domain = self._extract_domain(self.url)
        citation += f"{domain}. "
        
        if self.date:
            citation += f"Accessed {self.date}. "
        
        citation += f"<{self.url}>"
        
        return citation

    def to_apa(self) -> str:
        """Format citation in APA style."""
        if self.author:
            citation = f"{self.author}. "
        else:
            citation = ""
        
        citation += f"({self.date or 'n.d.'}). "
        citation += f"{self.title}. Retrieved from {self.url}"
        
        return citation

    def to_chicago(self) -> str:
        """Format citation in Chicago style."""
        if self.author:
            citation = f"{self.author}. "
        
        citation += f"\"{self.title}.\" "
        
        # Extract domain
        domain = self._extract_domain(self.url)
        citation += f"Accessed {self.date or 'n.d.'}. {self.url}"
        
        return citation

    def to_html(self) -> str:
        """Format citation as HTML link."""
        return f'<a href="{self.url}" target="_blank">{self.title}</a>'

    def to_markdown(self) -> str:
        """Format citation as Markdown link."""
        return f"[{self.title}]({self.url})"

    @staticmethod
    def _extract_domain(url: str) -> str:
        """Extract domain from URL."""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc or parsed.path
            # Remove www. prefix if present
            if domain.startswith("www."):
                domain = domain[4:]
            return domain
        except Exception:
            return url


class CitationService:
    """Service for managing and formatting citations."""

    def __init__(self):
        """Initialize citation service."""
        self.citations: Dict[str, Citation] = {}
        self.citation_count = 0

    def add_citation(
        self,
        url: str,
        title: str,
        date: Optional[str] = None,
        author: Optional[str] = None,
        source_type: str = "web",
    ) -> int:
        """
        Add a citation and get its reference number.
        
        Args:
            url: Source URL
            title: Citation title
            date: Publication date
            author: Author name
            source_type: Type of source
            
        Returns:
            Citation reference number
        """
        # Check if URL already exists
        for ref_num, citation in self.citations.items():
            if citation.url == url:
                return int(ref_num)
        
        # Add new citation
        self.citation_count += 1
        ref_num = str(self.citation_count)
        
        citation = Citation(
            title=title,
            url=url,
            date=date,
            author=author,
            source_type=source_type,
        )
        
        self.citations[ref_num] = citation
        logger.info(f"Added citation {ref_num}: {title}")
        
        return self.citation_count

    def add_citations_from_urls(self, urls: List[str]) -> List[int]:
        """
        Add multiple citations from URLs.
        
        Args:
            urls: List of URLs to add
            
        Returns:
            List of citation reference numbers
        """
        ref_numbers = []
        for url in urls:
            # Extract title from URL if possible
            title = self._extract_title_from_url(url)
            ref_num = self.add_citation(url, title)
            ref_numbers.append(ref_num)
        
        return ref_numbers

    def get_citation(self, ref_num: int) -> Optional[Citation]:
        """
        Get a citation by reference number.
        
        Args:
            ref_num: Citation reference number
            
        Returns:
            Citation object or None
        """
        return self.citations.get(str(ref_num))

    def format_bibliography(self, style: str = "markdown") -> str:
        """
        Format all citations as a bibliography.
        
        Args:
            style: Citation style (markdown, mla, apa, chicago, html)
            
        Returns:
            Formatted bibliography
        """
        if not self.citations:
            return "No sources cited."
        
        logger.info(f"Formatting bibliography with {len(self.citations)} citations in {style}")
        
        bibliography = []
        
        if style == "markdown":
            bibliography.append("## Sources\n")
            for ref_num in sorted(self.citations.keys(), key=int):
                citation = self.citations[ref_num]
                bibliography.append(f"{ref_num}. {citation.to_markdown()}")
        
        elif style == "mla":
            bibliography.append("Works Cited\n")
            for ref_num in sorted(self.citations.keys(), key=int):
                citation = self.citations[ref_num]
                bibliography.append(f"{citation.to_mla()}")
        
        elif style == "apa":
            bibliography.append("References\n")
            for ref_num in sorted(self.citations.keys(), key=int):
                citation = self.citations[ref_num]
                bibliography.append(f"{citation.to_apa()}")
        
        elif style == "chicago":
            bibliography.append("Bibliography\n")
            for ref_num in sorted(self.citations.keys(), key=int):
                citation = self.citations[ref_num]
                bibliography.append(f"{citation.to_chicago()}")
        
        elif style == "html":
            bibliography.append("<div class='bibliography'><h2>Sources</h2><ul>")
            for ref_num in sorted(self.citations.keys(), key=int):
                citation = self.citations[ref_num]
                bibliography.append(f"<li>{citation.to_html()}</li>")
            bibliography.append("</ul></div>")
        
        return "\n".join(bibliography)

    def get_citation_list(self) -> List[Dict[str, str]]:
        """
        Get all citations as a list of dictionaries.
        
        Returns:
            List of citation dicts
        """
        return [
            {
                "ref_num": ref_num,
                **citation.to_dict(),
            }
            for ref_num in sorted(self.citations.keys(), key=int)
            for citation in [self.citations[ref_num]]
        ]

    def get_urls(self) -> List[str]:
        """
        Get all citation URLs.
        
        Returns:
            List of URLs
        """
        return [citation.url for citation in self.citations.values()]

    def clear(self) -> None:
        """Clear all citations."""
        self.citations.clear()
        self.citation_count = 0
        logger.info("Cleared all citations")

    @staticmethod
    def _extract_title_from_url(url: str) -> str:
        """
        Extract a reasonable title from a URL.
        
        Args:
            url: URL to extract title from
            
        Returns:
            Extracted title
        """
        try:
            parsed = urlparse(url)
            
            # Try to get domain name
            domain = parsed.netloc.replace("www.", "").split(".")[0]
            
            # Try to get path
            path = parsed.path.strip("/").split("/")[-1]
            if path and path.endswith(".html"):
                path = path[:-5]
            
            if path:
                title = f"{domain.title()} - {path.replace('-', ' ').title()}"
            else:
                title = f"{domain.title()}"
            
            return title
        except Exception:
            return "Source"

    @staticmethod
    def create_citation_index(text: str, citations: List[str]) -> Tuple[str, Dict[int, str]]:
        """
        Create indexed citations in text.
        
        Args:
            text: Text to add citations to
            citations: List of citations to add
            
        Returns:
            Tuple of (indexed text, citation mapping)
        """
        citation_map = {}
        
        for i, citation in enumerate(citations, 1):
            text += f"\n[{i}] {citation}"
            citation_map[i] = citation
        
        return text, citation_map