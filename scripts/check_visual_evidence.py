#!/usr/bin/env python3
"""Check actual H3/Seedance video/frame hashes before a human visual review.

This verifies source version and extracted frame bytes, NOT image content,
reviewer independence, observed frame claims or any VFX quality score.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from prepare_visual_evidence import sha256


def verify(manifest_path, video):
    manifest_path, video = Path(manifest_path).resolve(), Path(video).resolve()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    problems = []
    if manifest.get("purpose") != "manual-review-candidate-frames":
        problems.append("Not an actual video review evidence manifest")
    if not video.is_file() or sha256(video) != manifest.get("source_sha256"):
        problems.append("Original video is missing or SHA-256 differs from captured version")
    if not manifest.get("candidate_frames"):
        problems.append("No candidate frames")
    root = manifest_path.parent
    ids = set()
    for item in manifest.get("candidate_frames", []):
        frame_id = item.get("frame_id")
        if frame_id in ids:
            problems.append("Repeated source frame index: " + str(frame_id))
        ids.add(frame_id)
        filename = item.get("filename", "")
        if not isinstance(filename, str):
            problems.append("Invalid candidate filename")
            continue
        p = (root / filename).resolve()
        if not p.is_relative_to(root):
            problems.append("Frame path escapes review directory: " + filename)
        elif not p.is_file() or sha256(p) != item.get("sha256"):
            problems.append("Frame missing or SHA-256 differs: " + filename)
    if manifest.get("review_status") != "not-reviewed" or manifest.get("actually_inspected_frame_ids") != []:
        # If the reviewer later edits these fields manually the manifest
        # remains an immutable extraction record; observations belong to QC report.
        problems.append("Extraction manifest should remain not-reviewed; put inspections in separate QC report")
    return problems, {"shot_id": manifest.get("shot_id"), "model": manifest.get("model"),
                      "frames": len(manifest.get("candidate_frames", [])),
                      "source_sha256": manifest.get("source_sha256")}


def main():
    p = argparse.ArgumentParser(description="Check original video and frame SHA-256 evidence integrity")
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--video", type=Path, required=True)
    args = p.parse_args()
    try:
        problems, stats = verify(args.manifest, args.video)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        p.error(str(exc))
    print(json.dumps({"evidence_integrity_passed": not problems, "stats": stats,
                      "issues": problems, "visual_quality_verified": False},
                     ensure_ascii=False, indent=2))
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
