---
name: cinematic-vfx-director
description: Design and audit cinematic visual effects for AI video prompts and CG shots across live action, stylized CG, anime, fantasy, sci-fi, environmental effects, transformations, and action sequences. Use for VFX choice, timed effect behavior, weapon/character/environment effects, lighting response, prompt enhancement, or fixing detached and unreadable effects. Preserve user-specified shots, choreography and story.
---

# Cinematic VFX Director

> P5 is implemented as a **human-confirmed VFX option-first Agent workflow**, with MiniMax H3 as the default and Seedance as the only alternate video model. Includes two-model VFX prompt insertions, explicit multi-shot state checks, 566-atom retrieval and source-linked reference profiles. **Scripts validate and assemble approved text; they do not visually understand images or render/QC finished video.**

## Mission
Translate a VFX request into visible, causally grounded screen direction. Prioritize source → trigger → spatial anchor → trajectory/operation → target and environment response → decay / final state. Do **not** invent effects simply to make the shot busier.

## REQUIRED P5 gateway: 3–5 human-friendly VFX options BEFORE final prompt

**Default video platform: MiniMax H3. Only permitted alternate: Seedance.** If the user doesn't name a model, assume `minimax-h3`; if the user explicitly requests Seedance, use `seedance`. Do not offer Kling, Veo, Wan or a generic model as a third adapter. Seedance with no specified sub-version uses version-agnostic language; do not invent API/model settings.

**When the user only gives a scene, image, reference video, or vague request such as “给这个加一些特效” and hasn't named a specific effect**, the Agent MUST:

1. **Look at actual supplied information**, identifying which subject, prop, setting, lighting, action, duration and camera are visible/stated. For a still image, future actions/time points are unknown: do not claim a character will swing a sword merely because a sword is pictured. List uncertain details briefly. Lock identity, costume, count, spatial layout, camera, choreography and the original prompt as immutable.
2. **Consult actual skill knowledge**: classify medium × genre × style × effect family; read only the relevant source-linked [P4 profiles](references/cinematic-profile-routing.md), original [skill-movie director and construction guide](third_party/skill-movie/cinematic-vfx-director/SKILL.md) and [566 atom search](scripts/search_atoms.py); check material/light/temporal causality and existing scene compatibility.
3. **Offer 3–5 distinct, suitable choices in everyday language**, not 3–5 synonymous glows. For each show an easy name, **visible outcome**, **reason it fits the specific scene**, **intensity and risk/constraint**. Rank the best as recommended but **DO NOT auto-select it**. Do not propose attacks, flying slashes, magic circles, changes of clothing or camera unless the user allows them. Include low-intensity choices where possible; if none is suitable, say so instead of inventing meaningless effects.
4. **STOP and ask for user selection.** Example: “推荐A1剑刃逐渐点亮，A2剑周薄雾，A3剑面聚能，A4柔和受光。选哪个？也可组合A1+A4或选择不加。” Do not output an approved Effect Card or finalized video-model prompt at this stage. [Choice-first contract](references/choice-first-workflow.md); optional validated examples use `python scripts/recommend_options.py --package examples/recommendations/sword-image.json` (example is synthetic, not an image recognition claim).
5. **After explicit user choice**, use that option (or user-approved combination with one Primary effect per beat), derive timing/anchor/material/response from the actual scene, then create/verify the Effect Card and produce a MiniMax H3 or Seedance VFX-only prompt patch via `scripts/adapt_prompt.py`. Revisions should update only selected VFX, never silently rewrite the story.
6. **Bypass the menu only when appropriate**: user specified the exact effect and constraints clearly, is asking a terminology question, or asks to repair an already chosen effect. A vague “I want MJ-style” is an aesthetic intent rather than permission for unrequested magic. If the user asks for an explicit proposal rather than a finalized prompt, still show choices.

**Do not misrepresent the helper scripts:** they validate recommendation packages and explicit selection, not automatically infer what is in a supplied image. The multimodal Agent performs actual image analysis when available. Test fixtures are illustrative, not a one-size-fits-all lookup.

## P5 video model routing and multishot contracts

