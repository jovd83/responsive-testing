# Changelog

All notable changes to this project will be documented in this file.

## [1.5.0] - 2026-03-28

Author: `jovd:83`

### Changed

- Updated the report contract so every executed viewport result must carry screenshot evidence instead of reserving screenshots for failures only.
- Changed `scripts/generate_responsive_report.py` to prioritize per-result screenshots in the rendered screenshot section and enforce all-result screenshot coverage in strict mode.
- Refreshed the skill and repository docs to make full-matrix screenshot evidence explicit and bumped the documented repository version to `1.5.0`.

## [1.4.0] - 2026-03-28

Author: `jovd:83`

### Changed

- Upgraded `scripts/generate_responsive_overview.py` to classify scan types more cleanly, sort reports deterministically, and emit web-safe relative links for Markdown and HTML navigation.
- Enhanced overview bundles with target coverage summaries, richer child-report metadata, and embedded screenshot thumbnails for each linked report.
- Updated repository documentation to describe the stronger overview-report behavior and bumped the documented repository version to `1.4.0`.

## [1.3.0] - 2026-03-28

Author: `jovd:83`

### Added

- `schemas/responsive-report.schema.json` for machine-readable contract validation.
- Playwright and Cypress example snippets in `examples/`.
- GitHub Actions validation and release workflows in `.github/workflows/`.
- Generated sample report outputs and a visual preview screenshot for GitHub presentation.
- Static README badges for version, license, standard alignment, and report formats.
- Embedded screenshot rendering in generated Markdown and HTML reports when image artifacts are present.
- `scripts/generate_responsive_overview.py` for concatenated overview reports that link to shallow, deep, and edge-case bundles.

### Changed

- Updated repository docs to surface schema validation, examples, release automation, and preview assets.
- Bumped the documented repository version to `1.3.0`.

## [1.1.0] - 2026-03-28

Author: `jovd:83`

### Changed

- Rewrote `SKILL.md` into a stricter, enterprise-grade workflow with clearer activation rules, guardrails, memory boundaries, and output contracts.
- Upgraded the skill description and added explicit `license` frontmatter for better Agent Skills compliance.
- Expanded the repository README into a GitHub-ready package overview with responsibilities, boundaries, installation notes, validation guidance, and optional integrations.
- Strengthened report generation architecture with schema versioning, stricter validation, richer markdown and HTML outputs, and better template handling.

### Added

- `CONTRIBUTING.md` with contribution and release guidance.
- `agents/openai.yaml` for UI-facing metadata.
- `references/evaluation.md` with a repeatable evaluation strategy.
- `assets/report-template.html` for richer HTML rendering.
- `examples/sample-report-input.json` for report demo and contract testing.
- `.gitignore` to exclude generated artifacts and Python cache files.

### Removed

- Accidental Python cache artifacts from version control scope.

## [1.0.0] - 2026-03-28

Author: `jovd:83`

### Added

- Initial release of the `responsive-testing` agent skill.
- Core `SKILL.md` instructions for viewport-based responsive test workflows.
- Reference docs for framework detection, viewport strategy, and reporting format.
- Deterministic Python report generator for `json`, `md`, and `html` outputs.
- Default Markdown report template asset.
- Repository metadata files: `README.md`, `LICENSE`, and `CHANGELOG.md`.
