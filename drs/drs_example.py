import time
import json
from morpher import MorphRegistry, Morph
from morpher.morph import PromptConfig, HistoryConfig, FeedbackConfig
from morpher.morph_sequence import MorphSequence
from morpher.morph_evaluation import MorphEvaluator, MorphExecution
from drs_abstractions import *
from datetime import datetime
import os
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List
from pprint import pprint

def initialize_morph(morph_id, name, description, source, target, expert_role, instructions):
    return Morph(
        id=morph_id,
        name=name,
        description=description,
        source=source,
        target=target,
        prompt_config=PromptConfig(
            expert_role=expert_role,
            additional_instructions=instructions
        ),
        history_config=HistoryConfig(use_history=False),
        feedback_config=FeedbackConfig(use_feedback=False)
    )

# Initialize Morphs
narrative_segmenter = initialize_morph(
    "narrative_segmenter", "Narrative Segmenter", 
    "Segments an English narrative into clauses",
    english_narrative_abstraction, clause_segmentation_abstraction,
    "linguistic expert", "Ensure each clause is a complete thought or action."
)

clause_interpreter = initialize_morph(
    "clause_interpreter", "Clause Interpreter",
    "Interprets clauses as lambda expressions",
    clause_segmentation_abstraction, lambda_expressions_abstraction,
    "semantic analyst", "Use standard lambda calculus notation."
)

lambda_to_drs_updater = initialize_morph(
    "lambda_to_drs_updater", "Lambda to DRS Updater",
    "Converts lambda expressions to DRS update operations",
    lambda_expressions_abstraction, drs_updates_abstraction,
    "formal semanticist", "Ensure DRS updates are atomic and follow standard DRT conventions."
)

drs_assembler = initialize_morph(
    "drs_assembler", "DRS Assembler",
    "Assembles DRS updates into a final DRS",
    drs_updates_abstraction, final_drs_abstraction,
    "DRS expert", "Ensure the final DRS is well-formed and captures all information from the original narrative."
)

def print_drs(drs: FinalDRS):
    output = "Entities:\n"
    for entity in drs.entities:
        output += f"- {entity.name} ({entity.type})\n"
    output += "\nConditions:\n"
    for condition in drs.conditions:
        output += f"- {condition.predicate}({', '.join(condition.arguments)})\n"
    return output

def create_drs_pipeline(use_history: bool, use_feedback: bool):
    narrative_to_drs = MorphSequence([
        narrative_segmenter,
        clause_interpreter,
        lambda_to_drs_updater,
        drs_assembler
    ])

    # Create separate evaluators for each step (always using history)
    evaluators = {
        step.name: MorphEvaluator.create_with_config(
            step.name,
            history_config=HistoryConfig(use_history=True, max_history_items=10)
        ) for step in narrative_to_drs.steps
    }

    # Set use_history and use_feedback for all steps
    for step in narrative_to_drs.steps:
        step.history_config.use_history = use_history
        step.feedback_config.use_feedback = use_feedback

    return narrative_to_drs, evaluators

def run_drs_pipeline(narrative: str, narrative_to_drs: MorphSequence, evaluators: Dict[str, MorphEvaluator], iteration: int, output_file):
    print(f"\n{'='*50}")
    print(f"Processing Narrative (Iteration {iteration}):")
    print(f"{'='*50}")
    print(f"Input: {narrative}")
    print(f"Using history: {narrative_to_drs.steps[0].history_config.use_history}")
    print(f"Using feedback: {narrative_to_drs.steps[0].feedback_config.use_feedback}")

    output = f"\nNarrative: {narrative}\n"
    output += f"Using history: {narrative_to_drs.steps[0].history_config.use_history}\n"
    output += f"Using feedback: {narrative_to_drs.steps[0].feedback_config.use_feedback}\n"
    output += f"Iteration: {iteration}\n"
    output += "Transforming to DRS...\n"

    scores = {}
    start_time = time.time()

    try:
        input_data = EnglishNarrative(text=narrative)
        result = narrative_to_drs.forward(input_data)
        
        print("\nFinal DRS:")
        print(print_drs(result))
        
        output += "\nResulting DRS:\n"
        output += print_drs(result)
        output += "\nIntermediate steps and evaluations:\n"

        intermediate_input = input_data
        for step in narrative_to_drs.steps:
            print(f"\n{'-'*30}")
            print(f"Step: {step.name}")
            print(f"{'-'*30}")
            
            intermediate_result = step.forward(intermediate_input)
            
            print("Input:")
            pprint(intermediate_input.dict())
            print("\nOutput:")
            pprint(intermediate_result.dict())
            
            output += f"\n{step.name}:\n"
            output += json.dumps(intermediate_result.dict(), indent=2) + "\n"
            
            # Evaluate the step using its specific evaluator
            morph_execution = MorphExecution(
                input_data=intermediate_input.dict(),
                output_data=intermediate_result.dict(),
                timestamp=datetime.now().isoformat()
            )
            evaluation = evaluators[step.name].forward(morph_execution)
            
            scores[step.name] = evaluation.accuracy
            
            print(f"\nEvaluation for {step.name}:")
            print(f"Accuracy: {evaluation.accuracy:.2f}")
            print(f"Vote: {evaluation.vote}")
            print(f"Feedback: {evaluation.feedback}")
            
            output += f"\nEvaluation for {step.name}:\n"
            output += f"Accuracy: {evaluation.accuracy}\n"
            output += f"Feedback: {evaluation.feedback}\n"
            
            intermediate_input = intermediate_result

    except Exception as e:
        print(f"Error in iteration {iteration}: {str(e)}")
        output += f"Error in iteration {iteration}: {str(e)}\n"

    end_time = time.time()
    execution_time = end_time - start_time
    print(f"\nExecution time: {execution_time:.2f} seconds")
    output += f"\nExecution time: {execution_time:.2f} seconds\n"

    output_file.write(output)
    output_file.write("\n" + "-"*50 + "\n")

    return scores, execution_time

