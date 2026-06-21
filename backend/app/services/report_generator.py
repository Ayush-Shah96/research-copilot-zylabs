"""Report generation service for creating structured research reports."""
import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.workflows.states import ResearchState
from app.services.llm import get_llm_service
from app.services.prompts import PromptsService
from app.services.citation import CitationService

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generates structured research reports from workflow state."""
    
    def __init__(self):
        """Initialize the report generator."""
        self.llm = get_llm_service()
        self.citation_service = CitationService()
    
    def generate_report(self, state: ResearchState) -> Dict[str, Any]:
        """
        Generate a comprehensive research report from workflow state.
        
        Args:
            state: Final research workflow state
            
        Returns:
            Complete report as dictionary
        """
        logger.info(f"Generating report for {state.get('company_name')}")
        
        try:
            company_name = state.get("company_name", "Unknown Company")
            
            # Prepare analysis summary
            analysis_summary = self._prepare_analysis_summary(state)
            
            # Generate discovery questions
            discovery_questions = self._generate_discovery_questions(
                company_name,
                analysis_summary,
                state
            )
            
            # Generate outreach strategy
            outreach_strategy = self._generate_outreach_strategy(
                company_name,
                analysis_summary,
                state
            )
            
            # Compile unknowns
            unknowns = self._compile_unknowns(state)
            
            # Get sources
            sources = state.get("sources_used", [])
            
            # Create final report
            final_report = {
                "company_name": company_name,
                "generated_at": datetime.utcnow().isoformat(),
                "research_objective": state.get("research_objective", ""),
                "executive_summary": self._create_executive_summary(state),
                "company_overview": state.get("analyzed_overview", ""),
                "products_services": state.get("analyzed_products", ""),
                "target_customers": state.get("analyzed_customers", ""),
                "business_signals": state.get("analyzed_signals", ""),
                "risks_challenges": state.get("analyzed_risks", ""),
                "key_insights": state.get("key_insights", []),
                "opportunities": state.get("opportunities", []),
                "competitive_advantages": state.get("competitive_advantages", []),
                "discovery_questions": discovery_questions,
                "outreach_strategy": outreach_strategy,
                "unknowns": unknowns,
                "sources": sources,
                "quality_metrics": {
                    "quality_score": state.get("quality_score", 0),
                    "confidence_score": state.get("confidence_score", 0),
                    "completeness": state.get("completeness_percentage", 0),
                    "quality_checks": state.get("quality_checks_passed", {}),
                },
                "metadata": {
                    "research_depth": "comprehensive",
                    "source_count": len(sources),
                    "insights_count": len(state.get("key_insights", [])),
                    "questions_count": len(discovery_questions),
                }
            }
            
            logger.info(f"Report generated successfully with {len(discovery_questions)} questions")
            return final_report
            
        except Exception as e:
            logger.error(f"Report generation failed: {str(e)}")
            raise
    
    def _prepare_analysis_summary(self, state: ResearchState) -> str:
        """Prepare analysis summary for prompts."""
        return f"""
COMPANY: {state.get('company_name', 'N/A')}
OVERVIEW: {state.get('analyzed_overview', 'N/A')[:500]}
PRODUCTS: {state.get('analyzed_products', 'N/A')[:400]}
CUSTOMERS: {state.get('analyzed_customers', 'N/A')[:400]}
SIGNALS: {state.get('analyzed_signals', 'N/A')[:400]}
RISKS: {state.get('analyzed_risks', 'N/A')[:400]}
INSIGHTS: {', '.join(state.get('key_insights', [])[:5])}
"""
    
    def _generate_discovery_questions(
        self,
        company_name: str,
        analysis_summary: str,
        state: ResearchState
    ) -> List[Dict[str, str]]:
        """
        Generate discovery questions for sales conversations.
        
        Args:
            company_name: Company name
            analysis_summary: Analysis summary text
            state: Research state
            
        Returns:
            List of discovery questions with metadata
        """
        logger.info(f"Generating discovery questions for {company_name}")
        
        try:
            system_prompt = PromptsService.get_reporter_system_prompt()
            user_prompt = PromptsService.get_discovery_questions_prompt(
                company_name,
                analysis_summary
            )
            
            response = self.llm.chat(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.7,
                max_tokens=2000
            )
            
            # Try to extract JSON
            try:
                json_prompt = f"""Extract discovery questions from this response and return as JSON array:

{response}

