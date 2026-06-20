"""SessionStart: load CAD reference-rigor — only in a CAD context. Fails open."""
from __future__ import annotations

import glob
import json
import os
import sys

CONTEXT = (
    "cad-reference-rigor is active. Apply unambiguous CAD references: every "
    "part / feature / version / orientation reference must resolve, hard-stop on "
    "ambiguity, and hold your own output (files, commits, filenames, sidecars) to "
    "the same standard. Invoke the cad-reference-rigor skill when doing CAD work."
)

_CAD_GLOBS = ("*.scad", "*.step", "*.stp", "*.stl", "*.3mf", "*.blend", "*.f3d")
_CAD_DIRS = ("tools/featurekit", ".agents/skills/cad")


def build_context() -> str:
    return CONTEXT


def looks_like_cad_dir(path: str) -> bool:
    # returns False on any error; the real fail-open guard is in main()
    try:
        for pattern in _CAD_GLOBS:
            if glob.glob(os.path.join(path, pattern)):
                return True
        for sub in _CAD_DIRS:
            if os.path.isdir(os.path.join(path, sub)):
                return True
    except Exception:
        return False
    return False


def main() -> None:
    cwd = os.getcwd()
    try:
        data = json.load(sys.stdin)
        cwd = data.get("cwd", cwd) or cwd
    except Exception:
        pass
    try:
        if looks_like_cad_dir(cwd):
            print(json.dumps({
                "hookSpecificOutput": {
                    "hookEventName": "SessionStart",
                    "additionalContext": build_context(),
                }
            }))
    except Exception:
        pass
    sys.exit(0)


if __name__ == "__main__":
    main()
