"""
EDRS OpenAI Integration Utility
Secure wrapper for OpenAI API with local development support
"""

import os
import logging
from typing import Optional, Dict, Any, List
from django.conf import settings

logger = logging.getLogger(__name__)

class OpenAIService:
    """
    Secure OpenAI API service wrapper for EDRS
    Handles API calls with proper error handling and logging
    """
    
    def __init__(self):
        self.api_key = getattr(settings, 'OPENAI_API_KEY', '')
        self.model = getattr(settings, 'OPENAI_MODEL', 'gpt-3.5-turbo')
        self.max_tokens = getattr(settings, 'OPENAI_MAX_TOKENS', 1000)
        self.temperature = getattr(settings, 'OPENAI_TEMPERATURE', 0.7)
        self.enabled = getattr(settings, 'OPENAI_SETTINGS', {}).get('enabled', False)
        
        # Initialize OpenAI client only if enabled and API key exists
        self.client = None
        if self.enabled and self.api_key:
            try:
                import openai
                self.client = openai.OpenAI(api_key=self.api_key)
                logger.info("✅ OpenAI client initialized successfully")
            except ImportError:
                logger.warning("⚠️ OpenAI package not installed. Install with: pip install openai")
            except Exception as e:
                logger.error(f"❌ Failed to initialize OpenAI client: {e}")
    
    def is_available(self) -> bool:
        """Check if OpenAI service is available"""
        return self.client is not None and self.enabled
    
    def generate_text(
        self, 
        prompt: str, 
        system_message: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> Optional[str]:
        """
        Generate text using OpenAI API
        
        Args:
            prompt: The user prompt
            system_message: Optional system message for context
            max_tokens: Override default max tokens
            temperature: Override default temperature
            
        Returns:
            Generated text or None if failed
        """
        if not self.is_available():
            logger.warning("🔒 OpenAI service not available")
            return None
        
        try:
            messages = []
            if system_message:
                messages.append({"role": "system", "content": system_message})
            messages.append({"role": "user", "content": prompt})
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens or self.max_tokens,
                temperature=temperature or self.temperature
            )
            
            generated_text = response.choices[0].message.content
            logger.info(f"✅ Generated {len(generated_text)} characters")
            return generated_text
            
        except Exception as e:
            logger.error(f"❌ OpenAI API error: {e}")
            return None
    
    def analyze_document(self, content: str, analysis_type: str = "summary") -> Optional[str]:
        """
        Analyze document content using OpenAI
        
        Args:
            content: Document content to analyze
            analysis_type: Type of analysis (summary, keywords, sentiment, etc.)
            
        Returns:
            Analysis result or None if failed
        """
        if not self.is_available():
            return None
        
        system_messages = {
            "summary": "You are a document summarization assistant. Provide a concise, professional summary.",
            "keywords": "You are a keyword extraction assistant. Extract the most important keywords and phrases.",
            "sentiment": "You are a sentiment analysis assistant. Analyze the emotional tone and sentiment.",
            "classification": "You are a document classification assistant. Categorize the document type and content."
        }
        
        system_message = system_messages.get(analysis_type, system_messages["summary"])
        
        prompt = f"""
        Please analyze the following document content for {analysis_type}:

        Document Content:
        {content[:3000]}  # Limit content to avoid token limits

        Please provide a clear, structured analysis.
        """
        
        return self.generate_text(prompt, system_message)
    
    def generate_suggestions(self, context: str, task: str) -> List[str]:
        """
        Generate suggestions based on context and task
        
        Args:
            context: Context information
            task: Specific task or request
            
        Returns:
            List of suggestions
        """
        if not self.is_available():
            return []
        
        prompt = f"""
        Context: {context}
        Task: {task}
        
        Please provide 3-5 specific, actionable suggestions as a numbered list.
        Keep each suggestion concise and practical.
        """
        
        system_message = "You are a helpful assistant that provides practical suggestions and recommendations."
        
        response = self.generate_text(prompt, system_message)
        if response:
            # Parse numbered list from response
            suggestions = []
            for line in response.split('\n'):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-')):
                    # Clean up the suggestion text
                    suggestion = line.lstrip('0123456789.-) ').strip()
                    if suggestion:
                        suggestions.append(suggestion)
            return suggestions[:5]  # Limit to 5 suggestions
        
        return []
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check for OpenAI service
        
        Returns:
            Health status information
        """
        status = {
            'service': 'OpenAI API',
            'enabled': self.enabled,
            'configured': bool(self.api_key),
            'client_initialized': self.client is not None,
            'model': self.model,
            'status': 'unknown'
        }
        
        if not self.enabled:
            status['status'] = 'disabled'
            status['message'] = 'OpenAI integration is disabled'
        elif not self.api_key:
            status['status'] = 'not_configured'
            status['message'] = 'OpenAI API key not provided'
        elif not self.client:
            status['status'] = 'client_error'
            status['message'] = 'Failed to initialize OpenAI client'
        else:
            # Test API connection with minimal request
            try:
                test_response = self.generate_text("Hello", max_tokens=1)
                if test_response is not None:
                    status['status'] = 'healthy'
                    status['message'] = 'OpenAI API is accessible'
                else:
                    status['status'] = 'api_error'
                    status['message'] = 'OpenAI API request failed'
            except Exception as e:
                status['status'] = 'connection_error'
                status['message'] = f'Connection test failed: {str(e)}'
        
        return status


# Singleton instance
openai_service = OpenAIService()


# Django view helper functions
def get_openai_status() -> Dict[str, Any]:
    """Get OpenAI service status for health endpoints"""
    return openai_service.health_check()


def generate_ai_content(prompt: str, content_type: str = "general") -> Optional[str]:
    """
    Generate AI content with EDRS-specific context
    
    Args:
        prompt: User prompt
        content_type: Type of content (document, summary, analysis, etc.)
        
    Returns:
        Generated content or None
    """
    system_messages = {
        "document": "You are an expert document management assistant for the EDRS (Electronic Document Review System).",
        "summary": "You are a document summarization expert working with the EDRS platform.",
        "analysis": "You are a document analysis specialist integrated with EDRS.",
        "general": "You are an AI assistant helping with the EDRS Electronic Document Review System."
    }
    
    system_message = system_messages.get(content_type, system_messages["general"])
    
    return openai_service.generate_text(prompt, system_message)


def analyze_edrs_document(content: str, analysis_type: str = "summary") -> Optional[str]:
    """
    Analyze EDRS document content
    
    Args:
        content: Document content
        analysis_type: Type of analysis
        
    Returns:
        Analysis result
    """
    return openai_service.analyze_document(content, analysis_type)


# Security note: API key is stored securely in environment variables
# Never log or expose the actual API key in responses
logger.info(f"🤖 OpenAI Service initialized - Enabled: {openai_service.enabled}")
if openai_service.api_key:
    # Log only the first and last 4 characters for security
    masked_key = f"{openai_service.api_key[:7]}...{openai_service.api_key[-4:]}"
    logger.info(f"🔑 API Key configured: {masked_key}")
else:
    logger.warning("⚠️ OpenAI API key not configured")