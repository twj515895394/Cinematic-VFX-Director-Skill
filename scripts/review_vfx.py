#!/usr/bin/env python3
"""P6 source-reused VFX QC rubric aggregation and single-issue repair advice.

This script NEVER looks at video pixels. An Agent/reviewer must inspect
actual footage/frames (if available) and supply evidence-backed observations.
It reuses the vendored independent-review approach from effekseer-vfx-skill;
the 6-axis 0..2 rubric is this project's cinematic adapter (not upstream's
9-axis 0..3 filmstrip scoring).

Usage:
  python scripts/review_vfx.py --review tests/fixtures/qc/design-good-sword.json
  python scripts/review_vfx.py --review tests/fixtures/qc/design-bad-contact.json --json
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_FILE = ROOT / "data/schemas/qc-review.schema.json"
AXES = ("causality", "space", "timing", "style_intensity", "environment", "readability")
MIN_TOTAL = 10
HARD_FIXES = {
    "SOURCE_PROMPT_CHANGED": ("scope", "恢复原提示词的逐字内容，只以独立VFX增量提出修改；不要改镜头/剧情。"),
    "UNAUTHORIZED_ACTION": ("scope", "删除未经授权的新动作、攻击、运动或镜头，不以VFX设计扩写故事。"),
    "IDENTITY_DRIFT": ("identity", "约束人物/道具身份、数量和造型；只改变有授权的效果层。"),
    "EARLY_CONTACT": ("timing", "将命中火花和受体反应移到真实接触帧之后，不要提前生成。"),
    "DETACHED_ANCHOR": ("space", "把发光/粒子/变形前沿重新锚定现有表面或真实世界空间。"),
    "MISSING_ENV_RESPONSE": ("environment", "补上与既有光源、表面或风向一致的最小环境响应。"),
    "OCCLUSION": ("readability", "降低/移动遮挡主体的特效层，让眼睛、手部或接触点保持可读。"),
    "OVEREXPOSURE": ("readability", "减弱主效果高光/泛光面积，保留材质纹理和面部轮廓。"),
    "UNJUSTIFIED_INTENSITY": ("style_intensity", "降低到该镜头需要的强度档位，删除无因果的三级装饰。"),
    "STATE_JUMP": ("continuity", "保持同一效果在衔接镜头接缝处的身份、颜色、锚点与状态。"),
    "UNSUPPORTED_MODEL_CONTROL": ("model", "移除未经证实的生成器参数，仅保留H3或Seedance支持的自然语言VFX描述。"),
    "UNCONFIRMED_CHOICE": ("selection", "停止最终提示词生成，先展示3–5个适合的方案并等用户选定。"),
    "FABRICATED_REFERENCE": ("reference", "删除不存在的图片/视频/声音引用；只绑定实际提供的附件。"),
    "PHYSICS_MISMATCH": ("physics", "修正粒子/材料/风向/重力与画面中已存在的物理条件一致。"),
}
AXIS_FIXES = {
    "causality": ("visible trigger", "明确特效来源和已发生的触发动作，删除无来源的爆闪。"),
    "space": ("spatial anchor", "将特效位置、尺度与遮挡绑定到已有物体或场景。"),
    "timing": ("phase timing", "调整出现、真实接触与衰减的先后，避免错位和突然跳帧。"),
    "style_intensity": ("style/strength", "降低不合媒介/题材的亮度与粒子强度，保留主次关系。"),
    "environment": ("environment response", "补最少量真实的受光、材质、风向或接触反馈。"),
    "readability": ("focus/occlusion", "清理遮挡或无效亮层，让主体和主特效的目标清楚可读。"),
}


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate_review(review):
    schema = load(SCHEMA_FILE)
    errors = sorted(Draft202012Validator(schema).iter_errors(review),
                    key=lambda e: ("/".join(map(str, e.absolute_path)), e.message))
    if errors:
        e = errors[0]
        raise ValueError("Invalid QC review [%s]: %s" %
                         ("/".join(map(str, e.absolute_path)) or "$", e.message))
    if len({f["code"] for f in review["hard_failures"]}) != len(review["hard_failures"]):
        raise ValueError("Repeated hard-failure code: report each category once per review")
    observed = set(review["evidence"]["observed_frame_ids"])
    if review["evidence"]["kind"] != "design-only":
        if not observed:
            raise ValueError("Rendered review requires observed frames")
        # Explicit citations to frame identifiers are machine-checkable.
        # This DOES NOT prove those images exist or were actually inspected.
        allowed = {"frame:" + str(x) for x in observed}
        for axis, item in review["scores"].items():
            if not item["evidence_refs"]:
                raise ValueError("Rendered review needs evidence_refs for " + axis)
        for item in list(review["scores"].values()) + review["hard_failures"] + review["findings"]:
            for ref in item.get("evidence_refs", []):
                if ref not in allowed and ref not in review["evidence"]["asset_refs"]:
                    raise ValueError("Unknown inspected evidence reference: " + ref)
    return review


def evaluate(review):
    validate_review(review)
    total = sum(review["scores"][axis]["score"] for axis in AXES)
    zeros = [axis for axis in AXES if review["scores"][axis]["score"] == 0]
    blocking = [f["code"] for f in review["hard_failures"]]
    passed = total >= MIN_TOTAL and not zeros and not blocking

    evidence_kind = review["evidence"]["kind"]
    if not passed:
        verdict = ("design-needs-repair" if evidence_kind == "design-only"
                   else "reported-visual-needs-repair")
    elif evidence_kind == "design-only":
        verdict = "design-pass-pending-rendered-review"
    elif review["reviewer"]["role"] == "author":
        verdict = "self-review-pending-independent-review"
    else:
        verdict = "reviewer-reported-visual-pass"

    # Single-issue direction per iteration, copied in principle from original
    # independent effekseer review; do not automatically overwrite any prompt.
    next_fix = None
    if blocking:
        item = review["hard_failures"][0]
        target, action = HARD_FIXES[item["code"]]
        next_fix = {"source": "hard-failure", "code": item["code"], "target": target,
                    "observation": item["observation"], "suggested_minimal_change": action}
    elif not passed:
        weak_axis = min(AXES, key=lambda x: (review["scores"][x]["score"], AXES.index(x)))
        named = [x for x in review["findings"] if x["axis"] == weak_axis]
        target, action = AXIS_FIXES[weak_axis]
        next_fix = {"source": "weakest-axis", "code": weak_axis,
                    "target": named[0]["target"] if named else target,
                    "observation": review["scores"][weak_axis]["observation"],
                    "suggested_minimal_change": named[0]["minimal_change"] if named else action}

    return {
        "review_id": review["review_id"], "shot_id": review["shot_id"],
        "model": review["model"], "evidence_kind": evidence_kind,
        "reviewer_role": review["reviewer"]["role"],
        "score_total": total, "score_max": 12,
        "score_breakdown": {x: review["scores"][x]["score"] for x in AXES},
        "zero_axes": zeros, "hard_failure_codes": blocking,
        "rubric_passed": passed, "verdict": verdict,
        # Key distinction: NO automated image verification, even when a
        # reviewer claims they inspected images.
        "rendered_video_independently_verified_by_tool": False,
        "next_fix": next_fix,
        "immutable_constraints": list(review["immutable_constraints"]),
        "original_source_prompt": review["source_prompt"],
        "next_step": (
            "Request a separate independent reviewer and actual rendered-frame evidence; do not claim final visual QC."
            if passed and evidence_kind == "design-only" else
            "Independent evidence/artifact freshness must be externally checked before final ship."
            if passed else
            "Fix only the one nominated VFX issue, keep original prompt unchanged, then re-review."
        ),
    }


def main():
    p = argparse.ArgumentParser(description="Aggregate six-axis, evidence-aware VFX QC observations")
    p.add_argument("--review", type=Path, required=True)
    p.add_argument("--json", action="store_true")
    p.add_argument("--fail-on-blocked", action="store_true",
                   help="Return exit 1 if review fails rubric or has any hard failure")
    args = p.parse_args()
    try:
        result = evaluate(load(args.review))
    except (ValueError, FileNotFoundError, json.JSONDecodeError) as exc:
        p.error(str(exc))
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("%s: %s (%d/12)" % (result["review_id"], result["verdict"],
                                  result["score_total"]))
        if result["next_fix"]:
            print("ONE VFX FIX:", result["next_fix"]["suggested_minimal_change"])
        print(result["next_step"])
    return 1 if args.fail_on_blocked and not result["rubric_passed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
