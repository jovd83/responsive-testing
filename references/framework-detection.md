# Framework Detection

## 1. Detect Playwright

1. Search for:
   1. `playwright.config.*`
   2. `@playwright/test`
   3. `test.describe(`
   4. `devices[`
   5. `projects: [`
2. Treat the repo as Playwright-first when these files or patterns exist.
3. Reuse existing Playwright projects or device descriptors before inventing a new execution pattern.

## 2. Detect Cypress

1. Search for:
   1. `cypress.config.*`
   2. `cypress/e2e`
   3. `cy.viewport(`
   4. `describe(`
   5. `it(`
2. Treat the repo as Cypress-first when these files or patterns exist.
3. Reuse existing Cypress commands, fixtures, and custom commands before creating new helpers.

## 3. Detect Shared Or Mixed Setups

1. Inspect `package.json` scripts for multiple runners.
2. Prefer the framework already used for the page or journey under test.
3. Prefer the framework with the strongest existing coverage when the page has no tests yet.
4. Prefer the framework already wired into CI when the repository supports both runners equally.

## 4. Search Patterns

1. Use fast search commands such as:
   1. `rg "playwright|@playwright/test|playwright.config"`
   2. `rg "cypress|cy\\.viewport|cypress.config"`
   3. `rg "checkout|dashboard|pricing|nav|menu|modal"`
2. Search by feature name first.
3. Search by existing responsive clues next:
   1. `viewport`
   2. `device`
   3. `mobile`
   4. `tablet`
   5. `desktop`
4. Search for stable helper layers next:
   1. custom commands
   2. fixtures
   3. page objects
   4. auth helpers
   5. shared setup utilities

## 5. Decision Rule

1. Reuse the framework already present in the repo.
2. Reuse the existing test closest to the target journey.
3. Create new framework setup only when the repository has no frontend test stack and the user explicitly wants one.
4. Favor reuse candidates that already have stable auth, fixture, or navigation setup because they reduce responsive-test flakiness.
