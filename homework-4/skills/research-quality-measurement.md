# Research Quality Measurement Skill

## Purpose
Use this skill to score the quality of bug research before planning or fixing.
It standardizes how "good research" is judged and ensures outputs are usable by
the bug planner and bug fixer.

## Inputs
- `context/bugs/XXX/research/codebase-research.md`
- Source files referenced by the research document.

## Mandatory checks
1. Every `file:line` reference points to a real file and relevant lines.
2. Quoted snippets match source code semantically (exact text preferred).
3. Claims about root cause and impact are supported by evidence.
4. Reproduction steps are complete and executable.
5. Proposed fix direction is consistent with observed code behavior.

## Quality levels

### Q4 - Excellent
- All references valid and accurate.
- No contradictions.
- Root cause clearly proven.
- Reproduction steps deterministic.
- Ready for implementation planning without extra research.

### Q3 - Good
- Most references valid; only minor inaccuracies.
- Root cause likely correct.
- Reproduction mostly clear, with small ambiguity.
- Planner can proceed with minimal clarification.

### Q2 - Partial
- Some missing or incorrect references.
- Root cause is plausible but under-evidenced.
- Reproduction is incomplete or flaky.
- Additional research is required before planning.

### Q1 - Poor
- Multiple invalid references or mismatched snippets.
- Root cause unclear or speculative.
- Reproduction missing or nonfunctional.
- Not usable for planning/fixing.

## Pass/fail rule
- `PASS` only for Q3 or Q4.
- `FAIL` for Q1 or Q2.

## Required output format
When this skill is used, the verifier output must include:
- Verification Summary (PASS/FAIL, quality level)
- Verified Claims
- Discrepancies Found
- Research Quality Assessment (level + reasoning)
- References
