from morpher import MorphRegistry
from morpher.morph_sequence import MorphSequence
from drs_abstractions import *
from drs_morphs import narrative_segmenter, clause_interpreter, lambda_to_drs_updater, drs_assembler
from morpher.morph_evaluation import morph_evaluator, MorphExecution
import json
from datetime import datetime
import os

def print_drs(drs: FinalDRS):
    output = "Entities:\n"
    for entity in drs.entities:
        output += f"- {entity.name} ({entity.type})\n"
    output += "\nConditions:\n"
    for condition in drs.conditions:
        output += f"- {condition.predicate}({', '.join(condition.arguments)})\n"
    return output

def run_drs_pipeline(narrative: str, use_feedback_history: bool, output_file):
    narrative_to_drs = MorphSequence([
        narrative_segmenter,
        clause_interpreter,
        lambda_to_drs_updater,
        drs_assembler
    ])

    # Set use_feedback_history for all steps
    for step in narrative_to_drs.steps:
        step.use_feedback_history = use_feedback_history

    output = f"\nNarrative: {narrative}\n"
    output += f"Using feedback history: {use_feedback_history}\n"
    output += "Transforming to DRS...\n"

    try:
        input_data = EnglishNarrative(text=narrative)
        result = narrative_to_drs.forward(input_data)
        
        output += "\nResulting DRS:\n"
        output += print_drs(result)

        output += "\nIntermediate steps and evaluations:\n"
        intermediate_input = input_data
        for step in narrative_to_drs.steps:
            output += f"\n{step.name}:\n"
            intermediate_result = step.forward(intermediate_input)
            output += json.dumps(intermediate_result.dict(), indent=2) + "\n"
            
            # Evaluate the step
            morph_execution = MorphExecution(
                input_data=intermediate_input.dict(),
                output_data=intermediate_result.dict(),
                timestamp=datetime.now().isoformat()
            )
            evaluation = morph_evaluator.forward(morph_execution)
            step.backward(evaluation.dict())
            
            output += f"\nEvaluation for {step.name}:\n"
            output += f"Accuracy: {evaluation.accuracy}\n"
            output += f"Feedback: {evaluation.feedback}\n"
            
            intermediate_input = intermediate_result
            print(output)

    except Exception as e:
        output += f"Error: {str(e)}\n"

    output_file.write(output)
    output_file.write("\n" + "-"*50 + "\n")

def main():
    # Create Registry and register Abstractions and Morphs
    registry = MorphRegistry()
    registry.register_abstraction(english_narrative_abstraction)
    registry.register_abstraction(clause_segmentation_abstraction)
    registry.register_abstraction(lambda_expressions_abstraction)
    registry.register_abstraction(drs_updates_abstraction)
    registry.register_abstraction(final_drs_abstraction)

    registry.register_morph(narrative_segmenter)
    registry.register_morph(clause_interpreter)
    registry.register_morph(lambda_to_drs_updater)
    registry.register_morph(drs_assembler)
    registry.register_morph(morph_evaluator)

    # Example narratives
    narratives = [
        "John owns a car. The car is red. He drives it to work.",
        "Every farmer who owns a donkey beats it. Pedro is a farmer.",
        "Alice gave a book to Bob. He read it and enjoyed the story."
    ]

    # Ensure the output directory exists
    os.makedirs("output", exist_ok=True)

    # Run the pipeline twice, with and without feedback history
    for use_feedback_history in [False, True]:
        output_filename = f"output/drs_output_{'with' if use_feedback_history else 'without'}_feedback.md"
        with open(output_filename, 'w') as output_file:
            for narrative in narratives:
                run_drs_pipeline(narrative, use_feedback_history, output_file)

        print(f"Output saved to {output_filename}")

if __name__ == "__main__":
    main()