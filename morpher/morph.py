from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime
from .abstraction import Abstraction
from .llm_config import LLMConfig
import json

class MorphExecution(BaseModel):
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    timestamp: str
    evaluation: Optional[Dict[str, Any]] = None

    class Config:
        extra = "forbid"

class Morph(BaseModel):
    id: str = Field(..., description="Unique identifier for the morph")
    name: str = Field(..., description="Human-readable name of the morph")
    description: str = Field(..., description="Detailed description of what this morph does")
    source: Abstraction = Field(..., description="The source Abstraction for this morph")
    target: Abstraction = Field(..., description="The target Abstraction for this morph")
    llm_config: LLMConfig = Field(default_factory=LLMConfig)
    execution_history: List[MorphExecution] = Field(default_factory=list, description="History of morph executions")
    use_feedback_history: bool = Field(default=False, description="Flag to use feedback history for in-context learning")

    class Config:
        extra = "allow"

    def system_message(self) -> str:
        schema = self.target.model.model_json_schema()
        message = f"""You are an expert in transforming {self.source.name} to {self.target.name}. {self.description}
        Your response must adhere to the following JSON schema:
        {json.dumps(schema, indent=2)}
        """
        if self.use_feedback_history and self.execution_history:
            message += "\n\nPrevious feedback to consider:\n"
            for execution in reversed(self.execution_history[-5:]):  # Consider last 5 executions
                if execution.evaluation:
                    message += f"Input: {execution.input_data}\n"
                    message += f"Output: {execution.output_data}\n"
                    message += f"Feedback: {execution.evaluation.get('feedback', 'No feedback provided')}\n\n"
        return message

    def user_message(self, input_data: Any) -> str:
        return f"Transform the following {self.source.name} to {self.target.name} and provide the result in JSON format: {json.dumps(input_data.dict())}"

    def forward(self, input_data: Any) -> Any:
        if not isinstance(input_data, self.source.model):
            input_data = self.source.model.parse_obj(input_data)
        
        system_msg = self.system_message()
        user_msg = self.user_message(input_data)
        response = self.llm_config.generate_response(system_msg, user_msg, self.target.model)
        output_data = self.target.model.parse_obj(response)
        
        self.execution_history.append(MorphExecution(
            input_data=input_data.dict(),
            output_data=output_data.dict(),
            timestamp=datetime.now().isoformat()
        ))
        
        return output_data

    def backward(self, evaluation: Dict[str, Any]) -> None:
        if not self.execution_history:
            raise ValueError("No execution history to evaluate")
        self.execution_history[-1].evaluation = evaluation

    def __repr__(self) -> str:
        return f"Morph(id='{self.id}', name='{self.name}', source={self.source.name}, target={self.target.name})"