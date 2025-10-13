from typing import List
from ace.models import Bullet


def prune_bullets(bullets: List[Bullet], max_size: int) -> List[Bullet]:
    """Prune bullets based on score and helpful count."""
    if len(bullets) <= max_size:
        return bullets

    sorted_bullets = sorted(
        bullets,
        key=lambda b: (b.score, b.helpful_count),
        reverse=True
    )

    return sorted_bullets[:max_size]


def remove_harmful_bullets(bullets: List[Bullet], threshold: float = 0.3) -> List[Bullet]:
    """Remove harmful bullets based on score and helpful count."""
    return [b for b in bullets if b.score >= threshold or (b.helpful_count + b.harmful_count) == 0]
