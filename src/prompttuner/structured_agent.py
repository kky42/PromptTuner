from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import FewShotChatMessagePromptTemplate, ChatPromptTemplate
from langchain_openai import ChatOpenAI
import os

class AgentResponse(BaseModel):
    action: str = Field(description="Action to take: search, explain, or recommend")
    reasoning: str = Field(description="Why this action was chosen")
    confidence: float = Field(description="Confidence score between 0 and 1")

class StructuredOutputParserAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            base_url=os.getenv("DEEPSEEK_BASE_URL"),
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            model="deepseek-chat",
            temperature=0
        )
        self.parser = PydanticOutputParser(pydantic_object=AgentResponse)
        self.prompt = self._create_few_shot_prompt()
    
    def _create_few_shot_prompt(self):
        examples = [
            {
                "input": "What is machine learning?",
                "output": '{"action": "explain", "reasoning": "User asks for definition of a concept", "confidence": 0.9}'
            },
            {
                "input": "Find me Python tutorials",
                "output": '{"action": "search", "reasoning": "User wants to find resources", "confidence": 0.8}'
            },
            {
                "input": "Best IDE for Python?",
                "output": '{"action": "recommend", "reasoning": "User seeks recommendations", "confidence": 0.7}'
            }
        ]
        
        example_prompt = ChatPromptTemplate.from_template(
            "Human: {input}\nAI: {output}"
        )
        
        few_shot_prompt = FewShotChatMessagePromptTemplate(
            example_prompt=example_prompt,
            examples=examples,
        )
        
        final_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an AI assistant that responds with structured JSON output."),
            few_shot_prompt,
            ("human", "{input}"),
            ("system", "{format_instructions}")
        ])
        
        return final_prompt
    
    async def process(self, input_text: str) -> dict:
        formatted_prompt = await self.prompt.aformat(
            input=input_text,
            format_instructions=self.parser.get_format_instructions()
        )
        
        response = await self.llm.ainvoke(formatted_prompt)
        parsed_result = self.parser.parse(response.content)
        
        return parsed_result.model_dump()
