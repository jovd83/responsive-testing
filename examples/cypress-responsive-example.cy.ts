const viewports = [
  ["mobile-small", 375, 667],
  ["tablet-portrait", 768, 1024],
  ["desktop-wide", 1440, 900],
] as const;

describe("checkout responsive coverage", () => {
  viewports.forEach(([name, width, height]) => {
    it(`keeps checkout usable on ${name}`, () => {
      cy.viewport(width, height);
      cy.visit("/checkout");

      cy.findByRole("heading", { name: /checkout/i }).should("be.visible");
      cy.findByRole("button", { name: /place order|checkout/i }).should("be.visible");
      cy.get("body").should("not.have.css", "overflow-x", "scroll");
    });
  });
});
