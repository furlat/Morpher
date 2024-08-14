from pydantic import BaseModel, Field
from typing import Dict, Any, Type
from openai import OpenAI
import json

class LLMConfig(BaseModel):
    provider: str = Field(default="openai", description="The LLM provider")
    model: str = Field(default="gpt-4o-2024-08-06", description="The model to use")

    def generate_response(self, system_message: str, user_message: str, response_model: Type[BaseModel]) -> Dict[str, Any]:
        if self.provider == "openai":
            client = OpenAI()
            schema = response_model.model_json_schema()
            schema["additionalProperties"] = False  # Explicitly set additionalProperties to false
            completion = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": response_model.__name__,
                        "strict": True,
                        "schema": schema
                    }
                },
            )
            return json.loads(completion.choices[0].message.content)
        raise ValueError(f"Unsupported provider: {self.provider}")