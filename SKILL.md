---
name: responsive-testing
description: Use when an agent must plan, add, extend, or run responsive frontend testing across phones, tablets, laptops, desktops, or large screens, reuse existing tests before creating new ones, and generate a normalized responsive testing report in markdown, json, or html.
license: MIT
---

# Responsive Testing

## 1. Activate This Skill

1. Use this skill when the task involves responsive UI testing, breakpoint validation, viewport coverage, mobile or tablet regressions, layout verification, or responsive test reporting.
2. Use this skill when the agent must extend existing Playwright or Cypress coverage across multiple viewport sizes.
3. Use this skill when the task requires a reusable viewport strategy or a structured responsive test report.
4. Do not use this skill for API-only work, backend-only work, browser-compatibility-only work, or visual design tasks that do not require automated testing.

## 2. Confirm Preconditions

1. Identify the page, flow, or feature under test.
2. Identify the target environment:
   1. local dev server
   2. preview or staging deployment
   3. production-like environment approved for testing
3. Identify the existing frontend test framework from repository evidence before generating new tests.
4. Identify any required authentication, seed data, fixtures, feature flags, or environment variables.
5. Identify the requested report formats. Default to `json` and `markdown` when the user does not specify a format.
6. Identify the source of breakpoint truth:
   1. design system
   2. CSS framework config
   3. product requirement
   4. fallback matrix from this skill
7. If prerequisites are unclear, stop and inspect the repository before writing tests.

## 3. Search The Repository First

1. Search the repository for existing frontend tests before writing any new test.
2. Search for framework signals first:
   1. `playwright.config.*`
   2. `cypress.config.*`
   3. `package.json`
   4. `tests/`
   5. `e2e/`
   6. `spec/`
   7. `integration/`
3. Search for reusable test coverage next:
   1. feature name
   2. route name
   3. component name
   4. `mobile`
   5. `tablet`
   6. `viewport`
   7. `device`
4. Prefer reuse in this order:
   1. parameterize an existing high-value flow
   2. duplicate a narrowly scoped test and refactor it into a shared responsive pattern
   3. create one new focused responsive test only when no safe reusable base exists
5. Read [references/framework-detection.md](references/framework-detection.md) only when framework detection or test reuse selection is unclear.

## 4. Select The Execution Strategy

1. Reuse the repository's native test runner and conventions.
2. Prefer parameterized viewport coverage over duplicating full test files per device class.
3. Use existing device profiles, test fixtures, helpers, and artifact settings before introducing new ones.
4. Choose the smallest viewport matrix that covers the user request and product risk.
5. Start with the repository's official breakpoints when they exist.
6. Use the fallback matrix from [references/viewport-strategy.md](references/viewport-strategy.md) only when the repository does not define breakpoint coverage.
7. Expand coverage only when one of these conditions is true:
   1. layout behavior changes materially between breakpoints
   2. the page contains navigation, drawers, tables, grids, or dense forms
   3. the product contract explicitly names supported devices
   4. a bug report names a specific failing viewport class

## 5. Implement Or Extend Tests

1. Extend an existing test before creating a new test.
2. Preserve the original user journey and business assertion intent.
3. Add viewport parameters around that journey instead of cloning the entire flow for each size.
4. Add responsive assertions that verify behavior, not only appearance.
5. Prioritize these assertions:
   1. primary actions stay visible and reachable
   2. navigation remains usable in collapsed and expanded states
   3. dialogs, drawers, menus, and modals fit within the viewport
   4. critical content does not clip or overlap unexpectedly
   5. horizontal scrolling does not appear unless intentionally designed
   6. forms, tables, cards, and sticky elements remain usable
6. Capture at least one screenshot for every executed viewport result and preserve extra failure artifacts or traces when available.
7. Do not limit screenshots to failures only. Reports must show evidence for passed and failed viewport results alike.
8. Name viewport runs consistently with the viewport label.
9. Keep responsive-specific assertions isolated enough that failures can be diagnosed quickly.

