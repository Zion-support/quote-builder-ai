/* Exercise the browser controller with a minimal DOM adapter. No browser rendering is claimed. */
const test = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const path = require('node:path');
const core = require('../assets/quote.js');
const source = fs.readFileSync(path.join(__dirname, '../assets/quote.js'), 'utf8');
const locales = JSON.parse(fs.readFileSync(path.join(__dirname, '../_data/locales.json'), 'utf8'));
function page(locale) {
  const html = fs.readFileSync(path.join(__dirname, '..', locale === 'en' ? 'index.html' : locale + '/index.html'), 'utf8');
  const copy = JSON.parse(html.match(/<script type="application\/json" id="quote-copy">([\s\S]*?)<\/script>/)[1]);
  const elements = {};
  for (const [, id] of html.matchAll(/\bid="([^"]+)"/g)) {
    elements[id] = { value: '', checked: false, hidden: false, disabled: true, textContent: '', attrs: {}, handlers: {},
      addEventListener(type, fn) { this.handlers[type] = fn; },
      setAttribute(key, value) { this.attrs[key] = value; }, removeAttribute(key) { delete this.attrs[key]; },
      focus() { this.focused = true; }
    };
  }
  elements['quote-copy'].textContent = JSON.stringify(copy);
  function reset() {
    for (const id of core.COST_IDS) elements[id].value = '';
    elements.markup.value = '40'; elements.currency.value = locales[locale].currency;
    elements.notes.value = ''; elements.reviewed.checked = false;
  }
  reset(); elements['quote-form'].reset = reset;
  let clipboard = '';
  let prints = 0;
  const window = { document: { getElementById: id => elements[id] }, navigator: { clipboard: { writeText: async text => { clipboard = text; } } }, print: () => { prints += 1; } };
  vm.runInNewContext(source, { window, Intl, BigInt });
  return { elements, copy, clipboard: () => clipboard, prints: () => prints,
    event: (id, event) => elements[id].handlers[event]({ preventDefault() {} }) };
}
for (const locale of Object.keys(locales)) {
  test(locale + ': empty fields fail, fictional example calculates, edits invalidate, review remains user-reported', async () => {
    const p = page(locale); const e = p.elements;
    assert.equal(e.calculate.disabled, false);
    p.event('quote-form', 'submit');
    assert.equal(e.result.hidden, true);
    assert.equal(e.supplier.attrs['aria-invalid'], 'true');
    assert.equal(e['supplier-error'].textContent, p.copy.required);
    p.event('load-example', 'click');
    assert.equal(e.reviewed.checked, false);
    assert.equal(e['sample-status'].textContent, p.copy.sampleNote);
    p.event('quote-form', 'submit');
    assert.equal(e.result.hidden, false);
    assert.equal(e['result-state'].textContent, p.copy.draft);
    assert.ok(e['price-value'].textContent.includes('2') && e['price-value'].textContent.includes('800'));
    await p.event('copy-result', 'click');
    assert.ok(p.clipboard().includes(p.copy.summaryScope));
    assert.ok(p.clipboard().includes(p.copy.steps[3][1]));
    e.tax.value = '101'; p.event('tax', 'input');
    assert.equal(e.result.hidden, true);
    assert.equal(e['result-placeholder'].textContent, p.copy.stale);
    e.reviewed.checked = true;
    const text = '<img src=x onerror=alert(1)> & supplier reference';
    e.notes.value = text;
    p.event('quote-form', 'submit');
    assert.equal(e['result-state'].textContent, p.copy.reviewed);
    assert.equal(e['result-notes'].textContent, text);
    assert.equal(e['result-notes'].innerHTML, undefined);
    p.event('print-result', 'click');
    assert.equal(p.prints(), 1);
    e.currency.value = 'BRL'; p.event('currency', 'change');
    assert.equal(e.result.hidden, true);
    p.event('clear', 'click');
    assert.equal(e.supplier.value, '');
    assert.equal(e.reviewed.checked, false);
    assert.equal(e.result.hidden, true);
  });
}
