"""Centralized LLM service wrapper."""
import logging
from typing import Optional, Dict, List, Any
from datetime import datetime
import json

from openai import (
    OpenAI,
    APIError,
    APIConnectionError,
    RateLimitError,
    Timeout,
)
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from app.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """Service for interacting with OpenAI API."""

    def __init__(self):
        """Initialize the LLM service."""
    
        if not settings.OPENROUTER_API_KEY:
            logger.warning("OPENROUTER_API_KEY not configured")
    
        self.client = OpenAI(
            api_key=settings.OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": "http://localhost:3000",
                "X-Title": "ZyLabs AI Research Assistant",
            },
        )
    
        self.model = settings.OPENROUTER_MODEL
        self.temperature = settings.TEMPERATURE
        self.max_tokens = settings.MAX_TOKENS
        self.max_retries = settings.MAX_RETRIES
    
        self.token_usage = {
            "total_prompt_tokens": 0,
            "total_completion_tokens": 0,
            "total_tokens": 0,
        }
    def _call_openai(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        json_mode: bool = False,
    ) -> Dict[str, Any]:
        """
        Call OpenAI API with retry logic.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Override default temperature
            max_tokens: Override default max tokens
            json_mode: Whether to request JSON mode response
            
        Returns:
            API response dict
            
        Raises:
            APIError: If API call fails after retries
        """
        try:
            logger.debug(f"Calling OpenAI with {len(messages)} messages")
            
            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature or self.temperature,
                "max_tokens": max_tokens or self.max_tokens,
            }
            
            if json_mode:
                kwargs["response_format"] = {"type": "json_object"}
            
            response = self.client.chat.completions.create(**kwargs)
            
            # Track token usage
            if hasattr(response, "usage"):
                self.token_usage["total_prompt_tokens"] += response.usage.prompt_tokens
                self.token_usage["total_completion_tokens"] += response.usage.completion_tokens
                self.token_usage["total_tokens"] += response.usage.total_tokens
                
                logger.info(
                    f"Token usage - Prompt: {response.usage.prompt_tokens}, "
                    f"Completion: {response.usage.completion_tokens}, "
                    f"Total: {response.usage.total_tokens}"
                )
            
            return {
                "content": response.choices[0].message.content,
                "stop_reason": response.choices[0].finish_reason,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens if hasattr(response, "usage") else 0,
                    "completion_tokens": response.usage.completion_tokens if hasattr(response, "usage") else 0,
                },
            }
            
        except (APIError, RateLimitError, Timeout, APIConnectionError) as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error calling OpenAI: {str(e)}")
            raise

    def generate(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Generate text from a prompt.
        
        Args:
            prompt: The prompt to send to the model
            temperature: Override default temperature
            max_tokens: Override default max tokens
            
        Returns:
            Generated text response
        """
        logger.info(f"Generating response for prompt (len={len(prompt)})")
        
        try:
            messages = [{"role": "user", "content": prompt}]
            response = self._call_openai(messages, temperature, max_tokens)
            
            logger.info("Generation completed successfully")
            return response["content"]
            
        except Exception as e:
            logger.error(f"Generation failed: {str(e)}")
            # Return graceful fallback
            return f"Unable to generate response at this time: {str(e)}"

    def chat(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        previous_messages: Optional[List[Dict[str, str]]] = None,
    ) -> str:
        """
        Chat-based interaction with context.
        
        Args:
            system_prompt: System message to set context
            user_prompt: User's message
            temperature: Override default temperature
            max_tokens: Override default max tokens
            previous_messages: Previous messages for context
            
        Returns:
            Assistant's response
        """
        logger.info(f"Chat interaction with context length={len(system_prompt)}")
        
        try:
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add previous messages if provided
            if previous_messages:
                messages.extend(previous_messages)
            
            # Add current user message
            messages.append({"role": "user", "content": user_prompt})
            
            response = self._call_openai(messages, temperature, max_tokens)
            
            logger.info("Chat completed successfully")
            return response["content"]
            
        except Exception as e:
            logger.error(f"Chat failed: {str(e)}")
            return f"Unable to process your request at this time."

    def summarize(
        self,
        text: str,
        max_length: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> str:
        """
        Summarize text content.
        
        Args:
            text: Text to summarize
            max_length: Target length for summary (optional)
            temperature: Override default temperature
            
        Returns:
            Summarized text
        """
        logger.info(f"Summarizing text (len={len(text)})")
        
        try:
            prompt = f"Please provide a concise summary of the following text:\n\n{text}"
            
            if max_length:
                prompt += f"\n\nKeep the summary to approximately {max_length} words or less."
            
            messages = [{"role": "user", "content": prompt}]
            response = self._call_openai(messages, temperature=temperature or 0.5)
            
            logger.info("Summarization completed successfully")
            return response["content"]
            
        except Exception as e:
            logger.error(f"Summarization failed: {str(e)}")
            return "Unable to summarize text at this time."

    def extract_json(
        self,
        prompt: str,
        schema: Optional[str] = None,
        temperature: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Extract structured JSON from prompt.
        
        Uses OpenAI's JSON mode for guaranteed valid JSON responses.
        
        Args:
            prompt: The prompt requesting JSON output
            schema: Optional description of expected JSON schema
            temperature: Override default temperature
            
        Returns:
            Parsed JSON response
        """
        logger.info(f"Extracting JSON from prompt (len={len(prompt)})")
        
        try:
            full_prompt = prompt
            
            if schema:
                full_prompt += f"\n\nExpected schema:\n{schema}"
            
            full_prompt += "\n\nRespond with valid JSON only."
            
            messages = [{"role": "user", "content": full_prompt}]
            response = self._call_openai(
                messages,
                temperature=temperature or 0.3,
                json_mode=True
            )
            
            # Parse JSON response
            json_str = response["content"].strip()
            
            # Handle potential markdown code blocks
            if json_str.startswith("```"):
                json_str = json_str.split("```")[1]
                if json_str.startswith("json"):
                    json_str = json_str[4:]
                json_str = json_str.strip()
            
            result = json.loads(json_str)
            logger.info("JSON extraction completed successfully")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            return {"error": f"Invalid JSON response: {str(e)}"}
        except Exception as e:
            logger.error(f"JSON extraction failed: {str(e)}")
            return {"error": f"Extraction failed: {str(e)}"}

    def batch_process(
        self,
        prompts: List[str],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> List[str]:
        """
        Process multiple prompts efficiently.
        
        Args:
            prompts: List of prompts to process
            temperature: Override default temperature
            max_tokens: Override default max tokens
            
        Returns:
            List of responses
        """
        logger.info(f"Batch processing {len(prompts)} prompts")
        
        results = []
        for i, prompt in enumerate(prompts, 1):
            try:
                logger.debug(f"Processing prompt {i}/{len(prompts)}")
                result = self.generate(prompt, temperature, max_tokens)
                results.append(result)
            except Exception as e:
                logger.error(f"Error processing prompt {i}: {str(e)}")
                results.append(f"Error: {str(e)}")
        
        return results

    def get_token_usage(self) -> Dict[str, int]:
        """Get accumulated token usage."""
        return self.token_usage.copy()

    def reset_token_usage(self) -> None:
        """Reset token usage counter."""
        self.token_usage = {
            "total_prompt_tokens": 0,
            "total_completion_tokens": 0,
            "total_tokens": 0,
        }


# Global instance
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """Get or create the global LLM service instance."""
    global _llm_service
    
    if _llm_service is None:
        _llm_service = LLMService()
    
    return _llm_service