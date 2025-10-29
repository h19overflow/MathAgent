# Agent Output Format Documentation

## Overview
When an agent hits a recursion limit or encounters an error, it automatically saves the message history to a JSON file in the `agent_outputs/` directory for debugging and analysis.

## File Naming
```
agent_outputs/agent_output_{stage}_{error_type}_{timestamp}.json
```

Examples:
- `agent_output_extraction_RECURSION_LIMIT_20241029_143022.json`
- `agent_output_solver_RECURSION_LIMIT_20241029_143022.json`
- `agent_output_extraction_20241029_143022.json` (no error)

## Output Format

### Top-Level Structure
```json
{
  "timestamp": "2024-10-29T14:30:22.123456",
  "stage": "solver",
  "error_type": "RECURSION_LIMIT",
  "messages": [
    { ... },
    { ... }
  ]
}
```

### Message Entry
```json
{
  "index": 1,
  "type": "HumanMessage",
  "content": "Here is the extracted data...",
  "tool_calls": []
}
```

### Message Types

#### HumanMessage
User input to the agent
```json
{
  "index": 1,
  "type": "HumanMessage",
  "content": "Solve this problem: x + 5 = 10",
  "tool_calls": []
}
```

#### AIMessage (with tool calls)
Agent decides to call tools
```json
{
  "index": 2,
  "type": "AIMessage",
  "content": "I'll solve this equation using the solver tool.",
  "tool_calls": [
    {
      "tool_name": "solve_equation",
      "args": {"equation": "x + 5 = 10"}
    }
  ]
}
```

#### ToolMessage
Tool result returned to agent
```json
{
  "index": 3,
  "type": "ToolMessage",
  "content": "{\"solution\": {\"x\": 5}}"
}
```

#### AIMessage (final answer)
Agent's final response
```json
{
  "index": 4,
  "type": "AIMessage",
  "content": "FINAL ANSWER: x = 5",
  "tool_calls": []
}
```

## Example: Complete Solver Recursion Error

File: `agent_output_solver_RECURSION_LIMIT_20241029_143022.json`

```json
{
  "timestamp": "2024-10-29T14:30:22.123456",
  "stage": "solver",
  "error_type": "RECURSION_LIMIT",
  "messages": [
    {
      "index": 1,
      "type": "HumanMessage",
      "content": "Solve: Find the value of x where 2x + 3 = 11",
      "tool_calls": []
    },
    {
      "index": 2,
      "type": "AIMessage",
      "content": "I'll solve this equation step by step.",
      "tool_calls": [
        {
          "tool_name": "solve_equation",
          "args": {"equation": "2*x + 3 - 11"}
        }
      ]
    },
    {
      "index": 3,
      "type": "ToolMessage",
      "content": "{\"solution\": [4]}"
    },
    {
      "index": 4,
      "type": "AIMessage",
      "content": "Let me verify this solution...",
      "tool_calls": [
        {
          "tool_name": "check_inequality",
          "args": {"expression": "2*4 + 3"}
        }
      ]
    },
    {
      "index": 5,
      "type": "ToolMessage",
      "content": "Result: 11"
    },
    {
      "index": 6,
      "type": "AIMessage",
      "content": "Let me check once more to be sure...",
      "tool_calls": [
        {
          "tool_name": "simplify_expression",
          "args": {"expression": "2*x + 3 - 11"}
        }
      ]
    },
    {
      "index": 7,
      "type": "ToolMessage",
      "content": "{\"simplified\": \"2*x - 8\"}"
    },
    {
      "index": 8,
      "type": "AIMessage",
      "content": "Continuing verification...",
      "tool_calls": [
        {
          "tool_name": "solve_equation",
          "args": {"equation": "2*x - 8"}
        }
      ]
    },
    {
      "index": 9,
      "type": "ToolMessage",
      "content": "{\"solution\": [4]}"
    },
    {
      "index": 10,
      "type": "AIMessage",
      "content": "Checking again... (recursion limit hit after this)",
      "tool_calls": [
        {
          "tool_name": "check_inequality",
          "args": {"expression": "2*4 + 3 = 11"}
        }
      ]
    }
  ]
}
```

## How to Read

1. **Trace the conversation** - Follow `index` 1→2→3... to see what the agent did at each step
2. **Check tool calls** - Look for repeated tool calls which indicate looping
3. **Identify the issue** - See where the agent got stuck (e.g., repeatedly calling same tool)
4. **Update prompts** - Use the pattern to improve the system prompt to prevent loop

## Debugging Tips

### Sign of Infinite Loop
- Same `tool_name` appearing multiple times in consecutive messages
- `tool_calls` array not empty in messages near the end (should be empty at final answer)
- Messages count near 10 (your `recursion_limit` config value)

### Expected Successful Pattern
1. HumanMessage (user input)
2. AIMessage with tool_calls
3. ToolMessage (result)
4. AIMessage with tool_calls (optional, for verification)
5. ToolMessage (optional result)
6. AIMessage with **empty** tool_calls → "FINAL ANSWER: ..."

### Common Issues & Fixes

| Pattern | Issue | Fix |
|---------|-------|-----|
| Repeated tool X calls | Agent can't decide when to stop | Strengthen prompt with "FINAL ANSWER" format |
| All messages are HumanMessage | Agent never invoked | Check if tools are properly bound |
| AIMessage but no tool_calls | Wrong agent state | Verify tool schema |
| Tool result ignored | Agent not reading feedback | Check ToolMessage parsing |

## Where to Find Files

```
your_project/
├── logs/
│   └── math_agent_test_*.log         # Standard agent logs
├── agent_outputs/
│   ├── agent_output_extraction_*.json  # Extraction stage errors
│   ├── agent_output_solver_*.json      # Solver stage errors
│   └── agent_output_solver_RECURSION_LIMIT_*.json  # Specific recursion errors
```

## Integration with Logging

These JSON files **complement** the standard log files:
- **LOG FILES**: Timeline of actions, debug messages, full errors
- **JSON FILES**: Exact message conversation, tool calls, parameters

Use together for complete debugging:
1. Check `logs/` for when and why error occurred
2. Check `agent_outputs/` for what the agent conversation looked like
