# CAD Reference Rigor — Design Spec

Date: 2026-06-19
Status: design approved, pending implementation plan

## Problem

In CAD conversation, ambiguous language about **which part**, **which feature**,
**which version**, and **what orientation** causes wrong edits, wrong fit checks,
and artifacts (files, commits, legend writes) that read wrong months later.
The most expensive case: a printed-part claim with no version, or a "rotate it up"
with no frame.

This spec defines a **reference-rigor contract** enforced by a skill plus a hook,
applied to a STEP-first stack. It does not add CAD capability; it constrains how
parts/features/versions/orientation are *referred to* so every reference is
unambiguous.

## Target stack

```
build123d → STEP      authoring language (retires .scad)
cadpy / `cad` skill   the engine (runs build123d, emits STEP, selector refs)
featurekit (Mod 0–2)  feature-first layer — names features, populates the legend
cad-viewer + legend    the viewport — displays canonical part/feature names
                       extensible to Blender, Rhino, etc.
```

The contract binds to the **legend namespace** (part + feature names) plus version
and orientation. It is toolchain-agnostic: as long as a reference resolves to
`{part, feature, version, orientation}` unambiguously, rigor is satisfied
regardless of what authored the geometry. No reference is required to name
build123d / Blender / Rhino internals.

## 1. The four-field contract

Every CAD reference must resolve to:

| Field | Resolvable when… | Ambiguous when… |
|---|---|---|
| **part** | names a featurekit `Part.name` / STEP assembly label | bare "the part", "it" with no active binding, cross-project "the arm" |
| **feature** | names a registered featurekit feature `id` (slug) or `name`, with `kind` (`add`/`cut`); or explicitly the whole part | a name not in the part manifest; "the chamfer" with no part |
| **version** | a concrete version **and** artifact class — but **version is not yet a featurekit field** (see §8); until then it is sourced from the artifact path / git, and must be stated explicitly | "latest"/"current"; "check v15" with no artifact class; any version claim with no defined source |
| **orientation** | the world frame (mm, XY base, +Z up) or a **named datum** | "up"/"left"/"front" with no frame; viewport-relative terms |

Artifact classes: `source` (.py generator) · `step` (primary CAD) ·
`mesh` (.stl/.3mf/.glb secondary) · `print` (physical object).
"v15 printed" is valid (`print` ⇒ the physical v15). "check v15" is not
(source or step?).

## 2. Feature codification (authoritative definition)

Recovered from featurekit **Module 0** (the manifest contract) — the implemented
code at `tools/featurekit/featurekit/{model,naming,sidecar}.py`, which is the
authoritative source, not prose.

**A feature is an independently-built, labeled body. The printable part is their
fusion.**

```
assembly = STEP assembly compound of part bodies
part     = a featurekit Part(name=…) with an ordered feature list
feature  = an independently-built solid with a stable identity:
           · id       slug, unique within the part — ^[a-z0-9]+([-_][a-z0-9]+)*$
                      **the STEP part label == this id** (legend row ↔ 3D body binding)
           · name     human display name (shown in legend)
           · kind     add | cut
           · colorHex  #RRGGBB, deterministic from id unless pinned
print artifact = the single fused solid (the print source of truth)
feature view   = the same features kept DISTINCT — add solids opaque,
                 cut solids translucent ghost cutters, each labeled by id
```

The canonical feature handle is the **slug `id`** (== STEP part label), surfaced
in the legend by `name`. Selector refs (`#o1.f1`) remain the lower `cad`-skill
geometry primitive, but featurekit identity is the slug carried as the STEP label
— that is what a legend row binds to.

Consequences the contract depends on:

1. **Distinct by construction, fused only for print.** In the feature view each
   feature is its own geometry (a true partition) — isolation, coloring, and
   ownership are unambiguous. Boundaries merge only in the fused print solid,
   which is the print source of truth but not the addressable layer; the
   cover/shared-boundary subtlety lives there, not in the legend.
