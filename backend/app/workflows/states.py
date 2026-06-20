"""LangGraph workflow state definition."""
from typing import TypedDict, List, Optional, Dict, Any
from dataclasses import dataclass, field


class ResearchState(TypedDict, total=False):
    """State maintained throughout the research workflow."""
    
    # Input
    session_id: str
    company_name: str
    company_website: Optional[str]
    research_objective: str
    
    # Planner Node Output
    research_plan: str
    research_questions: List[str]
    search_keywords: List[str]
    data_sources: List[str]
    
    # Research Node Output
    raw_research_data: Dict[str, Any]
    company_info: Dict[str, str]
    website_content: Optional[str]
    products_info: str
    customers_info: str
    competitors_info: str
    news_articles: List[Dict[str, str]]
    social_media_data: Dict[str, Any]
    industry_data: Dict[str, Any]
    financial_data: Dict[str, Any]
    
    # Analysis Node Output
    analyzed_overview: str
    analyzed_products: str
    analyzed_customers: str
    analyzed_signals: str
    analyzed_risks: str
    key_insights: List[str]
    opportunities: List[str]
    competitive_advantages: List[str]
    
    # Quality Check Node Output
    quality_score: int
    quality_issues: List[str]
    requires_retry: bool
    retry_reason: Optional[str]
    quality_checks_passed: Dict[str, bool]
    confidence_score: float
    completeness_percentage: int
    
    # Reporter Node Output
    discovery_questions: List[Dict[str, str]]
    outreach_strategy: str
    unknowns: List[str]
    sources_used: List[str]
    
    # Final Report
    final_report: Dict[str, Any]
    
    # Metadata
    start_time: Optional[str]
    end_time: Optional[str]
    processing_status: str
    error_message: Optional[str]
    retry_count: int
    max_retries: int
    token_usage: Dict[str, int]


@dataclass
class WorkflowConfig:
    """Configuration for the research workflow."""
    
    # Model settings
    model_name: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 2000
    
    # Research settings
    research_depth: str = "comprehensive"  # basic, intermediate, comprehensive
    enable_web_search: bool = True
    search_result_count: int = 10
    
    # Quality settings
    quality_threshold: int = 70
    auto_retry: bool = True
    max_retries: int = 2
    
    # Timeout settings
    node_timeout: int = 300
    total_timeout: int = 600
    
    # Feature flags
    enable_social_media: bool = True
    enable_news_search: bool = True
    enable_industry_analysis: bool = True
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkflowConfig":
        """Create config from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})


@dataclass
class NodeMetadata:
    """Metadata about a workflow node."""
    
    name: str
    description: str
    timeout: int = 300
    retryable: bool = True
    critical: bool = False
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)


# Node metadata registry
NODE_METADATA = {
    "planner": NodeMetadata(
        name="Planner",
        description="Plans research strategy and questions",
        timeout=60,
        critical=True,
        outputs=["research_plan", "research_questions", "search_keywords"],
    ),
    "researcher": NodeMetadata(
        name="Researcher",
        description="Collects company research data",
        timeout=300,
        retryable=True,
        outputs=["raw_research_data", "company_info", "website_content"],
    ),
    "analyzer": NodeMetadata(
        name="Analyzer",
        description="Analyzes and synthesizes research data",
        timeout=240,
        retryable=True,
        outputs=[
            "analyzed_overview",
            "analyzed_products",
            "analyzed_customers",
            "analyzed_signals",
            "analyzed_risks",
        ],
    ),
    "quality_check": NodeMetadata(
        name="Quality Check",
        description="Validates research quality",
        timeout=120,
        critical=True,
        outputs=["quality_score", "quality_issues", "requires_retry"],
    ),
    "reporter": NodeMetadata(
        name="Reporter",
        description="Generates final research report",
        timeout=180,
        critical=True,
        outputs=[
            "discovery_questions",
            "outreach_strategy",
            "final_report",
        ],
    ),
}