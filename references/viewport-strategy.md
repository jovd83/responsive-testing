# Viewport Strategy

## 1. Default Matrix

1. Use this matrix when the repo does not define product breakpoints:
   1. `mobile-small` `375x667`
   2. `mobile-large` `430x932`
   3. `tablet-portrait` `768x1024`
   4. `tablet-landscape` `1024x768`
   5. `laptop` `1366x768`
   6. `desktop-wide` `1440x900`
   7. `desktop-large` `1920x1080`

## 2. Selection Rules

1. Start with three sizes for low-risk pages:
   1. one mobile
   2. one tablet
   3. one desktop
2. Use the full default matrix for layout-heavy pages.
3. Add extra sizes only for product-specific breakpoints, kiosk screens, or ultra-wide layouts.
4. Prefer user- or product-specified breakpoints over the fallback matrix.

## 3. Assertion Priorities

1. Assert behavior first:
   1. primary actions remain reachable
   2. navigation is usable
   3. dialogs fit the viewport
   4. content does not clip unexpectedly
   5. horizontal scrolling is absent unless intended
   6. sticky headers and footers do not block primary actions
2. Assert visual evidence second:
   1. screenshot on failure
   2. targeted visual comparison only when the repo already uses it

## 4. Structuring Tests

1. Parameterize one journey across many viewports.
2. Keep viewport labels stable in test names and reports.
3. Avoid cloning the same test file for each device class.
4. Separate responsive-only assertions from unrelated functional assertions when that improves debugging.

## 5. Device Emulation Guardrail

1. Use framework-native device emulation only when the repo already uses it or the user asks for it.
2. Do not claim realistic mobile behavior from width-only resizing when touch, orientation, or user-agent behavior matters.
3. Document when the run used width-only resizing versus richer device emulation so report readers understand the coverage boundary.
