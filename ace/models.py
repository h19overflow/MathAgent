"""Models for the ACE evaluation framework."""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class Bullet(BaseModel):
    """A bullet is a single piece of information that is used to evaluate the performance of the model."""

    id: str
    content: str
    helpful_count: int = 0
    harmful_count: int = 0
    metadata: Dict = Field(default_factory=dict)

    @property
    def score(self) -> float:
        """Calculate the score of the bullet."""
        total = self.helpful_count + self.harmful_count
        if total == 0:
            return 0.0
        return self.helpful_count / total


class Context(BaseModel):
    """A context is a collection of bullets that are used to evaluate the performance of the model."""

    bullets: List[Bullet] = Field(default_factory=list)

    def add_bullet(self, bullet: Bullet) -> None:
        """Add a bullet to the context."""
        self.bullets.append(bullet)

    def get_bullet_by_id(self, bullet_id: str) -> Optional[Bullet]:
        """Get a bullet by its id."""
        for bullet in self.bullets:
            if bullet.id == bullet_id:
                return bullet
        return None

    def remove_bullet(self, bullet_id: str) -> None:
        """Remove a bullet by its id."""
        self.bullets = [b for b in self.bullets if b.id != bullet_id]

    def to_prompt_context(self) -> str:
        """Convert the context to a prompt context."""
        if not self.bullets:
            return ""
        lines = ["Available strategies and insights:"]
        for bullet in self.bullets:
            lines.append(f"- {bullet.content}")
        return "\n".join(lines)


class BulletFeedback(BaseModel):
    """A bullet feedback is a single piece of information that is used to evaluate the performance of the model."""

    bullet_id: str
    helpful: bool
    reasoning: str = ""


class ReasoningTrace(BaseModel):
    """A reasoning trace is a collection of steps that are used to evaluate the performance of the model."""

    steps: List[str]
    bullet_references: List[str] = Field(default_factory=list)
    feedback: List[BulletFeedback] = Field(default_factory=list)


class Lesson(BaseModel):
    """A lesson is a single piece of information that is used to evaluate the performance of the model."""

    action: str
    bullet_id: Optional[str] = None
    content: Optional[str] = None
    helpful_increment: int = 0
    harmful_increment: int = 0
    metadata: Dict = Field(default_factory=dict)

class DeltaBullet(BaseModel):
    """A delta bullet is a single piece of information that is used to evaluate the performance of the model."""
    content: str = Field(..., description="The content of the delta bullet.")
    reason: str = Field(..., description="The reason for the delta bullet.")


class ReflectionOutput(BaseModel):
    """A reflection output is a single piece of information that is used to evaluate the performance of the model."""
    new_insights: List[DeltaBullet] = Field(..., description="The new insights from the reflection.")
