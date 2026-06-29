# Unit Tests FIRST Skill

## Purpose
Ensure generated unit tests follow FIRST principles:
- **F**ast
- **I**ndependent
- **R**epeatable
- **S**elf-validating
- **T**imely

## FIRST checks

### Fast
- Tests run quickly and avoid unnecessary I/O or sleeps.
- Unit tests must not call external services.

### Independent
- Each test sets up its own state.
- No dependency on test order.

### Repeatable
- Same input gives same result across runs.
- No random behavior unless seeded and controlled.

### Self-validating
- Tests assert exact outcomes automatically.
- No manual inspection required for pass/fail.

### Timely
- Tests cover newly changed code paths immediately.
- Prioritize regressions for the fixed bug(s) and security fix(es).

## Scope rule
- Generate tests only for code changed by the bug fixer.
- Do not add unrelated tests.

## Required report sections
`test-report.md` must include:
- Added/updated test files
- Mapping from changed code paths to tests
- FIRST compliance notes per test group
- Test execution command and result summary
- Remaining gaps (if any)
