---
name: cinematic-vfx-director
description: Design and audit cinematic visual effects for AI video prompts and CG shots across live action, stylized CG, anime, fantasy, sci-fi, environmental effects, transformations, and action sequences. Use for VFX choice, timed effect behavior, weapon/character/environment effects, lighting response, prompt enhancement, or fixing detached and unreadable effects. Preserve user-specified shots, choreography and story.
---

# Cinematic VFX Director

> P1 reference routing available: MIT upstream VFX art-direction and review files are vendored under `third_party/`, with a local routing guide. Atom search, automated QC and full video-model adapters are still planned.

## Mission
Translate a VFX request into visible, causally grounded screen direction. Prioritize source → trigger → spatial anchor → trajectory/operation → target and environment response → decay / final state. Do **not** invent effects simply to make the shot busier.

## Boundaries
- Respect user's fixed identity, scene, lens, camera, framing, pace, choreography and duration. Do not silently rewrite the base prompt.
- VFX enhances approved body/weapon actions; it does not author missing choreography or substitute for real contact.
- Work equally for **non-combat** effects: weather, disasters, optical phenomena, mechanical transformations, cosmic environments, dream sequences, material damage and stylized simulations.
- Determine **medium**, **genre**, **effect family** independently; use L0–L4 as this project's relative intensity grades, not an industry standard.
- One dominant effect/read per key beat; add subordinate environment and optical layers only if they clarify the scene.
- Do not automatically add shockwaves, magic circles, flying energy slashes, explosions, eye glow or excessive particle storms.

## Reuse mature upstream before inventing new rules
Read [Upstream routing](adapters/upstream-routing.md) first. For animation principles, elements, physics, brightness and medium-specific VFX art direction, use the existing [rng-vfx source](third_party/rng-vfx/skills/rng-vfx/SKILL.md) and its reference files. For effect design, layering, timing and review, use the existing [effekseer-vfx source](third_party/effekseer-vfx-skill/skills/effekseer-vfx/SKILL.md) and [independent VFX review](third_party/effekseer-vfx-skill/skills/vfx-review/SKILL.md). Treat game-engine-specific steps as background, not AI video prompt instructions. Only add this project's own rules where film/video use genuinely differs; keep vendored files unchanged.

## Procedure
1. Read the user's prompt, constraints, and deliverable: exploratory idea / existing prompt enhancement / per-shot design / repair / reference learning.
2. Preserve concrete facts. Identify the intended visual information and whether a VFX addition is necessary.
3. Choose medium and genre separately, set a sensible intensity if unspecified, and select a dominant family.
4. Describe the causal **effect card**: visible owner, specific trigger, form/material, path, depth/occlusion, effect on object/environment/light, peak, fade and endpoint. Include only visible phases.
5. Bind onset and peak to actual actions and contacts; avoid early hit flashes or inconsistent hand/weapon location.
6. Provide a concise **separate VFX enhancement paragraph** by default. Offer an integrated rewrite only when asked or clearly approved, while preserving the original.
7. Audit for causal errors, disconnected overlays, overbrightness, obstruction, anatomy/identity changes, exaggerated particles and unexplained new powers.
8. For multi-shot sequences, distinguish continuity (`effect_state_in/out`) from intentionally disconnected montage; never force one mode.
9. Never pretend the planned scripts or reference files already exist. Use normal knowledge until the indexed library is implemented.

## Quick example
**Request:** A semi-realistic CG woman firmly grips a floating violet sword; no attack.
**VFX enhancement:** The moment all five fingers close around the hilt, a narrow violet energy pulse travels *along the existing blade*, subtly intensifying the edge glow. A few purple-white particles spread briefly and settle beside the weapon; light spills naturally onto her hand, sleeve, jaw and nearby surfaces. No slash, projectile, shockwave or unrelated camera move.

## Documentation
See [Product design](docs/PRODUCT_DESIGN.md) and [Implementation plan](docs/IMPLEMENTATION_PLAN.md).
