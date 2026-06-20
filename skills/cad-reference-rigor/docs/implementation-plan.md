# CAD Reference Rigor Implementation Plan (universal)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a universal, toolchain-agnostic CAD reference-rigor skill plus fail-open prompt hooks at user level, mirrored into the git-tracked `claude-skills` repo.

**Architecture:** The skill holds the hard-stop judgment on the abstract four-field contract `{part, feature, version, orientation}` — it does NOT depend on featurekit; featurekit's legend is just the richest *source* of those fields where present. A `UserPromptSubmit` tripwire hook re-injects the rule on risky version-less CAD language; a `SessionStart` hook covers message #1 but only in a CAD context (so it stays quiet in unrelated repos). Both fail open (never block). Everything is installed under `~/.claude` (active everywhere) and mirrored to `claude-skills/skills/cad-reference-rigor/` for version control.

**Tech Stack:** Markdown (skill), Python 3.12 (hook scripts + pytest), JSON (`~/.claude/settings.json`).

## Global Constraints

- **Decoupled / toolchain-agnostic:** the skill binds to `{part, feature, version, orientation}` and must work with NO featurekit present (a downloaded STL, a Blender file). featurekit (`manifest.partVersion`, legend keyed by `id` → `{label, kind, color}`) is one *source* where present, never required. The featurekit `partVersion` change is explicitly OUT of this plan.
- **Placement:** active copies live under `~/.claude` (`C:\Users\immer\.claude`). The home user is `immer`; the dev repos are under `C:\Users\NICKESCHEN`. Mirror target is `C:\Users\NICKESCHEN\dev\claude-skills` (`OfficerPlotTwist/claude-skills`), layout `skills/<name>/`.
- **Strictness:** hard stop + ask. On an unresolvable reference, do not act: name the ambiguous field(s), give best candidate(s), require restatement/confirmation first.
- **Artifact classes:** `source` (generator: .py/.scad/.blend) · `step`/native CAD · `mesh` (.stl/.3mf/.glb/.obj) · `print` (physical). "v15 printed" valid; "check v15" not (which artifact?).
- **Orientation:** world frame (mm, base plane XY, +Z up) or a named datum. Viewport-relative terms with no frame are forbidden.
- **Symmetry:** the rules bind my output (files, commits, filenames, sidecars) as well as user input.
- **Anti-fatigue:** maintain + echo an `ACTIVE: part=… · version=… · artifact=… · frame=…` binding line; once bound, pronouns are allowed and echoed each use. Escape token: a message ending `~loose` or leading `[general]` is non-binding.
- **Fail open:** hooks never block — exit 0 always, never exit 2, swallow all errors.
- **Settings merge, never overwrite:** `~/.claude/settings.json` already exists (with `permissions`, `enabledPlugins`, etc. and an empty `"hooks": {}`). The wiring step must load it, set only the two hook entries, and write the whole object back.
- **SessionStart is CAD-gated:** because user-level hooks fire in every repo, the SessionStart hook injects only when the cwd looks like CAD work; otherwise it stays silent.

---

## Task 1: cad-reference-rigor skill (toolchain-agnostic)

**Files:**
- Create: `C:/Users/immer/.claude/skills/cad-reference-rigor/SKILL.md`

**Interfaces:**
- Produces: a user-level skill `cad-reference-rigor`, model-invocable, referenced by the hooks in Tasks 2–3 and mirrored in Task 4.

- [ ] **Step 1: Write the skill**

Create `C:/Users/immer/.claude/skills/cad-reference-rigor/SKILL.md`:

