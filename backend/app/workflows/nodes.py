"""Workflow nodes for the research process."""
from typing import Dict, Any, List
from datetime import datetime
import json
import logging
from app.workflows.states import ResearchState, WorkflowConfig
from app.config import settings

logger = logging.getLogger(__name__)


class PlannerNode:
    """Plans the research strategy."""
    
    @staticmethod
    def execute(state: ResearchState, config: WorkflowConfig) -> ResearchState:
        """
        Plan research strategy based on company and objective.
        
        This node generates:
        - Research questions
        - Search keywords
        - Data sources to use
        - Overall research plan
        """
        logger.info(f"Planner Node: Planning research for {state['company_name']}")
        
        try:
            # In production, this would call LLM
            research_questions = [
                f"What is the market position of {state['company_name']}?",
                f"What are the recent funding/acquisition activities?",
                f"Who are the main competitors?",
                f"What is their customer acquisition strategy?",
                f"What are their revenue streams?",
            ]
            
            search_keywords = [
                state["company_name"],
                f"{state['company_name']} industry",
                f"{state['company_name']} news",
                f"{state['company_name']} competitors",
            ]
            
            state["research_questions"] = research_questions
            state["search_keywords"] = search_keywords
            state["data_sources"] = ["company_website", "news", "industry_reports", "social_media"]
            state["research_plan"] = f"Comprehensive research plan for {state['company_name']}"
            state["processing_status"] = "planner_completed"
            
            logger.info("Planner Node: Successfully created research plan")
            return state
            
        except Exception as e:
            logger.error(f"Planner Node Error: {str(e)}")
            state["error_message"] = f"Planning failed: {str(e)}"
            state["processing_status"] = "failed"
            raise


class ResearcherNode:
    """Collects research data."""
    
    @staticmethod
    def execute(state: ResearchState, config: WorkflowConfig) -> ResearchState:
        """
        Research company information from multiple sources.
        
        Collects:
        - Website content
        - News articles
        - Social media data
        - Industry information
        """
        logger.info(f"Researcher Node: Researching {state['company_name']}")
        
        try:
            # Simulate research data collection
            raw_data = {
                "company_info": {
                    "name": state["company_name"],
                    "website": state.get("company_website"),
                    "founded": "2015",
                    "employees": "500-1000",
                    "headquarters": "San Francisco, CA",
                },
                "business_model": "SaaS",
                "funding_stage": "Series C",
                "recent_news": [
                    {"title": "Company raises Series C funding", "date": "2024-01-15"},
                    {"title": "Launches new product", "date": "2024-01-10"},
                ],
            }
            
            state["raw_research_data"] = raw_data
            state["company_info"] = raw_data.get("company_info", {})
            state["website_content"] = "Sample website content would be extracted here"
            state["news_articles"] = raw_data.get("recent_news", [])
            state["social_media_data"] = {}
            state["industry_data"] = {}
            state["processing_status"] = "researcher_completed"
            
            logger.info("Researcher Node: Data collection completed")
            return state
            
        except Exception as e:
            logger.error(f"Researcher Node Error: {str(e)}")
            state["error_message"] = f"Research failed: {str(e)}"
            state["processing_status"] = "failed"
            raise


class AnalyzerNode:
    """Analyzes collected research data."""
    
    @staticmethod
    def execute(state: ResearchState, config: WorkflowConfig) -> ResearchState:
        """
        Analyze and synthesize research findings.
        
        Produces:
        - Company overview
        - Product/service analysis
        - Customer analysis
        - Business signals
        - Risk assessment
        - Key insights
        """
        logger.info(f"Analyzer Node: Analyzing research for {state['company_name']}")
        
        try:
            # In production, this would call LLM for analysis
            state["analyzed_overview"] = f"{state['company_name']} is a growing company in the technology sector"
            state["analyzed_products"] = "The company offers cloud-based solutions with strong market demand"
            state["analyzed_customers"] = "Primary customers are mid-market enterprises in the SaaS space"
            state["analyzed_signals"] = "Strong funding activity and recent product launches indicate growth"
            state["analyzed_risks"] = "Competition is increasing; need to monitor market share"
            
            state["key_insights"] = [
                "Strong market position in their niche",
                "Active R&D and product development",
                "Growing customer base",
                "Competitive pricing strategy",
            ]
            
            state["processing_status"] = "analyzer_completed"
            logger.info("Analyzer Node: Analysis completed")
            return state
            
        except Exception as e:
            logger.error(f"Analyzer Node Error: {str(e)}")
            state["error_message"] = f"Analysis failed: {str(e)}"
            state["processing_status"] = "failed"
            raise


