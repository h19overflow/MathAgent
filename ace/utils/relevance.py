"""Relevance utils for the ACE evaluation framework."""
from typing import List
from ace.models import Bullet


def is_relevant(bullet: Bullet, query: str) -> bool:
    """Check if a bullet is relevant to a given query."""
    query_lower = query.lower()
    content_lower = bullet.content.lower()

    keywords = query_lower.split()
    matches = sum(1 for kw in keywords if kw in content_lower)

    relevance_threshold = 0.2
    return (matches / len(keywords)) >= relevance_threshold if keywords else False


def filter_relevant_bullets(bullets: List[Bullet], query: str) -> List[Bullet]:
    """Filter relevant bullets for a given query."""
    return [b for b in bullets if is_relevant(b, query)]
