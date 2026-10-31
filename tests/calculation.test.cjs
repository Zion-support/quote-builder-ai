const test = require('node:test');
const assert = require('node:assert/strict');
const { calculate, COST_IDS } = require('../assets/quote.js');
const inputs = extra => Object.assign(Object.fromEntries(COST_IDS.map(id => [id, '0'])), { currency: 'USD', markup: '40', supplier: '1000' }, extra);

test('all eight explicit cost components are included; 40% markup is not 40% margin', () => {
  const result = calculate(inputs({ supplier: '1000', labor: '200', equipment: '500', tax: '100', travel: '120', freight: '50', import: '30' }));
  assert.equal(result.valid, true);
  assert.equal(result.totalCents, 200000);
  assert.equal(result.priceCents, 280000);
  assert.equal(result.minimumCents, 280000);
  assert.equal(result.differenceCents, 80000);
  assert.ok(Math.abs(result.grossMargin - 2 / 7) < 1e-12);
});

test('decimal-comma inputs and a 41.25% markup calculate correctly', () => {
  const result = calculate(inputs({ supplier: '1200,00', markup: '41,25' }));
  assert.equal(result.priceCents, 169500);
  assert.equal(result.minimumCents, 168000);
  assert.equal(result.markupBasisPoints, 4125);
});

test('rounding always preserves the minimum and selected markup, including one cent', () => {
  assert.equal(calculate(inputs({ supplier: '0.01' })).priceCents, 2);
  for (const amount of ['0.01', '0.03', '1.07', '123.45', '1000000000']) {
    for (const markup of ['40', '40.01', '41.25', '99.99', '1000']) {
      const result = calculate(inputs({ supplier: amount, markup }));
      assert.equal(result.valid, true);
      const product = BigInt(result.totalCents) * (10000n + BigInt(result.markupBasisPoints));
      assert.ok(BigInt(result.priceCents) * 10000n >= product);
      assert.ok(BigInt(result.priceCents - 1) * 10000n < product);
      assert.ok(result.priceCents >= result.minimumCents);
    }
  }
});

test('unknown and invalid costs never produce a quote or treat empty values as zero', () => {
  for (const value of ['', ' ', '-1', 'NaN', 'Infinity', '1e3', '0x20', '1,000', '1.000,00', '1 000', '1.001', '1000000000.01']) {
    const result = calculate(inputs({ freight: value }));
    assert.equal(result.valid, false, value);
    assert.ok(result.errors.freight, value);
    assert.equal(result.priceCents, undefined);
  }
  const result = calculate(inputs({ supplier: '0' }));
  assert.deepEqual(result.errors, { total: 'zeroError' });
});

test('markup below 40%, unsupported currency and excessive precision are rejected', () => {
  for (const markup of ['', '-40', '0', '39.99', '1000.01', '40.001', '4e1']) {
    assert.equal(calculate(inputs({ markup })).valid, false, markup);
  }
  assert.equal(calculate(inputs({ currency: 'JPY' })).valid, false);
});

test('the supported maximum stays exact; costs do not depend on the currency', () => {
  const allMaximum = Object.fromEntries(COST_IDS.map(id => [id, '1000000000']));
  const result = calculate(inputs({ ...allMaximum, markup: '1000' }));
  assert.equal(result.totalCents, 800000000000);
  assert.equal(result.priceCents, 8800000000000);
  for (const currency of ['USD', 'BRL', 'EUR', 'GBP']) {
    assert.equal(calculate(inputs({ currency })).priceCents, 140000);
  }
});
