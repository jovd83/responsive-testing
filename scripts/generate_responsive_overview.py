#!/usr/bin/env python3
"""
Generate an overview report that links to and summarizes multiple responsive audit reports.
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import os
import re
from pathlib import Path
from typing import Any


IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}
SCAN_TYPE_ORDER = {"shallow": 0, "deep": 1, "edge": 2, "other": 3}
THUMBNAIL_LIMIT = 3


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate an overview report from multiple responsive report JSON files."
    )
    parser.add_argument(
        "--inputs",
        nargs="+",
        required=True,
        help="Input responsive report JSON files.",
    )
    parser.add_argument("--output-dir", required=True, help="Directory for the overview outputs.")
    parser.add_argument(
        "--basename",
        default="responsive-overview",
        help="Base filename for generated overview files.",
    )
    parser.add_argument(
        "--title",
        default="Responsive Testing Overview",
        help="Title for the generated overview report.",
    )
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=True)
        handle.write("\n")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def to_web_path(path: str) -> str:
    return path.replace("\\", "/")


def relpath(from_dir: Path, target: Path) -> str:
    return to_web_path(os.path.relpath(target.resolve(), start=from_dir.resolve()))


def infer_scan_type(data: dict[str, Any], path: Path) -> str:
    stem = path.stem.lower()
    parent_name = path.parent.name.lower()
    if "edge" in parent_name or "edge-responsive-audit" in stem or stem.endswith("-edge-audit"):
        return "edge"
    if "deep" in parent_name or "deep-responsive-audit" in stem or stem.endswith("-deep-audit"):
        return "deep"
    if "shallow" in parent_name or stem.endswith("responsive-audit"):
        return "shallow"

    haystack = " ".join(
        [
            stem,
            str(data.get("command", "")),
            " ".join(str(item) for item in data.get("new_tests", [])),
        ]
    ).lower()
    if "edge-case" in haystack or "edge case" in haystack:
        return "edge"
    if re.search(r"\bdeep\b", haystack):
        return "deep"
    if re.search(r"\bshallow\b", haystack) or re.search(r"\bsmoke\b", haystack):
        return "shallow"
    return "other"


def infer_label(scan_type: str, target: str, path: Path) -> str:
    if scan_type == "shallow":
        return "Shallow"
    if scan_type == "deep":
        return "Deep"
    if scan_type == "edge":
        return "Edge"
    stem = path.stem.replace("-", " ").strip()
    if target and target != "unspecified":
        return f"{target} | {stem.title()}"
    return stem.title()


def pick_page_label(target: str) -> str:
    return target if target and target != "unspecified" else "unspecified"


def collect_screenshot_entries(output_dir: Path, report_dir: Path, data: dict[str, Any]) -> list[dict[str, str]]:
    screenshots: list[dict[str, str]] = []
    for artifact in data.get("artifacts", []):
        artifact_path = report_dir / artifact
        if artifact_path.suffix.lower() not in IMAGE_SUFFIXES:
            continue
        screenshots.append(
            {
                "label": artifact_path.name,
                "path": relpath(output_dir, artifact_path),
            }
        )
    return screenshots


def resolve_rendered_report_path(report_dir: Path, json_path: Path, suffix: str) -> Path:
    same_stem = json_path.with_suffix(suffix)
    if same_stem.exists():
        return same_stem

    candidates = sorted(
        (candidate for candidate in report_dir.glob(f"*{suffix}") if candidate.is_file()),
        key=lambda candidate: candidate.stat().st_mtime,
        reverse=True,
    )
    if candidates:
        return candidates[0]
    return same_stem


def build_report_entry(output_dir: Path, json_path: Path) -> dict[str, Any]:
    data = load_json(json_path)
    report_dir = json_path.parent
    stem = json_path.stem
    summary = data.get("summary", {})
    target = str(data.get("target", "unspecified"))
    scan_type = infer_scan_type(data, json_path)
    screenshots = collect_screenshot_entries(output_dir, report_dir, data)
    markdown_path = resolve_rendered_report_path(report_dir, json_path, ".md")
    html_path = resolve_rendered_report_path(report_dir, json_path, ".html")
    return {
        "label": infer_label(scan_type, target, json_path),
        "page_label": pick_page_label(target),
        "target": target,
        "framework": data.get("framework", "unknown"),
        "command": data.get("command", "unspecified"),
        "generated_at": data.get("generated_at", ""),
        "scan_type": scan_type,
        "total_results": summary.get("total_results", 0),
        "passed": summary.get("passed", 0),
        "failed": summary.get("failed", 0),
        "skipped": summary.get("skipped", 0),
        "viewports_tested": summary.get("viewports_tested", 0),
        "findings_count": len(data.get("findings", [])),
        "artifacts_count": len(data.get("artifacts", [])),
        "notes": data.get("next_actions", []),
        "json_link": relpath(output_dir, json_path),
        "md_link": relpath(output_dir, markdown_path),
        "html_link": relpath(output_dir, html_path),
        "screenshots": screenshots,
        "thumbnail_screenshots": screenshots[:THUMBNAIL_LIMIT],
    }


def build_overview_payload(title: str, entries: list[dict[str, Any]]) -> dict[str, Any]:
    ordered_entries = sorted(
        entries,
        key=lambda entry: (
            entry["page_label"],
            SCAN_TYPE_ORDER.get(entry["scan_type"], SCAN_TYPE_ORDER["other"]),
            entry["label"],
        ),
    )
    unique_targets = sorted({entry["target"] for entry in ordered_entries if entry["target"]})
    unique_scan_types = list(dict.fromkeys(entry["scan_type"] for entry in ordered_entries))
    return {
        "schema_version": "1.1",
        "skill": "responsive-testing",
        "report_type": "overview",
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "title": title,
        "total_reports": len(ordered_entries),
        "targets": unique_targets,
        "scan_types": unique_scan_types,
        "summary": {
            "total_results": sum(entry["total_results"] for entry in ordered_entries),
            "passed": sum(entry["passed"] for entry in ordered_entries),
            "failed": sum(entry["failed"] for entry in ordered_entries),
            "skipped": sum(entry["skipped"] for entry in ordered_entries),
            "viewports_tested": sum(entry["viewports_tested"] for entry in ordered_entries),
            "reports_with_findings": sum(1 for entry in ordered_entries if entry["findings_count"] > 0),
            "targets_covered": len(unique_targets),
            "screenshot_artifacts": sum(len(entry["screenshots"]) for entry in ordered_entries),
        },
        "reports": ordered_entries,
    }


def render_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    scan_types = ", ".join(payload["scan_types"]) if payload["scan_types"] else "none"
    targets = payload["targets"]
    lines = [
        f"# {payload['title']}",
        "",
        "## Summary",
        "",
        f"- Generated at: {payload['generated_at']}",
        f"- Total reports: {payload['total_reports']}",
        f"- Targets covered: {summary['targets_covered']}",
        f"- Scan types: {scan_types}",
        f"- Total results: {summary['total_results']}",
        f"- Passed: {summary['passed']}",
        f"- Failed: {summary['failed']}",
        f"- Skipped: {summary['skipped']}",
        f"- Viewports tested across scans: {summary['viewports_tested']}",
        f"- Reports with findings: {summary['reports_with_findings']}",
        f"- Screenshot artifacts: {summary['screenshot_artifacts']}",
        "",
        "## Targets",
        "",
    ]

    if targets:
        lines.extend(f"- {target}" for target in targets)
    else:
        lines.append("- None")

    lines.extend(["", "## Report Links", ""])

    for entry in payload["reports"]:
        lines.extend(
            [
                f"### {entry['label']}",
                "",
                f"- Page: {entry['page_label']}",
                f"- Scan type: {entry['scan_type']}",
                f"- Generated at: {entry['generated_at'] or 'unspecified'}",
                f"- Framework: {entry['framework']}",
                f"- Results: {entry['passed']} passed, {entry['failed']} failed, {entry['skipped']} skipped",
                f"- Viewports tested: {entry['viewports_tested']}",
                f"- Findings: {entry['findings_count']}",
                f"- Screenshot artifacts: {len(entry['screenshots'])}",
                f"- Markdown: [{Path(entry['md_link']).name}]({entry['md_link']})",
                f"- HTML: [{Path(entry['html_link']).name}]({entry['html_link']})",
                f"- JSON: [{Path(entry['json_link']).name}]({entry['json_link']})",
                "",
            ]
        )
        if entry["thumbnail_screenshots"]:
            lines.append("Screenshot preview:")
            for screenshot in entry["thumbnail_screenshots"]:
                lines.append(
                    f"<a href=\"{screenshot['path']}\"><img src=\"{screenshot['path']}\" alt=\"{html.escape(screenshot['label'])}\" width=\"240\"></a>"
                )
            lines.append("")

    lines.extend(["## Concatenated Summary", ""])
    for entry in payload["reports"]:
        lines.extend(
            [
                f"### {entry['label']}",
                "",
                f"- Command: {entry['command']}",
                f"- Results: {entry['total_results']}",
                f"- Findings: {entry['findings_count']}",
            ]
        )
        if entry["notes"]:
            notes_text = " | ".join(str(note) for note in entry["notes"])
            lines.append(f"- Next actions: {notes_text}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def render_html(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    targets_markup = "".join(
        f"<li>{html.escape(target)}</li>" for target in payload["targets"]
    ) or "<li>None</li>"

    rows = []
    cards = []
    for entry in payload["reports"]:
        rows.append(
            "<tr>"
            f"<td>{html.escape(entry['label'])}</td>"
            f"<td>{html.escape(entry['page_label'])}</td>"
            f"<td>{html.escape(entry['scan_type'])}</td>"
            f"<td>{html.escape(entry['framework'])}</td>"
            f"<td>{entry['passed']}/{entry['total_results']}</td>"
            f"<td>{entry['findings_count']}</td>"
            f"<td><a href=\"{html.escape(entry['md_link'])}\">Markdown</a> | <a href=\"{html.escape(entry['html_link'])}\">HTML</a> | <a href=\"{html.escape(entry['json_link'])}\">JSON</a></td>"
            "</tr>"
        )

        preview_markup = "<p>No screenshots embedded for this report.</p>"
        if entry["thumbnail_screenshots"]:
            preview_markup = "<div class=\"screenshots-grid\">{items}</div>".format(
                items="".join(
                    (
                        "<figure class=\"screenshot-card\">"
                        f"<a href=\"{html.escape(screenshot['path'])}\">"
                        f"<img src=\"{html.escape(screenshot['path'])}\" alt=\"{html.escape(screenshot['label'])}\">"
                        "</a>"
                        f"<figcaption>{html.escape(screenshot['label'])}</figcaption>"
                        "</figure>"
                    )
                    for screenshot in entry["thumbnail_screenshots"]
                )
            )

        notes_markup = "".join(
            f"<li>{html.escape(str(note))}</li>" for note in entry["notes"]
        ) or "<li>None</li>"

        cards.append(
            "<section class=\"report-card\">"
            f"<h3>{html.escape(entry['label'])}</h3>"
            "<ul>"
            f"<li>Page: {html.escape(entry['page_label'])}</li>"
            f"<li>Scan type: {html.escape(entry['scan_type'])}</li>"
            f"<li>Generated at: {html.escape(entry['generated_at'] or 'unspecified')}</li>"
            f"<li>Command: <code>{html.escape(entry['command'])}</code></li>"
            f"<li>Results: {entry['passed']} passed, {entry['failed']} failed, {entry['skipped']} skipped</li>"
            f"<li>Viewports tested: {entry['viewports_tested']}</li>"
            f"<li>Screenshot artifacts: {len(entry['screenshots'])}</li>"
            "</ul>"
            f"{preview_markup}"
            "<h4>Next Actions</h4>"
            f"<ul>{notes_markup}</ul>"
            "</section>"
        )

    scan_types = ", ".join(payload["scan_types"]) if payload["scan_types"] else "none"
    sections = [
        "<!doctype html>",
        "<html lang=\"en\">",
        "<head>",
        "  <meta charset=\"utf-8\">",
        "  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">",
        f"  <title>{html.escape(payload['title'])}</title>",
        "  <style>",
        "    body { font-family: Arial, sans-serif; margin: 2rem; line-height: 1.5; color: #1f2937; background: #f8fafc; }",
        "    main { max-width: 1200px; margin: 0 auto; background: #ffffff; padding: 2rem; border-radius: 12px; box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08); }",
        "    h1, h2, h3, h4 { color: #0f172a; }",
        "    table { width: 100%; border-collapse: collapse; margin-bottom: 1.5rem; }",
        "    th, td { border: 1px solid #dbe2ea; padding: 0.75rem; vertical-align: top; text-align: left; }",
        "    th { background: #e2e8f0; }",
        "    code { background: #eef2ff; padding: 0.1rem 0.3rem; border-radius: 4px; }",
        "    ul { padding-left: 1.25rem; }",
        "    .report-card { border: 1px solid #dbe2ea; border-radius: 12px; padding: 1rem; margin-bottom: 1.5rem; background: #f8fafc; }",
        "    .screenshots-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1rem; margin-bottom: 1rem; }",
        "    .screenshot-card { margin: 0; border: 1px solid #dbe2ea; border-radius: 10px; padding: 0.75rem; background: #ffffff; }",
        "    .screenshot-card a { display: block; text-decoration: none; }",
        "    .screenshot-card img { width: 100%; max-height: 180px; object-fit: contain; border-radius: 8px; border: 1px solid #cbd5e1; background: #ffffff; }",
        "    .screenshot-card figcaption { margin-top: 0.5rem; font-size: 0.9rem; word-break: break-word; }",
        "  </style>",
        "</head>",
        "<body>",
        "  <main>",
        f"    <h1>{html.escape(payload['title'])}</h1>",
        "    <h2>Summary</h2>",
        "    <ul>",
        f"      <li>Generated at: {html.escape(payload['generated_at'])}</li>",
        f"      <li>Total reports: {payload['total_reports']}</li>",
        f"      <li>Targets covered: {summary['targets_covered']}</li>",
        f"      <li>Scan types: {html.escape(scan_types)}</li>",
        f"      <li>Total results: {summary['total_results']}</li>",
        f"      <li>Passed: {summary['passed']}</li>",
        f"      <li>Failed: {summary['failed']}</li>",
        f"      <li>Skipped: {summary['skipped']}</li>",
        f"      <li>Viewports tested across scans: {summary['viewports_tested']}</li>",
        f"      <li>Reports with findings: {summary['reports_with_findings']}</li>",
        f"      <li>Screenshot artifacts: {summary['screenshot_artifacts']}</li>",
        "    </ul>",
        "    <h2>Targets</h2>",
        f"    <ul>{targets_markup}</ul>",
        "    <h2>Report Links</h2>",
        "    <table>",
        "      <thead><tr><th>Report</th><th>Page</th><th>Scan type</th><th>Framework</th><th>Passes</th><th>Findings</th><th>Links</th></tr></thead>",
        f"      <tbody>{''.join(rows)}</tbody>",
        "    </table>",
        "    <h2>Concatenated Summary</h2>",
        *cards,
        "  </main>",
        "</body>",
        "</html>",
    ]
    return "\n".join(sections) + "\n"


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir)
    inputs = [Path(item) for item in args.inputs]
    entries = [build_report_entry(output_dir, path) for path in inputs]
    payload = build_overview_payload(args.title, entries)

    output_dir.mkdir(parents=True, exist_ok=True)
    write_json(output_dir / f"{args.basename}.json", payload)
    write_text(output_dir / f"{args.basename}.md", render_markdown(payload))
    write_text(output_dir / f"{args.basename}.html", render_html(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
