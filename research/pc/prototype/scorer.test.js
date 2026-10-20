// Run with: node --test
const test = require('node:test');
const assert = require('node:assert');
const S = require('./scorer.js');

const say = (s, step = 1, start = 1) =>
  s.split(/\s+/).filter(Boolean).map((text, i) => ({ text, t: start + i * step }));

test('month words and recogniser slips', () => {
  assert.strictEqual(S.monthIndex('December'), 11);
  assert.strictEqual(S.monthIndex('Sept'), 8);
  assert.strictEqual(S.monthIndex('Jule'), 6);
  assert.strictEqual(S.monthIndex('Septembre'), 8);
  assert.strictEqual(S.monthIndex('my'), -1);
  assert.strictEqual(S.monthIndex('the'), -1);
});

test('full months backwards scores 0', () => {
  const r = S.scoreMonthsBackwards(say('December November October September August July June May April March February January'));
  assert.strictEqual(r.score, 0);
  assert.strictEqual(r.correctInSequence, 12);
});

test('exactly 7 correct (December to June) scores 0', () => {
  assert.strictEqual(S.scoreMonthsBackwards(say('December November October September August July June')).score, 0);
});

test('6 correct then an error scores 1', () => {
  const r = S.scoreMonthsBackwards(say('December November October September August July May'));
  assert.strictEqual(r.score, 1);
  assert.strictEqual(r.correctInSequence, 6);
  assert.strictEqual(r.errors[0].type, 'omission');
});

test('slipping into forward order breaks the run', () => {
  const r = S.scoreMonthsBackwards(say('December November October November December'));
  assert.strictEqual(r.correctInSequence, 3);
  assert.strictEqual(r.score, 1);
});

test('stutters and restarts: best attempt counts', () => {
  const r = S.scoreMonthsBackwards(say('December November November uh December November October September August July June'));
  assert.strictEqual(r.correctInSequence, 7);
  assert.strictEqual(r.score, 0);
});

test('starting at November after the prompt is allowed', () => {
  assert.strictEqual(S.scoreMonthsBackwards(say('November October September August July June May')).score, 0);
});

test('reciting forwards from January scores 1', () => {
  const r = S.scoreMonthsBackwards(say('January February March April May June July'));
  assert.strictEqual(r.score, 1);
  assert.strictEqual(r.correctInSequence, 0);
});

test('refusal (speech but no months) scores 1; silence is untestable (2)', () => {
  assert.strictEqual(S.scoreMonthsBackwards(say("I don't want to")).score, 1);
  assert.strictEqual(S.scoreMonthsBackwards([]).score, 2);
});

test('one missing month asks again instead of failing; two missing still fail', () => {
  const one = S.scoreMonthsBackwards(say('December November October August July June May April'));
  assert.strictEqual(one.score, 1);
  assert.strictEqual(one.askAgain, true);
  const two = S.scoreMonthsBackwards(say('December November September August June May April'));
  assert.strictEqual(two.askAgain, false);
  assert.strictEqual(S.scoreMonthsBackwards(say('December November October September')).askAgain, false);
  assert.strictEqual(S.scoreMonthsBackwards(say('January February March April May June July')).askAgain, false);
});

test('timing measures', () => {
  const r = S.scoreMonthsBackwards(say('December November October', 2, 3));
  assert.strictEqual(r.latencySec, 3);
  assert.strictEqual(r.meanGapSec, 2);
  assert.strictEqual(r.durationSec, 4);
});

test('numbers and years in words', () => {
  assert.deepStrictEqual(S.numbersIn('eighty four'), [84]);
  assert.deepStrictEqual(S.numbersIn('the 4th'), [4]);
  assert.ok(S.yearsIn('nineteen forty two').includes(1942));
  assert.ok(S.yearsIn('twenty twenty six').includes(2026));
  assert.ok(S.yearsIn('two thousand and twenty six').includes(2026));
  assert.ok(S.yearsIn('2026').includes(2026));
});

const truth = { age: 84, birth: { day: 4, month: 5, year: 1942 }, year: 2026, placeWords: ['home', 'house'] };

test('AMT4: all correct scores 0', () => {
  const r = S.scoreAMT4({ age: "I'm eighty four", birth: 'the fourth of May nineteen forty two', place: 'at home', year: 'twenty twenty six' }, truth);
  assert.strictEqual(r.mistakes, 0);
  assert.strictEqual(r.score, 0);
});

test('AMT4: one mistake scores 1, two score 2, no answers untestable 2', () => {
  assert.strictEqual(S.scoreAMT4({ age: '84', birth: '4 May 1942', place: 'home', year: '1999' }, truth).score, 1);
  assert.strictEqual(S.scoreAMT4({ age: '70', birth: '4 May 1942', place: 'the station', year: '2026' }, truth).score, 2);
  assert.strictEqual(S.scoreAMT4({}, truth).score, 2);
});

test('total 4AT and meaning', () => {
  const months = { score: 1 };
  const amt4 = { score: 1 };
  assert.strictEqual(S.total4AT({ alertnessAbnormal: false, amt4, months, acuteChange: false }).total, 2);
  const r = S.total4AT({ alertnessAbnormal: false, amt4, months, acuteChange: true });
  assert.strictEqual(r.total, 6);
  assert.match(r.meaning, /Possible delirium/);
});

test('baseline comparison flags slowing', () => {
  const base = [{ latencySec: 2, meanGapSec: 1 }, { latencySec: 2.5, meanGapSec: 1.2 }, { latencySec: 1.5, meanGapSec: 0.8 }];
  const z = S.compareToBaseline({ latencySec: 6, meanGapSec: 3 }, base);
  assert.ok(z.latencySec > 3);
  assert.ok(z.meanGapSec > 3);
  assert.strictEqual(S.compareToBaseline({ latencySec: 6 }, base.slice(0, 2)), null);
});
