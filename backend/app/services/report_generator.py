"""Report generator service for creating structured research reports."""
import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.workflows.states import ResearchState
from app.services.llm import get_llm_service
from app.services.prompts import PromptsService

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Service for generating structured research reports."""

    def __init__(self):
        """Initialize the report generator."""
        self.llm_service = get_llm_service()

    def generate_discovery_questions(
        self,
        company_name: str,
        research_summary: str,
    ) -> List[Dict[str, str]]:
        """
        Generate discovery questions for sales engagement.
        
        Args:
            company_name: Name of the company
            research_summary: Summary of research findings
            
        Returns:
            List of discovery questions with metadata
        """
        logger.info(f"Generating discovery questions for {company_name}")
        
        try:
            prompt = PromptsService.get_discovery_questions_prompt(
                company_name,
                research_summary,
            )
            
            # Request JSON response
            schema = """[
                {
                    "question": "string",
                    "category": "string",
                    "priority": "high|medium|low"
                }
            ]"""
            
            result = self.llm_service.extract_json(prompt, schema)
            
            if isinstance(result, dict) and "error" in result:
                logger.error(f"Error generating discovery questions: {result['error']}")
                # Return default questions
                return self._get_default_questions()
            
            # Ensure it's a list
            questions = result if isinstance(result, list) else [result]
            
            logger.info(f"Generated {len(questions)} discovery questions")
            return questions[:10]  # Limit to 10 questions
            
        except Exception as e:
            logger.error(f"Error generating discovery questions: {str(e)}")
            return self._get_default_questions()

    def generate_outreach_strategy(
        self,
        company_name: str,
        company_overview: str,
        key_signals: str,
        identified_risks: str,
    ) -> str:
        """
        Generate recommended outreach strategy.
        
        Args:
            company_name: Name of the company
            company_overview: Overview of the company
            key_signals: Key business signals
            identified_risks: Identified risks and challenges
            
        Returns:
            Outreach strategy recommendation
        """
        logger.info(f"Generating outreach strategy for {company_name}")
        
        try:
            prompt = f"""Based on this research about {company_name}, create a concise outreach strategy:

COMPANY OVERVIEW:
{company_overview}

KEY SIGNALS:
{key_signals}

IDENTIFIED RISKS:
{identified_risks}

Provide a 3-4 paragraph outreach strategy that:
1. Identifies the best entry point and stakeholders
2. Suggests specific value propositions to emphasize
3. Recommends timing and approach
4. Highlights key talking points to address concerns"""
            
            strategy = self.llm_service.generate(prompt, temperature=0.6)
            
            logger.info("Outreach strategy generated successfully")
            return strategy
            
        except Exception as e:
            logger.error(f"Error generating outreach strategy: {str(e)}")
            return "Contact through company website to identify decision makers and discuss mutual opportunities."

    def identify_unknowns(
        self,
        company_name: str,
        research_data: str,
    ) -> List[str]:
        """
        Identify remaining unknowns and information gaps.
        
        Args:
            company_name: Name of the company
            research_data: Summary of gathered research data
            
        Returns:
            List of identified unknowns
        """
        logger.info(f"Identifying unknowns for {company_name}")
        
        try:
            prompt = f"""Based on this research about {company_name}, identify the key information gaps and unknowns:

RESEARCH GATHERED:
{research_data}

List 5-7 specific pieces of information that would be valuable to learn during customer conversations
but were not available through public research. Format as a JSON array of strings.

["Unknown 1", "Unknown 2", ...]"""
            
            result = self.llm_service.extract_json(prompt)
            
            if isinstance(result, dict) and "error" in result:
                logger.warning(f"Error identifying unknowns: {result['error']}")
                return self._get_default_unknowns()
            
            # Ensure it's a list
            unknowns = result if isinstance(result, list) else [result]
            
            logger.info(f"Identified {len(unknowns)} key unknowns")
            return unknowns[:10]
            
        except Exception as e:
            logger.error(f"Error identifying unknowns: {str(e)}")
            return self._get_default_unknowns()

    def generate_report(self, state: ResearchState) -> Dict[str, Any]:
        """
        Generate a comprehensive research report from workflow state.
        
        Args:
            state: Final workflow state with all research data
            
        Returns:
            Structured research report
        """
        logger.info(f"Generating final report for {state.get('company_name')}")
        
        try:
            company_name = state.get("company_name", "Unknown Company")
            
            # Extract key information from state
            company_overview = state.get("analyzed_overview", "")
            products_services = state.get("analyzed_products", "")
            target_customers = state.get("analyzed_customers", "")
            business_signals = state.get("analyzed_signals", "")
            risks_challenges = state.get("analyzed_risks", "")
            key_insights = state.get("key_insights", [])
            sources_used = state.get("sources_used", [])
            quality_score = state.get("quality_score", 0)
            
            # Generate discovery questions
            research_summary = f"{company_overview}\n{products_services}\n{business_signals}"
            discovery_questions = self.generate_discovery_questions(
                company_name,
                research_summary,
            )
            
            # Generate outreach strategy
            outreach_strategy = self.generate_outreach_strategy(
                company_name,
                company_overview,
                business_signals,
                risks_challenges,
            )
            
            # Identify unknowns
            research_data_summary = f"Overview: {company_overview}\nProducts: {products_services}\nCustomers: {target_customers}"
            unknowns = self.identify_unknowns(company_name, research_data_summary)
            
            # Compile final report
            report = {
                "metadata": {
                    "generated_at": datetime.utcnow().isoformat(),
                    "company_name": company_name,
                    "company_website": state.get("company_website"),
                    "research_objective": state.get("research_objective"),
                },
                "executive_summary": self._generate_executive_summary(
                    company_name,
                    company_overview,
                    key_insights,
                ),
                "company_overview": company_overview,
                "products_services": products_services,
                "target_customers": target_customers,
                "business_signals": business_signals,
                "risks_challenges": risks_challenges,
                "key_insights": key_insights,
                "discovery_questions": discovery_questions,
                "outreach_strategy": outreach_strategy,
                "unknowns": unknowns,
                "sources": sources_used,
                "quality": {
                    "quality_score": quality_score,
                    "completeness_percentage": self._calculate_completeness(state),
                },
            }
            
            logger.info(f"Final report generated successfully for {company_name}")
            return report
            
        except Exception as e:
            logger.error(f"Error generating final report: {str(e)}")
            return self._get_default_report(state)

    def _generate_executive_summary(
        self,
        company_name: str,
        overview: str,
        insights: List[str],
    ) -> str:
        """
        Generate an executive summary.
        
        Args:
            company_name: Company name
            overview: Company overview text
            insights: Key insights list
            
        Returns:
            Executive summary
        """
        try:
            prompt = f"""Create a 2-3 sentence executive summary of {company_name}:

