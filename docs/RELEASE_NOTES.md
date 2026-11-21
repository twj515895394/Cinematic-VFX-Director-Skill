# Release Candidate 0.1.0-rc.1 — Ready for User Acceptance

> Date: 2026-11-21. Status: **offline functionality released for user testing; actual MiniMax H3/Seedance video visual acceptance not yet performed**. GitHub `main` and a separately pinned release-candidate snapshot are distribution channels; no stable final tag until real acceptance.

## What works now

- **Copy-first VFX knowledge integration**: source-pinned upstream `skill-movie` (566 original bilingual atoms and lookup), `rng-vfx` (physics/motion/styles), `effekseer-vfx` (layering and independent review), `kanaworks-sakuga-vfx` (90 source-derived anime VFX metadata references) and MiniMax official H3 prompt-writing Skill. Original source files remain unchanged.
- **Four independent routing axes**: 14 VFX families, 9 render media, 14 genres, 9 aesthetic profiles; no unverified photoreal applicability assigned to anime cases.
- **Beginner-first Agent workflow**: for an underspecified scene/image/video, infer only grounded facts and offer **3–5 genuinely different VFX proposals**, explain visible outcome/why/strength/cost, await explicit user choice; for exact requests skip the menu.
- **Only two video-model output targets**: MiniMax H3 (default), Seedance on explicit choice. Use official H3 prompt Skill, version-agnostic Seedance rules; output additive VFX text by default, not fabricated model/video API controls.
- **Prompt safety/continuity**: approved Effect Cards, unmodified original, authorisation gate for integrated output; explicit continue/reset/independent multi-shot VFX state checks.
- **Review**: six 0–2 QC dimensions, 14 hard-failure categories, one top-issue fix per iteration; sixteen **synthetic design** positive/negative fixtures. `review_vfx.py` aggregates annotated reviews, **does not inspect pixels**.
- **Local user-acceptance tooling**: one-command offline check, source/link audit, video extraction candidate frame tool and `scripts/check_visual_evidence.py` source/frame SHA-256 integrity check and explicit `not-reviewed` metadata.

## Installation & one-command preflight

Python 3.11+ recommended. From the repository root:

```bash
python -m pip install -r requirements-dev.txt
python scripts/verify_all.py
```

For real video review candidate frames, optionally install `ffmpeg` and `ffprobe`:

```bash
python scripts/prepare_visual_evidence.py --video your_video.mp4 --shot-id S01 --model minimax-h3
```

This creates private, ignored `reviews/S01` frame candidates, **not** a QC pass report. See [User acceptance guide](USER_ACCEPTANCE.md) for 10 use cases and how to hand back actual failures.

## Release/acceptance evidence

- **Automated**: `scripts/verify_all.py` + GitHub Actions. Covers corpus integrity, recommended model scope, CLI smoke, recommendation gate, editor safety, sequence QC, design QA and repo documentation.
- **Still to be established by the user**: real output of both MiniMax H3 and Seedance, actual visual observations from original video/frames, reproducibility and quality after targeted repair.
- **Known evidence limitation**: all 90 Sakuga library references are sourced **2D anime/game animation metadata**, not already checked live-action, MJ-style, Pixar-like, or generated H3/Seedance video samples.
- **No network model calls**: the Skill directs prompts and reviewers; it does not bundle a hosted video-generation service, GPU video renderer, browser UI, or automatic vision-understanding Python model.

## Release policy

This is a **pre-acceptance candidate** (`0.1.0-rc.1`), not a stable quality-certified release. Keep this snapshot fixed during manual testing. After receiving the user's actual test findings, address reproducible defects, rerun all automated checks, then tag a stable version only if user accepts it.

## Documentation index

[Root Skill](../SKILL.md) · [README](../README.md) · [Implementation plan](IMPLEMENTATION_PLAN.md) · [Product design](PRODUCT_DESIGN.md) · [Four-axis profiles](../references/cinematic-profile-routing.md) · [Novice option-first](../references/choice-first-workflow.md) · [Two-model adapters](../references/model-adapters.md) · [Multi-shot](../references/multishot-states.md) · [Six-axis QC](../references/qc-rubric.md) · [Evidence workflow](../references/qc-review-workflow.md) · [User acceptance](USER_ACCEPTANCE.md).
