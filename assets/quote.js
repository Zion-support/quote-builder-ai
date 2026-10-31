/* Local arithmetic only. No network requests, browser storage or external dependencies. */
(function (root) {
  'use strict';
  const COST_IDS = ['supplier', 'labor', 'equipment', 'tax', 'travel', 'freight', 'import', 'other'];
  const CURRENCIES = ['USD', 'BRL', 'EUR', 'GBP'];
  function decimalUnits(value, maximum) {
    const raw = String(value == null ? '' : value).trim();
    if (!raw) return { error: 'required' };
    if (!/^\d+(?:[.,]\d{1,2})?$/.test(raw)) return { error: 'invalid' };
    const parts = raw.replace(',', '.').split('.');
    const whole = Number(parts[0]);
    if (!Number.isSafeInteger(whole) || whole > maximum) return { error: 'invalid' };
    const units = whole * 100 + Number((parts[1] || '').padEnd(2, '0'));
    return Number.isSafeInteger(units) && units <= maximum * 100 ? { units } : { error: 'invalid' };
  }
  function priceAt(costCents, markupBasisPoints) {
    const numerator = BigInt(costCents) * (10000n + BigInt(markupBasisPoints));
    return Number((numerator + 9999n) / 10000n);
  }
  function calculate(values) {
    const errors = {};
    const costs = {};
    COST_IDS.forEach(id => {
      const parsed = decimalUnits(values[id], 1000000000);
      if (parsed.error) errors[id] = parsed.error === 'required' ? 'required' : 'moneyError';
      else costs[id] = parsed.units;
    });
    const markup = decimalUnits(values.markup, 1000);
    if (markup.error || markup.units < 4000) errors.markup = 'markupError';
    if (!CURRENCIES.includes(values.currency)) errors.currency = 'required';
    if (Object.keys(errors).length) return { valid: false, errors };
    const totalCents = COST_IDS.reduce((sum, id) => sum + costs[id], 0);
    if (totalCents === 0) return { valid: false, errors: { total: 'zeroError' } };
    const priceCents = priceAt(totalCents, markup.units);
    const differenceCents = priceCents - totalCents;
    return {
      valid: true, costs, totalCents, priceCents, differenceCents,
      minimumCents: priceAt(totalCents, 4000), markupBasisPoints: markup.units,
      grossMargin: differenceCents / priceCents, currency: values.currency
    };
  }
  const api = { calculate, priceAt, COST_IDS, CURRENCIES };
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (!root.document) return;
  const document = root.document;
  const form = document.getElementById('quote-form');
  if (!form) return;
  const copy = JSON.parse(document.getElementById('quote-copy').textContent);
  const $ = id => document.getElementById(id);
  const inputIds = COST_IDS.concat(['markup', 'currency', 'notes', 'reviewed']);
  let latest = null;
  let summary = '';
  const money = (cents, currency) => new Intl.NumberFormat(copy.intl, {
    style: 'currency', currency, currencyDisplay: 'code', minimumFractionDigits: 2, maximumFractionDigits: 2
  }).format(cents / 100);
  const percent = fraction => new Intl.NumberFormat(copy.intl, {
    style: 'percent', maximumFractionDigits: 2
  }).format(fraction);
  function clearErrors() {
    inputIds.forEach(id => {
      $(id).removeAttribute('aria-invalid');
      const error = $(id + '-error');
      if (error) { error.textContent = ''; error.hidden = true; }
    });
    $('form-error').textContent = '';
    $('form-error').hidden = true;
  }
  function hideResult(message) {
    latest = null;
    summary = '';
    $('result').hidden = true;
    $('result-placeholder').hidden = false;
    $('result-placeholder').textContent = message;
    $('copy-status').textContent = '';
  }
  inputIds.forEach(id => {
    $(id).addEventListener('input', () => {
      if (latest) hideResult(copy.stale);
      $('sample-status').textContent = '';
    });
    $(id).addEventListener('change', () => { if (latest) hideResult(copy.stale); });
  });
  form.addEventListener('submit', event => {
    event.preventDefault();
    clearErrors();
    const values = Object.fromEntries(COST_IDS.concat(['markup', 'currency']).map(id => [id, $(id).value]));
    const result = calculate(values);
    if (!result.valid) {
      hideResult(copy.emptyResult);
      $('form-error').hidden = false;
      $('form-error').textContent = result.errors.total ? copy.zeroError : copy.formError;
      let focus = null;
      Object.entries(result.errors).forEach(([id, key]) => {
        if (id === 'total') return;
        $(id).setAttribute('aria-invalid', 'true');
        const error = $(id + '-error');
        if (error) { error.textContent = copy[key]; error.hidden = false; }
        focus = focus || $(id);
      });
      (focus || $('form-error')).focus();
      return;
    }
    latest = result;
    const reviewed = $('reviewed').checked;
    const state = reviewed ? copy.reviewed : copy.draft;
    $('result-state').textContent = state;
    $('result-state-body').textContent = reviewed ? copy.reviewedBody : copy.draftBody;
    $('total-value').textContent = money(result.totalCents, result.currency);
    $('markup-value').textContent = percent(result.markupBasisPoints / 10000);
    $('floor-value').textContent = money(result.minimumCents, result.currency);
    $('price-value').textContent = money(result.priceCents, result.currency);
    $('profit-value').textContent = money(result.differenceCents, result.currency);
    $('margin-value').textContent = percent(result.grossMargin);
    COST_IDS.forEach(id => { $('result-' + id).textContent = money(result.costs[id], result.currency); });
    const notes = $('notes').value.trim();
    $('result-notes-wrap').hidden = !notes;
    $('result-notes').textContent = notes;
    const labels = Object.fromEntries(copy.costs.map(row => [row[0], row[1]]));
    summary = [copy.summaryHeading, copy.summaryStatus + ': ' + state, '',
      ...COST_IDS.map(id => labels[id] + ': ' + money(result.costs[id], result.currency)), '',
      copy.total + ': ' + money(result.totalCents, result.currency),
      copy.markupResult + ': ' + percent(result.markupBasisPoints / 10000),
      copy.floor + ': ' + money(result.minimumCents, result.currency),
      copy.price + ': ' + money(result.priceCents, result.currency),
      copy.profit + ': ' + money(result.differenceCents, result.currency),
      copy.margin + ': ' + percent(result.grossMargin), '', copy.formula,
      ...(notes ? ['', copy.resultNotes + ':', notes] : []), '',
      reviewed ? copy.reviewedBody : copy.draftBody, copy.summaryScope,
      copy.steps[3][1]
    ].join('\n');
    $('result-placeholder').hidden = true;
    $('result').hidden = false;
    $('result-title').focus();
  });
  $('clear').addEventListener('click', () => {
    form.reset();
    clearErrors();
    hideResult(copy.emptyResult);
    $('sample-status').textContent = '';
    $('supplier').focus();
  });
  $('load-example').addEventListener('click', () => {
    const sample = ['1000', '200', '500', '100', '120', '50', '30', '0'];
    COST_IDS.forEach((id, i) => { $(id).value = sample[i]; });
    $('markup').value = '40';
    $('reviewed').checked = false;
    $('notes').value = '';
    clearErrors();
    hideResult(copy.emptyResult);
    $('sample-status').textContent = copy.sampleNote;
    $('supplier').focus();
  });
  $('copy-result').addEventListener('click', async () => {
    if (!latest) return;
    try {
      await root.navigator.clipboard.writeText(summary);
      $('copy-status').textContent = copy.copied;
    } catch (_) { $('copy-status').textContent = copy.copyFailed; }
  });
  $('print-result').addEventListener('click', () => { if (latest) root.print(); });
  $('calculate').disabled = false;
  $('load-example').disabled = false;
})(typeof window !== 'undefined' ? window : globalThis);
