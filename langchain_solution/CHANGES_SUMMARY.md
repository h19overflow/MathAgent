# Agent Recursion Fix - Complete Implementation Summary

## Problem Statement
The LangChain math agent was hitting the default 25-step recursion limit when processing Form 4/5 math problems, without producing solutions. The agent was stuck in an infinite tool-calling loop.

## Root Cause
LangChain's `create_agent()` operates in a tool-calling loop that continues until:
1. Model emits a final response (no tool calls)
2. Recursion limit is reached
3. Exception occurs

**Issue**: The system prompt didn't explicitly instruct the model when/how to stop, causing infinite tool-calling.

---

## Solutions Implemented

### 1. Explicit Stopping Instructions
**File**: `agent.py` lines 114-117, 297-300

Added clear "FINAL ANSWER" format to prompts:
```python
IMPORTANT: After completing all steps, provide your FINAL ANSWER in this format:
FINAL ANSWER: [Your complete answer here]

Once you provide the FINAL ANSWER above, STOP and do not call any more tools.
```

**Why**: LLMs respond to explicit instructions about when to stop.

---

### 2. Recursion Limit Configuration
**File**: `agent.py` lines 300 (extraction), 391 (solver)

Set stage-specific limits:
```python
# Extraction: Quick task, no tools needed
result = self.extraction_agent.invoke(
    {"messages": [message]},
    config={"recursion_limit": 5}
)

# Solver: May need multiple tool calls
result = self.solver_agent.invoke(
    {"messages": [...]},
    config={"recursion_limit": 10}
)
```

**Rationale**:
- **5 (extraction)**: Should complete in 1-2 steps; catches issues faster
- **10 (solver)**: Allows ~5 tool calls (each call + result = 2 steps); still prevents runaway loops

---

### 3. Error Handling & Message Logging
**File**: `agent.py` lines 27-91, 303-314 (extraction), 394-405 (solver)

Implemented comprehensive error capture:

#### New Function: `save_agent_output()`
```python
def save_agent_output(stage: str, result: dict, error_type: str = None) -> str:
    """Save agent conversation to agent_outputs/agent_output_{stage}_{error_type}_{timestamp}.json"""
    # Creates nicely formatted JSON with all messages
    # Captures tool calls, content, message types
    # Returns filepath for reference
```

#### Error Handling Pattern
```python
try:
    result = agent.invoke(..., config={"recursion_limit": N})
except GraphRecursionError as e:
    logger.error(f"✗ RECURSION LIMIT REACHED: {str(e)}")
    result = e.result if hasattr(e, 'result') else {"messages": []}
    save_agent_output("extraction", result, error_type="RECURSION_LIMIT")
    return f"Error: Recursion limit reached. Check agent_outputs/ for history.", 0
except Exception as e:
    logger.error(f"✗ Error: {str(e)}")
    return f"Error: {str(e)}", 0
```

---

## File Changes

### Modified Files
1. **`agent.py`** - Core changes
   - Added imports: `GraphRecursionError`, `json`, `datetime`
   - Added `save_agent_output()` function (65 lines)
   - Updated SOLVER_PROMPT with explicit stop instructions
   - Updated both `extract_from_image()` and `solve_from_extraction()` with error handling
   - Configured recursion limits on agent invocations

### New Documentation Files
1. **`AGENT_RECURSION_FIX.md`** - Technical deep-dive on the problem and solution
2. **`AGENT_OUTPUT_FORMAT.md`** - Complete guide to reading the JSON output files
3. **`CHANGES_SUMMARY.md`** - This file

---

## Output Structure

When agent hits recursion limit, a JSON file is created:

**Location**: `agent_outputs/agent_output_solver_RECURSION_LIMIT_20241029_143022.json`

**Format**:
```json
{
  "timestamp": "2024-10-29T14:30:22.123456",
  "stage": "solver",
  "error_type": "RECURSION_LIMIT",
  "messages": [
    {
      "index": 1,
      "type": "HumanMessage",
      "content": "...",
      "tool_calls": []
    },
    {
      "index": 2,
      "type": "AIMessage",
      "content": "...",
      "tool_calls": [{"tool_name": "solve_equation", "args": {...}}]
    },
    ...
  ]
}
```

**Useful for**:
- Debugging why agent looped
- Identifying repeated tool calls
- Understanding agent decision-making
- Improving prompts based on actual behavior

---

## Testing & Validation

### Expected Behavior After Fix

