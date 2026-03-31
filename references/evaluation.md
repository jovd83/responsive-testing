# Evaluation Strategy

## 1. Purpose

Use this guide to evaluate whether the skill produces reliable, reusable, and appropriately scoped responsive testing work.

## 2. Positive Trigger Cases

1. Add responsive coverage for checkout and output a Markdown report.
2. Audit our Cypress suite for tablet and desktop responsiveness.
3. Reuse our Playwright nav tests across a mobile, tablet, and desktop matrix.
4. Generate an HTML report from normalized responsive test results.

## 3. Negative Trigger Cases

1. Write API tests for the payments service.
2. Make the landing page look more modern.
3. Compare Chrome and Firefox rendering differences.
4. Design a new mobile navigation pattern.

## 4. Quality Checks

1. The agent searches the repository before creating new tests.
2. The agent detects the existing test framework from repository evidence.
3. The agent proposes a viewport matrix that matches the task scope.
4. The agent reuses or extends existing tests whenever reasonable.
5. The agent produces a normalized report with stable structure.
6. The agent does not fabricate execution results when tests were not run.

## 5. Failure Signals

1. The agent creates new tests without first looking for reusable ones.
2. The agent duplicates one spec per viewport instead of parameterizing.
3. The agent treats screenshots as the only responsive assertion strategy.
4. The agent expands to a full browser-by-viewport matrix without request or justification.
5. The agent stores ephemeral findings as persistent memory without explicit instruction.

## 6. Suggested Validation Loop

1. Run a repository audit task.
2. Run an extension task for an existing Playwright suite.
3. Run an extension task for an existing Cypress suite.
4. Run an analysis-only task.
5. Run report generation against `examples/sample-report-input.json`.
6. Compare outputs against the quality checks above.
