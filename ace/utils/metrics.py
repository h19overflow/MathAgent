"""Metrics tracking for ACE framework."""
import logging
from typing import Dict, Any
from ace.models import Context

logger = logging.getLogger(__name__)


def log_context_metrics(context: Context, iteration: int) -> Dict[str, Any]:
    """Log and return context metrics."""
    total_bullets = len(context.bullets)
    helpful_bullets = sum(1 for b in context.bullets if b.helpful_count > 0)
    harmful_bullets = sum(1 for b in context.bullets if b.harmful_count > 0)
    neutral_bullets = total_bullets - helpful_bullets - harmful_bullets

    avg_score = sum(b.score for b in context.bullets) / total_bullets if total_bullets > 0 else 0

    metrics = {
        "iteration": iteration,
        "total_bullets": total_bullets,
        "helpful_bullets": helpful_bullets,
        "harmful_bullets": harmful_bullets,
        "neutral_bullets": neutral_bullets,
        "avg_score": avg_score
    }

    logger.info(
        f"Iteration {iteration} | Bullets: {total_bullets} "
        f"(Helpful: {helpful_bullets}, Harmful: {harmful_bullets}, Neutral: {neutral_bullets}) "
        f"| Avg Score: {avg_score:.2f}"
    )

    return metrics


def log_refinement_event(
    before_count: int,
    after_count: int,
    reason: str
) -> None:
    """Log context refinement event."""
    removed = before_count - after_count
    logger.info(
        f"Context refinement: {reason} | "
        f"Before: {before_count} | After: {after_count} | Removed: {removed}"
    )
