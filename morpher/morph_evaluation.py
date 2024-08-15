from pydantic import BaseModel, Field
from typing import Dict, Any, Type, List, Literal
from datetime import datetime
from .abstraction import Abstraction
from .morph import Morph, PromptConfig, HistoryConfig, FeedbackConfig
from .llm_config import LLMConfig
import json

class MorphExecution(BaseModel):
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    timestamp: str

    class Config:
        extra = "forbid"

class MorphExecutionAbstraction(Abstraction):
    model: Type[MorphExecution] = MorphExecution

class EvaluationResult(BaseModel):
    vote: Literal["insufficient", "below_average", "average", "above_average", "excellent"] = Field(..., description="Vote on the morph execution")
    accuracy: float = Field(..., description="Accuracy score of the morph execution")
    feedback: str = Field(..., description="Detailed feedback on the morph execution")

    class Config:
        extra = "forbid"

class EvaluationAbstraction(Abstraction):
    model: Type[EvaluationResult] = EvaluationResult

class MorphEvaluator(Morph):
    def __init__(self, morph_name: str):
        super().__init__(
            id=f"{morph_name}_evaluator",
            name=f"{morph_name} Evaluator",
            description=f"Evaluates the quality of {morph_name} execution",
            source=MorphExecutionAbstraction(
                id="morph_execution",
                name="Morph Execution",
                description="Represents a single execution of a morph"
            ),
            target=EvaluationAbstraction(
                id="evaluation_result",
                name="Evaluation Result",
                description="Represents the evaluation of a morph execution"
            ),
            prompt_config=PromptConfig(
                expert_role="AI model evaluator",
                additional_instructions="Assess the quality of the given morph execution and provide an accuracy score (between 0 and 1) and detailed feedback."
            ),
            history_config=HistoryConfig(use_history=True, max_history_items=5),
            feedback_config=FeedbackConfig(use_feedback=False)
        )

    def backward(self, evaluation: Dict[str, Any]) -> None:
        raise NotImplementedError("MorphEvaluator does not support backward operation")

    def user_message(self, input_data: MorphExecution) -> str:
        return f"Evaluate the quality of this transformation and provide your assessment in JSON format. Input: {input_data.input_data}\nOutput: {input_data.output_data}"

    @classmethod
    def create_with_config(cls, morph_name: str, **config):
        instance = cls(morph_name)
        for key, value in config.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
            else:
                raise ValueError(f"Invalid configuration parameter: {key}")
        
        if instance.feedback_config.use_feedback:
            raise ValueError("MorphEvaluator does not support feedback configuration")
        
        return instance