Return JSON array with this structure:
[
    {{"question": "Question text?", "category": "category", "priority": "high"}}
]"""
                
                questions_data = self.llm.extract_json(json_prompt)
                
                if isinstance(questions_data, list):
                    return questions_data[:10]  # Limit to 10 questions
                elif isinstance(questions_data, dict) and "questions" in questions_data:
                    return questions_data["questions"][:10]
            except Exception as e:
                logger.warning(f"Could not parse questions JSON: {str(e)}")
            
            # Fallback: Parse response manually
            return self._parse_discovery_questions(response)
            
        except Exception as e:
            logger.error(f"Error generating discovery questions: {str(e)}")
            return self._default_discovery_questions(company_name)
    
    def _generate_outreach_strategy(
        self,
        company_name: str,
        analysis_summary: str,
        state: ResearchState
    ) -> str:
        """
        Generate recommended outreach strategy.
        
        Args:
            company_name: Company name
            analysis_summary: Analysis summary
            state: Research state
            
        Returns:
            Outreach strategy text
        """
        logger.info(f"Generating outreach strategy for {company_name}")
        
        try:
            prompt = f"""Based on this research about {company_name}, develop a strategic outreach approach:

{analysis_summary}

Create a concise outreach strategy that includes:
1. Key messaging angles
2. Best channels for engagement
3. Recommended conversation starters
4. Timeline and cadence suggestions
5. Success criteria

Be specific and actionable."""
            
            response = self.llm.generate(prompt, temperature=0.7, max_tokens=1500)
            return response
            
        except Exception as e:
            logger.error(f"Error generating outreach strategy: {str(e)}")
            return f"Schedule introductory call with {company_name} to understand their business needs and explore partnership opportunities."
    
    def _compile_unknowns(self, state: ResearchState) -> List[str]:
        """
        Compile list of unknowns and information gaps.
        
        Args:
            state: Research state
            
        Returns:
            List of unknown items
        """
        unknowns = []
        
        # Check for missing analysis sections
        if not state.get("analyzed_customers"):
            unknowns.append("Detailed customer segmentation and target market breakdown")
        
        if not state.get("analyzed_risks"):
            unknowns.append("Specific business risks and market challenges")
        
        if not state.get("financial_data"):
            unknowns.append("Financial metrics, funding history, and revenue information")
        
        if len(state.get("news_articles", [])) < 2:
            unknowns.append("Recent company news and product announcements")
        
        # Add generic unknowns
        unknowns.extend([
            "Specific go-to-market strategy and customer acquisition approach",
            "Internal organizational structure and key leadership details",
            "Detailed pricing strategy and packaging",
        ])
        
        return unknowns[:10]  # Return top 10 unknowns
    
    def _create_executive_summary(self, state: ResearchState) -> str:
        """
        Create executive summary from research findings.
        
        Args:
            state: Research state
            
        Returns:
            Executive summary text
        """
        company_name = state.get("company_name", "Company")
        overview = state.get("analyzed_overview", "")[:200]
        insights = state.get("key_insights", [])[:3]
        
        summary = f"{company_name} is a company of interest based on recent research. "
        
        if overview:
            summary += f"{overview} "
        
        if insights:
            summary += f"Key insights include: {', '.join(insights)}. "
        
        summary += "Detailed analysis and discovery questions are provided below for sales engagement."
        
        return summary
    
    def _parse_discovery_questions(self, response: str) -> List[Dict[str, str]]:
        """
        Parse discovery questions from unstructured response.
        
        Args:
            response: LLM response text
            
        Returns:
            List of parsed questions
        """
        questions = []
        
        # Extract numbered items (1., 2., etc.)
        lines = response.split("\n")
        current_question = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if line starts with number
            if line[0].isdigit() and "." in line[:3]:
                if current_question:
                    questions.append(current_question)
                
                question_text = line.split(".", 1)[1].strip()
                current_question = {
                    "question": question_text,
                    "category": "discovery",
                    "priority": "medium"
                }
        
        if current_question:
            questions.append(current_question)
        
        # Return at least some questions
        return questions if questions else self._default_discovery_questions("Company")
    
    def _default_discovery_questions(self, company_name: str) -> List[Dict[str, str]]:
        """Get default discovery questions."""
        return [
            {
                "question": f"What is {company_name}'s primary business model and revenue streams?",
                "category": "business_model",
                "priority": "high"
            },
            {
                "question": f"Who are {company_name}'s main target customers and market segments?",
                "category": "market",
                "priority": "high"
            },
            {
                "question": f"What are the key products/services {company_name} offers?",
                "category": "products",
                "priority": "high"
            },
            {
                "question": f"What recent developments or announcements has {company_name} made?",
                "category": "signals",
                "priority": "medium"
            },
            {
                "question": f"What are {company_name}'s main competitors and how do they differentiate?",
                "category": "competition",
                "priority": "medium"
            },
            {
                "question": f"What growth stage is {company_name} in (startup, scaling, mature)?",
                "category": "stage",
                "priority": "medium"
            },
        ]


# Global instance
_report_generator: Optional[ReportGenerator] = None


def get_report_generator() -> ReportGenerator:
    """Get or create the global report generator instance."""
    global _report_generator
    
    if _report_generator is None:
        _report_generator = ReportGenerator()
    
    return _report_generator