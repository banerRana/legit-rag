from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from openai import OpenAI
import json
from .base_component import BaseComponent
from ..config import Settings

@dataclass
class ReformulatedQuery:
    refined_text: str
    keywords: List[str]

class BaseQueryReformulator(BaseComponent, ABC):
    """Base class for query reformulation"""
    def __init__(self):
        super().__init__(name="reformulator")
    
    def _execute(self, query: str) -> ReformulatedQuery:
        """Execute reformulation"""
        return self.reformulate(query)
    
    @abstractmethod
    def reformulate(self, query: str) -> ReformulatedQuery:
        """Reformulate the query and generate keywords."""
        pass

class LLMQueryReformulator(BaseQueryReformulator):
    def __init__(self, model: str = "gpt-4-turbo-preview"):
        super().__init__()
        settings = Settings()
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = model
    
    def reformulate(self, query: str) -> ReformulatedQuery:
        prompt = f"""Given the user query, reformulate it to be more precise and extract key search terms.
Return your response in this JSON format:
{{
    "refined_query": "reformulated question",
    "keywords": ["key1", "key2", "key3"]
}}

Only return the JSON object, no other text.

User Query: {query}"""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{
                "role": "user",
                "content": prompt
            }],
            temperature=0,
            response_format={ "type": "json_object" }
        )
        
        result = json.loads(response.choices[0].message.content)
        return ReformulatedQuery(
            refined_text=result["refined_query"],
            keywords=result["keywords"]
        ) 