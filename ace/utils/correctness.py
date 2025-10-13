"""Solution correctness evaluation."""
from pydantic import BaseModel, Field
from pydantic_ai import Agent


class CorrectnessAnalysis(BaseModel):
    """Analysis of solution correctness."""
    is_correct: bool = Field(..., description="Whether the solution is correct")
    error_type: str = Field(..., description="Type of error if incorrect (e.g., 'calculation', 'interpretation', 'none')")
    mistake_description: str = Field(..., description="Description of the mistake made, or 'none' if correct")
    correct_approach: str = Field(..., description="Brief description of the correct approach")


async def check_solution_correctness(
    agent: Agent,
    solution: str,
    ground_truth: str,
    question_context: str = ""
) -> CorrectnessAnalysis:
    """Check if solution matches ground truth and identify errors."""
    prompt = f"""Compare this solution to the ground truth answer.

Solution: {solution[:3000]}
Ground Truth: {ground_truth}
{f"Context: {question_context}" if question_context else ""}

Analyze:
1. Is the solution CORRECT? (Yes/No)
2. If incorrect, what TYPE of error? (calculation, interpretation, method, logic, or none)
3. Describe the MISTAKE made (or 'none' if correct)
4. What is the CORRECT approach?

Be precise and specific in your analysis."""

    try:
        result = await agent.run(prompt, result_type=CorrectnessAnalysis)
        return result.output
    except Exception:
        return CorrectnessAnalysis(
            is_correct=False,
            error_type="evaluation_failed",
            mistake_description="Could not evaluate correctness",
            correct_approach="Unknown"
        )
