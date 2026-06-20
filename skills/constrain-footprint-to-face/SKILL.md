---
name: constrain-footprint-to-face
description: Use when a user names a specific face/edge/feature to base new geometry on — keep the new geometry's footprint constrained to that exact entity, never its bounding box.
---

<!-- provenance (staged by /no) -->
<!-- original-prompt: "extrude face f2 into a smoothly rounded cover over the slot, no visible holes, with a small clearance pocket for the clip" -->
<!-- dissatisfaction: model built the cover from f2's BOUNDING BOX (RectangleRounded) instead of f2's actual outline; "footprint should be constrained to the specified face" -->
<!-- intended-outcome: new geometry derived from the named face's true boundary (outer_wire), with smoothing applied TO that outline, never a bbox substitution -->
<!-- baseline-quality: 0.0 -->
<!-- champion-quality: 0.887 (strategy: terse-imperative; vs rubric+example 0.5875, checklist 0.4425) -->
<!-- date: 2026-06-20 -->
<!-- depth: light -->

When the user names a specific face, edge, or feature (e.g. `f2`) to base new
geometry on, the new geometry's footprint MUST come from THAT entity's actual
boundary — `face.outer_wire()` / its real outline — never its bounding box,
nor a substituted rectangle/primitive, nor a hand-typed approximation.

This holds even when a secondary goal (smoothness, simplicity, a clean fillet)
is easier on a bounding box. Derive the footprint from the named entity first,
THEN apply rounding/fillets to that exact outline. If a secondary goal genuinely
can't be met on the true outline, say so and ask — do not silently swap the
named reference for a convenient stand-in.