```markdown
---
name: cad-reference-rigor
description: Enforce unambiguous CAD references in any toolchain. Use whenever discussing or acting on CAD parts, features, versions, prints, or orientation (build123d/STEP, OpenSCAD, Blender, Rhino, or downloaded meshes) — require part + feature + version + orientation to resolve unambiguously, hard-stop on ambiguity, and hold your own output (files, commits, filenames, sidecars) to the same standard.
---

# CAD Reference Rigor

Every CAD reference — in the user's message OR in anything you write — must resolve
on four fields. This is toolchain-agnostic: it applies to build123d/STEP, OpenSCAD,
Blender, Rhino, and raw downloaded meshes alike. If any field is genuinely
unresolvable, **hard-stop**: do not act, name the ambiguous field(s), state your
best candidate(s), and require a restatement or confirmation first.

## The four-field contract

| Field | Resolved when… | Ambiguous when… |
|---|---|---|
| **part** | a named part/assembly: a featurekit `Part.name`/STEP label, a Blender object name, or a model/file name | bare "the part"/"it" with no active binding; cross-project "the arm" |
| **feature** | a named, addressable sub-element of THAT part (a featurekit feature `id`/`name`, a named body/group, or an explicitly described region), or explicitly the whole part | an unnamed/unanchored feature word; "the chamfer" with no part |
| **version** | a concrete version token (e.g. `v15`, `v05b`) **and** an artifact class | "latest"/"current"; "check v15" with no artifact class |
| **orientation** | the world frame (mm, base XY, +Z up) or a named datum | "up"/"left"/"front" with no frame; viewport-relative terms |

Artifact classes: `source` (.py/.scad/.blend generator) · `step`/native CAD ·
`mesh` (.stl/.3mf/.glb/.obj) · `print` (physical). "v15 printed" is valid
(`print` ⇒ physical v15). "check v15" is not.

**Version sources, in order of trust:** an explicit user statement → a featurekit
`manifest.partVersion` (where featurekit is in use) → the file path / basename →
a git tag. "latest"/"current" are never valid — resolve to a concrete token and
echo it, or hard-stop.

## Feature codification

A feature is a named, addressable sub-element of a single part — not necessarily a
separate object. Where the toolchain gives identity, bind to it:

- **featurekit/STEP:** each feature is an independently-built labeled body whose
  **STEP part label == its slug `id`**; the printable part is the fused solid;
  `cut` features are translucent ghost-cutter bodies. The legend sidecar
  (`<part>.features.step.js`) names them — `manifest.features` keyed by `id`, each
  `{label, kind, color}`, with `manifest.partVersion`. A feature `id` is unique
  only *within a part* and meaningful only against a `{part, version}`.
- **Blender/Rhino/other:** bind to the named body / group / layer the tool exposes.
- **Raw mesh (no provenance):** there is no built-in identity — the reference must
  be made explicit (a described region + the part + version). Never let an
  unanchored feature word stand.

## Hard-stop protocol

On an unresolvable reference, respond like:

> ⛔ AMBIGUOUS — <field(s)>. <why>. Candidate(s): <if any>. Restate as <example>.
> (Not proceeding until resolved.)

A valid restatement supplies the missing field at this altitude: a named
part/feature, a concrete version token + artifact class, or a world frame / named
datum.

## Anti-fatigue (do not cry wolf)

- **Active binding line.** Maintain and echo `ACTIVE: part=… · version=… ·
  artifact=… · frame=…`. Once bound, pronouns ("it", "the part") are fine — echo
  the resolved binding each use so a wrong carry is caught. Re-echo after any
  context compaction.
- **Escape token.** A message ending `~loose` or leading `[general]` is abstract /
  non-binding — suspend the hard stop for it.
- **Consolidate.** A message with several ambiguities gets ONE consolidated stop
  listing all of them, never first-ambiguity whack-a-mole.

## Your own output

Before writing any part/feature/version/orientation reference into a file, commit
message, filename, or sidecar, self-check it against the contract. Never write
"rotate the part up" — resolve the part, the version, and the orientation frame
first.
```

- [ ] **Step 2: Verify the skill is well-formed**

Run: `head -4 "C:/Users/immer/.claude/skills/cad-reference-rigor/SKILL.md"`
Expected: valid YAML frontmatter with `name: cad-reference-rigor` and a `description:` line.

- [ ] **Step 3: Commit (in the claude-skills mirror — see Task 4 for repo setup)**

No commit here; the skill is committed as part of the Task 4 mirror. This task's deliverable is the active file under `~/.claude`. (Subagent: report DONE; the controller stages the mirror in Task 4.)

---

## Task 2: UserPromptSubmit tripwire hook

A deterministic, fail-open script: when a prompt uses risky part/print/orientation language with no concrete version and no escape token, inject a rigor reminder. Pure logic is unit-tested; I/O is a thin wrapper.

**Files:**
- Create: `C:/Users/immer/.claude/hooks/cad_rigor_tripwire.py`
- Create: `C:/Users/immer/.claude/hooks/conftest.py`
- Test: `C:/Users/immer/.claude/hooks/test_cad_rigor_tripwire.py`