2. **Subtractive features are first-class.** A `cut` is its own labeled,
   translucent ghost-cutter solid — "the finger hole" is a named body, not an
   inferred void.
3. **A feature reference is meaningless without its part.** `id` is unique only
   *within a part*; a feature reference must carry — or inherit from active
   context — its parent `Part.name`.
4. **Feature identity is version-scoped — but featurekit does not record the
   version (§8).** The same `id` can denote different geometry across design
   versions, and a feature can vanish between versions. A feature name resolves
   only against `{part, version}`; since version is not a manifest field, this is
   the spec's load-bearing open gap.

The naming-rigor gate is **already enforced at generation** (`naming.validate_slug`
+ `Part.validate()`): invalid slug, duplicate `id`, empty `name`, bad `kind`, or
zero `add` features all hard-fail generation. The rigor contract reuses this gate
for feature ids in my output rather than re-implementing it.

## 3. Hard-stop rules

On a **genuinely unresolvable** reference (cannot be resolved from the active
binding or the message itself), I do not act. I:

1. State which field(s) are ambiguous and why.
2. State my best candidate(s) if any.
3. Require a restatement or confirmation before proceeding.

```
You: "the part is printed, check the fit"
Me:  ⛔ AMBIGUOUS — version + artifact unresolved.
     Active binding has no version. Which printed version?
     Restate e.g. "v15 print is printed".  (Will not proceed until resolved.)
```

A valid restatement supplies the missing field(s) at the contract's altitude
(§1) — a legend part/feature, a concrete version + artifact class, or a world
frame / named datum.

## 4. Symmetry — the rules bind my output too

The contract is not only on user input. Before I write **any** part / feature /
version / orientation reference into a file, commit message, STEP/STL filename,
README, or legend entry, I self-check it against §1. If I am about to write
"rotate the part up", I resolve it first. The artifacts are where ambiguity does
the most downstream damage, so my output is held to the same standard as your
input.

## 5. Anti-fatigue

Rigor that cries wolf gets disabled. Three mitigations:

- **Active-context binding line.** I maintain and echo a single binding:
  `ACTIVE: part=… · version=… · artifact=… · frame=…`. Once bound, pronouns
  ("it", "the part") are allowed, but I echo the resolved binding each time so a
  wrong carry is caught immediately. Rigor without retyping. The binding is
  restated after context compaction (the rule survives via the hook; the *binding*
  survives because I re-echo it).
