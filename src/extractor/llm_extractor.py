from typing import Optional, Tuple, Dict

from src.model import GoogleAI


class LLMExtractor:

    def __init__(self, api_key: str, url: str) -> None:
        self.llm = GoogleAI(api_key = api_key,
                                url = url)

    def extract(self, prompt_system: str, data: str, model_name: str = "gemini-2.0-flash") -> Tuple[str, Dict]:
        response = self.llm.generate(prompt_system, data, model_name)
        usage = response.usage.to_dict() 
        answer = response.choices[0].message.content
        return answer, usage
