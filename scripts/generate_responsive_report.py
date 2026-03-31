#!/usr/bin/env python3
"""
Generate normalized responsive testing reports from a JSON input file.

Supported output formats:
- json
- md
- html
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
from pathlib import Path
from string import Template
from typing import Any


SKILL_NAME = "responsive-testing"
SCHEMA_VERSION = "1.0"
VALID_STATUSES = {"passed", "failed", "skipped"}
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
DEFAULT_MARKDOWN_TEMPLATE_PATH = REPO_ROOT / "assets" / "report-template.md"
DEFAULT_HTML_TEMPLATE_PATH = REPO_ROOT / "assets" / "report-template.html"


DEFAULT_MARKDOWN_TEMPLATE = """# Responsive Testing Report

## Summary

- Schema version: ${schema_version}
- Generated at: ${generated_at}
- Framework: ${framework}
- Target: ${target}
- Command: ${command}
- Reused tests: ${reused_tests_count}
- New tests: ${new_tests_count}
- Total results: ${total_results}
- Passed: ${passed}
- Failed: ${failed}
- Skipped: ${skipped}

## Reused Tests

${reused_tests_block}

## New Tests

${new_tests_block}

## Viewports

${viewports_block}

## Results

${results_block}

## Findings

${findings_block}

## Screenshots

${screenshots_block}

## Artifacts

${artifacts_block}

## Next Actions