**Interfaces:**
- Produces: `evaluate(prompt: str) -> str | None` in `cad_rigor_tripwire` — returns the reminder to inject, or `None`. `main()` reads the UserPromptSubmit stdin JSON and prints `{"hookSpecificOutput":{"hookEventName":"UserPromptSubmit","additionalContext":<reminder>}}` on a match, always exiting 0.

- [ ] **Step 1: Add a conftest so the hook module is importable in tests**

Create `C:/Users/immer/.claude/hooks/conftest.py`:

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
```

- [ ] **Step 2: Write the failing tests**

Create `C:/Users/immer/.claude/hooks/test_cad_rigor_tripwire.py`:

```python
from cad_rigor_tripwire import evaluate


def test_fires_on_printed_without_version():
    assert evaluate("the part is printed, check the fit") is not None


def test_silent_when_version_present():
    assert evaluate("v15 is printed, check the fit") is None


def test_fires_on_rotate_the_part_without_version():
    assert evaluate("rotate the part up") is not None


def test_escape_suffix_suppresses():
    assert evaluate("how do mounts handle airflow ~loose") is None


def test_escape_prefix_suppresses():
    assert evaluate("[general] rotate concepts in CAD") is None


def test_silent_on_unrelated_prompt():
    assert evaluate("what time is it") is None


def test_silent_on_empty():
    assert evaluate("") is None
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `cd "C:/Users/immer/.claude/hooks" && python -m pytest -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'cad_rigor_tripwire'`

- [ ] **Step 4: Write the hook**

Create `C:/Users/immer/.claude/hooks/cad_rigor_tripwire.py`:

```python
"""UserPromptSubmit tripwire: nudge toward CAD reference rigor. Fails open."""
from __future__ import annotations

import json
import re
import sys

RISKY = re.compile(
    r"\b(printed|print|reprint|rotate|rotated|flip|flipped|mirror|mirrored)\b"
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
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd "C:/Users/immer/.claude/hooks" && python -m pytest -q`
Expected: PASS (7 passed)

- [ ] **Step 6: Smoke-test the stdin/stdout contract**

Run:

```bash
echo '{"prompt":"the part is printed"}' | python -u "C:/Users/immer/.claude/hooks/cad_rigor_tripwire.py"; echo "exit=$?"
echo '{"prompt":"v15 is printed"}'      | python -u "C:/Users/immer/.claude/hooks/cad_rigor_tripwire.py"; echo "exit=$?"
echo 'not json at all'                  | python -u "C:/Users/immer/.claude/hooks/cad_rigor_tripwire.py"; echo "exit=$?"
```

Expected: first prints a JSON object with `additionalContext`, exit=0; second prints nothing, exit=0; third (malformed) prints nothing, exit=0 (fail open).

- [ ] **Step 7: Report DONE** (commit happens in Task 4 mirror).

---

## Task 3: SessionStart hook + settings.json wiring

Cover message #1 with a SessionStart reminder, but only in a CAD context; and merge both hooks into the existing `~/.claude/settings.json`.

**Files:**
- Create: `C:/Users/immer/.claude/hooks/cad_rigor_session_start.py`
- Test: `C:/Users/immer/.claude/hooks/test_cad_rigor_session_start.py`
- Modify: `C:/Users/immer/.claude/settings.json`

**Interfaces:**
- Consumes: the tripwire from Task 2 (same hooks dir / conftest).
- Produces: `build_context() -> str` and `looks_like_cad_dir(path: str) -> bool` in `cad_rigor_session_start`; a merged `settings.json` registering both hooks.

- [ ] **Step 1: Write the failing tests**

Create `C:/Users/immer/.claude/hooks/test_cad_rigor_session_start.py`:

```python
import os

from cad_rigor_session_start import build_context, looks_like_cad_dir


def test_context_mentions_skill_and_rigor():
    ctx = build_context()
    assert "cad-reference-rigor" in ctx
    assert "version" in ctx.lower()


def test_looks_like_cad_dir_true_for_cad_markers(tmp_path):
    (tmp_path / "part.scad").write_text("// scad", encoding="utf-8")
    assert looks_like_cad_dir(str(tmp_path)) is True


def test_looks_like_cad_dir_true_for_step(tmp_path):
    (tmp_path / "widget.step").write_text("ISO-10303", encoding="utf-8")
    assert looks_like_cad_dir(str(tmp_path)) is True


def test_looks_like_cad_dir_false_for_plain_dir(tmp_path):
    (tmp_path / "notes.txt").write_text("hi", encoding="utf-8")
    assert looks_like_cad_dir(str(tmp_path)) is False
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd "C:/Users/immer/.claude/hooks" && python -m pytest test_cad_rigor_session_start.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'cad_rigor_session_start'`

