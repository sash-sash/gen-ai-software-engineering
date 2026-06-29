"""4-Agent pipeline orchestrator.

This script runs the homework pipeline by invoking REAL Cursor agents
(`cursor-agent`) in order. Each agent runs with its own model (read from the
`*.agent.md` frontmatter) and is responsible for reading its own skills and
producing its output artifact.

Run order:
  Research Verifier -> Bug Fixer -> Security Verifier -> Unit Test Generator

Before running, the application source is reset from `seed/` to its original
(buggy) state so the agents always have something concrete to fix.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SEED = ROOT / "seed"
SRC = ROOT / "src"
TESTS = ROOT / "tests"
AGENTS_DIR = ROOT / "agents"
SKILLS_DIR = ROOT / "skills"
BUG_DIR = ROOT / "context" / "bugs" / "001"
RESEARCH_DIR = BUG_DIR / "research"
LOG_DIR = BUG_DIR / "logs"

MAX_RETRIES = 3
RETRY_SLEEP_SEC = 4


def agent_command() -> str:
    """Resolve the cursor-agent launcher (.cmd on Windows)."""
    local = os.environ.get("LOCALAPPDATA")
    if local:
        candidate = Path(local) / "cursor-agent" / "agent.cmd"
        if candidate.exists():
            return str(candidate)
    # Fallback: rely on PATH.
    return "agent"


def read_model(agent_file: str, default: str = "composer-2.5-fast") -> str:
    """Read the `model:` value from an agent's frontmatter."""
    text = (AGENTS_DIR / agent_file).read_text(encoding="utf-8")
    match = re.search(r"^model:\s*(.+)$", text, re.MULTILINE)
    return match.group(1).strip() if match else default


def reset_to_seed() -> None:
    """Restore src/ and tests/ from the seeded (buggy) baseline."""
    for sub in ("src", "tests"):
        dst = ROOT / sub
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(SEED / sub, dst)
    print("  - src/ and tests/ reset to seeded (buggy) state")


