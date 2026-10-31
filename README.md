# Zion Service Cost Planner

A browser-local worksheet for service pricing scenarios. The repository keeps its existing `quote-builder-ai` name and English URL. This implementation performs arithmetic; it does not generate content with AI, query suppliers, connect a CRM, send quotations or authorize operations.

## Published routes

- [English](https://ziontechgroup.com/quote-builder-ai/)
- [Português](https://ziontechgroup.com/quote-builder-ai/pt/)
- [Español](https://ziontechgroup.com/quote-builder-ai/es/)
- [Français](https://ziontechgroup.com/quote-builder-ai/fr/)
- [Deutsch](https://ziontechgroup.com/quote-builder-ai/de/)

These are the intended publication routes. A commit alone does not establish that GitHub Pages has deployed them.

## Calculation and review

Enter separate supplier services, technician labor, parts/equipment/rentals, taxes, travel, freight, import/clearance and other documented costs. Blank values mean unknown; zero must be explicitly entered for a nonapplicable line. Use one currency and avoid double counting. The worksheet does not calculate taxes or convert currencies.

Planning price = total recorded cost × (1 + markup / 100). The minimum markup is 40%; this is approximately 28.57% gross margin on the price, not 40% gross margin. Prices are rounded upward to a cent using integer arithmetic so rounding cannot breach the requested markup. Each cost accepts 0–1,000,000,000 currency units, and markup accepts 40–1,000%, both with at most two decimals. All offered currencies have two decimal minor units.

The output remains a planning scenario. An optional checkbox records the user's own review of current cost evidence; it does not independently verify evidence or approve a client quotation. The worksheet cannot approve a client quote, purchase, reservation, supplier commitment or dispatch. Written customer acceptance, the corresponding purchase order and operational arrangements belong to a separate commercial process; they are not created or checked by this app.

Inputs remain in the tab. There are no network requests containing cost data, browser storage, analytics, dependencies or generated client records. Users can copy or print a scenario themselves. Reloading or changing language does not transfer inputs to another page. The fictional example is deliberately labeled and does not contain market rates.

## Maintain and verify

```sh
python3 scripts/render.py
python3 scripts/render.py --check
python3 -m unittest discover -s tests -p 'test_*.py'
node --test tests/calculation.test.cjs tests/browser-state.test.cjs
```

Static copy is maintained in `_data/locales.json`; the renderer produces complete searchable HTML, metadata and navigation for each locale. All editions use one shared calculation/runtime implementation and stylesheet. Existing hosting configuration is unchanged.

## Related resources

[App catalog](https://ziontechgroup.com/apps/) · [App network](https://ziontechgroup.com/zion-app-network/) · [Datacenter service-request guide](https://ziontechgroup.com/zion-app-network/datacenter-service-request-guide-2026.html) · [Operational planning tools](https://ziontechgroup.com/apps/operational-planning-tools.html) · [Free Discovery](https://ziontechgroup.com/discovery/)
