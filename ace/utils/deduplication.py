from typing import List
from ace.models import Bullet


def calculate_similarity(text1: str, text2: str) -> float:
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())

    if not words1 or not words2:
        return 0.0

    intersection = words1.intersection(words2)
    union = words1.union(words2)

    return len(intersection) / len(union)


def deduplicate_bullets(bullets: List[Bullet], threshold: float = 0.7) -> List[Bullet]:
    if not bullets:
        return []

    deduplicated = []
    for bullet in bullets:
        is_duplicate = False
        for existing in deduplicated:
            similarity = calculate_similarity(bullet.content, existing.content)
            if similarity >= threshold:
                existing.helpful_count += bullet.helpful_count
                existing.harmful_count += bullet.harmful_count
                is_duplicate = True
                break

        if not is_duplicate:
            deduplicated.append(bullet)

    return deduplicated
