from typing import List
import logging
from ace.models import Context, Lesson, Bullet
from ace.utils.deduplication import deduplicate_bullets
from ace.utils.pruning import prune_bullets, remove_harmful_bullets

logger = logging.getLogger(__name__)


def curate_context(
    context: Context,
    lessons: List[Lesson],
    max_context_size: int = 20,
    refinement_mode: str = "lazy"
) -> Context:
    before_count = len(context.bullets)

    for lesson in lessons:
        if lesson.action == "add" and lesson.content:
            new_bullet = Bullet(
                id=lesson.bullet_id,
                content=lesson.content,
                metadata=lesson.metadata
            )
            context.add_bullet(new_bullet)
            logger.debug(f"Added bullet: {lesson.content[:50]}...")

        elif lesson.action in ("increment_helpful", "increment_harmful") and lesson.bullet_id:
            bullet = context.get_bullet_by_id(lesson.bullet_id)
            if bullet:
                bullet.helpful_count += lesson.helpful_increment
                bullet.harmful_count += lesson.harmful_increment
                logger.debug(f"Updated bullet {bullet.id}: +{lesson.helpful_increment}h/{lesson.harmful_increment}harm")

    should_refine = (
        refinement_mode == "eager" or
        (refinement_mode == "lazy" and len(context.bullets) > max_context_size)
    )

    if should_refine:
        before_refine = len(context.bullets)
        context.bullets = deduplicate_bullets(context.bullets)
        after_dedup = len(context.bullets)
        context.bullets = remove_harmful_bullets(context.bullets)
        after_harmful = len(context.bullets)
        context.bullets = prune_bullets(context.bullets, max_context_size)
        after_prune = len(context.bullets)

        logger.info(
            f"Refinement ({refinement_mode}): {before_refine} -> "
            f"dedup:{after_dedup} -> harmful:{after_harmful} -> prune:{after_prune}"
        )

    return context