def plot_results(results, timestamp):
    steps = ["Narrative Segmenter", "Clause Interpreter", "Lambda to DRS Updater", "DRS Assembler"]
    n_iterations = len(results["history_and_feedback"])
    iterations = range(1, n_iterations + 1)

    fig, axs = plt.subplots(2, 2, figsize=(20, 20))
    fig.suptitle("DRS Experiment Results")

    for i, step in enumerate(steps):
        ax = axs[i // 2, i % 2]
        history_and_feedback = [np.mean([narrative["scores"].get(step, 0) for narrative in iteration]) 
                                for iteration in results["history_and_feedback"]]
        only_history = [np.mean([narrative["scores"].get(step, 0) for narrative in iteration]) 
                        for iteration in results["only_history"]]
        no_history_no_feedback = [np.mean([narrative["scores"].get(step, 0) for narrative in iteration]) 
                                  for iteration in results["no_history_no_feedback"]]
        
        ax.plot(iterations, history_and_feedback, label="History and Feedback", marker='o')
        ax.plot(iterations, only_history, label="Only History", marker='s')
        ax.plot(iterations, no_history_no_feedback, label="No History, No Feedback", marker='^')
        ax.set_title(step)
        ax.set_xlabel("Iteration")
        ax.set_ylabel("Average Score")
        ax.legend()
        ax.grid(True)

        ax.set_xticks(iterations)
        ax.set_xticklabels(iterations)

    plt.tight_layout()
    plt.savefig(f"output/drs_experiment_results_{timestamp}.png")
    plt.close()

def main():
    print("Initializing DRS Experiment")
    print("===========================")

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

    print("Registered Abstractions:")
    for abstraction in registry.list_abstractions():
        print(f"- {abstraction.name}")

    print("\nRegistered Morphs:")
    for morph in registry.list_morphs():
        print(f"- {morph.name}")

    n_iterations = 15  # Reduced for faster debugging
    narratives = [
        "In a small village, a young boy discovered a magical stone. The stone granted him incredible powers. He used these powers to help the villagers, who were amazed and grateful for his kindness."
    ]

    print(f"\nNumber of iterations: {n_iterations}")
    print(f"Number of narratives: {len(narratives)}")

    # Ensure the output directory exists
    os.makedirs("output", exist_ok=True)

    results = {
        "history_and_feedback": [],
        "only_history": [],
        "no_history_no_feedback": []
    }

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    experiments = [
        ("history_and_feedback", True, True),
        ("only_history", True, False),
        ("no_history_no_feedback", False, False)
    ]

    for exp_name, use_history, use_feedback in experiments:
        print(f"\n{'='*50}")
        print(f"Running experiment: {exp_name}")
        print(f"{'='*50}")

        output_filename = f"output/drs_output_{exp_name}_{timestamp}.md"
        
        # Create the pipeline and evaluators for each experiment condition
        narrative_to_drs, evaluators = create_drs_pipeline(use_history, use_feedback)
        
        with open(output_filename, 'w') as output_file:
            for iteration in range(n_iterations):
                print(f"\nIteration {iteration + 1}")
                iteration_results = []
                for i, narrative in enumerate(narratives):
                    print(f"\nProcessing narrative {i + 1}")
                    scores, execution_time = run_drs_pipeline(narrative, narrative_to_drs, evaluators, iteration + 1, output_file)
                    iteration_results.append({
                        "scores": scores,
                        "execution_time": execution_time
                    })
                results[exp_name].append(iteration_results)
        
        print(f"Output saved to {output_filename}")

    # Save results to a JSON file
    results_filename = f"output/drs_experiment_results_{timestamp}.json"
    with open(results_filename, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nDetailed results saved to {results_filename}")

    # Plot results
    plot_filename = f"output/drs_experiment_results_{timestamp}.png"
    plot_results(results, timestamp)
    print(f"Results plot saved to {plot_filename}")

    print("\nExperiment completed.")

if __name__ == "__main__":
    main()