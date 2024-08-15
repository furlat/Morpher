import time
import json
from morpher import MorphRegistry
from morpher.morph_sequence import MorphSequence
from drs_abstractions import *
from drs_morphs import narrative_segmenter, clause_interpreter, lambda_to_drs_updater, drs_assembler
from morpher.morph_evaluation import MorphEvaluator, MorphExecution
from datetime import datetime
import os
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict

def print_drs(drs: FinalDRS):
    output = "Entities:\n"
    for entity in drs.entities:
        output += f"- {entity.name} ({entity.type})\n"
    output += "\nConditions:\n"
    for condition in drs.conditions:
        output += f"- {condition.predicate}({', '.join(condition.arguments)})\n"
    return output

def create_drs_pipeline(use_feedback_history: bool):
    narrative_to_drs = MorphSequence([
        narrative_segmenter,
        clause_interpreter,
        lambda_to_drs_updater,
        drs_assembler
    ])

    # Create separate evaluators for each step
    evaluators = {
        step.name: MorphEvaluator(step.name) for step in narrative_to_drs.steps
    }

    # Set use_feedback_history for all steps and evaluators
    for step in narrative_to_drs.steps:
        step.use_feedback_history = use_feedback_history
    for evaluator in evaluators.values():
        evaluator.use_feedback_history = True

    return narrative_to_drs, evaluators

def run_drs_pipeline(narrative: str, narrative_to_drs: MorphSequence, evaluators: Dict[str, MorphEvaluator], iteration: int, output_file):
    output = f"\nNarrative: {narrative}\n"
    output += f"Using feedback history: {narrative_to_drs.steps[0].use_feedback_history}\n"
    output += f"Iteration: {iteration}\n"
    output += "Transforming to DRS...\n"

    scores = {}
    start_time = time.time()

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
            print(f"Completed step: {step.name}")
            # print(f"Output: {intermediate_result.dict()}")
            
            # Evaluate the step using its specific evaluator
            morph_execution = MorphExecution(
                input_data=intermediate_input.dict(),
                output_data=intermediate_result.dict(),
                timestamp=datetime.now().isoformat()
            )
            evaluation = evaluators[step.name].forward(morph_execution)
            step.backward(evaluation.dict())
            
            scores[step.name] = evaluation.accuracy
            
            output += f"\nEvaluation for {step.name}:\n"
            output += f"Accuracy: {evaluation.accuracy}\n"
            output += f"Feedback: {evaluation.feedback}\n"
            
            intermediate_input = intermediate_result
            print(f"Completed step: {step.name} with accuracy: {evaluation.accuracy:.2f} and vote: {evaluation.vote}")

    except Exception as e:
        output += f"Error in iteration {iteration}: {str(e)}\n"

    end_time = time.time()
    execution_time = end_time - start_time
    output += f"\nExecution time: {execution_time:.2f} seconds\n"

    output_file.write(output)
    output_file.write("\n" + "-"*50 + "\n")

    return scores, execution_time

def plot_results(results, timestamp):
    steps = ["Narrative Segmenter", "Clause Interpreter", "Lambda to DRS Updater", "DRS Assembler"]
    n_iterations = len(results["with_feedback"])  # Get the actual number of iterations
    iterations = range(1, n_iterations + 1)

    fig, axs = plt.subplots(2, 2, figsize=(15, 15))
    fig.suptitle("DRS Experiment Results")

    for i, step in enumerate(steps):
        ax = axs[i // 2, i % 2]
        with_feedback = [np.mean([narrative["scores"].get(step, 0) for narrative in iteration]) 
                         for iteration in results["with_feedback"]]
        without_feedback = [np.mean([narrative["scores"].get(step, 0) for narrative in iteration]) 
                            for iteration in results["without_feedback"]]
        
        ax.plot(iterations, with_feedback, label="With Feedback", marker='o')
        ax.plot(iterations, without_feedback, label="Without Feedback", marker='s')
        ax.set_title(step)
        ax.set_xlabel("Iteration")
        ax.set_ylabel("Average Score")
        ax.legend()
        ax.grid(True)

        # Set x-axis ticks to show all iteration numbers
        ax.set_xticks(iterations)
        ax.set_xticklabels(iterations)

    plt.tight_layout()
    plt.savefig(f"output/drs_experiment_results_{timestamp}.png")
    plt.close()

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

    n_iterations = 10  # Set the number of iterations for debugging

    # Example narratives
    # narratives = [
    #     "John owns a car. The car is red. He drives it to work.",
    #     "Every farmer who owns a donkey beats it. Pedro is a farmer.",
    #     "Alice gave a book to Bob. He read it and enjoyed the story."
    # ]
    narratives_dict = {
    1: "The cat sits on the mat. The mat is blue. It sleeps there all day.",
    2: "A teacher teaches students. The students learn quickly and ask many questions. The teacher answers them patiently.",
    3: "Maria bought a new dress. She wore it to the party. Everyone complimented her on her beautiful dress.",
    4: "A scientist discovered a new planet. The planet orbits a distant star. The scientist shared the discovery with the world.",
    5: "Tom has two dogs. One is large, and the other is small. He takes both dogs for a walk in the park every morning.",
    6: "The chef cooked a delicious meal. The guests enjoyed the meal and praised the chef for the excellent cooking. The chef smiled and thanked them.",
    7: "In the library, Sarah found an old book. The book was dusty and covered in cobwebs. She opened it and began to read the fascinating stories within.",
    8: "A musician composed a beautiful symphony. The orchestra performed it flawlessly. The audience was moved to tears by the music, and they gave a standing ovation.",
    9: "The detective solved the mystery. He gathered all the clues and questioned the suspects. In the end, he revealed the culprit, who confessed to the crime.",
    10: "In a small village, a young boy discovered a magical stone. The stone granted him incredible powers. He used these powers to help the villagers, who were amazed and grateful for his kindness."
}

    narratives = [
        
        narratives_dict[10]
       
    ]

    # Ensure the output directory exists
    os.makedirs("output", exist_ok=True)

    results = {
        "with_feedback": [],
        "without_feedback": []
    }

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    for use_feedback_history in [False,True]:
        key = "with_feedback" if use_feedback_history else "without_feedback"
        output_filename = f"output/drs_output_{key}_{timestamp}.md"
        print(f"\nStarting runs {'with' if use_feedback_history else 'without'} feedback history")
        
        # Create the pipeline and evaluators once for each feedback scenario
        narrative_to_drs, evaluators = create_drs_pipeline(use_feedback_history)
        
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
                    print(f"Execution time: {execution_time:.2f} seconds")
                results[key].append(iteration_results)
        
        print(f"Output saved to {output_filename}")

    # Save results to a JSON file
    with open(f"output/drs_experiment_results_{timestamp}.json", "w") as f:
        json.dump(results, f, indent=2)

    # Plot results
    plot_results(results, timestamp)

    print(f"\nExperiment completed. Results saved to output/drs_experiment_results_{timestamp}.json and output/drs_experiment_results_{timestamp}.png")

if __name__ == "__main__":
    main()