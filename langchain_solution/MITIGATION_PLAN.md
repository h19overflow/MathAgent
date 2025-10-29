# Math Agent Error Mitigation Plan (POC)

## Executive Summary
This plan addresses key error patterns from Form 4 (22 marks lost across 10 errors) and Form 5 (20 marks lost across 5 errors) through a three-phase experimental approach using LangChain agents with progressively complex capabilities.

---

## Error Analysis & Root Causes

### Common Mistake Patterns (F4 + F5)
| Category | Root Cause | Frequency | Impact |
|----------|-----------|-----------|--------|
| **Conceptual/Methodological Errors** | Wrong formulas, incorrect inequality directions, flawed graphing logic | 4 instances (F4) | High (10 marks) |
| **Calculation Errors** | Summing errors, Σfx² miscalculation, single value calculation failures | 2 instances (F4) + 2 instances (F5) | Medium (9 marks total) |
| **Misinterpretation** | Answering wrong question, wrong assessment method, misreading diagrams | 4 instances (F4+F5) | High (15 marks F5 alone) |
| **Omission/Incomplete** | Missing answer parts, incomplete numerical results | 3 instances (F4) | Medium (5 marks) |

---

## Phase 1: SymPy/NumPy Tools + Agent (Baseline POC)

### Goal
Add mathematical tools to the base agent to catch calculation and basic conceptual errors.

### Tools to Implement
```
math_tools/
├── sympy_solver.py           # Symbolic math: solve equations, simplify, expand
├── numpy_calculator.py       # Numerical: sum, mean, variance, std, matrix ops
├── inequality_grapher.py     # Visualize inequalities, detect boundary errors
└── statistics_utils.py       # Σfx², frequency analysis, percentages
```

### Agent Structure
- **LangChain Agent** with ReAct loop
- Tools available: calculator, sympy solver, statistics analyzer, graph validator
- **Validation Step**: After each calculation, re-verify with different method
- **Output Checklist**: Ensure all question parts are addressed

### Expected Wins
- ✅ Catch arithmetic errors (re-calculate sums using NumPy)
- ✅ Catch inequality mistakes (symbolic verification with SymPy)
- ✅ Catch incomplete answers (checklist against question structure)

### Expected Gaps
- ❌ Won't solve misinterpretation errors (wrong question answered)
- ❌ Won't fix conceptual methodology if question is misunderstood
- ❌ Graph visualization limited without visual validation

### Success Metric
Reduce calculation errors by 80%+ on Form 4/5 retests.

---

## Phase 2: Visual Interpreter Agent (If Phase 1 Insufficient)

### Goal
Add a sub-agent specialized in interpreting visual/diagram information from questions.

### How It Works
1. **Main Agent** encounters a geometry/graph question
2. **Main Agent** sends request to **Visual Interpreter Agent**:
   ```python
   {
     "coordinates": [(x1, y1), (x2, y2), ...],
     "focus_points": ["boundary_line", "intersection", "shaded_region"],
     "question_snippet": "Identify the region satisfying x + y ≤ 5"
   }
   ```
3. **Visual Interpreter Agent** returns state with observations:
   ```python
   {
     "identified_boundaries": [...],
     "inequality_directions": ["≤", "≥"],
     "critical_points": [...],
     "visual_confidence": 0.85
   }
   ```
4. **Main Agent** uses this state to construct better response

### Tools in Visual Interpreter
- Matplotlib for rendering coordinates
- Scipy for intersection detection
- Simple CV heuristics (corner detection, line recognition)

### Expected Wins
- ✅ Prevent misreading of diagram values (catches the "80m segment" error)
- ✅ Validate inequality directions on graphs
- ✅ Identify shaded regions correctly

### Expected Gaps
- ❌ Won't help with "answered completely different question" errors
- ❌ Doesn't improve conceptual understanding
- ❌ Requires coordinate extraction (manual or OCR)

### Success Metric
Reduce geometry/graph misinterpretation by 70%+ on Form 4 questions.

---

## Phase 3: Deep Agent with Sub-Agents (Full POC)

### Goal
Decompose complex math problems into sub-problems, each solved by specialized sub-agents.

### Architecture

