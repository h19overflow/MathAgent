Top mistakes
Inequality boundary/strictness errors: wrong direction, non-strict vs strict mismatch, missing required boundary, or using the wrong line for a region definition.

Omission or incomplete final answers: missing a required subpart, omitting a value previously derived in the working, or failing to report final numeric results explicitly.

Arithmetic/summation mistakes: correct method but incorrect totals due to addition or intermediate aggregate errors, propagating to final answers.

Misinterpretation of criterion: optimizing the wrong objective (e.g., shortest vs safest) despite correct calculations.

Incorrect numeric answers across parts: multiple final values not matching ground truth in a single multi-part problem.

Why these happen
Inequalities are brittle because small sign or strictness changes flip feasible regions, and mental algebra under time pressure amplifies such slips.

Output omissions occur when the agent’s working and final “answer list” diverge, especially in multi-part or multi-value prompts without an explicit completeness check.

Arithmetic slips arise from manual aggregation of intermediate quantities, especially when switching units or reusing partially correct sums.

---

Possible Tools:
Tooling to reduce errors
Symbolic math and inequality solver: integrate a SymPy or Z3-backed tool to solve, simplify, and verify inequalities with strictness, including point-sampling checks to validate region descriptions programmatically.

Base-N and exact arithmetic utilities: add deterministic base-conversion and rational arithmetic to avoid rounding drift and off-by-one digit issues in numeral systems and fraction-heavy tasks.

Unit/consistency checker: use a Pint-based unit engine plus dimensional-analysis assertions for kinematics, rates, and mixed-unit problems to prevent numerics that pass algebra but fail units.

Answer completeness guard: a checklist tool that parses the prompt into required subparts and verifies the final output includes a concrete value for each, matching any items discovered during working (e.g., “final list must include all validated candidates”).

Objective/criterion extractor: a lightweight classifier that surfaces and locks task criteria (e.g., “safest” vs “shortest”) before computation, with a pre-submit reminder if the chosen objective and final choice are misaligned.

Calculation ledger with auto-verify: execute a Python scratchpad to compute aggregates, re-run independent recomputations, and assert equality of alternative derivations before emitting final values.

Final-answer schema: require structured JSON output for each subpart with fields {label, value, units, rationale_hash}, and a validator that blocks emission if any required field is missing or inconsistent with earlier derived entities.