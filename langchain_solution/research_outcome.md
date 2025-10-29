


## The Core Problem with Math Agents

Math agents fail in specific ways that cause NaN, empty responses, or wrong tool calls:[^5_4][^5_5][^5_1]

**Hallucination in calculations** - LLMs predict patterns, not compute actual math[^5_2][^5_6]

**Tool validation errors** - Missing arguments or incorrect tool schemas[^5_7][^5_8]

**Expression parsing failures** - numexpr and eval() fail on certain LLM-generated expressions[^5_1]

**Empty responses after max iterations** - Agent hits iteration limits without producing final answers[^5_5]

**Tool memory issues** - Agent forgets which tools were used and repeats incorrect selections[^5_9]

## Solutions from Production Math Agents

### 1. Robust Error Handling with Retry Logic

LangChain's official recommendation for math tools - implement **automatic retry with exception feedback**:[^5_7]

```python
from langchain_core.messages import AIMessage, HumanMessage, ToolCall, ToolMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

class MathToolException(Exception):
    """Custom exception for math tool errors."""
    def __init__(self, tool_call: ToolCall, exception: Exception) -> None:
        super().__init__()
        self.tool_call = tool_call
        self.exception = exception

def execute_tool_with_exception(msg: AIMessage, config) -> str:
    """Execute tool and raise custom exception on failure."""
    try:
        # Your tool execution logic
        tool_name = msg.tool_calls[^5_0]["name"]
        tool_args = msg.tool_calls[^5_0]["args"]
        
        # Execute the tool from your category map
        result = tool_registry[tool_name].invoke(tool_args, config=config)
        return result
    except Exception as e:
        raise MathToolException(msg.tool_calls[^5_0], e)

def exception_to_messages(inputs: dict) -> dict:
    """Convert exception to messages for retry."""
    exception = inputs.pop("exception")
    
    # Critical: Tell the model what went wrong
    messages = [
        AIMessage(content="", tool_calls=[exception.tool_call]),
        ToolMessage(
            tool_call_id=exception.tool_call["id"],
            content=f"Tool call failed: {str(exception.exception)}\n"
                   f"Error type: {type(exception.exception).__name__}\n"
                   f"Arguments provided: {exception.tool_call['args']}"
        ),
        HumanMessage(
            content="The tool call raised an error. Analyze the error message, "
                   "then try calling the tool again with CORRECTED arguments. "
                   "Ensure all required fields are provided."
        ),
    ]
    
    inputs["last_output"] = messages
    return inputs

# Build self-correcting chain
prompt = ChatPromptTemplate.from_messages([
    ("system", "{domain_prompt}"),  # Your specialized prompt per category
    ("human", "{input}"),
    ("placeholder", "{last_output}"),  # For error injection
])

llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0)
llm_with_tools = llm.bind_tools(your_category_tools)

chain = prompt | llm_with_tools | execute_tool_with_exception

# Self-correcting chain with fallback
self_correcting_chain = chain.with_fallbacks(
    [exception_to_messages | chain],
    exception_key="exception"
)

# Execute
result = self_correcting_chain.invoke({
    "domain_prompt": "You are an SPM Form 4/5 Mathematics expert...",
    "input": "Solve: 2x² + 5x - 3 = 0"
})
```


### 2. Strict Input Validation for Math Tools

The numexpr parsing issue is notorious. Implement **input sanitization**:[^5_1]