- [ ] **Step 3: Write the SessionStart hook**

Create `C:/Users/immer/.claude/hooks/cad_rigor_session_start.py`:

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd "C:/Users/immer/.claude/hooks" && python -m pytest test_cad_rigor_session_start.py -q`
Expected: PASS (4 passed)

- [ ] **Step 5: Merge the hooks into settings.json (do NOT overwrite)**

Run this exact script (loads the existing settings, sets only the two hook entries, writes back):

```bash
python - <<'PY'
import json, pathlib
p = pathlib.Path.home() / ".claude" / "settings.json"
data = json.loads(p.read_text(encoding="utf-8"))
hooks = data.setdefault("hooks", {})
hooks["SessionStart"] = [{
    "matcher": "startup|resume|clear|compact",
    "hooks": [{
        "type": "command",
        "command": "python -u \"${HOME}/.claude/hooks/cad_rigor_session_start.py\"",
        "timeout": 30,
    }],
}]
hooks["UserPromptSubmit"] = [{
    "matcher": "*",
    "hooks": [{
        "type": "command",
        "command": "python -u \"${HOME}/.claude/hooks/cad_rigor_tripwire.py\"",
        "timeout": 15,
    }],
}]
p.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
print("merged hooks into", p)
PY
```

Both commands use `${HOME}/.claude/hooks/...` (user-level config), not `${CLAUDE_PROJECT_DIR}`, which would resolve to the active project rather than the home config.

- [ ] **Step 6: Validate settings.json still parses and kept prior keys**

Run:

```bash
python - <<'PY'
import json, pathlib
d = json.loads((pathlib.Path.home()/".claude"/"settings.json").read_text(encoding="utf-8"))
assert "permissions" in d and "enabledPlugins" in d, "lost prior keys!"
assert set(d["hooks"]) >= {"SessionStart", "UserPromptSubmit"}, "hooks missing"
print("settings.json OK; hooks:", list(d["hooks"]))
PY
```

Expected: `settings.json OK; hooks: ['SessionStart', 'UserPromptSubmit']` (order may vary) and no assertion error.

- [ ] **Step 7: Smoke-test the SessionStart contract (CAD-gated)**

Run:

```bash
printf '{"source":"startup","cwd":"%s"}' "$(pwd)" | python -u "C:/Users/immer/.claude/hooks/cad_rigor_session_start.py"; echo "exit=$?"
echo '{"source":"startup","cwd":"C:/Windows"}' | python -u "C:/Users/immer/.claude/hooks/cad_rigor_session_start.py"; echo "exit=$?"
```

Expected: first (a CAD repo cwd) prints a JSON object mentioning `cad-reference-rigor`, exit=0; second (non-CAD cwd) prints nothing, exit=0.

- [ ] **Step 8: Live verification**

After Task 4, the implementer notes that hooks register on a fresh Claude Code session. Confirm manually: (a) a new session in a CAD repo injects the SessionStart context; (b) typing `the part is printed` surfaces the tripwire reminder while `v15 is printed` does not. Record the result.

- [ ] **Step 9: Report DONE** (commit happens in Task 4 mirror).

---

## Task 4: Mirror to the claude-skills repo

Version-control the whole capability in `OfficerPlotTwist/claude-skills`, following the `/no` `skills/<name>/` convention, plus the hook scripts and a settings snippet.

**Files (in `C:/Users/NICKESCHEN/dev/claude-skills`):**
- Create: `skills/cad-reference-rigor/SKILL.md` (copy of the active skill)
- Create: `skills/cad-reference-rigor/hooks/cad_rigor_tripwire.py`, `cad_rigor_session_start.py`, `conftest.py`, `test_cad_rigor_tripwire.py`, `test_cad_rigor_session_start.py` (copies of the active hooks)
- Create: `skills/cad-reference-rigor/settings-snippet.json` (the `hooks` block to merge)
- Create: `skills/cad-reference-rigor/README.md` (install/mirror note)

**Interfaces:**
- Consumes: the active files from Tasks 1–3.

- [ ] **Step 1: Copy the active files into the mirror**

```bash
SRC_SKILL="C:/Users/immer/.claude/skills/cad-reference-rigor"
SRC_HOOKS="C:/Users/immer/.claude/hooks"
DST="C:/Users/NICKESCHEN/dev/claude-skills/skills/cad-reference-rigor"
mkdir -p "$DST/hooks"
cp "$SRC_SKILL/SKILL.md" "$DST/SKILL.md"
for f in cad_rigor_tripwire.py cad_rigor_session_start.py conftest.py test_cad_rigor_tripwire.py test_cad_rigor_session_start.py; do
  cp "$SRC_HOOKS/$f" "$DST/hooks/$f"
