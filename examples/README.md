# Examples

## Purpose

Use these examples to understand the skill's expected report contract and the recommended structure for responsive test reuse in popular frontend runners.

## Files

- `sample-report-input.json`: normalized report input used for demos and validation
- `playwright-responsive-example.ts`: Playwright example for parameterized viewport testing
- `cypress-responsive-example.cy.ts`: Cypress example for parameterized viewport testing
- `generated/`: sample rendered outputs generated from the normalized report input
  - includes embedded screenshot rendering for every executed viewport result in the sample matrix

## Notes

1. These snippets are examples, not drop-in production code.
2. Adapt selectors, URLs, auth, and fixture setup to the target repository.
3. Keep the repository-first rule: reuse and extend existing tests before creating new ones.
4. Include screenshot evidence for passed and failed executed results, not only for findings.
