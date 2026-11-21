---
name: cinematic-vfx-director
description: Design and audit cinematic visual effects for AI video prompts and CG shots across live action, stylized CG, anime, fantasy, sci-fi, environmental effects, transformations, and action sequences. Use for VFX choice, timed effect behavior, weapon/character/environment effects, lighting response, prompt enhancement, or fixing detached and unreadable effects. Preserve user-specified shots, choreography and story.
---

# Cinematic VFX Director

> P3: the original skill-movie director/construction knowledge, 566-atom search and P2 data validation are integrated with a non-invasive VFX workflow and an Effect Card → copyable text compiler. **The compiler does not itself interpret new scripts, understand image frames, select effects, or provide model-specific rendering guarantees.** Full model adapters and rendered-video QC are later stages.

## Mission
Translate a VFX request into visible, causally grounded screen direction. Prioritize source → trigger → spatial anchor → trajectory/operation → target and environment response → decay / final state. Do **not** invent effects simply to make the shot busier.

## Boundaries
- Respect user's fixed identity, scene, lens, camera, framing, pace, choreography and duration. Do not silently rewrite the base prompt.
- VFX enhances approved body/weapon actions; it does not author missing choreography or substitute for real contact.
- Work equally for **non-combat** effects: weather, disasters, optical phenomena, mechanical transformations, cosmic environments, dream sequences, material damage and stylized simulations.
- Determine **medium**, **genre**, **effect family** independently; use L0–L4 as this project's relative intensity grades, not an industry standard.
- One dominant effect/read per key beat; add subordinate environment and optical layers only if they clarify the scene.
- Do not automatically add shockwaves, magic circles, flying energy slashes, explosions, eye glow or excessive particle storms.

## Primary VFX director and construction workflow (reused)

1. Read the **original** [cinematic-vfx-director](third_party/skill-movie/cinematic-vfx-director/SKILL.md) for shot-level VFX choices, causal hierarchy, medium routing and repair branches. Its references are preserved in the same vendored subtree.
2. Read the **original** [vfx-effect-construction-engine](third_party/skill-movie/vfx-effect-construction-engine/SKILL.md) when a concrete effect needs source/trigger/path/lifecycle/interaction design, and select a small number of atoms from its unchanged bank.
3. For original search behavior: `python third_party/skill-movie/vfx-effect-construction-engine/scripts/search_vfx_atoms.py "剑气" --limit 8`. For real project family filtering use `python scripts/search_atoms.py "剑气" --family weapon --limit 8 --json`. For precise curated tags use `python scripts/search_atoms.py "雨滴" --tag rain --tag weather --json`. The wrapper invokes the original scoring function; **do not paste 566 terms into the prompt**.
4. For the exact meanings of each query parameter, consult [P2 search and validation](docs/SEARCH_AND_VALIDATION.md). `--family`, `--role`, `--category`, and `--tag` actually filter; `--medium`, `--genre`, and `--style` are context only and must not be presented as verified atom applicability. For film-specific constraints, consult [four-axis taxonomy](references/taxonomy.md), [causal grammar](references/effect-grammar.md), [state lifecycle](references/lifecycle.md), [composition rules](references/composition-rules.md) and [curated upstream atom IDs](data/curated_atoms.json). The upstream bank uses its own family names; the wrapper maps rather than modifies them.
5. Vendored `skill-movie` modules mention other specialized skills (action-choreography-reference, ai-material-realism, cinematic-audiovisual-language, cinematic-music-sound-design, seedance-vfx). Treat those as **optional external integrations**, not required local dependencies. This Skill preserves their ownership boundaries and must work without them.
6. When the user asks for an example, use [six initial Effect Card examples](examples/effect-cards.json) as structure references, not copy-pasted visual content. These include realistic weather and non-combat transformation.

## Reuse mature upstream before inventing new rules
Read [Upstream routing](adapters/upstream-routing.md) first. For animation principles, elements, physics, brightness and medium-specific VFX art direction, use the existing [rng-vfx source](third_party/rng-vfx/skills/rng-vfx/SKILL.md) and its reference files. For effect design, layering, timing and review, use the existing [effekseer-vfx source](third_party/effekseer-vfx-skill/skills/effekseer-vfx/SKILL.md) and [independent VFX review](third_party/effekseer-vfx-skill/skills/vfx-review/SKILL.md). Treat game-engine-specific steps as background, not AI video prompt instructions. Only add this project's own rules where film/video use genuinely differs; keep vendored files unchanged.