def run_agent(step_name: str, agent_file: str, prompt: str) -> str:
    """Invoke a real cursor-agent run for one pipeline step."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    model = read_model(agent_file)
    launcher = agent_command()

    command = [
        "cmd",
        "/c",
        launcher,
        "-p",
        "--model",
        model,
        "--output-format",
        "text",
        "--force",
        "--trust",
    ]

    print(f"  - agent: {agent_file}")
    print(f"  - model: {model}")

    last_output = ""
    for attempt in range(1, MAX_RETRIES + 1):
        proc = subprocess.run(
            command,
            cwd=ROOT,
            input=prompt,
            text=True,
            capture_output=True,
        )
        last_output = (proc.stdout or "") + (proc.stderr or "")
        if proc.returncode == 0:
            log_path = LOG_DIR / f"{step_name}.log"
            log_path.write_text(
                f"# {step_name} (model={model})\n\n{last_output}\n",
                encoding="utf-8",
            )
            print(f"  - OK (attempt {attempt}), log: {log_path.name}")
            return last_output
        print(f"  - attempt {attempt} failed (rc={proc.returncode}); retrying...")
        time.sleep(RETRY_SLEEP_SEC)

    log_path = LOG_DIR / f"{step_name}.FAILED.log"
    log_path.write_text(last_output, encoding="utf-8")
    raise RuntimeError(f"Agent step '{step_name}' failed after {MAX_RETRIES} attempts")


def prompt_research_verifier() -> str:
    return (
        "You are running as the Bug Research Verifier agent for this workspace.\n"
        "1. Read your agent definition: agents/research-verifier.agent.md\n"
        "2. Read the skill: skills/research-quality-measurement.md and apply it.\n"
        "3. Read context/bugs/001/research/codebase-research.md.\n"
        "4. Verify every claim and file reference against the real files in src/.\n"
        "5. WRITE the file context/bugs/001/research/verified-research.md with these "
        "sections: Verification Summary (PASS/FAIL and Research Quality level per the "
        "skill), Verified Claims, Discrepancies Found, Research Quality Assessment "
        "(level + reasoning), References.\n"
        "Do NOT modify any source code. Only create/overwrite verified-research.md.\n"
        "When done, reply with a one-line confirmation."
    )


def prompt_bug_fixer() -> str:
    return (
        "You are running as the Bug Fixer agent for this workspace.\n"
        "1. Read agents/bug-fixer.agent.md.\n"
        "2. Read context/bugs/001/implementation-plan.md, "
        "context/bugs/001/research/verified-research.md and "
        "context/bugs/001/bug-context.md.\n"
        "3. Apply every fix from the implementation plan to the files in src/ "
        "(rounding bug, people>0 validation, hardcoded secret + secure compare, "
        "receipt path traversal).\n"
        "4. Run the tests with: py -m pytest -q\n"
        "5. WRITE context/bugs/001/fix-summary.md with sections: Changes Made (file, "
        "location, before/after summary, test result), Overall Status, Manual "
        "Verification, References.\n"
        "Keep changes minimal and traceable to the plan. "
        "When done, reply with a one-line confirmation."
    )


def prompt_security_verifier() -> str:
    return (
        "You are running as the Security Vulnerabilities Verifier agent.\n"
        "1. Read agents/security-verifier.agent.md.\n"
        "2. Read context/bugs/001/fix-summary.md and the current files in src/.\n"
        "3. Review the changed code for: injection, hardcoded secrets, insecure "
        "comparisons, missing validation, unsafe dependencies, path traversal, and "
        "XSS/CSRF where relevant.\n"
        "4. WRITE context/bugs/001/security-report.md. Each finding MUST include: "
        "severity (CRITICAL/HIGH/MEDIUM/LOW/INFO), file:line, impact, and remediation. "
        "Include a short risk summary.\n"
        "Report only. Do NOT edit any code. "
        "When done, reply with a one-line confirmation."
    )


def prompt_unit_test_generator() -> str:
    return (
        "You are running as the Unit Test Generator agent.\n"
        "1. Read agents/unit-test-generator.agent.md.\n"
        "2. Read the skill skills/unit-tests-FIRST.md and apply FIRST principles.\n"
        "3. Read context/bugs/001/fix-summary.md and the changed files in src/.\n"
        "4. Generate unit tests ONLY for the changed/new behavior (rounding fix, "
        "people>0 validation, secure admin-key check, receipt traversal protection). "
        "Put them under tests/ (e.g. tests/test_api.py).\n"
        "5. Run the tests with: py -m pytest -q (they must pass).\n"
        "6. WRITE context/bugs/001/test-report.md with: test files added/updated, "
        "mapping from changed code to tests, FIRST compliance notes, test command and "
        "results, remaining gaps.\n"
        "When done, reply with a one-line confirmation."
    )


def main() -> int:
    print("== 4-Agent Pipeline (real cursor-agent orchestration) ==")

    print("Step 0/4: Reset application to seeded buggy state")
    reset_to_seed()

    print("Step 1/4: Bug Research Verifier")
    run_agent("01-research-verifier", "research-verifier.agent.md", prompt_research_verifier())

    print("Step 2/4: Bug Fixer")
    run_agent("02-bug-fixer", "bug-fixer.agent.md", prompt_bug_fixer())

    print("Step 3/4: Security Verifier")
    run_agent("03-security-verifier", "security-verifier.agent.md", prompt_security_verifier())

    print("Step 4/4: Unit Test Generator")
    run_agent("04-unit-test-generator", "unit-test-generator.agent.md", prompt_unit_test_generator())

    print("== Pipeline complete ==")
    print("Artifacts:")
    print(f"- {RESEARCH_DIR / 'verified-research.md'}")
    print(f"- {BUG_DIR / 'fix-summary.md'}")
    print(f"- {BUG_DIR / 'security-report.md'}")
    print(f"- {BUG_DIR / 'test-report.md'}")
    print(f"- agent logs in {LOG_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
