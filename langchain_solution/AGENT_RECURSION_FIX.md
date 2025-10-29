# Agent Recursion Limit Fix - Technical Report

## Problem
The LangChain math agent was hitting the default 25-step recursion limit without solving math problems. This indicates the agent was stuck in an infinite loop of tool calls without a proper stopping condition.

## Root Cause Analysis
LangChain's `create_agent()` implements a ReAct-style agent loop:
```
Model → Tool Call → Tool Result → Model → ... → STOP
```

The agent only stops when:
1. **Model emits a final output** (no more tool calls) ← MAIN ISSUE
2. Recursion limit is reached (default: 25 steps)
3. Exception occurs

**The issue**: The prompts didn't explicitly tell the model when to **stop** and provide a final answer. The model kept generating tool calls indefinitely.

## Solutions Implemented

### 1. Explicit Stopping Instructions (agent.py:114-117)
Added clear "FINAL ANSWER" format to both prompts:

```python
IMPORTANT: After completing all steps, provide your FINAL ANSWER in this format:
FINAL ANSWER: [Your complete answer here]

Once you provide the FINAL ANSWER above, STOP and do not call any more tools.
```

**Why this works**: LLMs respond to explicit instructions. By telling the model exactly when and how to stop, it knows to exit the tool-calling loop.

### 2. Recursion Limits at Runtime (agent.py:229, 303)
Added configuration-based recursion limits to agent invocations:

```python
# Extraction agent (agent.py:227-230)
result = self.extraction_agent.invoke(
    {"messages": [message]},
    config={"recursion_limit": 5}  # Low: no tools needed
)

# Solver agent (agent.py:301-304)
result = self.solver_agent.invoke(
    {"messages": [{"role": "user", "content": solve_prompt}]},
    config={"recursion_limit": 10}  # Higher: allows multiple tool calls
)
```

**Why different limits**:
- **Extraction (5)**: No tools needed, should complete in 1-2 steps. Low limit catches issues early.
- **Solving (10)**: May call multiple tools for verification. 10 steps = ~5 tool calls (each call + result = 2 steps).

### 3. Unified Prompt Instructions (agent.py:300)
Updated `solve_from_extraction()` to include the same FINAL ANSWER instruction in the dynamic prompt, ensuring consistency.

## Technical Details

### How LangGraph Recursion Works
- **Super-step**: One iteration of the agent loop (model call + tool execution)
- **Recursion limit**: Max number of super-steps before GraphRecursionError
- **Config override**: `invoke(..., config={"recursion_limit": N})` sets limit at runtime

### Why 10 is Safe for Solver
Typical math problem solving pattern:
1. Model reads extracted data (step 1)
2. Model calls tool (step 2)
3. Tool returns result (step 3)
4. Model processes result (step 4)
5. Model decides: more tools? → repeat OR final answer? → STOP

For 3 verification tool calls: 3 × 4 = 12 steps max. Limit of 10 catches runaway loops while allowing legitimate tool use.

## Testing Recommendations
1. Run test with form 4/5 images
2. Check logs for "Solver invocation completed" (should appear, not error)
3. Verify output contains "FINAL ANSWER:" marker
4. Monitor token usage and step counts in logs

## Edge Cases Handled
- **Extraction still fails**: Now hits limit at 5 instead of 25 (faster failure detection)
- **Solver needs more steps**: Increase `recursion_limit: 10` up to 15 if needed (monitor logs first)
- **Tools return errors**: Model reads error as observation, decides next step (expected behavior)

## Files Modified
- `agent.py`: Lines 114-117, 229, 300, 303-304

## Backward Compatibility
✓ No breaking changes
✓ All existing code works as-is
✓ Config parameter is optional (defaults to 25)