done
ls -R "$DST"
```

- [ ] **Step 2: Write the settings snippet**

Create `C:/Users/NICKESCHEN/dev/claude-skills/skills/cad-reference-rigor/settings-snippet.json`:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|resume|clear|compact",
        "hooks": [
          {
            "type": "command",
            "command": "python -u \"${HOME}/.claude/hooks/cad_rigor_session_start.py\"",
            "timeout": 30
          }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "python -u \"${HOME}/.claude/hooks/cad_rigor_tripwire.py\"",
            "timeout": 15
          }
        ]
      }
    ]
  }
}
```

- [ ] **Step 3: Write the README**

Create `C:/Users/NICKESCHEN/dev/claude-skills/skills/cad-reference-rigor/README.md`:

```markdown
# cad-reference-rigor

Universal CAD reference-rigor: hard-stop on ambiguous part / feature / version /
orientation references, in any toolchain. Hand-authored (not `/no`-generated);
mirrored here for version control.

## Install (active copies under ~/.claude)
- `SKILL.md` → `~/.claude/skills/cad-reference-rigor/SKILL.md`
- `hooks/*.py` → `~/.claude/hooks/`
- Merge `settings-snippet.json`'s `hooks` block into `~/.claude/settings.json`
  (do not overwrite the file).

## Test
`cd ~/.claude/hooks && python -m pytest -q`
```

- [ ] **Step 4: Verify the mirrored tests pass from the mirror copy**

```bash
cd "C:/Users/NICKESCHEN/dev/claude-skills/skills/cad-reference-rigor/hooks" && python -m pytest -q
```

Expected: PASS (11 passed — 7 tripwire + 4 session-start).

- [ ] **Step 5: Stage on a branch and open a PR (controller-gated push)**

```bash
cd "C:/Users/NICKESCHEN/dev/claude-skills"
git checkout main && git pull --ff-only
git checkout -b "add/cad-reference-rigor"
git add skills/cad-reference-rigor
git commit -m "add(cad-reference-rigor): universal CAD reference-rigor skill + hooks"
git push -u origin "add/cad-reference-rigor"
gh pr create -R OfficerPlotTwist/claude-skills --head "add/cad-reference-rigor" \
  --title "add(cad-reference-rigor): universal CAD reference-rigor skill + hooks" \
  --body "Hand-authored universal rigor skill + fail-open hooks, mirrored from ~/.claude. Promote (merge) to mark complete."
```

The push/PR is an outward action — the controller confirms with the human before running Step 5. Local commit may proceed; the push + `gh pr create` wait for explicit go.

- [ ] **Step 6: Report DONE** with the PR URL (or the local branch state if the push was deferred).

---

## Self-review notes

- **Spec coverage:** four-field contract + feature codification + hard-stop + symmetry + anti-fatigue → Task 1 skill. Mechanism (UserPromptSubmit, SessionStart, fail open) → Tasks 2–3. Decoupling / toolchain-agnostic + universal placement + claude-skills mirror → Global Constraints + Tasks 1, 4. featurekit `partVersion` → explicitly out of scope.
- **Settings safety:** Task 3 Step 5 merges via read-modify-write and Step 6 asserts prior keys survive. The `${HOME}` vs `${CLAUDE_PROJECT_DIR}` correction is called out explicitly.
- **Placement:** active under `~/.claude` (home user `immer`); mirror under `C:/Users/NICKESCHEN/dev/claude-skills`. No Cad_design `.claude/` changes; the `feature-legend-panel` branch is untouched by this plan.
- **Type consistency:** `evaluate`, `build_context`, `looks_like_cad_dir` signatures match between def and test/use. Hook command paths use `${HOME}/.claude/hooks/<script>` consistently in settings and snippet.
- **Outward-action gate:** the only push/PR (Task 4 Step 5) is explicitly controller-gated, not silently run by a subagent.
```