- **Escape token.** A message ending `~loose` (or leading `[general]`) is abstract
  / non-binding; the hard stop is suspended for it. ("how do wall mounts handle
  airflow `~loose`".)
- **Consolidated stops.** A message with several ambiguities gets **one**
  consolidated stop listing all of them — never first-ambiguity whack-a-mole.

Drifting words ("latest", "current", "the one we just changed") are not valid
version specs; I resolve them to a concrete version and echo it, or hard-stop if
I cannot.

## 6. Mechanism

```
SessionStart      → load the cad-reference-rigor skill (covers message #1)
UserPromptSubmit  → keyword tripwire (printed|it|this|that|rotate|flip|mirror|
                    up|down|left|right|front|back|the part|the feature …)
                    · if a risky phrase appears without a nearby qualifier
                      (a concrete version like vNN, a world-frame axis / named datum,
                      or a legend part/feature name) → inject a rigor reminder AND
                      force-load the skill
                    · FAILS OPEN: any script error must never block input
cad-reference-rigor skill → the judgment: §1–§5 applied to input AND output
```

The hook is a deterministic tripwire whose only guarantees are (a) re-injecting
the rule so it survives long contexts and (b) force-loading the skill. It cannot
itself judge meaning. The skill holds the judgment. Neither alone is a full
guarantee; together they are as close as the platform allows. `~loose` / `[general]`
messages bypass the tripwire injection.

## 7. Reused stack primitives (do not reinvent)

- **Orientation frame** is already defined by the `cad` skill: mm, base plane XY,
  +Z up, origin per `positioning.md`; assemblies carry named mating datums and
  part-local frames. The rigor rule *requires* orientation in this world frame or
  a named datum and *forbids* viewport-relative terms. No per-part README datum
  block is needed.
- **Feature identity** is the featurekit slug `id`, carried as the **STEP part
  label** (`label == id`); the legend `name` is its display. Rigor binds to the
  `id`/`name`, not to selector refs. The generation-time naming gate (`naming.py`)
  already guarantees slugs are valid and unique.
- **Artifact** classes (`source` .py / `step` / `mesh` .stl/.3mf/.glb / `print`)
  are clean under STEP-first: generator and STEP share a basename, removing the
  variant-filename ambiguity of the old `.scad`/`_blendercut`/`_ported` layout.
  **Version, however, is not carried anywhere in featurekit** (§8).

## 8. Resolved bindings + the version gap

Recovered from the implemented featurekit (`tools/featurekit`) and its spec
(`docs/superpowers/specs/2026-06-19-feature-first-cad-design.md`). The legend
schema is now bound to real fields:

featurekit has **two schema layers**; the rigor contract binds to the **legend
sidecar** (the viewer-canonical form). Verified empirically by rendering
`featurekit.sidecar.render_sidecar`, not by reading source (an earlier source read
was stale).

**Authoring model** (`featurekit.model.Feature`, what you write in Python):
`id`, `name`, `kind`, optional `color` pin. `Part.manifest()` emits ordered rows
`{id, name, kind, colorHex}`.

**Legend sidecar** (`<part>.features.step.js`, what the viewer legend renders and
the contract binds to): a single `manifest` object containing —

| Key | Value |
|---|---|
| `schemaVersion` | currently **1** |
| `step.path` | repo-relative posix path to the features STEP |
| `view` | `{colorMode: "diagnostic", ghostCutters: true}` (**inside** `manifest`) |
| `features` | **object keyed by feature `id`**, each value `{label, kind, color}` |

So authoring `name` → sidecar `label`, authoring `colorHex` → sidecar `color`. The
`id` is both the object key and the STEP part label, so a legend reference resolves
`id → {label, kind, color}` unambiguously.

**The version gap — the one binding featurekit does NOT provide.**
featurekit carries **no part-design version**. The only `version` in the schema is
`schemaVersion` (the manifest *format* version), not the part's design revision.
So the contract's `version` field — the very thing the original requirement is
built on ("which version was printed") — **cannot bind to the legend today.** This
must be resolved before the skill can enforce version rigor. Candidate sources, to
decide at plan time:

1. **Artifact path / basename** — encode `vNN` in the model directory or STEP
   basename (e.g. `models/macmini-mount/v15/…`); cheap, no featurekit change, but
   convention-only and easy to desync from the geometry.
2. **Git** — the commit/tag is the version; precise and automatic, but a printed
   physical object does not carry its commit, so "which version is printed" still
   needs a human-stated link.
3. **New featurekit manifest field** — add `manifest.partVersion` (and/or a
   per-feature `since`/`validUntil`) so version travels with the part and the
   legend can display it. Most robust; requires a featurekit Module 0 change and a
   `schemaVersion` bump.

**Decision (locked): (3) with (1) as interim.** Add `manifest.partVersion` to
featurekit Module 0 and bump `schemaVersion` to 2, so version travels with the
part and the legend can display it. Until that field ships, encode `vNN` in the
model directory / STEP basename as the interim source. This pulls a **small
featurekit Module 0 change into scope** (new field + schema bump + legend display
of `partVersion`); the implementation plan owns sequencing it ahead of the
version-rigor rule.

Until `partVersion` is populated, the hard-stop rule treats *every* version-bearing
claim as requiring an explicit, human-stated version + artifact class — there is no
field to infer it from.

## Scope

In scope: reference rigor on part / feature / version / orientation, enforced by
skill + hook, symmetric across input and output, for the build123d→STEP stack and
any toolchain that feeds the legend.

Out of scope: CAD generation behavior, manufacturability/tolerance checking,
the featurekit feature-naming algorithm itself, and the legend panel UI.