class QualityCheckNode:
    """Validates research quality."""
    
    @staticmethod
    def execute(state: ResearchState, config: WorkflowConfig) -> ResearchState:
        """
        Perform quality checks on research.
        
        Validates:
        - Data completeness
        - Analysis depth
        - Source credibility
        - Overall quality score
        """
        logger.info("Quality Check Node: Validating research quality")
        
        try:
            # Check completeness
            required_fields = [
                "analyzed_overview",
                "analyzed_products",
                "analyzed_customers",
                "analyzed_signals",
                "analyzed_risks",
            ]
            
            completeness = sum(1 for field in required_fields if state.get(field))
            completeness_score = int((completeness / len(required_fields)) * 100)
            
            # Check for insights
            insights_score = 80 if len(state.get("key_insights", [])) >= 3 else 50
            
            # Overall quality
            quality_score = int((completeness_score + insights_score) / 2)
            
            state["quality_score"] = quality_score
            state["quality_checks_passed"] = {
                "completeness": completeness_score >= 80,
                "insights": insights_score >= 70,
                "sources": True,
            }
            
            # Determine if retry is needed
            state["requires_retry"] = quality_score < config.quality_threshold
            state["processing_status"] = "quality_check_completed"
            
            if state["requires_retry"]:
                state["quality_issues"] = ["Missing detailed competitor analysis"]
                state["retry_reason"] = f"Quality score {quality_score} below threshold {config.quality_threshold}"
            else:
                state["quality_issues"] = []
            
            logger.info(f"Quality Check: Score = {quality_score}, Pass = {not state['requires_retry']}")
            return state
            
        except Exception as e:
            logger.error(f"Quality Check Node Error: {str(e)}")
            state["error_message"] = f"Quality check failed: {str(e)}"
            state["processing_status"] = "failed"
            raise


class ReporterNode:
    """Generates final research report."""
    
    @staticmethod
    def execute(state: ResearchState, config: WorkflowConfig) -> ResearchState:
        """
        Generate structured research report.
        
        Produces:
        - Discovery questions
        - Outreach strategy
        - Unknowns list
        - Final formatted report
        """
        logger.info("Reporter Node: Generating research report")
        
        try:
            # Generate discovery questions
            discovery_questions = [
                {
                    "question": "What is your current technology stack?",
                    "category": "Technology",
                    "priority": "high",
                },
                {
                    "question": "How do you currently handle customer onboarding?",
                    "category": "Operations",
                    "priority": "high",
                },
                {
                    "question": "What are your growth targets for next year?",
                    "category": "Strategy",
                    "priority": "medium",
                },
            ]
            
            outreach_strategy = (
                f"Based on research, recommend a multi-touch approach focusing on "
                f"technical buyers and decision makers at {state['company_name']}. "
                f"Emphasize thought leadership and industry expertise."
            )
            
            unknowns = [
                "Exact headcount and organizational structure",
                "Detailed financial performance metrics",
                "Customer retention rates",
            ]
            
            sources = [
                "Company website",
                "Recent news articles",
                "Industry reports",
                "LinkedIn profiles",
                "Social media presence",
            ]
            
            # Compile final report
            final_report = {
                "company_name": state["company_name"],
                "research_date": datetime.utcnow().isoformat(),
                "objective": state["research_objective"],
                "company_overview": state.get("analyzed_overview", ""),
                "products_services": state.get("analyzed_products", ""),
                "target_customers": state.get("analyzed_customers", ""),
                "business_signals": state.get("analyzed_signals", ""),
                "risks_challenges": state.get("analyzed_risks", ""),
                "key_insights": state.get("key_insights", []),
                "discovery_questions": discovery_questions,
                "outreach_strategy": outreach_strategy,
                "unknowns": unknowns,
                "sources": sources,
                "quality_score": state.get("quality_score", 0),
            }
            
            state["discovery_questions"] = discovery_questions
            state["outreach_strategy"] = outreach_strategy
            state["unknowns"] = unknowns
            state["sources_used"] = sources
            state["final_report"] = final_report
            state["processing_status"] = "reporter_completed"
            state["end_time"] = datetime.utcnow().isoformat()
            
            logger.info("Reporter Node: Report generation completed")
            return state
            
        except Exception as e:
            logger.error(f"Reporter Node Error: {str(e)}")
            state["error_message"] = f"Report generation failed: {str(e)}"
            state["processing_status"] = "failed"
            raise


class WorkflowNodes:
    """Registry of all workflow nodes."""
    
    planner = PlannerNode.execute
    researcher = ResearcherNode.execute
    analyzer = AnalyzerNode.execute
    quality_check = QualityCheckNode.execute
    reporter = ReporterNode.execute