## P3 decision workflow: intent → effect → prompt delta

Read [director workflow](references/director-workflow.md), [combination gates](references/combination-gates.md) and [output contract](references/output-contract.md) as the **local adaptation** of the two upstream VFX skills. Use the established upstream source documents first; do not rewrite their technical foundations.

1. **Classify the user request**: knowledge/terminology, explore, augment an existing prompt, design an effect, repair a failed effect, or multi-shot planning. For terminology queries, answer the question without inventing a shot.
2. **Lock the original** before changing anything: original `source_prompt` verbatim, identity, count, costume, object shape, contact, choreography, timing, camera, composition, existing editing rhythm and negative constraints. Unknown input is unknown, not permission to add actions.
3. **Separate four axes**: medium (rendering), genre (world), style_profiles (aesthetic), and dominant VFX family (effect function). "MJ-like" belongs to aesthetic direction; it does **not** imply magic or energy effects. Choose conservative intensity L0–L4. If VFX adds no readable information, recommend none.
4. **Assign an effect job**: one `primary_read` per beat (e.g. activation, speed, contact, spatial boundary, transformation frontier). Use causal source → visible trigger → fixed anchor → form/path → receiver/environment/light response → decay/settled state. Only include observable phases, not a forced charge/explosion lifecycle.
5. **Reuse the upstream construction engine**: read its original grammar and family atlas, retrieve a small set of unique-task atom IDs via `scripts/search_atoms.py` (original score function preserved), optionally consult `rng-vfx` for physics/styles and `effekseer-vfx-skill` for layering/review. Avoid piling on synonyms or default shockwaves, spells, trails or debris.
6. **Run composition gates**: actual grip before weapon activation, actual contact before hit flash, motion path before trail, visible deformation front before transformation. One dominant effect per beat; secondary light/wind/debris only as warranted. Never change body motion, camera, editing or identity to justify a VFX idea.
7. **Prepare an approved Effect Card**: use `data/schemas/effect-card.schema.json` and examples in `examples/effect-cards.json` and `tests/fixtures/p3_scenarios.json`. The card's `vfx_delta` is a concise **human/Agent-reviewed** text addition, not auto-invented by the compiler.
8. **Default output**: show the original prompt unchanged and a separate VFX delta. The user may paste it into their prompt. If the user explicitly approves integration, and the card scope is `explicitly-approved-integration`, the compiler may **append** a new VFX section while retaining every original character. It does not insert text into existing user sections or rewrite the script.
9. **Editorial QC and repair**: check trigger/contact order, screen-space anchoring, medium-specific light/occlusion, intensity, subject readability and constraints. For defects, suggest the smallest directional fix and preserve the rest. P3 structural checks are not visual video QC (P6).
10. **Multi-shot**: decide continuity vs independence from user story, not a blanket preference. Detailed state propagation/automatic checks belong to P5. For every shot, keep the planned start and end effect state consistent.

### CLI (optional deterministic compilation of an approved card)

```bash
python -m pip install -r requirements-dev.txt
python scripts/compile_prompt.py --card sample.sword-activation
python scripts/compile_prompt.py --card sample.sword-activation --json
```

The first command prints the unchanged source and independent VFX delta; JSON includes audit-only internal atom IDs. To append, both explicit `--integrated --approved` and the Card's integrated scope are required. Never claim that approval was received solely because the CLI can append. **Do not put internal IDs, rejected effect variants or technical QC labels into the copyable prompt.**

## Quick example
**Request:** A semi-realistic CG woman firmly grips a floating violet sword; no attack.
**VFX enhancement:** The moment all five fingers close around the hilt, a narrow violet energy pulse travels *along the existing blade*, subtly intensifying the edge glow. A few purple-white particles spread briefly and settle beside the weapon; light spills naturally onto her hand, sleeve, jaw and nearby surfaces. No slash, projectile, shockwave or unrelated camera move.

## Documentation
See [Product design](docs/PRODUCT_DESIGN.md), [Implementation plan](docs/IMPLEMENTATION_PLAN.md), [P3 workflow](references/director-workflow.md), [output contract](references/output-contract.md) and [ten-shot evaluation](examples/ten-shot-validation.md).
