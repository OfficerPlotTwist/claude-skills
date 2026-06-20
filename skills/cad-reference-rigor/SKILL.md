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