```python
from langchain_core.tools import tool
import re
from typing import Optional

@tool
def safe_calculator(expression: str) -> str:
    """
    Calculate mathematical expressions safely.
    Only accepts valid math expressions with numbers and operators.
    """
    # Strict validation
    allowed_chars = r'^[0-9+\-*/().\s\^√π]*$'
    if not re.match(allowed_chars, expression):
        return (
            f"Invalid expression: '{expression}'. "
            "Only numbers and operators (+, -, *, /, ^, √) are allowed. "
            "Remove any text or variables and try again."
        )
    
    # Replace common LLM mistakes
    expression = expression.replace("^", "**")  # Convert ^ to **
    expression = expression.replace("√", "math.sqrt")
    
    try:
        import math
        result = eval(expression, {"__builtins__": {}}, {"math": math})
        return f"Result: {result}"
    except Exception as e:
        return (
            f"Calculation error: {str(e)}. "
            f"The expression '{expression}' is malformed. "
            "Please simplify and try again with basic operators only."
        )

@tool
def quadratic_solver(a: float, b: float, c: float) -> str:
    """
    Solve quadratic equation ax² + bx + c = 0.
    Returns roots in exact format for SPM answers.
    
    Args:
        a: Coefficient of x² (must not be 0)
        b: Coefficient of x
        c: Constant term
    """
    # Validation
    if a == 0:
        return "Error: 'a' cannot be 0 for quadratic equations. Use linear equation solver instead."
    
    import math
    discriminant = b**2 - 4*a*c
    
    if discriminant > 0:
        root1 = (-b + math.sqrt(discriminant)) / (2*a)
        root2 = (-b - math.sqrt(discriminant)) / (2*a)
        return f"Two real roots: x₁ = {root1:.4f}, x₂ = {root2:.4f}"
    elif discriminant == 0:
        root = -b / (2*a)
        return f"One repeated root: x = {root:.4f}"
    else:
        real_part = -b / (2*a)
        imag_part = math.sqrt(abs(discriminant)) / (2*a)
        return f"Complex roots: x = {real_part:.4f} ± {imag_part:.4f}i"
```


### 3. Specialized Tool Descriptions (Critical!)

Your tool descriptions must be **extremely precise** for math domains:[^5_10][^5_1]

```python
# BAD - Vague description
calculator_tool = Tool(
    name="Calculator",
    func=safe_calculator,
    description="Useful for math calculations"
)

# GOOD - Explicit, constrained description
calculator_tool = Tool(
    name="Calculator",
    func=safe_calculator,
    description=(
        "Calculate numerical expressions ONLY. "
        "Input must be a pure mathematical expression with numbers and operators. "
        "Examples: '25 * 4', '(10 + 5) / 3', 'sqrt(144)'. "
        "DO NOT include: variables, equations, text, or word problems. "
        "For equations with unknowns, use the equation_solver tool instead."
    )
)

quadratic_tool = Tool(
    name="QuadraticSolver",
    func=quadratic_solver,
    description=(
        "Solve quadratic equations in form ax² + bx + c = 0. "
        "Input: Three numbers (a, b, c) where a≠0. "
        "Use this ONLY when equation is already in standard form. "
        "For word problems, extract coefficients first. "
        "Example: For '2x² + 5x - 3 = 0', input a=2, b=5, c=-3"
    )
)
```


### 4. Domain-Specific Prompts for SPM Math

Based on SPM Form 4/5 syllabus, create **topic-specific prompts**:[^5_11][^5_12]

