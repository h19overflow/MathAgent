# Math Agent with Tools - Phase 1 POC (Two-Stage Pipeline)

## Overview
This is the Phase 1 implementation of the Math Agent error mitigation system. It implements a **two-stage pipeline** architecture that mirrors `run_model_test.py`:

**Stage 1: Extraction** - Vision-based extraction agent analyzes problem images and extracts:
- Problem type and question text
- Visual elements (coordinates, diagrams, data)
- Constraints and qualitative requirements

**Stage 2: Solving** - Solver agent with 28 mathematical tools verifies calculations and solves problems:
- Symbolic equation solving (SymPy)
- Numerical verification (NumPy)
- Inequality validation and graphing
- Statistical analysis

## Directory Structure
```
agent_n_tools/
├── __init__.py          # Package initialization
├── agent.py             # Main agent orchestrator
├── README.md            # This file
└── tools/
    ├── __init__.py      # Tools package initialization
    ├── sympy_solver.py           # Symbolic math tools (5 tools)
    ├── numpy_calculator.py       # Numerical calculation tools (8 tools)
    ├── inequality_grapher.py     # Inequality validation tools (5 tools)
    └── statistics_utils.py       # Statistics tools (8 tools)
```

## Available Tools (28 Total)

### SymPy Solver Tools (5)
- `solve_equation`: Solve algebraic equations symbolically
- `simplify_expression`: Simplify mathematical expressions
- `expand_expression`: Expand factored expressions to polynomial form
- `check_inequality`: Solve inequalities symbolically
- `factor_expression`: Factor mathematical expressions

### NumPy Calculator Tools (8)
- `calculate_sum`: Sum a list of numbers
- `calculate_mean`: Calculate average
- `calculate_variance`: Calculate variance
- `calculate_standard_deviation`: Calculate standard deviation
- `calculate_percentage`: Calculate percentage of a value
- `calculate_sum_of_squares`: Calculate Σx²
- `calculate_frequency_distribution`: Get unique values and counts
- `validate_sum`: Verify if sum matches expected value

### Inequality Grapher Tools (5)
- `plot_linear_inequality`: Visualize inequalities on 2D graph
- `validate_point_in_inequality`: Check if a point satisfies an inequality
- `find_inequality_intercepts`: Find x and y intercepts
- `check_boundary_line`: Determine if boundary is solid or dashed
- `validate_inequality_solution_set`: Validate multiple points against inequality

### Statistics Utils Tools (8)
- `calculate_grouped_mean`: Mean of grouped data
- `calculate_grouped_variance`: Variance of grouped data
- `calculate_grouped_standard_deviation`: Standard deviation of grouped data
- `calculate_sum_fx`: Calculate Σfx (frequency × midpoint)
- `calculate_sum_fx_squared`: Calculate Σfx² (frequency × midpoint²)
- `calculate_cumulative_frequency`: Get cumulative frequencies
- `calculate_relative_frequency`: Calculate relative frequencies and percentages
- `calculate_median_class`: Find median class for grouped data

## Usage

### Text-Only Solving (Legacy Mode)
```python
from agent_n_tools import MathAgent

# Initialize the agent
agent = MathAgent()

# Solve a text problem directly
problem = "Solve the equation: 2x + 5 = 15"
solution = agent.solve(problem)
print(solution)
```

### Image Processing (Two-Stage Pipeline)
```python
from agent_n_tools import MathAgent

# Initialize the agent
agent = MathAgent()

# Process an image through extraction → solving
result = agent.process_image("path/to/math_problem.png")

print(f"Status: {result['status']}")
print(f"Extracted Data:\n{result['extracted_data']}")
print(f"Solution:\n{result['llm_answer']}")
print(f"Tokens Used: {result['tokens_used']}")
print(f"Model: {result['model']}")
```

### Direct Extraction and Solving
```python
# Stage 1: Extract from image
extracted_data, tokens = agent.extract_from_image("problem.png")

# Stage 2: Solve from extracted data
solution, tokens = agent.solve_from_extraction(extracted_data)
```

### Running the Examples
```bash
python agent.py
```

This will run 4 example scenarios:
1. Text-Only (Algebra): Solve 2x + 5 = 15
2. Statistics: Calculate Σfx and Σfx² with variance
3. Inequality: Validate boundary and points
4. Image Processing: Process sample_math_problem.png (if exists)