- Use [two-model adapter rules](references/model-adapters.md) and `data/model_profiles.json`. For MiniMax H3, **read the original official** [H3 prompt-writing SKILL](third_party/minimax-h3/skills/h3-prompt-writing/SKILL.md) and its base/ref guides. When producing an entire approved H3 prompt, follow official T2VA/I2VA/FL2VA/L2VA/Ref2VA structure rather than inventing field names or reference labels. The deterministic `scripts/adapt_prompt.py` returns a *VFX insertion for an existing shot*, not a complete audiovisual prompt. It defaults to H3.
- For Seedance, read the official linked ByteDance sources in [model adapters](references/model-adapters.md), keep real reference media tags grounded in actual supplied assets, describe VFX triggers and environment response in plain shot language, and never assume a particular Seedance minor version or controls.
- For multi-shot use [VFX state contract](references/multishot-states.md) and `python scripts/check_shot_states.py --file examples/sequences/continuous-sword.json`. **Only connect shots explicitly designated `continue`**; `independent` montage scenes need no inherited state; `reset` needs a reason. Check color, anchor, identity and status at a cut, but do not alter the edit or fabricate video continuity.
- The P3 output authorization remains in force: default original text unchanged + independent VFX delta. An integrated full output needs explicit user approval and the existing Card scope gate; no user selection alone grants permission to alter unrelated elements.

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

## P4 progressive knowledge and visual reference retrieval

Read [cinematic profile routing](references/cinematic-profile-routing.md) to understand four independent axes and the source-linked knowledge plan. **Before composing any effect**, select only the relevant family, medium, genre and style; do not read every profile or every case at once.

1. Use `python scripts/lookup_profile.py --axis family --id <family>` to retrieve project-specific anchors, lifecycle, practical errors and the actual vendored upstream references. Repeat for medium, genre and explicit style as needed. For example, `--axis style --id mj-dreamlike` adds a dreamlike look; it does not invent magic or a projectile.
2. Read the original upstream art direction/physics/medium documents listed in each profile's `read_first` when craft detail is needed. Use our profiles only for the missing cinematic routing layer; preserve Copy-First.
3. Search the original 566-atom skill-movie bank via `scripts/search_atoms.py`. The P2 `medium/genre/style` parameters on **atom search** are context, NOT real atom-specific suitability filters.
4. For concrete **anime-style VFX** examples, optionally query `python scripts/search_cases.py --element water --form impact --limit 8` or `--paired-with water_charge_01`. These 90 records are derived from the pinned original `third_party/kanaworks-sakuga-vfx/catalog.json`, with original form, FPS, frames, tags, combination links and per-case preview URLs.
5. **Do not misrepresent sourced examples:** all 90 imported references are 2D anime-game effects, `curation_status=metadata-only`. They are not vetted photoreal-film, Pixar-like, MJ dreamscape or generative-video model results. `source_metadata` records are verifiable metadata; `observed_strengths` and `failure_modes` are not filled by pretending to have viewed the previews.
6. Case metadata offers visual reference and a possible effect layout, not an authorization to change the user's story, movement or look. Use medium-specific guidance to adapt any selected visual patterns; keep the original prompt untouched by default.

See [visual case documentation](docs/VISUAL_CASE_LIBRARY.md) for source links, review status, exact query semantics and catalog update checks.

## P3 decision workflow: intent → effect → prompt delta

Read [director workflow](references/director-workflow.md), [combination gates](references/combination-gates.md) and [output contract](references/output-contract.md) as the **local adaptation** of the two upstream VFX skills. Use the established upstream source documents first; do not rewrite their technical foundations.

1. **Classify the user request**: knowledge/terminology, explore, augment an existing prompt, design an effect, repair a failed effect, or multi-shot planning. For an under-specified VFX addition request with scene/image, **follow REQUIRED P5 choice-first gateway before continuing**; for terminology or explicit single-VFX requests, answer directly.
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
See [Product design](docs/PRODUCT_DESIGN.md), [Implementation plan](docs/IMPLEMENTATION_PLAN.md), [P5 choice-first workflow](references/choice-first-workflow.md), [P5 MiniMax H3/Seedance adapters](references/model-adapters.md), [multi-shot states](references/multishot-states.md), [P3 workflow](references/director-workflow.md), [P4 source-linked profiles](references/cinematic-profile-routing.md), [visual cases](docs/VISUAL_CASE_LIBRARY.md) and [output contract](references/output-contract.md).
