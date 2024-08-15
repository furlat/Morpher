from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Type
from datetime import datetime
import json
from .abstraction import Abstraction
from .llm_config import LLMConfig

class MorphExecution(BaseModel):
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    timestamp: str
    evaluation: Optional[Dict[str, Any]] = None

    class Config:
        extra = "forbid"

class PromptConfig(BaseModel):
    expert_role: str = Field(default="expert", description="The role of the AI in this transformation")
    additional_instructions: Optional[str] = Field(default=None, description="Any additional instructions for the task")

    def generate_system_message(self, source: Abstraction, target: Abstraction, description: str, schema: Dict[str, Any]) -> str:
        message = f"""You are an {self.expert_role} in transforming {source.name} to {target.name}. {description}

Source ({source.name}): {source.description}
Target ({target.name}): {target.description}

Your response must adhere to the following JSON schema:
{json.dumps(schema, indent=2)}
"""
        if self.additional_instructions:
            message += f"\nAdditional instructions: {self.additional_instructions}"
        return message

    def generate_user_message(self, source: Abstraction, target: Abstraction, input_data: Any) -> str:
        return f"Transform the following {source.name} to {target.name} and provide the result in JSON format: {json.dumps(input_data.dict())}"

class HistoryConfig(BaseModel):
    use_history: bool = Field(default=False, description="Whether to use execution history in prompts")
    max_history_items: int = Field(default=5, description="Maximum number of history items to include")
    max_history_length: int = Field(default=1000, description="Maximum total length of history in characters")

class FeedbackConfig(BaseModel):
    use_feedback: bool = Field(default=False, description="Whether to use feedback in prompts")
    max_feedback_items: int = Field(default=5, description="Maximum number of feedback items to include")
    max_feedback_length: int = Field(default=500, description="Maximum total length of feedback in characters")

class Morph(BaseModel):
    id: str = Field(..., description="Unique identifier for the morph")
    name: str = Field(..., description="Human-readable name of the morph")
    description: str = Field(..., description="Detailed description of what this morph does")
    source: Abstraction = Field(..., description="The source Abstraction for this morph")
    target: Abstraction = Field(..., description="The target Abstraction for this morph")
    llm_config: LLMConfig = Field(default_factory=LLMConfig)
    execution_history: List[MorphExecution] = Field(default_factory=list, description="History of morph executions")
    prompt_config: PromptConfig = Field(default_factory=PromptConfig)
    history_config: HistoryConfig = Field(default_factory=HistoryConfig)
    feedback_config: FeedbackConfig = Field(default_factory=FeedbackConfig)

    class Config:
        extra = "allow"

    def generate_history_message(self) -> str:
        if not self.history_config.use_history or not self.execution_history:
            return ""
        
        message = "\n\nPrevious executions to consider:\n"
        total_length = 0
        for execution in reversed(self.execution_history[-self.history_config.max_history_items:]):
            history_item = f"Input: {execution.input_data}\nOutput: {execution.output_data}\n\n"
            if total_length + len(history_item) > self.history_config.max_history_length:
                break
            message += history_item
            total_length += len(history_item)
        
        return message[:self.history_config.max_history_length]

    def generate_feedback_message(self) -> str:
        if not self.feedback_config.use_feedback or not self.execution_history:
            return ""
        
        message = "\n\nPrevious feedback to consider:\n"
        total_length = 0
        for execution in reversed(self.execution_history[-self.feedback_config.max_feedback_items:]):
            if execution.evaluation:
                feedback_item = f"Input: {execution.input_data}\n"
                feedback_item += f"Output: {execution.output_data}\n"
                feedback_item += f"Feedback: {execution.evaluation.get('feedback', 'No feedback provided')}\n\n"
                
                if total_length + len(feedback_item) > self.feedback_config.max_feedback_length:
                    break
                
                message += feedback_item
                total_length += len(feedback_item)
        
        return message[:self.feedback_config.max_feedback_length]

    def system_message(self) -> str:
        schema = self.target.model.model_json_schema()
        message = self.prompt_config.generate_system_message(
            self.source, self.target, self.description, schema
        )
        
        return message

    def user_message(self, input_data: Any) -> str:
        message= self.prompt_config.generate_user_message(self.source, self.target, input_data)
        message += self.generate_history_message()
        message += self.generate_feedback_message()
        return message
    
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