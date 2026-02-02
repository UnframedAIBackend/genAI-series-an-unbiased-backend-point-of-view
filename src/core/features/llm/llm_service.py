from typing import Any

from litellm import completion

from src.core.configuration.configuration import config


class LlmService:
    def __init__(self):
        self.host = config.get("OLLAMA_HOST")
        self.model = config.get("GENERATION_MODEL")
        print("host", self.host)
        print("model", self.model)

    def generate(self, prompt: str) -> str:
        """
        Generates text using the configured LLM.
        """
        try:
            response: Any = completion(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                api_base=self.host,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating answer: {str(e)}"