## Problem Categories Addressed

### Phase 1 Goals
✅ **Calculation Errors** - Tools validate arithmetic (sum, variance, Σfx²)
✅ **Incomplete Answers** - Agent tracks all question parts
✅ **Inequality Mistakes** - Tools validate boundaries and solution regions
✅ **Basic Conceptual** - Symbolic solving catches methodology issues

### Not Addressed in Phase 1
❌ **Question Misinterpretation** - Requires Phase 2+ (Visual Interpreter or Deep Agent)
❌ **Diagram Misreading** - Requires Phase 2+ (Visual Interpreter)
❌ **Complex Multi-domain Problems** - Requires Phase 3 (Deep Agent with sub-agents)

## Error Patterns from Form 4/5 Addressed

### From Form 4 (22 marks lost)
- **10 marks (Conceptual)**: Inequality graphing errors → caught by boundary validators
- **5 marks (Omission)**: Missing answer parts → agent tracks completeness
- **4 marks (Calculation)**: Σfx² errors, summing mistakes → validated by tools
- **3 marks (Misinterpretation)**: Safe route vs shortest route → Phase 2+

### From Form 5 (20 marks lost)
- **15 marks (Misinterpretation)**: Wrong question, diagram errors → Phase 2+
- **5 marks (Calculation)**: Percentage calculation errors → caught by tools

## Running Test Suite

A test script (`test_lang_agent.py`) is provided in the parent `langchain_solution/` directory:

```bash
# Test on Form 4
python test_lang_agent.py --form 4 --model claude-3-5-sonnet-20241022

# Test on Form 5
python test_lang_agent.py --form 5 --model claude-3-5-sonnet-20241022
```

This script:
- Reads CSV: `QAs/test_questions_mathform{4,5}.csv`
- Processes images from: `QAs/Soalan maths/form {4,5}/`
- Outputs results to: `QAs/langchain_results/test_results_form{4,5}_*.csv`
- Uses the same column structure as `run_model_test.py`

Output columns:
- `image_filename`: Original image filename
- `ground_truth`: Expected answer
- `marking_scheme`: Marking criteria
- `extracted_data`: Extracted structured data (Stage 1)
- `llm_answer`: Solver output (Stage 2)
- `tokens_used`: Total tokens consumed
- `status`: SUCCESS or ERROR
- `model`: Model used

## Dependencies
```
langchain>=0.1.0
langchain-anthropic>=0.1.0
sympy>=1.12
numpy>=1.24
matplotlib>=3.7
scipy>=1.10
pandas>=1.5.0
tqdm>=4.65.0
```

Install with:
```bash
uv add langchain langchain-anthropic sympy numpy matplotlib scipy pandas tqdm
```

## Architecture Notes

### Two-Stage Pipeline
1. **Extraction Agent** (no tools)
   - Uses vision capabilities of Claude
   - Outputs structured format: PROBLEM TYPE, QUESTION, VISUAL DATA, CONSTRAINTS
   - Critical for catching diagram misinterpretation early

2. **Solver Agent** (28 math tools)
   - Uses extracted structured data
   - Verifies calculations with tools
   - Applies constraints before finalizing answer
   - Returns final solution with reasoning

This mirrors the approach in `run_model_test.py` but with specialized math tools instead of generic solving.

## Notes for POC
- Uses Claude 3.5 Sonnet as the base LLM (configurable)
- All tools have type hints and clear documentation
- Error handling in each tool prevents agent crashes
- Image encoding handled automatically (PNG, JPEG, GIF, WebP)
- Token counting to be implemented (currently returns 0)
- Extraction prompt and solver prompt can be tuned for better results

## Next Steps (Phase 2+)
1. **Run test suite** on Form 4/5 against baseline from run_model_test.py
2. **Compare error rates**: Focus on calculation vs. misinterpretation errors
3. **If calculation errors reduced by 80%+**: Phase 2 is optional
4. **If still encountering misinterpretation issues**, proceed to:
   - **Phase 2**: Visual Interpreter Agent for better diagram understanding
   - **Phase 3**: Deep Agent with specialized sub-agents (Algebra, Statistics, Geometry)
