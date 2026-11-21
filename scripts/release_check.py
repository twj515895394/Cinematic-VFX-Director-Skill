#!/usr/bin/env python3
"""P7 offline checks for links, source snapshots and release scope."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")


def project_docs(root=ROOT):
    docs = [root / "README.md", root / "SKILL.md"]
    for d in ("docs", "references", "examples", "adapters"):
        docs += sorted((root / d).rglob("*.md"))
    return [p for p in docs if p.is_file()]


def local_link_issues(root=ROOT):
    problems, count = [], 0
    for source in project_docs(root):
        fence = False
        for lineno, line in enumerate(source.read_text(encoding="utf-8").splitlines(), 1):
            if line.lstrip().startswith(("~~~", chr(96) * 3)):
                fence = not fence
                continue
            if fence:
                continue
            for match in LINK.finditer(line):
                raw = match.group(1).strip()
                if raw.startswith("<") and raw.endswith(">"):
                    raw = raw[1:-1]
                else:
                    raw = raw.split(" ", 1)[0]
                if not raw or raw.startswith(("#", "//", "/")):
                    continue
                parsed = urlsplit(raw)
                if parsed.scheme or parsed.netloc or not parsed.path:
                    continue
                count += 1
                target = (source.parent / unquote(parsed.path)).resolve()
                if not target.is_relative_to(root.resolve()):
                    problems.append("%s:%s escapes repository: %s" % (source.relative_to(root), lineno, raw))
                elif not target.exists():
                    problems.append("%s:%s broken link: %s" % (source.relative_to(root), lineno, raw))
    return problems, count


def snapshot_issues(root=ROOT):
    issues = []
    sources = json.loads((root / "data/sources.json").read_text(encoding="utf-8"))["sources"]
    if len(sources) != 5:
        issues.append("Expected five upstream source registrations")
    for item in sources:
        folder = root / item.get("vendor_path", "")
        actual = sum(p.is_file() and p.suffix not in (".pyc", ".pyo")
                     and "__pycache__" not in p.parts and ".pytest_cache" not in p.parts
                     for p in folder.rglob("*")) if folder.is_dir() else 0
        if actual != item.get("vendored_file_count"):
            issues.append("Vendor file count differs: %s" % item.get("id", "?"))
        if len(item.get("upstream_commit", "")) != 40:
            issues.append("Unpinned upstream: %s" % item.get("id", "?"))
        for path in item.get("integration", []):
            if not (root / path).is_file():
                issues.append("Missing integration %s: %s" % (item.get("id", "?"), path))
    return issues


def guardrail_issues(root=ROOT):
    problems = []
    profile = json.loads((root / "data/model_profiles.json").read_text(encoding="utf-8"))
    if profile["default_model"] != "minimax-h3" or set(profile["models"]) != {"minimax-h3", "seedance"}:
        problems.append("Model scope must be H3 default + Seedance only")
    for name in ("README.md", "SKILL.md", "VERSION", "CHANGELOG.md",
                 "docs/USER_ACCEPTANCE.md", "docs/RELEASE_NOTES.md",
                 "references/choice-first-workflow.md", "references/qc-review-workflow.md"):
        if not (root / name).is_file():
            problems.append("Missing release artifact: " + name)
    version_file = root / "VERSION"
    if version_file.is_file():
        if not re.fullmatch(r"\d+\.\d+\.\d+-rc\.\d+", version_file.read_text(encoding="utf-8").strip()):
            problems.append("Version must describe a pre-acceptance RC")
    skill = (root / "SKILL.md").read_text(encoding="utf-8")
    # Distinct Skill identity: don't collide with the original upstream
    # cinematic-vfx-director Skill stored under third_party/.
    frontmatter = re.match(r"\A---\r?\n(.*?)\r?\n---\r?\n", skill, re.S)
    if frontmatter is None:
        problems.append("Root SKILL.md is missing valid YAML frontmatter")
    else:
        metadata = frontmatter.group(1)
        if re.search(r"(?m)^name: Cinematic-VFX-Director-Skill$", metadata) is None:
            problems.append("Root skill name must be exactly Cinematic-VFX-Director-Skill")
        if re.search(r"(?m)^description: >-$", metadata) is None:
            problems.append("Skill description must use bilingual YAML folded text")
        for phrase in ("中文：", "English:"):
            if phrase not in metadata:
                problems.append("Missing bilingual Skill metadata description: " + phrase)
    for phrase in ("# Cinematic-VFX-Director-Skill", "**中文简介：**", "**English overview:**"):
        if phrase not in skill:
            problems.append("Missing canonical bilingual root Skill intro: " + phrase)
    readme = (root / "README.md").read_text(encoding="utf-8")
    for phrase in ("# Cinematic-VFX-Director-Skill", "**中文简介：**", "**English introduction:**"):
        if phrase not in readme:
            problems.append("Missing canonical bilingual README intro: " + phrase)
    for phrase in ("3–5", "minimax-h3", "seedance", "design-pass-pending-rendered-review"):
        if phrase not in skill:
            problems.append("Missing root Skill workflow guarantee: " + phrase)
    if not (root / ".gitignore").is_file() or "reviews/" not in (root / ".gitignore").read_text(encoding="utf-8"):
        problems.append("Private reviews directory must be ignored")
    return problems


def verify(root=ROOT):
    links, n = local_link_issues(root)
    issues = links + snapshot_issues(root) + guardrail_issues(root)
    return issues, {"docs": len(project_docs(root)), "local_links": n,
                    "version": (root / "VERSION").read_text(encoding="utf-8").strip()}


def main():
    parser = argparse.ArgumentParser(description="Check P7 Skill release readiness")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    problems, stats = verify()
    if args.json:
        print(json.dumps({"passed": not problems, "stats": stats, "issues": problems},
                         ensure_ascii=False, indent=2))
    else:
        print("P7 readiness:", stats)
        for issue in problems:
            print("FAIL:", issue)
        print("PASS: static release readiness" if not problems else "FAIL: release readiness")
    return int(bool(problems))


if __name__ == "__main__":
    raise SystemExit(main())
