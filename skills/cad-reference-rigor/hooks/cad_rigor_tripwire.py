"""UserPromptSubmit tripwire: nudge toward CAD reference rigor. Fails open."""
from __future__ import annotations

import json
import re
import sys

RISKY = re.compile(
    r"\b(printed|print|reprint|rotate|rotated|flip|flipped|mirror|mirrored"
    r"|move|moved|moving|position|positioned|reposition|repositioned"
    r"|orient|oriented|reorient)\b"
    r"|\bthe part\b|\bthe feature\b",
    re.I,
)
VERSION = re.compile(r"\bv\d+[a-z]?\b", re.I)
ESCAPE_SUFFIX = "~loose"
ESCAPE_PREFIX = "[general]"

REMINDER = (
    "cad-reference-rigor check: this prompt uses part/print/orientation language "
    "with no concrete version (e.g. vNN). Before acting, ensure the reference "
    "resolves to {part, feature, version+artifact, orientation}. If it does not, "
    "hard-stop and ask. See the cad-reference-rigor skill."
)


def evaluate(prompt: str) -> str | None:
    """Return the reminder to inject, or None to stay silent."""
    if not prompt:
        return None
    text = prompt.strip()
    if text.endswith(ESCAPE_SUFFIX) or text.lower().startswith(ESCAPE_PREFIX):
        return None
    if RISKY.search(text) and not VERSION.search(text):
        return REMINDER
    return None


def main() -> None:
    try:
        data = json.load(sys.stdin)
        ctx = evaluate(data.get("prompt", "") or "")
        if ctx:
            print(json.dumps({
                "hookSpecificOutput": {
                    "hookEventName": "UserPromptSubmit",
                    "additionalContext": ctx,
                }
            }))
    except Exception:
        pass  # fail open: never block the user's prompt
    sys.exit(0)


if __name__ == "__main__":
    main()
