import { test, expect } from "@playwright/test";

const viewports = [
  { name: "mobile-small", width: 375, height: 667 },
  { name: "tablet-portrait", width: 768, height: 1024 },
  { name: "desktop-wide", width: 1440, height: 900 },
];

for (const viewport of viewports) {
  test(`checkout remains usable on ${viewport.name}`, async ({ page }) => {
    await page.setViewportSize({ width: viewport.width, height: viewport.height });

    await page.goto("/checkout");
    await expect(page.getByRole("heading", { name: /checkout/i })).toBeVisible();
    await expect(page.getByRole("button", { name: /place order|checkout/i })).toBeVisible();

    const bodyOverflowX = await page.evaluate(() => getComputedStyle(document.body).overflowX);
    expect(bodyOverflowX).not.toBe("scroll");
  });
}