```python
# Category: Algebra (Quadratic Functions, Systems of Equations)
algebra_prompt = """You are an SPM Form 4/5 Mathematics expert specializing in Algebra.

Topics you handle:
- Quadratic Functions (Chapter 2, Form 4)
- Systems of Equations (Chapter 3, Form 4)
- Matrices (Chapter 4, Form 5)

CRITICAL RULES:
1. ALWAYS show step-by-step working (required in SPM format)
2. Give EXACT answers (fractions/surds) unless question asks for decimals
3. For quadratic equations: Check discriminant first, then solve
4. For word problems: Define variables clearly before solving
5. For matrices: Show dimension compatibility before operations

Available tools and when to use them:
- QuadraticSolver: When equation is in form ax² + bx + c = 0
- MatrixCalculator: For matrix addition, subtraction, multiplication
- SystemSolver: For simultaneous equations (2 or 3 variables)

If a tool returns an error:
- Re-read the error message carefully
- Check if you provided all required arguments
- Verify the format matches tool requirements
- Try an alternative approach if needed
"""

# Category: Geometry & Trigonometry
geometry_prompt = """You are an SPM Form 4/5 Mathematics expert specializing in Geometry and Trigonometry.

Topics you handle:
- Trigonometry II (Chapter 9, Form 4)
- Trigonometry III (Chapter 6, Form 5)
- Bearing (Chapter 8, Form 5)

CRITICAL RULES:
1. Use DEGREES (not radians) unless stated otherwise in SPM
2. Draw mental diagrams - describe the geometric setup first
3. For bearing problems: Always start from North (000°), measure clockwise
4. Show all angle calculations and conversions

Available tools:
- TrigCalculator: Sin, cos, tan, inverse trig functions (in degrees)
- BearingCalculator: For navigation and bearing problems
- AngleConverter: Convert between degrees, minutes, seconds

Common mistakes to AVOID:
- Using radians instead of degrees
- Forgetting to convert DMS (degrees/minutes/seconds)
- Wrong quadrant for inverse trig functions
"""

# Map categories to prompts
category_prompts = {
    "algebra": algebra_prompt,
    "geometry": geometry_prompt,
    "statistics": statistics_prompt,
    "calculus": calculus_prompt,
}
```


### 5. Implement Wolfram Alpha Integration

For complex SPM problems, integrate **Wolfram Alpha** (reduces hallucination by 80%+):[^5_13][^5_6]

```python
from langchain.utilities.wolfram_alpha import WolframAlphaAPIWrapper
from langchain_core.tools import Tool

# Initialize Wolfram Alpha
wolfram = WolframAlphaAPIWrapper()

wolfram_tool = Tool(
    name="WolframAlpha",
    func=wolfram.run,
    description=(
        "Use Wolfram Alpha for COMPLEX mathematical problems that other tools cannot solve. "
        "This is a fallback for: "
        "- Advanced calculus (differentiation, integration) "
        "- Complex algebraic manipulations "
        "- Exact symbolic solutions "
        "Input: Natural language math query. "
        "Example: 'solve 3x^3 - 5x^2 + 2x - 7 = 0' "
        "Use this LAST after simpler tools fail."
    )
)

# Add to your tool list
tools = [
    safe_calculator,
    quadratic_solver,
    # ... other SPM-specific tools
    wolfram_tool  # Fallback for difficult problems
]
```


### 6. Increase Max Iterations and Add Timeout

Empty responses often come from hitting iteration limits:[^5_5]

```python
from langgraph.prebuilt import create_react_agent

# Create agent with proper limits
agent = create_react_agent(
    model=llm,
    tools=your_category_tools,
    state_modifier=category_prompts["algebra"],
    max_iterations=10,  # Increase from default (usually 5)
    max_execution_time=60.0,  # 60 second timeout
)

# Add explicit final answer instruction
final_answer_instruction = """
After using tools and gathering information, you MUST provide a final answer.

Format your final answer as:
FINAL ANSWER: [your answer here with full working shown]

Do not end your response without a FINAL ANSWER.
"""
```


### 7. Tool Memory and Context Tracking

For multi-step SPM problems, track tool usage:[^5_9]

```python
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages

class MathAgentState(TypedDict):
    messages: Annotated[list, add_messages]
    tools_used: list[str]  # Track which tools were called
    domain: str  # algebra, geometry, etc.
    error_count: int  # Track errors for circuit breaking
    working_shown: str  # Accumulate step-by-step working

def track_tool_usage(state: MathAgentState):
    """Middleware to track tools and prevent loops."""
    last_message = state["messages"][-1]
    
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        tool_name = last_message.tool_calls[^5_0]["name"]
        state["tools_used"].append(tool_name)
        
        # Prevent infinite tool loops
        if state["tools_used"].count(tool_name) > 3:
            return {
                "messages": [HumanMessage(
                    content=f"You've called {tool_name} 3 times. "
                           "Try a different approach or provide final answer."
                )]
            }
    
    return state
```


