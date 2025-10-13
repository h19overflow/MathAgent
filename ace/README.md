# ACE (Agentic Context Engineering) Implementation

Implementation of the ACE framework from the research paper for adaptive mathematical problem-solving.

## Architecture

```
ace/
├── models.py           # Bullet, Context, ReasoningTrace, Lesson
├── generator.py        # Generate solutions with context-aware reasoning
├── reflector.py        # Extract delta updates via LLM reflection
├── curator.py          # Merge deltas with grow-and-refine
├── orchestrator.py     # Pipeline: Generate → Reflect → Curate
└── utils/
    ├── relevance.py    # Bullet relevance filtering
    ├── deduplication.py # Semantic deduplication (Jaccard)
    ├── embeddings.py   # Embedding support for future enhancement
    └── pruning.py      # Context size management
```

## Key Principles (from Paper)

### 1. Incremental Delta Updates
- Context as structured bullets (not monolithic prompts)
- Each bullet has: unique ID, helpful/harmful counters, content
- Reflector produces compact delta contexts (add/increment operations)
- Curator merges deltas deterministically without full rewrites

### 2. Grow-and-Refine
- **Lazy refinement**: Deduplicate/prune only when context exceeds max size
- **Eager refinement**: Deduplicate/prune after every delta
- Semantic deduplication merges similar bullets
- Pruning maintains top-k helpful bullets

### 3. Multi-Epoch Adaptation
- Context evolves across problems
- Helpful strategies accumulate higher scores
- Harmful strategies are deprioritized or removed
- New insights extracted via LLM reflection

## Workflow

```
For each query:
  1. Generator: Solve problem using relevant bullets → reasoning trace
  2. Reflector: Analyze trace → extract delta lessons (LLM-based)
  3. Curator: Apply deltas → grow context → refine if needed
  4. Updated context ready for next query
```

## Usage

```python
from ace.orchestrator import initialize_context, run_ace_pipeline
from pydantic_ai import Agent

agent = Agent("gemini-2.0-flash-exp")
context = initialize_context()

for problem in problems:
    answer, context = await run_ace_pipeline(
        agent, context, query, image_data, ground_truth,
        refinement_mode="lazy"  # or "eager"
    )
```

## Running Tests

```bash
python run_ace_test.py --form 4
python run_ace_test.py --form 5
```

Results: `QAs/ace-results/test_results_form{4,5}_ace.csv`

## Design Principles

- KISS: Files under 150 lines
- SRP: Single responsibility per module
- Incremental: Delta updates, not full rewrites
- Adaptive: Context evolves from experience