## 6. Run The Smallest Useful Scope

1. Run only the selected responsive scope first.
2. Do not multiply the entire end-to-end suite across every viewport unless the user explicitly requests full-matrix execution.
3. Record these run details:
   1. framework
   2. command
   3. application area
   4. reused tests
   5. new tests
   6. viewport matrix
   7. artifact paths
   8. pass or fail status per viewport
4. If failures occur across all viewports, verify the base journey is stable before diagnosing responsive behavior.
5. Capture and record screenshot evidence for every executed result, not only failing ones.
6. If failures are viewport-specific, capture enough evidence to explain the regression without rerunning unrelated suites.

## 7. Produce The Normalized Report

1. Build one normalized JSON report before generating human-readable output.
2. Use the schema and rendering rules in [references/reporting-format.md](references/reporting-format.md) when the output contract matters.
3. Use `scripts/generate_responsive_report.py` to render `json`, `markdown`, and `html`.
4. Use [assets/report-template.md](assets/report-template.md) as the default Markdown template unless the repository intentionally overrides it.
5. Include these minimum report fields:
   1. schema version
   2. skill name
   3. generated timestamp
   4. framework
   5. target
   6. command
   7. reused tests
   8. new tests
   9. viewports
   10. results
   11. summary
   12. findings
   13. artifacts
   14. next actions
6. Ensure every executed result in `results` contains at least one screenshot artifact so the rendered report shows complete visual evidence across the full matrix.
7. When multiple scan types or multiple page scopes are produced separately, generate an overview report that links to the individual report bundles with `scripts/generate_responsive_overview.py`.

## 8. Follow The Output Contract

1. Return or save:
   1. changed or created test files
   2. normalized JSON report path
   3. rendered Markdown report path when requested
   4. rendered HTML report path when requested
2. Summarize:
   1. which tests were reused
   2. which tests were created
   3. which viewports were covered
   4. which viewports failed
   5. which defects were observed
   6. which follow-up actions are recommended
3. If the task only asked for analysis, do not fabricate execution results.
4. If tests could not be run, state what blocked execution and still provide the planned matrix plus reusable test candidates.

## 9. Respect Guardrails

1. Do not create a new frontend test stack when the repository already has one.
2. Do not generate brand-new tests before checking for reusable coverage.
3. Do not duplicate a full spec file per viewport when parameterization is practical.
4. Do not rely on screenshots alone as the responsive oracle.
5. Do not hardcode brittle pixel-perfect assertions unless the product contract explicitly requires them.
6. Do not claim realistic mobile behavior from width-only resizing when touch or device emulation materially changes behavior.
7. Do not mix responsive expansion with unrelated browser-matrix expansion unless the user explicitly requests both.
8. Do not persist runtime observations as shared memory automatically.

## 10. Use The Memory Model Deliberately

1. Treat the current investigation, grep results, selected viewport matrix, and temporary findings as runtime memory only.
2. Persist project-local knowledge only when the repository already has a local place for stable testing conventions, fixtures, or reusable report inputs.
3. Do not create cross-agent shared memory inside this skill.
4. If broader cross-repository memory is explicitly required, integrate with an external shared-memory skill instead of embedding that concern here.

## 11. Read Additional References Only When Needed

1. Read [references/framework-detection.md](references/framework-detection.md) when framework detection, reuse selection, or mixed-runner decisions are unclear.
2. Read [references/viewport-strategy.md](references/viewport-strategy.md) when you need a default matrix, assertion priorities, or device-emulation guidance.
3. Read [references/reporting-format.md](references/reporting-format.md) when you need the normalized report schema or rendering rules.
4. Read [references/evaluation.md](references/evaluation.md) when you need a repeatable quality gate for this skill or a repository using it.

## 12. Follow These Examples

