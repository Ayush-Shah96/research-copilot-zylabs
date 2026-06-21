"""Prompts service storing all LLM prompts for the research workflow."""
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


class PromptsService:
    """Service providing all prompts used in the research workflow."""
    
    # Planner prompts
    PLANNER_PROMPT_TEMPLATE = """You are an expert research planner. Given a company and research objective, 
create a comprehensive research plan.

Company Name: {company_name}
Company Website: {company_website}
Research Objective: {research_objective}

Create a detailed research plan including:
1. Key research questions to answer
2. Specific search keywords to use
3. Primary data sources to check
4. Potential information gaps

Provide the plan in a structured format."""

    PLANNER_SYSTEM_PROMPT = """You are an expert research strategy consultant. Your role is to analyze company 
information requests and create comprehensive, actionable research plans.

Key responsibilities:
- Identify the most relevant research angles
- Suggest specific keywords and search terms
- Recommend appropriate data sources
- Highlight potential information gaps and risks

Always think strategically about what information would be most valuable."""

    # Researcher prompts
    RESEARCHER_SYSTEM_PROMPT = """You are an expert research analyst skilled at extracting and synthesizing 
company information from various sources.

Your expertise includes:
- Analyzing company websites and public information
- Identifying key business metrics and indicators
- Understanding market positioning
- Recognizing competitive advantages and challenges
- Extracting actionable insights from data

Always be accurate and cite specific information sources."""

    RESEARCHER_ANALYSIS_PROMPT_TEMPLATE = """Based on the following research data about {company_name}, 
extract and organize key information:

RESEARCH DATA:
{research_data}

Please extract and structure:
1. Company overview and positioning
2. Key products/services offered
3. Primary target customers/market
4. Recent business signals (funding, launches, partnerships)
5. Identified competitors
6. Any risks or challenges mentioned

Provide clear, factual information based on the data provided."""

    # Analyzer prompts
    ANALYZER_SYSTEM_PROMPT = """You are an expert business analyst with deep industry knowledge.

Your role is to:
- Synthesize disparate research findings into coherent insights
- Identify strategic implications and patterns
- Assess competitive positioning
- Highlight growth opportunities and risks
- Extract actionable intelligence for sales and business development

Provide balanced, insightful analysis grounded in the evidence."""

    ANALYZER_PROMPT_TEMPLATE = """Analyze and synthesize the following company research:

COMPANY: {company_name}
RESEARCH OBJECTIVE: {research_objective}

GATHERED INFORMATION:
- Company Overview: {company_info}
- Products/Services: {products_info}
- Market/Customers: {market_info}
- News/Signals: {news_info}
- Competitors: {competitors_info}

Provide comprehensive analysis including:
1. Strategic assessment of company positioning
2. Analysis of business model and revenue streams
3. Customer base and market fit
4. Growth signals and momentum
5. Key risks and challenges
6. Opportunities for engagement
7. Key insights and takeaways

Format as a structured analysis."""

    # Quality check prompts
    QUALITY_CHECK_SYSTEM_PROMPT = """You are a quality assurance expert for research reports.

Your role is to:
- Assess completeness and depth of research
- Identify information gaps
- Evaluate confidence levels in findings
- Recommend areas needing additional research
- Ensure factual accuracy and source validity

Provide constructive feedback to improve research quality."""

    QUALITY_CHECK_PROMPT_TEMPLATE = """Evaluate the quality and completeness of this research report about {company_name}:

RESEARCH ANALYSIS:
{analysis_data}

CRITERIA FOR QUALITY:
1. Completeness - Are all key business aspects covered?
2. Depth - Is the analysis sufficiently detailed?
3. Confidence - How confident are we in the findings?
4. Information Gaps - What critical information is missing?
5. Source Credibility - Are sources reliable?

Provide:
- Overall quality score (0-100)
- Key strengths
- Major gaps or weaknesses
- Recommendations for improvement
- Confidence levels for each major finding"""

    # Reporter prompts
    REPORTER_SYSTEM_PROMPT = """You are an expert business report writer.

Your role is to:
- Synthesize research into clear, actionable reports
- Create compelling discovery questions for sales teams
- Develop strategic outreach approaches
- Highlight key unknowns and risks
- Format information for maximum clarity and impact

Write in a professional, concise manner."""

    REPORTER_PROMPT_TEMPLATE = """Create a comprehensive research report for {company_name} based on this analysis:

ANALYSIS SUMMARY:
{analysis_summary}

CREATE:
1. Executive Summary - Key findings and positioning
2. Company Profile - Overview of the organization
3. Products & Services - What they offer and key features
4. Target Market - Who they serve and why
5. Business Signals - Growth indicators and momentum
6. Competitive Position - How they compare to competitors
7. Risks & Challenges - Key obstacles and concerns
8. Discovery Questions - 5-7 specific questions to ask during outreach
9. Outreach Strategy - Recommended approach for engagement
10. Information Gaps - Key unknowns that need clarification

Format as a professional business report suitable for a sales team."""

    DISCOVERY_QUESTIONS_PROMPT_TEMPLATE = """Generate discovery questions for a sales conversation with {company_name}.

Based on this research:
{research_summary}

Create 7-10 discovery questions that:
1. Demonstrate research and preparation
2. Uncover critical business needs and challenges
3. Explore organizational decisions and processes
4. Identify pain points and opportunities
5. Are natural conversational questions
6. Lead to deeper engagement

For each question, include:
- The question itself
- Why it's important (category)
- Suggested priority (high/medium/low)

Format as JSON array."""

    # Chat prompts
    CHAT_SYSTEM_PROMPT_TEMPLATE = """You are an expert sales intelligence assistant helping prepare for customer 
conversations with {company_name}.

You have comprehensive research about the company including:
- Business model and products
- Market positioning and customers
- Recent news and signals
- Key risks and opportunities
- Competitive landscape

RESEARCH REPORT:
{research_report}

Your role is to:
- Answer questions about the company based on research
- Provide strategic insights for sales engagement
- Suggest relevant talking points
- Help identify discovery opportunities
- Connect research to business outcomes

Always cite specific information from the research when possible.
If information is not available, indicate what unknowns remain."""

    CHAT_RESPONSE_PROMPT_TEMPLATE = """Based on this company research, answer the following question:

QUESTION: {user_question}

RESEARCH CONTEXT:
{research_context}

Provide:
1. A direct answer to the question
2. Supporting evidence from the research
3. Any relevant caveats or unknowns
4. Suggestions for deeper exploration if relevant

Be concise but informative."""

    # Summarization prompts
    SUMMARIZE_CONTENT_PROMPT_TEMPLATE = """Summarize the following content about {company_name} in 2-3 sentences, 
highlighting the most important points:

CONTENT:
{content}

Focus on business-relevant information."""

    @staticmethod
    def get_planner_prompt(company_name: str, website: str, objective: str) -> str:
        """Get planner node prompt."""
        return PromptsService.PLANNER_PROMPT_TEMPLATE.format(
            company_name=company_name,
            company_website=website or "Unknown",
            research_objective=objective,
        )

    @staticmethod
    def get_planner_system_prompt() -> str:
        """Get planner system prompt."""
        return PromptsService.PLANNER_SYSTEM_PROMPT

    @staticmethod
    def get_researcher_prompt(
        company_name: str,
        search_results: str,
        website_content: str = "",
    ) -> str:
        """Get researcher node prompt."""
        return PromptsService.RESEARCHER_ANALYSIS_PROMPT_TEMPLATE.format(
            company_name=company_name,
            research_data=f"{search_results}\n\n{website_content}" if website_content else search_results,
        )

    @staticmethod
    def get_researcher_system_prompt() -> str:
        """Get researcher system prompt."""
        return PromptsService.RESEARCHER_SYSTEM_PROMPT

    @staticmethod
    def get_analyzer_prompt(
        company_name: str,
        research_objective: str,
        company_info: str,
        products_info: str,
        market_info: str,
        news_info: str,
        competitors_info: str,
    ) -> str:
        """Get analyzer node prompt."""
        return PromptsService.ANALYZER_PROMPT_TEMPLATE.format(
            company_name=company_name,
            research_objective=research_objective,
            company_info=company_info,
            products_info=products_info,
            market_info=market_info,
            news_info=news_info,
            competitors_info=competitors_info,
        )

    @staticmethod
    def get_analyzer_system_prompt() -> str:
        """Get analyzer system prompt."""
        return PromptsService.ANALYZER_SYSTEM_PROMPT

    @staticmethod
    def get_quality_check_prompt(company_name: str, analysis_data: str) -> str:
        """Get quality check node prompt."""
        return PromptsService.QUALITY_CHECK_PROMPT_TEMPLATE.format(
            company_name=company_name,
            analysis_data=analysis_data,
        )

    @staticmethod
    def get_quality_check_system_prompt() -> str:
        """Get quality check system prompt."""
        return PromptsService.QUALITY_CHECK_SYSTEM_PROMPT

    @staticmethod
    def get_reporter_prompt(company_name: str, analysis_summary: str) -> str:
        """Get reporter node prompt."""
        return PromptsService.REPORTER_PROMPT_TEMPLATE.format(
            company_name=company_name,
            analysis_summary=analysis_summary,
        )

    @staticmethod
    def get_reporter_system_prompt() -> str:
        """Get reporter system prompt."""
        return PromptsService.REPORTER_SYSTEM_PROMPT

    @staticmethod
    def get_discovery_questions_prompt(company_name: str, research_summary: str) -> str:
        """Get discovery questions prompt."""
        return PromptsService.DISCOVERY_QUESTIONS_PROMPT_TEMPLATE.format(
            company_name=company_name,
            research_summary=research_summary,
        )

    @staticmethod
    def get_chat_system_prompt(company_name: str, research_report: str) -> str:
        """Get chat system prompt with research context."""
        return PromptsService.CHAT_SYSTEM_PROMPT_TEMPLATE.format(
            company_name=company_name,
            research_report=research_report,
        )

    @staticmethod
    def get_chat_response_prompt(user_question: str, research_context: str) -> str:
        """Get chat response prompt."""
        return PromptsService.CHAT_RESPONSE_PROMPT_TEMPLATE.format(
            user_question=user_question,
            research_context=research_context,
        )

    @staticmethod
    def get_summarize_prompt(company_name: str, content: str) -> str:
        """Get content summarization prompt."""
        return PromptsService.SUMMARIZE_CONTENT_PROMPT_TEMPLATE.format(
            company_name=company_name,
            content=content,
        )