```
┌─────────────────────────────────────────┐
│    Main Deep Agent (LangChain)          │
│  ├─ Questions Parser                    │
│  ├─ Problem Decomposer                  │
│  └─ Answer Aggregator                   │
└─────────────────────────────────────────┘
            │
            ├─→ Sub-Agent: Algebra Solver
            │    └─ Tools: SymPy (solve, simplify, expand)
            │
            ├─→ Sub-Agent: Statistics Analyzer
            │    └─ Tools: NumPy (variance, freq, percentages)
            │
            ├─→ Sub-Agent: Geometry Validator
            │    └─ Tools: SymPy geometry + Visual Interpreter
            │
            └─→ Sub-Agent: Graph Interpreter (Optional)
                 └─ Tools: Matplotlib + coordinate validator
```

### How It Works
1. **Main Agent** parses question and identifies problem types
2. **Main Agent** routes to appropriate Sub-Agent(s)
3. Each **Sub-Agent** solves its portion using specialized tools
4. **Main Agent** validates all parts are complete and correct
5. **Main Agent** aggregates final answer

### Expected Wins
- ✅ Specialized reasoning per math domain
- ✅ Reduces conceptual errors (focused sub-agents)
- ✅ Better error isolation (know which step failed)
- ✅ Tool reuse and modularity

### Expected Gaps
- ❌ Still won't catch fundamental question misinterpretation (why agent answered blood pressure instead of blood glucose)
- ❌ Requires careful prompt engineering per sub-agent
- ❌ More complex to debug

### Success Metric
Achieve 85%+ score on Form 4/5 with minimal re-attempts.

---

## Implementation Roadmap

### Phase 1 Timeline (Week 1)
- [ ] Create `math_tools/` directory structure
- [ ] Implement `sympy_solver.py` with: solve(), simplify(), inequality validation
- [ ] Implement `numpy_calculator.py` with: sum(), variance(), standard deviation()
- [ ] Implement `inequality_grapher.py` with basic line plotting
- [ ] Create base agent with tool bindings
- [ ] Test on 5 Form 4 questions (subset of 10 errors)

### Phase 2 Timeline (Week 2, if needed)
- [ ] Create `visual_interpreter_agent.py`
- [ ] Add matplotlib visualization tools
- [ ] Create state schema for visual observations
- [ ] Integrate as tool in main agent
- [ ] Test on geometry/graph subset

### Phase 3 Timeline (Week 3+, if needed)
- [ ] Create `deep_agent_orchestrator.py`
- [ ] Implement sub-agents (Algebra, Statistics, Geometry)
- [ ] Route questions to correct sub-agents
- [ ] Validate completeness before final answer
- [ ] Full test on 22 Form 5 questions

---

## Technical Stack

```
Core:
  - LangChain (Agent + DeepLearning if available)
  - LangGraph (Graph-based agent workflows)

Math Libraries:
  - SymPy (symbolic math, equation solving)
  - NumPy (numerical calculations, statistics)
  - SciPy (advanced stats, optimization)

Visualization:
  - Matplotlib (plotting inequalities, graphs)
  - Pillow (image handling if needed)

Testing:
  - pytest (unit tests for each tool)
  - Custom test cases from Form 4/5
```

---

## Success Criteria & Rollout

| Phase | Target | Success Metric | Go/No-Go |
|-------|--------|---|---|
| **Phase 1** | Catch calculation errors | 80%+ reduction in arithmetic mistakes | If ≥80%, proceed; else iterate |
| **Phase 2** | Handle visual interpretation | 70%+ accuracy on geometry questions | If needed & viable |
| **Phase 3** | Full problem decomposition | 85%+ score on all test forms | POC completion |

---

## Risk & Mitigation

| Risk | Likelihood | Mitigation |
|------|-----------|---|
| Agent still misinterprets question text | High | Require explicit question rephrasing step; use semantic chunking to validate understanding |
| Tools don't catch all edge cases | Medium | Add assertion/validation loops; test extensively with Form 4/5 data |
| Deep agent becomes too complex to debug | Medium | Keep each sub-agent simple; add detailed logging at each step |
| Visual interpreter fails on edge diagrams | Medium | Phase 2 is optional; fall back to numeric input if OCR/coordinate extraction fails |

---

## Notes for POC
- **Focus on simplicity**: Each phase should be testable independently
- **No premature optimization**: Use in-memory state; can cache later
- **Extensive logging**: Every tool call, every decision, every validation
- **Fail-fast design**: Halt and report specific errors rather than guessing
- **Manual seeding**: For Phase 1, assume coordinates/values are provided; don't attempt OCR

---

## Next Steps
1. Review this plan and provide feedback
2. Confirm Phase 1 scope and tool priorities
3. Create test harness for Form 4/5 questions
4. Begin Phase 1 implementation
