import pytest
from dotenv import load_dotenv
load_dotenv()
from prompttuner.structured_agent import StructuredOutputParserAgent

@pytest.mark.asyncio
async def test_structured_agent_basic():
    agent = StructuredOutputParserAgent()
    result = await agent.process("What is the capital of France?")
    
    assert "action" in result
    assert "reasoning" in result
    assert "confidence" in result
    assert isinstance(result["confidence"], float)

@pytest.mark.asyncio
async def test_structured_agent_with_examples():
    agent = StructuredOutputParserAgent()
    result = await agent.process("How do I cook pasta?")
    
    assert result["action"] in ["search", "explain", "recommend"]
    assert len(result["reasoning"]) > 10
    assert 0 <= result["confidence"] <= 1
