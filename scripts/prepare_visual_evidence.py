#!/usr/bin/env python3
"""Prepare real, provenance-bound video frames for manual VFX review.

Requires installed ffprobe and ffmpeg for actual videos. This tool EXTRACTS
candidate frames, never assigns QC scores and never claims the frames were
observed by a reviewer. Keep user-generated videos under ignored reviews/.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODELS = ("minimax-h3", "seedance")


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sample_times(duration, count=9):
    if not 2 <= count <= 30:
        raise ValueError("sample count must be 2–30")
    if not 0 < duration < 86400:
        raise ValueError("video duration must be between 0 and 24 hours")
    # Include start/end neighborhood and mid-effect milestones. Do not assume 24fps.
    end = max(0, duration - min(.02, duration / 100))
    return [round(end * i / (count - 1), 6) for i in range(count)]


def probe_video(video, command="ffprobe"):
    cmd = [command, "-v", "error", "-show_entries",
           "format=duration:stream=codec_type,width,height,r_frame_rate,avg_frame_rate,duration",
           "-of", "json", str(video)]
    raw = subprocess.run(cmd, check=True, capture_output=True, text=True)
    obj = json.loads(raw.stdout)
    streams = [s for s in obj.get("streams", []) if s.get("codec_type") == "video"]
    if not streams:
        raise ValueError("No video stream in source file")
    stream = streams[0]
    fps_str = stream.get("avg_frame_rate") or stream.get("r_frame_rate") or ""
    try:
        fps = float(Fraction(fps_str))
    except (ValueError, ZeroDivisionError):
        raise ValueError("Unable to read actual source video fps") from None
    duration = float(stream.get("duration") or obj.get("format", {}).get("duration") or 0)
    if fps <= 0 or duration <= 0:
        raise ValueError("Video duration/FPS must be positive")
    return {"duration_seconds": duration, "fps": fps,
            "frame_width": stream.get("width"), "frame_height": stream.get("height")}


def prepare(video, output_dir, model, shot_id, count=9, *, probe="ffprobe", extractor="ffmpeg"):
    video = Path(video).resolve()
    out = Path(output_dir).resolve()
    if model not in MODELS:
        raise ValueError("Only MiniMax H3 or Seedance are supported")
    if not video.is_file():
        raise FileNotFoundError(video)
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", shot_id):
        raise ValueError("shot-id must be 1–128 alphanumeric / dot / underscore / hyphen characters")
    for cmd in (probe, extractor):
        if not shutil.which(cmd):
            raise FileNotFoundError("Install ffprobe and ffmpeg first: " + cmd)
    info = probe_video(video, probe)
    times = sample_times(info["duration_seconds"], count)
    out.mkdir(parents=True, exist_ok=True)
    frames = []
    used = set()
    for i, time_seconds in enumerate(times):
        frame_id = min(round(time_seconds * info["fps"]),
                       max(0, int(info["duration_seconds"] * info["fps"]) - 1))
        if frame_id in used:
            continue  # Short clips cannot provide more unique frames than exist.
        used.add(frame_id)
        img = out / ("frame_%07d.png" % frame_id)
        cmd = [extractor, "-hide_banner", "-loglevel", "error",
               "-ss", "%.6f" % time_seconds, "-i", str(video),
               "-frames:v", "1", "-y", str(img)]
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        if not img.is_file() or img.stat().st_size == 0:
            raise RuntimeError("Could not extract sample frame %s" % frame_id)
        frames.append({"frame_id": frame_id, "time_seconds": time_seconds,
                       "filename": img.name, "sha256": sha256(img)})
    if not frames:
        raise ValueError("No candidate frames extracted")
    manifest = {
        "schema_version": "1.0", "purpose": "manual-review-candidate-frames",
        "model": model, "shot_id": shot_id, "source_name": video.name,
        "source_sha256": sha256(video), "source_size_bytes": video.stat().st_size,
        "source_metadata": info, "candidate_frames": frames,
        "actually_inspected_frame_ids": [],
        "review_status": "not-reviewed",
        "notice": ("Extraction and checksums do not mean someone inspected frames. "
                   "Open the video and frames, record actual inspected frame IDs "
                   "and use qc-review.schema.json only after review."),
    }
    (out / "evidence-manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return manifest


def main():
    p = argparse.ArgumentParser(description="Extract traceable frame candidates for real H3/Seedance visual QC")
    p.add_argument("--video", type=Path, required=True)
    p.add_argument("--model", choices=MODELS, default="minimax-h3")
    p.add_argument("--shot-id", required=True)
    p.add_argument("--output-dir", type=Path, help="Default: reviews/<shot-id>")
    p.add_argument("--sample-count", type=int, default=9)
    args = p.parse_args()
    output = args.output_dir or (ROOT / "reviews" / args.shot_id)
    try:
        result = prepare(args.video, output, args.model, args.shot_id, args.sample_count)
    except (ValueError, FileNotFoundError, RuntimeError, OSError, subprocess.CalledProcessError) as exc:
        p.error(str(exc))
    print("Prepared %s real frame candidates in %s" %
          (len(result["candidate_frames"]), Path(output).resolve()))
    print("Video SHA-256: " + result["source_sha256"])
    print("Status: NOT REVIEWED. A human/visual Agent must actually inspect footage before scoring.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
