from morpher import Morph
from drs_abstractions import english_narrative_abstraction, final_drs_abstraction, EnglishNarrative, FinalDRS
from drs_morphs import narrative_segmenter, clause_interpreter, lambda_to_drs_updater, drs_assembler
from morpher.morph_evaluation import morph_evaluator, MorphExecution, EvaluationResult
from typing import Any, List
import json
from pydantic import Field
from datetime import datetime

class NarrativeToDRS(Morph):
    steps: List[Morph] = Field(default_factory=list, description="List of morphs to apply in sequence")

    def __init__(self, **data):
        super().__init__(
            id="narrative_to_drs",
            name="Narrative to DRS",
            description="Transforms an English narrative to a Discourse Representation Structure",
            source=english_narrative_abstraction,
            target=final_drs_abstraction,
            steps=[
                narrative_segmenter,
                clause_interpreter,
                lambda_to_drs_updater,
                drs_assembler
            ],
            use_feedback_history=True,
            **data
        )

    def forward(self, input_data: EnglishNarrative) -> FinalDRS:
        intermediate_results = [input_data]
        for step in self.steps:
            output = step.forward(intermediate_results[-1])
            intermediate_results.append(output)
        
        final_result = intermediate_results[-1]
        
        # Perform backward pass
        self.backward_pass(intermediate_results)
        
        return final_result

    def backward_pass(self, intermediate_results: List[Any]):
        for i in range(len(self.steps) - 1, -1, -1):
            step = self.steps[i]
            input_data = intermediate_results[i]
            output_data = intermediate_results[i + 1]
            
            morph_execution = MorphExecution(
                input_data=input_data.dict(),
                output_data=output_data.dict(),
                timestamp=datetime.now().isoformat()
            )
            
            evaluation = morph_evaluator.forward(morph_execution)
            step.backward(evaluation.dict())
            
            print(f"\nEvaluation for {step.name}:")
            print(f"Accuracy: {evaluation.accuracy}")
            print(f"Feedback: {evaluation.feedback}")

    def system_message(self) -> str:
        schema = self.target.model.model_json_schema()
        return f"""You are a linguistic expert. Transform the given English narrative into a Discourse Representation Structure (DRS).
        Your response must adhere to the following JSON schema:
        {json.dumps(schema, indent=2)}
        """

    def user_message(self, input_data: EnglishNarrative) -> str:
        return f"Transform this English narrative into a DRS and provide the result in JSON format: {input_data.text}"

narrative_to_drs = NarrativeToDRS()