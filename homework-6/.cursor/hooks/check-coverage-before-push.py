"""Block git push when homework-6 coverage is below 80%."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
HOMEWORK_DIR = REPO_ROOT / "homework-6"


def allow() -> int:
    print(json.dumps({"permission": "allow"}))
    return 0


def deny(user_message: str, agent_message: str) -> int:
    print(
        json.dumps(
            {
                "permission": "deny",
                "user_message": user_message,
                "agent_message": agent_message,
            }
        )
    )
    return 0


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return allow()

    command = str(payload.get("command", ""))
    if not command.startswith("git push"):
        return allow()

    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "--cov=.", "--cov-fail-under=80", "--cov-report=term-missing", "-q"],
        cwd=HOMEWORK_DIR,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode == 0:
        return allow()

    output = (proc.stdout + "\n" + proc.stderr).strip()
    return deny(
        "Push blocked: homework-6 coverage is below 80% (or tests failed).",
        f"Coverage hook blocked git push.\n\n{output[-1500:]}",
    )


if __name__ == "__main__":
    raise SystemExit(main())
