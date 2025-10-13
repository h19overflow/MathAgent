"""Orchestrator for the ACE evaluation framework."""
import uuid
from pydantic_ai import Agent
from ace.models import Context, Bullet
from ace.generator import generate_with_context
from ace.reflector import reflect_on_reasoning
from ace.curator import curate_context


INITIAL_BULLETS = [
    "Identify diagram type first (graph, Venn, histogram, network)",
    "Extract all numerical values and labels before solving",
    "State the explicit goal clearly",
    "Show every calculation step with intermediate results",
    "Verify final answer matches question format and units",
]


def initialize_context() -> Context:
    """Initialize the context for the ACE evaluation framework."""
    context = Context()
    for content in INITIAL_BULLETS:
        bullet = Bullet(
            id=str(uuid.uuid4()),
            content=content,
            helpful_count=1,
            harmful_count=0,
            metadata={"source": "initial", "epoch": 0}
        )
        context.add_bullet(bullet)
    return context


async def run_ace_pipeline(
    agent: Agent,
    context: Context,
    query: str,
    image_data: bytes,
    ground_truth: str,
    refinement_mode: str = "lazy",
    use_llm_feedback: bool = False,
    use_correctness_check: bool = False,
    max_context_size: int = 20
) -> tuple[str, Context, int]:
    """Run the ACE evaluation pipeline."""
    total_tokens = 0

    trace = await generate_with_context(
        agent, context, query, image_data, ground_truth, use_llm_feedback
    )
    total_tokens += getattr(trace, 'tokens_used', 0)

    lessons = await reflect_on_reasoning(agent, trace, ground_truth, use_correctness_check)

    updated_context = curate_context(
        context,
        lessons,
        max_context_size=max_context_size,
        refinement_mode=refinement_mode
    )

    answer = " ".join(trace.steps)
    return answer, updated_context, total_tokens