OVERVIEW: {overview}

KEY INSIGHTS: {', '.join(insights[:3])}

Make it compelling and suitable for a sales pitch."""
            
            summary = self.llm_service.generate(prompt, max_tokens=300, temperature=0.6)
            return summary
            
        except Exception as e:
            logger.error(f"Error generating executive summary: {str(e)}")
            return f"{company_name} is a company with notable market presence and growth indicators."

    def _calculate_completeness(self, state: ResearchState) -> int:
        """
        Calculate research completeness percentage.
        
        Args:
            state: Workflow state
            
        Returns:
            Completeness percentage (0-100)
        """
        required_fields = [
            "analyzed_overview",
            "analyzed_products",
            "analyzed_customers",
            "analyzed_signals",
            "analyzed_risks",
            "key_insights",
        ]
        
        filled = sum(1 for field in required_fields if state.get(field))
        completeness = int((filled / len(required_fields)) * 100)
        
        return min(completeness, 100)

    @staticmethod
    def _get_default_questions() -> List[Dict[str, str]]:
        """Get default discovery questions."""
        return [
            {
                "question": "What are your primary business objectives for the next 12 months?",
                "category": "Strategy",
                "priority": "high",
            },
            {
                "question": "How is your current technology stack supporting your business growth?",
                "category": "Technology",
                "priority": "high",
            },
            {
                "question": "What are your biggest operational challenges today?",
                "category": "Operations",
                "priority": "high",
            },
            {
                "question": "How do you currently handle customer acquisition and retention?",
                "category": "Sales/Marketing",
                "priority": "medium",
            },
            {
                "question": "What does success look like for your organization?",
                "category": "Strategy",
                "priority": "medium",
            },
        ]

    @staticmethod
    def _get_default_unknowns() -> List[str]:
        """Get default unknowns list."""
        return [
            "Detailed organizational structure and key decision makers",
            "Internal budget allocation and spending priorities",
            "Specific technology stack and infrastructure details",
            "Customer acquisition cost and lifetime value metrics",
            "Recent executive changes or strategic initiatives",
        ]

    @staticmethod
    def _get_default_report(state: ResearchState) -> Dict[str, Any]:
        """Get a default report structure."""
        company_name = state.get("company_name", "Unknown Company")
        
        return {
            "metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "company_name": company_name,
                "company_website": state.get("company_website"),
                "research_objective": state.get("research_objective"),
            },
            "executive_summary": f"Research report for {company_name} with available public information.",
            "company_overview": state.get("analyzed_overview", "Information pending"),
            "products_services": state.get("analyzed_products", "Information pending"),
            "target_customers": state.get("analyzed_customers", "Information pending"),
            "business_signals": state.get("analyzed_signals", "Information pending"),
            "risks_challenges": state.get("analyzed_risks", "Information pending"),
            "key_insights": state.get("key_insights", []),
            "discovery_questions": ReportGenerator._get_default_questions(),
            "outreach_strategy": "Contact through official channels to discuss mutual business opportunities.",
            "unknowns": ReportGenerator._get_default_unknowns(),
            "sources": state.get("sources_used", []),
            "quality": {
                "quality_score": state.get("quality_score", 0),
                "completeness_percentage": 60,
            },
        }


# Global instance
_report_generator: Optional[ReportGenerator] = None


def get_report_generator() -> ReportGenerator:
    """Get or create the global report generator instance."""
    global _report_generator
    
    if _report_generator is None:
        _report_generator = ReportGenerator()
    
    return _report_generator