from pydantic import BaseModel, Field
from typing import Dict, Any, Type, List, Literal
from datetime import datetime
from morpher.abstraction import Abstraction
from morpher.morph import Morph
from morpher.llm_config import LLMConfig
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
    feedback_history: List[Dict[str, Any]] = Field(default_factory=list, description="History of feedbacks provided")
    use_feedback_history: bool = Field(default=False, description="Toggle to use feedback history")

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
            )
        )

    def system_message(self) -> str:
        schema = self.target.model.model_json_schema()
        message = f"""You are an AI model evaluator. Assess the quality of the given morph execution and provide an accuracy score (between 0 and 1) and detailed feedback.
        Your response must adhere to the following JSON schema:
        {json.dumps(schema, indent=2)}
        """
        if self.use_feedback_history and self.feedback_history:
            message += "\n\nPrevious feedbacks to consider:\n"
            for feedback in reversed(self.feedback_history[-5:]):  # Consider last 5 feedbacks
                message += f"Input: {feedback['input']}\n"
                message += f"Output: {feedback['output']}\n"
                message += f"Previous Feedback: {feedback['feedback']}\n\n"
        return message

    def user_message(self, input_data: MorphExecution) -> str:
        return f"Evaluate the quality of this transformation and provide your assessment in JSON format. Input: {input_data.input_data}\nOutput: {input_data.output_data}"

    def forward(self, input_data: MorphExecution) -> EvaluationResult:
        result = super().forward(input_data)
        if self.use_feedback_history:
            self.feedback_history.append({
                "input": input_data.input_data,
                "output": input_data.output_data,
                "feedback": result.feedback
            })
        return result