#!/usr/bin/env python3
"""Rebuild the 90-case cinematic index from the UNCHANGED KanaWorks catalog.

This is a thin structure adapter, not a new VFX knowledge base.
The source is kept verbatim in third_party/kanaworks-sakuga-vfx/catalog.json.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = ROOT / "third_party/kanaworks-sakuga-vfx/catalog.json"
OUTPUT = ROOT / "data/catalog/cases.json"
UPSTREAM_COMMIT = "7cfc9e6bd6ecc0239f3c141e9c5c42cbdc8bb365"
GITHUB_TREE = ("https://github.com/kanaworksai-hue/kanaworks-sakuga-vfx"
               "/tree/" + UPSTREAM_COMMIT + "/assets/")
PREVIEW_RAW = ("https://raw.githubusercontent.com/kanaworksai-hue/kanaworks-sakuga-vfx"
               "/" + UPSTREAM_COMMIT + "/assets/")

FAMILY_BY_FORM = {
    "column": ["elemental"],
    "impact": ["impact", "elemental"],
    "projectile": ["elemental", "motion"],
    "vortex": ["elemental", "atmospheric"],
    "strike": ["elemental", "impact"],
    "aura": ["energy", "elemental"],
    "charge": ["energy", "elemental"],
    "shield": ["energy", "elemental"],
    "slash": ["weapon", "motion", "elemental"],
}


def make_case(asset):
    pairs = [v for v in asset.get("pairs", {}).values() if isinstance(v, str) and v]
    fx = [name for name, value in asset.get("fx", {}).items()
          if value is not None and (name != "hit_stop_s" or value != 0)]
    contact = asset.get("contact_frame")
    markers = ([{
        "label": "source-contact-frame",
        "description": "上游标注第 %s 帧为接触/触发帧（未人工审核）" % contact,
        "time_seconds": round(contact / asset["fps"], 5),
    }] if isinstance(contact, int) and not isinstance(contact, bool) else [])
    base = asset["element"] + "/" + asset["id"] + "/"
    return {
        "case_id": "sakuga." + asset["id"],
        "title": asset["id"].replace("_", " "),
        "medium": "anime-2d",
        "genres": [],
        "style_profiles": ["anime-sakuga"],
        "family_ids": FAMILY_BY_FORM.get(asset["form"], ["elemental"]),
        "atom_ids": [],  # No invented link to skill-movie atom bank.
        "description": "上游 %s 元素、%s 形态的 %s 帧动画特效（%s fps）；仅代表原素材元数据，尚未逐帧审核。" % (
            asset["element"], asset["form"], asset["frames"], asset["fps"]),
        "source_url": GITHUB_TREE + base,
        "source_id": "sakuga-vfx",
        "license_notes": "KanaWorks_AI VFX Asset License 1.0；标注 VFX: KanaWorks_AI (@KanaWorks_AI)；素材版权归原作者。",
        "static_preview_url": PREVIEW_RAW + base + "preview.webp",
        "motion_preview_url": None,
        "time_markers": markers,
        "observed_strengths": [],
        "failure_modes": [],
        "reproduction_notes": "根据原始 catalog.json 构建检索索引。按需查看原站动态预览；不得将游戏效果直接当作已验证的真人电影/视频模型效果。",
        "asset_distribution": "external-link-only",
        "curation_status": "metadata-only",
        "source_asset_id": asset["id"],
        "upstream_revision": UPSTREAM_COMMIT,
        "source_metadata": {
            "element": asset["element"],
            "form": asset["form"],
            "frames": asset["frames"],
            "fps": asset["fps"],
            "loop": asset["loop"],
            "anchor": asset["anchor"],
            "orientation": asset["orientation"],
            "source_tags": asset.get("tags", []),
            "source_use_cases": asset.get("use_cases", []),
            "paired_source_ids": pairs,
            "fx_components": fx,
        },
    }


def build_catalog(raw=None):
    raw = raw if raw is not None else json.loads(UPSTREAM.read_text(encoding="utf-8"))
    return {"schema_version": "1.0", "cases": [make_case(a) for a in raw["assets"]]}


def main():
    p = argparse.ArgumentParser(description="Regenerate/check cinematic case index from vendored original.")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--check", action="store_true", help="Exit nonzero if derived case index has drifted")
    g.add_argument("--write", action="store_true", help="Write deterministic case index")
    args = p.parse_args()
    generated = build_catalog()
    if args.check:
        existing = json.loads(OUTPUT.read_text(encoding="utf-8"))
        if generated != existing:
            p.error("Derived case index differs from pinned upstream; use --write and review changes.")
        print("PASS: %d source cases match derived index" % len(generated["cases"]))
    else:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(json.dumps(generated, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("Wrote %d case references" % len(generated["cases"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
