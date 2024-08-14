from pydantic import BaseModel, Field
from typing import List
from morpher import Abstraction, Morph, MorphRegistry
from morpher.morph_evaluation import morph_evaluator, EvaluationResult, MorphExecution
import json

class MathQuestion(BaseModel):
    question: str = Field(..., description="The math question to be solved")

    class Config:
        extra = "forbid"

class Step(BaseModel):
    explanation: str = Field(..., description="Explanation of the step")
    output: str = Field(..., description="Mathematical output of the step")

    class Config:
        extra = "forbid"

class MathSolution(BaseModel):
    steps: List[Step] = Field(..., description="List of steps to solve the problem")
    final_answer: str = Field(..., description="The final answer to the math question")

    class Config:
        extra = "forbid"

class MathSolverMorph(Morph):
    def system_message(self) -> str:
        schema = self.target.model.model_json_schema()
        return f"""You are a helpful math tutor. Solve the given math problem step by step.
        Your response must adhere to the following JSON schema:
        {json.dumps(schema, indent=2)}
        """

    def user_message(self, input_data: MathQuestion) -> str:
        return f"Solve this math problem step by step and provide the solution in JSON format: {input_data.question}"

# Create Abstractions
math_question_abstraction = Abstraction(
    id="math_question",
    name="Math Question",
    description="Represents a mathematical question",
    model=MathQuestion
)

math_solution_abstraction = Abstraction(
    id="math_solution",
    name="Math Solution",
    description="Represents a step-by-step solution to a math question",
    model=MathSolution
)

# Create Morph
math_solver_morph = MathSolverMorph(
    id="math_solver",
    name="Math Problem Solver",
    description="Solves a given math problem step by step",
    source=math_question_abstraction,
    target=math_solution_abstraction
)

# Create Registry and register Abstractions and Morphs
registry = MorphRegistry()
registry.register_abstraction(math_question_abstraction)
registry.register_abstraction(math_solution_abstraction)
registry.register_morph(math_solver_morph)
registry.register_morph(morph_evaluator)

def main():
    # Use the Morph to solve a math problem
    question = MathQuestion(question="Solve the equation: 2x + 5 = 13")
    
    try:
        solution = math_solver_morph.forward(question)
        print("Problem:", question.question)
        print("\nSolution:")
        for i, step in enumerate(solution.steps, 1):
            print(f"Step {i}:")
            print(f"Explanation: {step.explanation}")
            print(f"Output: {step.output}")
            print()
        print(f"Final Answer: {solution.final_answer}")
        
        # Evaluate the morph execution
        try:
            morph_execution = MorphExecution(
                input_data=question.dict(),
                output_data=solution.dict(),
                timestamp=''  # You might want to add a real timestamp here
            )
            evaluation = morph_evaluator.forward(morph_execution)
            
            print("\nEvaluation:")
            print(f"Accuracy: {evaluation.accuracy}")
            print(f"Feedback: {evaluation.feedback}")
            
            # Update the morph's history with the evaluation
            math_solver_morph.backward(evaluation.dict())
        except Exception as e:
            print(f"Error during evaluation: {str(e)}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()