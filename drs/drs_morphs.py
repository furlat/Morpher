from morpher import Morph
from drs_abstractions import *
from typing import Dict, Any
import json

class NarrativeSegmenter(Morph):
    def __init__(self):
        super().__init__(
            id="narrative_segmenter",
            name="Narrative Segmenter",
            description="Segments an English narrative into clauses",
            source=english_narrative_abstraction,
            target=clause_segmentation_abstraction
        )

    def system_message(self) -> str:
        schema = self.target.model.model_json_schema()
        return f"""You are a linguistic expert. Segment the given narrative into clauses.
        Your response must adhere to the following JSON schema:
        {json.dumps(schema, indent=2)}
        """

    def user_message(self, input_data: EnglishNarrative) -> str:
        return f"Segment this narrative into clauses and provide the result in JSON format: {input_data.text}"

class ClauseInterpreter(Morph):
    def __init__(self):
        super().__init__(
            id="clause_interpreter",
            name="Clause Interpreter",
            description="Interprets clauses as lambda expressions",
            source=clause_segmentation_abstraction,
            target=lambda_expressions_abstraction
        )

    def system_message(self) -> str:
        schema = self.target.model.model_json_schema()
        return f"""You are a linguistic expert. Convert the given clauses to lambda calculus expressions.
        Your response must adhere to the following JSON schema:
        {json.dumps(schema, indent=2)}
        """

    def user_message(self, input_data: ClauseSegmentation) -> str:
        clauses = [clause.text for clause in input_data.clauses]
        return f"Convert these clauses to lambda expressions and provide the result in JSON format: {json.dumps(clauses)}"

class LambdaToDRSUpdater(Morph):
    def __init__(self):
        super().__init__(
            id="lambda_to_drs_updater",
            name="Lambda to DRS Updater",
            description="Converts lambda expressions to DRS update operations",
            source=lambda_expressions_abstraction,
            target=drs_updates_abstraction
        )

    def system_message(self) -> str:
        schema = self.target.model.model_json_schema()
        return f"""You are a linguistic expert. Convert the given lambda expressions to DRS update operations.
        Your response must adhere to the following JSON schema:
        {json.dumps(schema, indent=2)}
        """

    def user_message(self, input_data: LambdaExpressions) -> str:
        expressions = [expr.expression for expr in input_data.expressions]
        return f"Convert these lambda expressions to DRS updates and provide the result in JSON format: {json.dumps(expressions)}"

class DRSAssembler(Morph):
    def __init__(self):
        super().__init__(
            id="drs_assembler",
            name="DRS Assembler",
            description="Assembles DRS updates into a final DRS",
            source=drs_updates_abstraction,
            target=final_drs_abstraction
        )

    def system_message(self) -> str:
        schema = self.target.model.model_json_schema()
        return f"""You are a linguistic expert. Assemble the given DRS updates into a final DRS.
        Your response must adhere to the following JSON schema:
        {json.dumps(schema, indent=2)}
        """

    def user_message(self, input_data: DRSUpdates) -> str:
        updates = [update.dict() for update in input_data.updates]
        return f"Assemble these DRS updates into a final DRS and provide the result in JSON format: {json.dumps(updates)}"

narrative_segmenter = NarrativeSegmenter()
clause_interpreter = ClauseInterpreter()
lambda_to_drs_updater = LambdaToDRSUpdater()
drs_assembler = DRSAssembler()