${next_actions_block}
"""


DEFAULT_HTML_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>${title}</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 2rem; line-height: 1.5; color: #1f2937; background: #f8fafc; }
    main { max-width: 1100px; margin: 0 auto; background: #ffffff; padding: 2rem; border-radius: 12px; box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08); }
    h1, h2 { color: #0f172a; }
    table { width: 100%; border-collapse: collapse; margin-bottom: 1.5rem; }
    th, td { border: 1px solid #dbe2ea; padding: 0.75rem; vertical-align: top; text-align: left; }
    th { background: #e2e8f0; }
    code { background: #eef2ff; padding: 0.1rem 0.3rem; border-radius: 4px; }
    .screenshots-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1rem; margin-bottom: 1.5rem; }
    .screenshot-card { border: 1px solid #dbe2ea; border-radius: 10px; padding: 0.75rem; background: #f8fafc; }
    .screenshot-card a { display: block; text-decoration: none; }
    .screenshot-card img { width: 100%; max-height: 220px; object-fit: contain; border-radius: 8px; border: 1px solid #cbd5e1; background: #ffffff; }
    .screenshot-card h3 { margin-top: 0; margin-bottom: 0.5rem; font-size: 1rem; }
    ul { padding-left: 1.25rem; }
  </style>
</head>
<body>
  <main>
    <h1>${title}</h1>
    ${body}
  </main>
</body>
</html>
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate responsive testing reports.")
    parser.add_argument("--input", required=True, help="Path to input JSON file.")
    parser.add_argument(
        "--format",
        nargs="+",
        choices=["json", "md", "html"],
        default=["json", "md"],
        help="Output formats to generate.",
    )
    parser.add_argument("--output-dir", required=True, help="Directory for generated files.")
    parser.add_argument(
        "--template",
        help="Optional Markdown template path. Defaults to assets/report-template.md.",
    )
    parser.add_argument(
        "--html-template",
        help="Optional HTML template path. Defaults to assets/report-template.html.",
    )
    parser.add_argument(
        "--basename",
        default="responsive-report",
        help="Base filename for generated report files.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail when required fields are missing or invalid.",
    )
    parser.add_argument(
        "--title",
        default="Responsive Testing Report",
        help="Title for the generated HTML report.",
    )
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def dump_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=True)
        handle.write("\n")


def read_template(path: Path | None, fallback: str) -> Template:
    if path is None:
        return Template(fallback)
    return Template(path.read_text(encoding="utf-8"))


def ensure_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def ensure_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def ensure_defaults(data: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(data)
    normalized.setdefault("schema_version", SCHEMA_VERSION)
    normalized.setdefault("skill", SKILL_NAME)
    normalized.setdefault("generated_at", dt.datetime.now(dt.timezone.utc).isoformat())
    normalized.setdefault("framework", "unknown")
    normalized.setdefault("target", "unspecified")
    normalized.setdefault("command", "unspecified")
    normalized["reused_tests"] = ensure_list(normalized.get("reused_tests"))
    normalized["new_tests"] = ensure_list(normalized.get("new_tests"))
    normalized["viewports"] = ensure_list(normalized.get("viewports"))
    normalized["results"] = ensure_list(normalized.get("results"))
    normalized["summary"] = ensure_dict(normalized.get("summary"))
    normalized["findings"] = ensure_list(normalized.get("findings"))
    normalized["artifacts"] = ensure_list(normalized.get("artifacts"))
    normalized["next_actions"] = ensure_list(normalized.get("next_actions"))

    summary = normalized["summary"]
    results = normalized["results"]
    summary.setdefault("total_results", len(results))
    summary.setdefault("passed", sum(1 for item in results if item.get("status") == "passed"))
    summary.setdefault("failed", sum(1 for item in results if item.get("status") == "failed"))
    summary.setdefault("skipped", sum(1 for item in results if item.get("status") == "skipped"))
    summary.setdefault("viewports_tested", len(normalized["viewports"]))
    for result in normalized["results"]:
        for artifact in ensure_list(result.get("artifacts")):
            if artifact not in normalized["artifacts"]:
                normalized["artifacts"].append(artifact)
    for finding in normalized["findings"]:
        artifact = str(finding.get("artifact", "")).strip()
        if artifact and artifact not in normalized["artifacts"]:
            normalized["artifacts"].append(artifact)
    normalized["results"] = sorted(
        results,
        key=lambda item: (str(item.get("viewport", "")), str(item.get("test", ""))),
    )
    return normalized


def validate_report(data: dict[str, Any], strict: bool) -> None:
    errors: list[str] = []
    required_scalars = [
        "schema_version",
        "skill",
        "generated_at",
        "framework",
        "target",
        "command",
    ]

    for field in required_scalars:
        value = data.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"Field '{field}' must be a non-empty string.")

    for viewport in data.get("viewports", []):
        if not isinstance(viewport, dict):
            errors.append("Each viewport must be an object.")
            continue
        for key in ("name", "category"):
            if not isinstance(viewport.get(key), str) or not viewport.get(key):
                errors.append(f"Viewport field '{key}' must be a non-empty string.")
        for key in ("width", "height"):
            if not isinstance(viewport.get(key), int):
                errors.append(f"Viewport field '{key}' must be an integer.")

    for result in data.get("results", []):
        if not isinstance(result, dict):
            errors.append("Each result must be an object.")
            continue
        if result.get("status") not in VALID_STATUSES:
            errors.append(
                f"Result status '{result.get('status')}' must be one of {sorted(VALID_STATUSES)}."
            )
        for key in ("test", "viewport"):
            if not isinstance(result.get(key), str) or not result.get(key):
                errors.append(f"Result field '{key}' must be a non-empty string.")
        duration = result.get("duration_ms")
        if duration is not None and not isinstance(duration, int):
            errors.append("Result field 'duration_ms' must be an integer when present.")
        if not isinstance(result.get("artifacts", []), list):
            errors.append("Result field 'artifacts' must be a list.")
        if strict and result.get("status") != "skipped":
            image_artifacts = [
                str(item).strip() for item in result.get("artifacts", []) if is_image_path(str(item).strip())
            ]
            if not image_artifacts:
                errors.append(
                    "Each executed result must include at least one image artifact for screenshot evidence."
                )

    for finding in data.get("findings", []):
        if not isinstance(finding, dict):
            errors.append("Each finding must be an object.")
            continue
        for key in ("severity", "viewport", "area", "message"):
            if not isinstance(finding.get(key), str) or not finding.get(key):
                errors.append(f"Finding field '{key}' must be a non-empty string.")

    if strict and errors:
        raise ValueError("Report validation failed:\n- " + "\n- ".join(errors))


def format_string_list(items: list[str]) -> str:
    if not items:
        return "- None"
    return "\n".join(f"- {item}" for item in items)


def format_viewports(viewports: list[dict[str, Any]]) -> str:
    if not viewports:
        return "- None"
    lines = []
    for viewport in viewports:
        lines.append(
            "- {name}: {width}x{height} ({category})".format(
                name=viewport.get("name", "unknown"),
                width=viewport.get("width", "?"),
                height=viewport.get("height", "?"),
                category=viewport.get("category", "unspecified"),
            )
        )
    return "\n".join(lines)


def format_results(results: list[dict[str, Any]]) -> str:
    if not results:
        return "- None"
    lines = []
    for result in results:
        artifacts = ", ".join(result.get("artifacts", [])) or "none"
        notes = result.get("notes", "")
        suffix = f" | notes: {notes}" if notes else ""
        lines.append(
            "- [{status}] {test} @ {viewport} | duration_ms: {duration} | artifacts: {artifacts}{suffix}".format(
                status=result.get("status", "unknown"),
                test=result.get("test", "unknown"),
                viewport=result.get("viewport", "unknown"),
                duration=result.get("duration_ms", "?"),
                artifacts=artifacts,
                suffix=suffix,
            )
        )
    return "\n".join(lines)


def format_findings(findings: list[dict[str, Any]]) -> str:
    if not findings:
        return "- None"
    lines = []
    for finding in findings:
        artifact = finding.get("artifact", "none")
        lines.append(
            "- [{severity}] {viewport} | {area} | {message} | artifact: {artifact}".format(
                severity=finding.get("severity", "info"),
                viewport=finding.get("viewport", "unspecified"),
                area=finding.get("area", "unspecified"),
                message=finding.get("message", ""),
                artifact=artifact,
            )
        )
    return "\n".join(lines)


def is_image_path(path: str) -> bool:
    return Path(path).suffix.lower() in IMAGE_SUFFIXES


def collect_screenshots(data: dict[str, Any]) -> list[dict[str, str]]:
    screenshots: list[dict[str, str]] = []
    seen: set[str] = set()

    for result in data.get("results", []):
        for artifact_value in result.get("artifacts", []):
            artifact = str(artifact_value).strip()
            if artifact and is_image_path(artifact) and artifact not in seen:
                seen.add(artifact)
                screenshots.append(
                    {
                        "path": artifact,
                        "title": f"{result.get('viewport', 'unspecified')} - {result.get('test', 'unspecified')}",
                        "caption": str(result.get("notes", "")),
                    }
                )

    for finding in data.get("findings", []):
        artifact = str(finding.get("artifact", "")).strip()
        if artifact and is_image_path(artifact) and artifact not in seen:
            seen.add(artifact)
            screenshots.append(
                {
                    "path": artifact,
                    "title": f"{finding.get('viewport', 'unspecified')} - {finding.get('area', 'unspecified')}",
                    "caption": str(finding.get("message", "")),
                }
            )

    for artifact_value in data.get("artifacts", []):
        artifact = str(artifact_value).strip()
        if artifact and is_image_path(artifact) and artifact not in seen:
            seen.add(artifact)
            screenshots.append(
                {
                    "path": artifact,
                    "title": Path(artifact).name,
                    "caption": "",
                }
            )

    return screenshots


def format_screenshots_markdown(screenshots: list[dict[str, str]]) -> str:
    if not screenshots:
        return "- None"
    blocks = []
    for screenshot in screenshots:
        title = screenshot["title"]
        path = screenshot["path"]
        caption = screenshot["caption"]
        block = [
            f"### {title}",
            f"<a href=\"{path}\"><img src=\"{path}\" alt=\"{title}\" width=\"320\"></a>",
        ]
        if caption:
            block.append(caption)
        blocks.append("\n\n".join(block))
    return "\n\n".join(blocks)


def render_markdown(data: dict[str, Any], template: Template) -> str:
    summary = data["summary"]
    screenshots = collect_screenshots(data)
    payload = {
        "schema_version": data["schema_version"],
        "generated_at": data["generated_at"],
        "framework": data["framework"],
        "target": data["target"],
        "command": data["command"],
        "reused_tests_count": len(data["reused_tests"]),
        "new_tests_count": len(data["new_tests"]),
        "total_results": summary["total_results"],
        "passed": summary["passed"],
        "failed": summary["failed"],
        "skipped": summary["skipped"],
        "reused_tests_block": format_string_list(data["reused_tests"]),
        "new_tests_block": format_string_list(data["new_tests"]),
        "viewports_block": format_viewports(data["viewports"]),
        "results_block": format_results(data["results"]),
        "findings_block": format_findings(data["findings"]),
        "screenshots_block": format_screenshots_markdown(screenshots),
        "artifacts_block": format_string_list(data["artifacts"]),
        "next_actions_block": format_string_list(data["next_actions"]),
    }
    return template.safe_substitute(payload).rstrip() + "\n"


def build_html_list(items: list[str], code: bool = False) -> str:
    if not items:
        return "<ul><li>None</li></ul>"
    if code:
        rows = "".join(f"<li><code>{html.escape(item)}</code></li>" for item in items)
    else:
        rows = "".join(f"<li>{html.escape(item)}</li>" for item in items)
    return f"<ul>{rows}</ul>"


def build_html_table(headers: list[str], rows: list[list[str]]) -> str:
    head = "".join(f"<th>{html.escape(header)}</th>" for header in headers)
    body_rows = []
    for row in rows:
        cells = "".join(f"<td>{cell}</td>" for cell in row)
        body_rows.append(f"<tr>{cells}</tr>")
    return f"<table><thead><tr>{head}</tr></thead><tbody>{''.join(body_rows)}</tbody></table>"


def render_screenshots_html(screenshots: list[dict[str, str]]) -> str:
    if not screenshots:
        return "<p>None</p>"

    cards = []
    for screenshot in screenshots:
        title = html.escape(screenshot["title"])
        path = html.escape(screenshot["path"])
        caption = html.escape(screenshot["caption"])
        caption_html = f"<p>{caption}</p>" if caption else ""
        cards.append(
            "<div class=\"screenshot-card\">"
            f"<h3>{title}</h3>"
            f"<a href=\"{path}\"><img src=\"{path}\" alt=\"{title}\"></a>"
            f"{caption_html}"
            f"<p><code>{path}</code></p>"
            "</div>"
        )
    return f"<div class=\"screenshots-grid\">{''.join(cards)}</div>"


def render_html_body(data: dict[str, Any]) -> str:
    summary = data["summary"]
    screenshots = collect_screenshots(data)
    sections = [
        "<h2>Summary</h2>",
        build_html_table(
            ["Field", "Value"],
            [
                ["Schema version", html.escape(str(data["schema_version"]))],
                ["Generated at", html.escape(str(data["generated_at"]))],
                ["Framework", html.escape(str(data["framework"]))],
                ["Target", html.escape(str(data["target"]))],
                ["Command", f"<code>{html.escape(str(data['command']))}</code>"],
                ["Reused tests", html.escape(str(len(data["reused_tests"])))],
                ["New tests", html.escape(str(len(data["new_tests"])))],
                ["Total results", html.escape(str(summary["total_results"]))],
                ["Passed", html.escape(str(summary["passed"]))],
                ["Failed", html.escape(str(summary["failed"]))],
                ["Skipped", html.escape(str(summary["skipped"]))],
            ],
        ),
        "<h2>Reused Tests</h2>",
        build_html_list([str(item) for item in data["reused_tests"]], code=True),
        "<h2>New Tests</h2>",
        build_html_list([str(item) for item in data["new_tests"]], code=True),
    ]

    viewport_rows = [
        [
            html.escape(str(viewport.get("name", ""))),
            html.escape(str(viewport.get("width", ""))),
            html.escape(str(viewport.get("height", ""))),
            html.escape(str(viewport.get("category", ""))),
        ]
        for viewport in data["viewports"]
    ]
    sections.extend(
        [
            "<h2>Viewports</h2>",
            build_html_table(["Name", "Width", "Height", "Category"], viewport_rows)
            if viewport_rows
            else "<p>None</p>",
        ]
    )

    result_rows = [
        [
            html.escape(str(result.get("test", ""))),
            html.escape(str(result.get("viewport", ""))),
            html.escape(str(result.get("status", ""))),
            html.escape(str(result.get("duration_ms", ""))),
            html.escape(str(result.get("notes", ""))),
            "<br>".join(html.escape(str(path)) for path in result.get("artifacts", [])) or "None",
        ]
        for result in data["results"]
    ]
    sections.extend(
        [
            "<h2>Results</h2>",
            build_html_table(
                ["Test", "Viewport", "Status", "Duration ms", "Notes", "Artifacts"],
                result_rows,
            )
            if result_rows
            else "<p>None</p>",
        ]
    )

    finding_rows = [
        [
            html.escape(str(finding.get("severity", ""))),
            html.escape(str(finding.get("viewport", ""))),
            html.escape(str(finding.get("area", ""))),
            html.escape(str(finding.get("message", ""))),
            html.escape(str(finding.get("artifact", ""))),
        ]
        for finding in data["findings"]
    ]
    sections.extend(
        [
            "<h2>Findings</h2>",
            build_html_table(
                ["Severity", "Viewport", "Area", "Message", "Artifact"],
                finding_rows,
            )
            if finding_rows
            else "<p>None</p>",
            "<h2>Screenshots</h2>",
            render_screenshots_html(screenshots),
            "<h2>Artifacts</h2>",
            build_html_list([str(item) for item in data["artifacts"]], code=True),
            "<h2>Next Actions</h2>",
            build_html_list([str(item) for item in data["next_actions"]]),
        ]
    )
    return "\n".join(sections)


def render_html_report(data: dict[str, Any], template: Template, title: str) -> str:
    body = render_html_body(data)
    return template.safe_substitute(title=html.escape(title), body=body).rstrip() + "\n"


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def main() -> int:
    args = parse_args()
    input_path = Path(args.input)
    output_dir = Path(args.output_dir)
    markdown_template_path = Path(args.template) if args.template else (
        DEFAULT_MARKDOWN_TEMPLATE_PATH if DEFAULT_MARKDOWN_TEMPLATE_PATH.exists() else None
    )
    html_template_path = Path(args.html_template) if args.html_template else (
        DEFAULT_HTML_TEMPLATE_PATH if DEFAULT_HTML_TEMPLATE_PATH.exists() else None
    )

    normalized = ensure_defaults(load_json(input_path))
    validate_report(normalized, args.strict)
    output_dir.mkdir(parents=True, exist_ok=True)

    if "json" in args.format:
        dump_json(output_dir / f"{args.basename}.json", normalized)

    markdown_text = ""
    if "md" in args.format or "html" in args.format:
        markdown_template = read_template(markdown_template_path, DEFAULT_MARKDOWN_TEMPLATE)
        markdown_text = render_markdown(normalized, markdown_template)

    if "md" in args.format:
        write_text(output_dir / f"{args.basename}.md", markdown_text)

    if "html" in args.format:
        html_template = read_template(html_template_path, DEFAULT_HTML_TEMPLATE)
        html_report = render_html_report(normalized, html_template, args.title)
        write_text(output_dir / f"{args.basename}.html", html_report)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