#### Success Case
```
logs/math_agent_test_20241029_143022.log
✓ Extraction successful
✓ Solver invocation completed
✓ Results saved to CSV
```

#### Recursion Limit Hit
```
logs/math_agent_test_20241029_143022.log
✗ RECURSION LIMIT REACHED: recursion limit (10) exceeded
✓ Agent output saved to: agent_outputs/agent_output_solver_RECURSION_LIMIT_20241029_143022.json

Check:
1. agent_outputs/ for message history
2. Identify repeated tool calls
3. Update SOLVER_PROMPT if needed
```

### How to Test

```bash
python -m langchain_solution.test_lang_agent --form 4 --model google_genai:gemini-2.5-flash-lite
```

Monitor:
1. **logs/** - For timeline and diagnostics
2. **agent_outputs/** - For message conversation (if error occurs)
3. **QAs/langchain_results/** - For CSV results

---

## Configuration Tuning

If you get recursion limit errors, try these adjustments:

```python
# In solve_from_extraction():
config={"recursion_limit": 15}  # Increase from 10 if more tool calls needed
```

### Recommendation Matrix

| Scenario | Limit | Reason |
|----------|-------|--------|
| Simple arithmetic (1 tool call) | 5 | Safer |
| Multi-step algebra (2-3 tools) | 10 | Balanced (DEFAULT) |
| Complex with verification (4-5 tools) | 15 | Allow chains |
| Debug mode (understand all calls) | 25 | Original default |

**Rule of Thumb**: Set limit to `(max_tool_calls * 2) + 1`

---

## Error Types Captured

The system now handles:

| Error Type | Location | Action |
|------------|----------|--------|
| `GraphRecursionError` | extract_from_image() | Save partial state, log clearly |
| `GraphRecursionError` | solve_from_extraction() | Save full conversation history |
| Generic `Exception` | Both stages | Caught by outer try-except, logged |
| Tool execution errors | Agent loop | Captured in ToolMessage content |

---

## Key Improvements

✅ **Explicit stopping condition** - Model knows when to output final answer
✅ **Reasonable iteration limits** - Stage-specific, prevents runaway loops
✅ **Complete message history** - JSON files for debugging
✅ **Clear error messages** - Points to agent_outputs/ for more info
✅ **Structured logging** - Timestamps and context preserved
✅ **No breaking changes** - Backward compatible with existing code

---

## Next Steps (Optional Enhancements)

1. **Implement token counting** - Track actual token usage (currently 0)
2. **Add response format validation** - Ensure "FINAL ANSWER:" is present
3. **Implement exponential backoff** - Retry with higher recursion_limit on failure
4. **Add metrics dashboard** - Track success rate, avg steps, tool call patterns
5. **Fine-tune limits per problem type** - Different limits for algebra vs statistics

---

## Files Modified Summary

```
langchain_solution/
├── agent_n_tools/
│   └── agent.py                    ← MODIFIED (agent + error handling)
├── AGENT_RECURSION_FIX.md          ← NEW (technical details)
├── AGENT_OUTPUT_FORMAT.md          ← NEW (output format guide)
├── CHANGES_SUMMARY.md              ← NEW (this file)
└── agent_outputs/                  ← NEW (created on first error)
    ├── agent_output_extraction_*.json
    └── agent_output_solver_*.json
```

---

## Questions & Troubleshooting

**Q: Agent still hits recursion limit?**
A: Check `agent_outputs/` JSON file for repeated tool calls. Update SOLVER_PROMPT to add more specific stopping condition.

**Q: No agent_outputs/ folder created?**
A: It's created automatically on first error. Check logs for error details.

**Q: How do I know if it's working?**
A:
1. Check logs for "✓ Solver invocation completed" (success)
2. Check for "FINAL ANSWER:" in the CSV results
3. No JSON files in agent_outputs/ is a good sign (no errors)

**Q: Should I increase recursion_limit?**
A: Only if you see legitimate tool calls in agent_outputs/ JSON. Otherwise, fix the prompt to stop earlier.

---

## Contact & Notes

For issues related to:
- **Agent prompts**: Check SOLVER_PROMPT wording, add more explicit stop conditions
- **Tool errors**: Check tool implementations in tools/ directory
- **Message format**: Review AGENT_OUTPUT_FORMAT.md for structure
- **Recursion behavior**: Check LangChain docs on GraphRecursionError

Last Updated: 2024-10-29
Status: ✅ Ready for testing
