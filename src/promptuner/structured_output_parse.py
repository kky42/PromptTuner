import os
import asyncio
from typing import Type, TypeVar
from pydantic import BaseModel
from agents import Agent, Runner, set_tracing_disabled, set_default_openai_api
from openai import AsyncOpenAI

# Disable tracing globally
set_tracing_disabled(True)

T = TypeVar('T', bound=BaseModel)


class StructuredOutputAgent:
    """Agent that extracts structured output from queries using Pydantic models."""
    
    def __init__(self, api_key: str = None, base_url: str = None, model: str = None):
        """
        Initialize the agent with API credentials.
        
        Args:
            api_key: API key. If None, will use DEEPSEEK_API_KEY or OPENAI_API_KEY env var.
            base_url: Base URL for API. If None, will use DEEPSEEK_BASE_URL env var.
            model: Model name. If None, will use deepseek-chat for DeepSeek or gpt-4o-mini for OpenAI.
        """
        # Set up API credentials - prefer DeepSeek
        if not api_key:
            api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not base_url:
            base_url = os.getenv("DEEPSEEK_BASE_URL")
        
        # Configure environment for agents SDK
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
        if base_url:
            os.environ["OPENAI_BASE_URL"] = base_url
            # Use Chat Completions API for third-party providers
            set_default_openai_api("chat_completions")
            
        # Set default model based on provider
        if not model:
            if base_url and "deepseek" in base_url.lower():
                model = "deepseek-chat"
            else:
                model = "gpt-4o-mini"
        
        self.agent = Agent(
            name="StructuredExtractor",
            instructions="You are an expert at extracting structured information from text. Always return valid JSON that matches the provided schema exactly.",
            model=model
        )
    
    def extract(self, query: str, model_class: Type[T], instructions: str = None) -> T:
        """
        Extract structured output from a query using the specified Pydantic model.
        
        Args:
            query: The input query to process
            model_class: Pydantic BaseModel class defining the expected structure
            instructions: Optional additional instructions for extraction
            
        Returns:
            Instance of the specified Pydantic model
            
        Raises:
            ValueError: If extraction fails or validation fails
        """
        if not query or not isinstance(query, str):
            raise ValueError("Query must be a non-empty string")
        
        # Build the prompt
        schema = model_class.model_json_schema()
        base_prompt = f"""
Extract structured information from the following query and return it as JSON that matches this schema:

Schema:
{schema}

Query: {query}

{instructions or ''}

Return only valid JSON that matches the schema exactly.
"""
        
        try:
            # Use the agent to process the query
            result = asyncio.run(Runner.run(self.agent, base_prompt))
            
            # Extract content from result
            if hasattr(result, 'final_output'):
                content = result.final_output
            elif hasattr(result, 'content'):
                content = result.content
            elif isinstance(result, str):
                content = result
            else:
                content = str(result)
            
            # Extract JSON from response
            json_data = self._extract_json_from_text(content)
            
            # Validate and create model instance
            return model_class.model_validate(json_data)
            
        except Exception as e:
            raise ValueError(f"Failed to extract structured output: {e}")
    
    def _extract_json_from_text(self, text: str) -> dict:
        """Extract JSON from text response."""
        import json
        
        text = text.strip()
        
        # Find JSON in text
        start_idx = text.find('{')
        if start_idx == -1:
            raise ValueError("No JSON found in response")
        
        # Find matching closing brace
        brace_count = 0
        end_idx = -1
        
        for i in range(start_idx, len(text)):
            if text[i] == '{':
                brace_count += 1
            elif text[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    end_idx = i
                    break
        
        if end_idx == -1:
            raise ValueError("No matching closing brace found")
        
        json_text = text[start_idx:end_idx + 1]
        
        try:
            return json.loads(json_text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in response: {e}")


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    class PersonInfo(BaseModel):
        name: str
        age: int
        city: str
        occupation: str = None
    
    # Check if DeepSeek API is available
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")
    deepseek_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    
    if not deepseek_key:
        print("Please set DEEPSEEK_API_KEY in .env file")
        exit(1)
    
    agent = StructuredOutputAgent(
        api_key=deepseek_key,
        base_url=deepseek_url, 
        model="deepseek-chat"
    )
    
    # Simple test
    query = "John is 30 years old and works as a software developer in New York City"
    result = agent.extract(query, PersonInfo)
    print(f"Result: {result}")