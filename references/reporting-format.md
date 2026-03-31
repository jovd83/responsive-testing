# Reporting Format

## 1. Normalized JSON Schema

1. Build one JSON object with these top-level fields:
   1. `schema_version`
   2. `skill`
   3. `generated_at`
   4. `framework`
   5. `target`
   6. `command`
   7. `reused_tests`
   8. `new_tests`
   9. `viewports`
   10. `results`
   11. `summary`
   12. `findings`
   13. `artifacts`
   14. `next_actions`

## 2. Required Scalar Fields

1. `schema_version`, `skill`, `generated_at`, `framework`, `target`, and `command` must be non-empty strings.
2. Use schema version `1.0` for the current repository contract.

## 3. Viewport Object

1. Represent each viewport as:
   1. `name`
   2. `width`
   3. `height`
   4. `category`
2. Use integers for `width` and `height`.

## 4. Result Object

1. Represent each result as:
   1. `test`
   2. `viewport`
   3. `status`
   4. `duration_ms`
   5. `notes`
   6. `artifacts`
2. Restrict `status` to:
   1. `passed`
   2. `failed`
   3. `skipped`
3. For every executed result with status `passed` or `failed`, include at least one image artifact in `artifacts` so the report can render screenshot evidence for the full audited matrix.

## 5. Summary Object

1. Include:
   1. `total_results`
   2. `passed`
   3. `failed`
   4. `skipped`
   5. `viewports_tested`

## 6. Rendering Rules

1. Render Markdown for human review.
2. Render HTML when the user wants browser-friendly sharing.
3. Keep JSON as the source of truth.
4. Sort results by viewport name and then test name for deterministic output.
5. Render reused tests and new tests explicitly, not only as counts.

## 7. Required Findings Format

1. Write each finding with:
   1. `severity`
   2. `viewport`
   3. `area`
   4. `message`
   5. `artifact`
2. When `artifact` points to an image file, render that image as a screenshot in Markdown and HTML reports.

## 8. Required Next Actions Format

1. Write each next action as one imperative sentence.

## 9. Validation Rule

1. Validate the report before rendering outputs when strict mode is enabled.
2. Fail fast on missing required fields, invalid statuses, or malformed viewport objects.
3. Use [schemas/responsive-report.schema.json](../schemas/responsive-report.schema.json) when machine-readable schema validation is required.

## 10. Screenshot Rule

1. Treat image artifacts such as `.png`, `.jpg`, `.jpeg`, `.gif`, `.webp`, and `.svg` as embeddable screenshots.
2. Prefer relative image paths when the report and screenshots are stored together.
3. Keep screenshots discoverable through both the dedicated screenshot section and the artifact listings.
4. Do not limit screenshots to findings or failures. The screenshot section should reflect all executed viewport results.

## 11. Multi-Report Overview Rule

1. When more than one scan type or more than one page scope is reported separately, generate one overview report that links to the individual bundles.
2. Use `scripts/generate_responsive_overview.py` to aggregate the individual JSON reports into one overview `json`, `md`, and `html` bundle.
3. Keep the individual reports intact and treat the overview as a navigation and summary layer, not a replacement for the source bundles.
4. Normalize overview links to web-safe relative paths so the Markdown and HTML bundle can be opened directly from disk.
5. Include scan type labels, target or page labels, and screenshot thumbnail previews for each child report when image artifacts are present.