1. Example: extend existing Playwright checkout coverage
   1. Input:
      ```text
      Add responsive coverage for checkout and produce markdown plus json output.
      ```
   2. Actions:
      1. Search for checkout Playwright specs.
      2. Reuse the checkout happy-path spec.
      3. Parameterize it across the selected viewport matrix.
      4. Run only the checkout responsive scope.
      5. Save `artifacts/responsive-report.json`.
      6. Render `artifacts/responsive-report.md`.
   3. Expected output:
      ```text
      Reused tests: tests/checkout.spec.ts
      New tests: none
      Reports: artifacts/responsive-report.json, artifacts/responsive-report.md
      ```

2. Example: extend existing Cypress dashboard coverage
   1. Input:
      ```text
      Test the dashboard on mobile, tablet, and desktop and produce json plus html output.
      ```
   2. Actions:
      1. Search for dashboard Cypress specs.
      2. Reuse the existing dashboard smoke flow.
      3. Iterate that flow across the requested viewport set.
      4. Capture screenshots for every executed viewport result.
      5. Save normalized JSON.
      6. Render HTML from the normalized data.
   3. Expected output:
      ```text
      Reused tests: cypress/e2e/dashboard.cy.ts
      Reports: artifacts/responsive-report.json, artifacts/responsive-report.html
      Failed viewports: tablet-portrait
      ```

3. Example: no reusable tests found
   1. Input:
      ```text
      Add responsive testing for the pricing page.
      ```
   2. Actions:
      1. Search the repo for pricing coverage.
      2. Confirm no reusable test exists.
      3. Create one focused responsive test for the main pricing journey.
      4. Run the minimum useful matrix.
      5. Generate normalized JSON and Markdown reports.
   3. Expected output:
      ```text
      Reused tests: none
      New tests: 1
      Reports: artifacts/responsive-report.json, artifacts/responsive-report.md
      ```

4. Example: analysis-only request
   1. Input:
      ```text
      Audit our current Playwright suite for responsive readiness and tell me what should be reused.
      ```
   2. Actions:
      1. Inspect the repository for reusable specs and helpers.
      2. Propose a viewport matrix and reuse candidates.
      3. Do not fabricate run output.
   3. Expected output:
      ```text
      Reuse candidates: 4
      New tests required: 1
      Execution: not run
      ```

## 13. Troubleshoot Predictably

1. Problem: framework is unclear
   1. Fix: inspect `package.json`, config files, and test directories.
   2. Fix: read [references/framework-detection.md](references/framework-detection.md).

2. Problem: no reusable tests are available
   1. Fix: create one focused happy-path responsive test for the highest-value journey.
   2. Fix: keep the new test parameterized by viewport.

3. Problem: all viewports fail immediately
   1. Fix: verify the base journey, environment, auth, and seed data at one stable desktop viewport.
   2. Fix: only resume responsive diagnosis after base stability is confirmed.

4. Problem: screenshot diffs are noisy
   1. Fix: prefer DOM, visibility, overflow, and interaction assertions for primary pass-fail logic.
   2. Fix: keep screenshots as evidence only.

5. Problem: report output is inconsistent
   1. Fix: normalize the raw results into one JSON schema first.
   2. Fix: regenerate final outputs with `scripts/generate_responsive_report.py`.

6. Problem: the task requires broader knowledge sharing
   1. Fix: keep current findings in runtime memory unless there is an explicit local persistence location.
   2. Fix: use an external shared-memory skill for cross-agent reuse instead of extending this skill's scope.

## 14. Complete The Task

1. Confirm the repository was searched for reusable tests first.
2. Confirm the framework was detected from repository evidence.
3. Confirm the viewport matrix was justified.
4. Confirm existing tests were reused or adapted where possible.
5. Confirm the report was generated in the requested format or explain why execution was blocked.
6. Confirm the final output identifies reused tests, new tests, failures, artifacts, and next actions.
