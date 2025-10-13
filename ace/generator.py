"""Generator for the ACE evaluation framework."""
from typing import List, Optional
import logging
from pydantic import BaseModel
from pydantic_ai import Agent, BinaryContent
from ace.models import Context, ReasoningTrace, BulletFeedback

logger = logging.getLogger(__name__)


class BulletEvaluation(BaseModel):
    """A bullet evaluation is a single piece of information
     that is used to evaluate the performance of the model."""
    bullet_id: str
    was_helpful: bool
    reason: str


class GeneratorOutput(BaseModel):
    """A generator output is a single piece of information
    that is used to evaluate the performance of the model."""
    solution: str
    bullet_evaluations: List[BulletEvaluation]


async def generate_with_context(
    agent: Agent,
    context: Context,
    query: str,
    image_data: bytes,
    ground_truth: Optional[str] = None,
    use_llm_feedback: bool = False
) -> ReasoningTrace:

    """Generate a solution with a given context, query, and image data."""
    from ace.utils.relevance import filter_relevant_bullets

    relevant_bullets = [b for b in context.bullets if b.helpful_count > 0 or b.harmful_count == 0]
    relevant_bullets = filter_relevant_bullets(relevant_bullets, query)

    logger.debug(f"Using {len(relevant_bullets)}/{len(context.bullets)} relevant bullets")

    bullet_list = "\n".join([
        f"[ID:{b.id}] {b.content}"
        for b in relevant_bullets
    ])

    enhanced_prompt = f"""{query}

        Available strategies (reference by ID if used):
        {bullet_list}

        Solve the problem step-by-step. After your solution,
        evaluate which strategies were helpful or harmful."""

    result = await agent.run([enhanced_prompt,
    BinaryContent(data=image_data, media_type='image/png'),
    ])
    solution_text = result.output

    if use_llm_feedback and ground_truth:
        from ace.utils.feedback import evaluate_bullet_usefulness
        feedback_list = await evaluate_bullet_usefulness(
            agent, relevant_bullets, solution_text, ground_truth
        )
    else:
        feedback_list = []
        for bullet in relevant_bullets:
            mentioned = bullet.id in solution_text or any(
                word in solution_text.lower()
                for word in bullet.content.lower().split()[:5]
            )
            feedback_list.append(BulletFeedback(
                bullet_id=bullet.id,
                helpful=mentioned,
                reasoning="Referenced in solution" if mentioned else "Not used"
            ))

    return ReasoningTrace(
        steps=[solution_text],
        bullet_references=[b.id for b in relevant_bullets if b.id in solution_text],
        feedback=feedback_list
    )