## SPM-Specific Best Practices

**Create tools for each SPM topic**:[^5_12][^5_11]

- Form 4: Functions, Quadratics, Sets, Reasoning, Indices/Surds, Linear Law, Statistics, Probability, Trigonometry
- Form 5: Progressions, Linear Programming, Integration, Vectors, Matrices, Variations, Probability, Bearing, Earth Geometry

**Use SPM answer format** in your system prompts - require step-by-step working and exact answers (fractions/surds)[^5_14]

**Test with past year SPM papers** to identify which categories cause most errors[^5_11]

**Temperature = 0** for all math operations to prevent hallucination[^5_1]

**Validate numerical answers** - check if results make sense in context (e.g., probability must be 0-1)[^5_7]

Your category approach is correct - the key is adding **robust error handling, strict validation, and self-correction loops** to handle the inevitable tool calling errors that plague math agents.[^5_8][^5_5][^5_7]
<span style="display:none">[^5_15][^5_16][^5_17][^5_18][^5_19][^5_20][^5_21][^5_22][^5_23][^5_24][^5_25][^5_26][^5_27]</span>

<div align="center">⁂</div>

[^5_1]: https://github.com/hwchase17/langchain/issues/3071

[^5_2]: https://cognitiveclass.ai/courses/how-to-build-ai-math-assistant-with-langchain-tool-calling

[^5_3]: https://www.geeksforgeeks.org/artificial-intelligence/building-a-math-application-with-langchain-agents/

[^5_4]: https://arxiv.org/html/2508.09932v1

[^5_5]: https://github.com/langgenius/dify/issues/20499

[^5_6]: https://www.alibabacloud.com/blog/lobechat-uses-the-wolframalpha-mcp-tool-to-reduce-llm-hallucinations_602178

[^5_7]: https://python.langchain.com/docs/how_to/tools_error/

[^5_8]: https://github.com/langchain-ai/langchain/discussions/25792

[^5_9]: https://github.com/n8n-io/n8n/issues/14361

[^5_10]: https://www.designveloper.com/blog/how-to-build-ai-agents-with-langchain/

[^5_11]: http://spmaddmaths.blog.onlinetuition.com.my

[^5_12]: https://www.scribd.com/doc/264014806/Syllabus-Modern-Mathematics-SPM

[^5_13]: https://www.wolfram.com/resources/tools-for-AIs/

[^5_14]: https://www.reddit.com/r/malaysia/comments/dyej4d/even_teachers_struggling_with_spm_add_maths/

[^5_15]: https://python.langchain.com/api_reference/langchain/chains/langchain.chains.llm_math.base.LLMMathChain.html

[^5_16]: https://forum.langchain.com/t/how-to-force-a-tool-call-for-an-agent/1554

[^5_17]: https://anyflip.com/micr/vdwy/basic/51-100

[^5_18]: https://arxiv.org/html/2408.02275v1

[^5_19]: https://langchain-ai.github.io/langgraphjs/how-tos/tool-calling-errors/

[^5_20]: https://www.wolframalpha.com/examples/mathematics

[^5_21]: https://www.wolframalpha.com

[^5_22]: https://www.reddit.com/r/math/comments/1c25llh/can_wolfram_ever_get_wrong_answers/

[^5_23]: https://store.pelangibooks.com/products/focus-spm-2025-mathematics-form-4-5

[^5_24]: https://www.warnacemerlang.edu.my/addmaths-online-tuition

[^5_25]: https://www.berrygoodtuitioncentre.com/spm-online-tuition-class

[^5_26]: https://purelystartup.com/post/ai-agents-for-education

[^5_27]: https://www.facebook.com/groups/parttimetutormalaysia/

