# Message Object Access Fix

## Issue
LangChain agent messages are **objects**, not dictionaries. Using `.get()` method on objects fails.

## Problem Code
```python
final_message = result["messages"][-1]
solution = final_message.get("content", str(result))  # ❌ Objects don't have .get()
```

## Solution Applied
Implement fallback pattern that handles both dict and object types:

```python
final_message = result["messages"][-1]

# Handle both dict and message object types
if hasattr(final_message, 'get'):
    # Dict-like access
    solution = final_message.get("content", str(result))
elif hasattr(final_message, 'content'):
    # Object attribute access
    solution = final_message.content
else:
    # Fallback to string conversion
    solution = str(final_message)
```

## Files Updated
- `agent.py:328-333` - Extraction method (cleaned up from long ternary)
- `agent.py:423-428` - Solver method (fixed from dict-only access)

## Pattern Applied
This pattern is now consistent across:
1. **extract_from_image()** - Extracts problem description
2. **solve_from_extraction()** - Extracts final solution
3. **save_agent_output()** - Saves messages to JSON

## Message Types in LangChain

| Type | Structure | Access |
|------|-----------|--------|
| HumanMessage | Object with `.content` | `msg.content` |
| AIMessage | Object with `.content` + `.tool_calls` | `msg.content`, `msg.tool_calls` |
| ToolMessage | Object with `.content` | `msg.content` |
| Dict | Dict with keys | `msg.get("content")` |

## Testing

The fix handles:
- ✅ Message objects from LangChain agents
- ✅ Dict responses (backward compatibility)
- ✅ Nested content (lists, complex objects)
- ✅ Fallback to string conversion

## Why This Works

```python
# Before: Assumes dict only
final_message.get("content")  # Fails on objects

# After: Intelligent fallback
if hasattr(final_message, 'get'):      # Is it dict-like?
elif hasattr(final_message, 'content'):  # Is it a message object?
else:                                   # Convert to string as last resort
```

This approach is robust and handles edge cases gracefully.
