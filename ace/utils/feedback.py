"""LLM-based bullet feedback evaluation."""
from typing import List
from pydantic import BaseModel
from pydantic_ai import Agent
from ace.models import Bullet, BulletFeedback


class BulletRating(BaseModel):
    """Rating for a single bullet."""
    bullet_id: str
    rating: str
    reason: str


class FeedbackEvaluation(BaseModel):
    """Structured feedback evaluation output."""
    ratings: List[BulletRating]


async def evaluate_bullet_usefulness(
    agent: Agent,
    bullets: List[Bullet],
    solution: str,
    ground_truth: str
) -> List[BulletFeedback]:
    """Evaluate which bullets were actually helpful using LLM."""
    if not bullets:
        return []

    bullet_list = "\n".join([
        f"[{b.id}] {b.content}"
        for b in bullets
    ])

    prompt = f"""Evaluate which strategies were helpful or harmful in this solution.

Solution: {solution[:3000]}
Ground Truth: {ground_truth}

Strategies used:
{bullet_list}

For each strategy, rate as: HELPFUL, HARMFUL, or NEUTRAL
- HELPFUL: Strategy contributed to correct reasoning
- HARMFUL: Strategy led to errors or confusion
- NEUTRAL: Strategy was mentioned but not impactful

Be strict: only mark as HELPFUL if it genuinely improved the solution."""

    try:
        result = await agent.run(prompt, result_type=FeedbackEvaluation)

        feedback_list = []
        rating_map = {r.bullet_id: r for r in result.output.ratings}

        for bullet in bullets:
            rating = rating_map.get(bullet.id)
            if rating:
                is_helpful = rating.rating.upper() == "HELPFUL"
                feedback_list.append(BulletFeedback(
                    bullet_id=bullet.id,
                    helpful=is_helpful,
                    reasoning=rating.reason
                ))

        return feedback_list
    except Exception:
        return [
            BulletFeedback(bullet_id=b.id, helpful=False, reasoning="Evaluation failed")
            for b in bullets
        ]
