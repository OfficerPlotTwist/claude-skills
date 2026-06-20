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
