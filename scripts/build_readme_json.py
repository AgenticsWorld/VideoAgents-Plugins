#!/usr/bin/env python3
"""Turn README.md into a structured readme.json for the plugin download page.

The zip files under plugins/ are the source of truth for *which* plugins exist;
README.md only supplies the copy. Every plugin must end up with a name, a
one-line summary, a description and a prompt example in every language block,
otherwise this script fails instead of publishing a half-empty catalog.

Usage:
  build_readme_json.py --readme README.md --plugins-dir plugins \
      --download-base https://example.com/path/ --out readme.json
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SCHEMA_VERSION = 1
REQUIRED_FIELDS = ("name", "summary", "description", "prompt")


def fail(msg: str) -> None:
    print(f"::error::{msg}", file=sys.stderr)
    sys.exit(1)


# --------------------------------------------------------------------------
# README parsing
# --------------------------------------------------------------------------

def split_languages(md: str) -> dict[str, str]:
    """Split the README on its top-level '## ' sections into language blocks."""
    blocks: dict[str, str] = {}
    matches = list(re.finditer(r"^## +(.+?) *$", md, flags=re.M))
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(md)
        lang = "en" if "english" in m.group(1).strip().lower() else "zh"
        blocks.setdefault(lang, md[m.end():end])
    return blocks


def parse_catalog(block: str) -> dict[str, dict[str, str]]:
    """Parse the plugin table: | **id** tag | one-liner | [file.zip](...) |"""
    out: dict[str, dict[str, str]] = {}
    row_re = re.compile(r"^\|(.+)\|$", flags=re.M)
    for m in row_re.finditer(block):
        cells = [c.strip() for c in m.group(1).split("|")]
        if len(cells) < 3:
            continue
        head = re.match(r"\*\*([a-z0-9][a-z0-9-]*)\*\*\s*(.*)$", cells[0])
        if not head:
            continue  # header row, separator row, or an unrelated table
        plugin_id = head.group(1)
        zip_m = re.search(r"\(([^)]*?([A-Za-z0-9._-]+\.zip))\)", cells[2])
        out[plugin_id] = {
            "tag": head.group(2).strip(),
            "summary": cells[1].strip(),
            "file": zip_m.group(2) if zip_m else "",
        }
    return out


def parse_sections(block: str) -> dict[str, dict]:
    """Parse '#### id — Title' sections into a lead paragraph plus bullets."""
    out: dict[str, dict] = {}
    heads = list(re.finditer(r"^#### +([a-z0-9][a-z0-9-]*)\s*[—–-]\s*(.+?) *$",
                             block, flags=re.M))
    for i, m in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(block)
        body = block[m.end():end]
        # Stop at the next section of any level (e.g. '### Installation').
        nxt = re.search(r"^#{1,3} ", body, flags=re.M)
        if nxt:
            body = body[:nxt.start()]

        lead_lines: list[str] = []
        points: list[dict] = []
        current: dict | None = None
        for raw in body.splitlines():
            line = raw.rstrip()
            bullet = re.match(r"^[-*] +(.*)$", line)
            if bullet:
                text = bullet.group(1).strip()
                # '**Label**: rest' with either an ASCII or full-width colon.
                lab = re.match(r"^\*\*(.+?)\*\*\s*[:：]\s*(.*)$", text)
                current = ({"label": lab.group(1).strip(), "text": lab.group(2).strip()}
                           if lab else {"label": None, "text": text})
                points.append(current)
            elif line.startswith("  ") and current and line.strip():
                current["text"] += " " + line.strip()  # bullet continuation
            elif line.strip():
                if not points:
                    lead_lines.append(line.strip())
            else:
                current = None

        out[m.group(1)] = {
            "title": m.group(2).strip(),
            "description": {"lead": " ".join(lead_lines).strip(), "points": points},
        }
    return out


def parse_prompts(block: str) -> dict[str, str]:
    """Parse '**id ...:**' headings followed by a fenced code block."""
    out: dict[str, str] = {}
    pat = re.compile(
        r"^\*\*([a-z0-9][a-z0-9-]*)[^*\n]*\*\*\s*[:：]?\s*$\n+```[a-z]*\n(.*?)^```",
        flags=re.M | re.S,
    )
    for m in pat.finditer(block):
        out[m.group(1)] = m.group(2).strip()
    return out


# --------------------------------------------------------------------------
# Assembly
# --------------------------------------------------------------------------

def git_last_modified(path: Path) -> str | None:
    try:
        ts = subprocess.run(
            ["git", "log", "-1", "--format=%cI", "--", str(path)],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        return ts or None
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def build(readme: Path, plugins_dir: Path, download_base: str) -> dict:
    md = readme.read_text(encoding="utf-8")
    blocks = split_languages(md)
    if "zh" not in blocks:
        fail("README.md: no language block found")

    parsed = {
        lang: {
            "catalog": parse_catalog(b),
            "sections": parse_sections(b),
            "prompts": parse_prompts(b),
        }
        for lang, b in blocks.items()
    }
    languages = sorted(parsed)

    zips = sorted(p for p in plugins_dir.glob("*.zip") if p.is_file())
    if not zips:
        fail(f"no .zip files found under {plugins_dir}/")

    base = download_base.rstrip("/") + "/"
    plugins: list[dict] = []
    problems: list[str] = []

    for zp in zips:
        plugin_id = zp.stem
        entry = {
            "id": plugin_id,
            "file": zp.name,
            "download_url": base + zp.name,
            "size": zp.stat().st_size,
            "updated_at": git_last_modified(zp),
        }

        for lang in languages:
            cat = parsed[lang]["catalog"].get(plugin_id, {})
            sec = parsed[lang]["sections"].get(plugin_id, {})
            desc = sec.get("description") or {"lead": "", "points": []}
            entry[lang] = {
                "name": sec.get("title", "") or cat.get("tag", ""),
                "tag": cat.get("tag", ""),
                "summary": cat.get("summary", ""),
                "description": desc,
                "prompt": parsed[lang]["prompts"].get(plugin_id, ""),
            }

            for field in REQUIRED_FIELDS:
                value = entry[lang][field]
                empty = (not value["lead"] and not value["points"]) \
                    if field == "description" else not value
                if empty:
                    problems.append(f"{plugin_id} [{lang}]: missing {field}")

        plugins.append(entry)

    # Copy referenced in README but with no zip on disk, or vice versa.
    for lang in languages:
        for plugin_id in parsed[lang]["catalog"]:
            if not (plugins_dir / f"{plugin_id}.zip").is_file():
                problems.append(f"{plugin_id} [{lang}]: in README catalog but no zip file")

    if problems:
        fail("README.md and plugins/ are out of sync:\n  - " + "\n  - ".join(problems))

    return {
        "schema": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "commit": os.environ.get("GITHUB_SHA", "")[:7] or None,
        "repository": os.environ.get("REPO_URL") or None,
        "languages": languages,
        "plugins": plugins,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--readme", default="README.md", type=Path)
    ap.add_argument("--plugins-dir", default="plugins", type=Path)
    ap.add_argument("--download-base", required=True,
                    help="URL prefix the zip files are served from")
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()

    data = build(args.readme, args.plugins_dir, args.download_base)
    args.out.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print(f"Wrote {args.out} ({args.out.stat().st_size} bytes)")
    for p in data["plugins"]:
        langs = " ".join(
            f"{lang}:{len(p[lang]['description']['points'])}pts/"
            f"{len(p[lang]['prompt'])}c" for lang in data["languages"]
        )
        print(f"  {p['id']:<20} {p['size']:>7}B  {langs}")


if __name__ == "__main__":
    main()
