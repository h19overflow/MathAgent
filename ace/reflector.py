"""Reflector for the ACE evaluation framework."""
from typing import List
import uuid
import logging
from pydantic_ai import Agent
from ace.models import ReasoningTrace, Lesson, DeltaBullet, ReflectionOutput

logger = logging.getLogger(__name__)


async def reflect_on_reasoning(
    agent: Agent,
    trace: ReasoningTrace,
    ground_truth: str,
    use_correctness_check: bool = False
) -> List[Lesson]:
    """Reflect on the reasoning of the model."""
    lessons = []

    for feedback in trace.feedback:
        if feedback.helpful:
            lessons.append(Lesson(
                action="increment_helpful",
                bullet_id=feedback.bullet_id,
                helpful_increment=1
            ))
        else:
            lessons.append(Lesson(
                action="increment_harmful",
                bullet_id=feedback.bullet_id,
                harmful_increment=1
            ))

    solution_text = "\n".join(trace.steps)

    if use_correctness_check:
        from ace.utils.correctness import check_solution_correctness
        correctness = await check_solution_correctness(agent, solution_text, ground_truth)

        if correctness.is_correct:
            reflection_prompt = f"""Analyze this CORRECT solution to extract reusable strategies.

Solution: {solution_text[:3000]}
Ground Truth: {ground_truth}

Extract 0-2 novel insights that made this solution successful.
Focus on strategies that could help solve similar problems.
Be specific and actionable."""
        else:
            reflection_prompt = f"""Analyze this INCORRECT solution to prevent future errors.

Solution: {solution_text[:3000]}
Ground Truth: {ground_truth}

Error Type: {correctness.error_type}
Mistake: {correctness.mistake_description}
Correct Approach: {correctness.correct_approach}

Extract 0-2 lessons about:
1. What went wrong and why
2. How to avoid this error in future
Be specific and actionable."""
    else:
        reflection_prompt = f"""Analyze this math solution to extract NEW reusable strategies.

Solution: {solution_text[:5000]}
Ground Truth: {ground_truth}

Extract 0-2 novel insights that could help solve similar problems.
Only output genuinely new patterns not already in the knowledge base.
Be specific and actionable."""

    try:
        result = await agent.run(reflection_prompt, output_type=ReflectionOutput)

        for delta in result.output.new_insights[:2]:
            if delta.content and len(delta.content) > 10:
                lessons.append(Lesson(
                    action="add",
                    bullet_id=str(uuid.uuid4()),
                    content=delta.content,
                    metadata={"source": "llm_reflection", "reason": delta.reason}
                ))
                logger.debug(f"Extracted insight: {delta.content[:60]}...")
    except Exception as e:
        logger.warning(f"Reflection failed: {e}")

    return lessons
