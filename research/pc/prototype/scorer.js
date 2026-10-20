// Spoken 4AT scoring. Pure functions, no dependencies; works in Node and the browser.
// Scoring follows the official 4AT guide (https://www.the4at.com/userguide).
// Speech only supplies the answers and timings; the scoring itself is rule-based.

(function (root) {
  'use strict';

  const MONTHS = ['january', 'february', 'march', 'april', 'may', 'june', 'july',
    'august', 'september', 'october', 'november', 'december'];

  // Common short forms and recogniser slips for older or accented speech.
  const ALIASES = {
    jan: 0, febuary: 1, feb: 1, mar: 2, apr: 3, jun: 5, jul: 6, jule: 6, julie: 6,
    aug: 7, sep: 8, sept: 8, oct: 9, nov: 10, dec: 11,
  };

  function levenshtein(a, b) {
    const d = Array.from({ length: a.length + 1 }, (_, i) => [i]);
    for (let j = 1; j <= b.length; j++) d[0][j] = j;
    for (let i = 1; i <= a.length; i++) {
      for (let j = 1; j <= b.length; j++) {
        d[i][j] = Math.min(d[i - 1][j] + 1, d[i][j - 1] + 1,
          d[i - 1][j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1));
      }
    }
    return d[a.length][b.length];
  }

  // Returns a month index 0-11, or -1 if the word is not a month.
  function monthIndex(word) {
    const w = String(word).toLowerCase().replace(/[^a-z]/g, '');
    if (!w) return -1;
    const exact = MONTHS.indexOf(w);
    if (exact >= 0) return exact;
    if (w in ALIASES) return ALIASES[w];
    if (w.length < 5) return -1; // too short to fuzzy-match safely ("may" vs "my")
    let best = -1, bestDist = 3;
    MONTHS.forEach((m, i) => {
      const dist = levenshtein(w, m);
      if (dist < bestDist) { best = i; bestDist = dist; }
    });
    return best;
  }

  // words: [{ text, t }] where t is seconds from the end of the instruction.
  // Longest correct backwards run from December or November (the 4AT allows one prompt,
  // "what is the month before December?"). A repeated month is ignored as a stutter;
  // saying December again restarts the attempt, and the best attempt counts.
  function scoreMonthsBackwards(words, opts) {
    const o = Object.assign({ spokeAtAll: words.length > 0 }, opts);
    const months = words.map(w => ({ m: monthIndex(w.text), t: w.t })).filter(x => x.m >= 0);

    let best = 0, run = 0, expected = null, last = null;
    const errors = [];
    for (const { m } of months) {
      if (m === 11 || (expected === null && m === 10)) {
        // fresh start (December, or November after the prompt)
        run = 1; expected = m - 1; last = m;
      } else if (expected === null) {
        errors.push({ type: 'bad-start', month: MONTHS[m] });
        continue;
      } else if (m === last) {
        continue; // repetition
      } else if (m === expected) {
        run++; expected--; last = m;
      } else {
        errors.push({ type: m > last ? 'forward' : 'omission', month: MONTHS[m], expected: MONTHS[(expected + 12) % 12] });
        expected = null; // the run is broken
      }
      best = Math.max(best, run);
      if (expected < 0) expected = null; // reached January
    }

    let score;
    if (best >= 7) score = 0;
    else if (months.length > 0 || o.spokeAtAll) score = 1; // started but <7, or refused
    else score = 2; // untestable: no response at all

    // Speech recognisers often drop one month from a spoken list. If the answer would pass
    // with exactly one month missing, the app should ask again rather than count a failure.
    const askAgain = score === 1 && runWithOneGap(months.map(x => x.m)) >= 7;

    const times = months.map(x => x.t);
    const gaps = times.slice(1).map((t, i) => t - times[i]);
    return {
      score,
      askAgain,
      correctInSequence: best,
      errors,
      latencySec: times.length ? times[0] : null,
      meanGapSec: gaps.length ? gaps.reduce((a, b) => a + b, 0) / gaps.length : null,
      maxGapSec: gaps.length ? Math.max(...gaps) : null,
      durationSec: times.length ? times[times.length - 1] - times[0] : null,
    };
  }

  // Longest backwards run from December/November that allows a single missing month.
  function runWithOneGap(ms) {
    let best = 0;
    for (let s = 0; s < ms.length; s++) {
      if (ms[s] !== 11 && ms[s] !== 10) continue;
      let run = 1, last = ms[s], gapUsed = false;
      for (let i = s + 1; i < ms.length; i++) {
        const m = ms[i];
        if (m === last) continue;
        if (m === last - 1) { run++; last = m; }
        else if (!gapUsed && m === last - 2) { run++; last = m; gapUsed = true; }
        else break;
      }
      best = Math.max(best, run);
    }
    return best;
  }

  const NUMBER_WORDS = {
    zero: 0, one: 1, two: 2, three: 3, four: 4, five: 5, six: 6, seven: 7, eight: 8, nine: 9,
    ten: 10, eleven: 11, twelve: 12, thirteen: 13, fourteen: 14, fifteen: 15, sixteen: 16,
    seventeen: 17, eighteen: 18, nineteen: 19, twenty: 20, thirty: 30, forty: 40, fifty: 50,
    sixty: 60, seventy: 70, eighty: 80, ninety: 90,
    first: 1, second: 2, third: 3, fourth: 4, fifth: 5, sixth: 6, seventh: 7, eighth: 8,
    ninth: 9, tenth: 10, eleventh: 11, twelfth: 12, thirteenth: 13, fourteenth: 14,
    fifteenth: 15, sixteenth: 16, seventeenth: 17, eighteenth: 18, nineteenth: 19,
    twentieth: 20, thirtieth: 30,
  };

  // "eighty four" -> 84, "84" or "84th" -> 84, "two thousand and five" -> 2005.
  // Returns the numbers found, in order.
  function numbersIn(text) {
    const out = [];
    let acc = null;
    for (let tok of String(text).toLowerCase().replace(/-/g, ' ').split(/[^a-z0-9]+/)) {
      tok = tok.replace(/^(\d+)(st|nd|rd|th)$/, '$1');
      if (/^\d+$/.test(tok)) { if (acc !== null) out.push(acc); acc = null; out.push(+tok); continue; }
      if (tok in NUMBER_WORDS) {
        const v = NUMBER_WORDS[tok];
        if (acc !== null && acc >= 1000 && acc % 100 === 0 && v < 100) acc += v;
        else if (acc !== null && acc % 10 === 0 && acc >= 20 && v < 10) acc += v;
        else { if (acc !== null) out.push(acc); acc = v; }
      } else if (tok === 'hundred' && acc !== null) acc *= 100;
      else if (tok === 'thousand' && acc !== null) acc *= 1000;
      else if (tok === 'and' && acc !== null && acc >= 100) continue;
      else if (acc !== null) { out.push(acc); acc = null; }
    }
    if (acc !== null) out.push(acc);
    return out;
  }

  // Years are often said as "nineteen forty two" or "twenty twenty six".
  function yearsIn(text) {
    const n = numbersIn(text);
    const years = n.filter(x => x >= 1900 && x <= 2100);
    for (let i = 0; i + 1 < n.length; i++) {
      if ((n[i] === 19 || n[i] === 20) && n[i + 1] >= 0 && n[i + 1] < 100) years.push(n[i] * 100 + n[i + 1]);
    }
    return years;
  }

  // truth: { age, birth: {day, month (1-12), year}, year, placeWords: [...] }
  // answers: { age, birth, place, year } as recognised text.
  function scoreAMT4(answers, truth) {
    const a = answers || {};
    const items = {
      age: numbersIn(a.age || '').includes(truth.age),
      birth: (() => {
        const t = String(a.birth || '');
        const months = t.split(/\s+/).map(monthIndex).filter(m => m >= 0);
        const nums = numbersIn(t);
        return yearsIn(t).includes(truth.birth.year) && months.includes(truth.birth.month - 1) &&
          nums.some(x => x === truth.birth.day);
      })(),
      place: truth.placeWords.some(w => String(a.place || '').toLowerCase().includes(w.toLowerCase())),
      year: yearsIn(a.year || '').includes(truth.year),
    };
    const answered = Object.values(a).some(v => v && String(v).trim());
    const mistakes = Object.values(items).filter(ok => !ok).length;
    // 0 mistakes = 0; 1 mistake = 1; 2 or more, or untestable = 2
    const score = !answered ? 2 : mistakes === 0 ? 0 : mistakes === 1 ? 1 : 2;
    return { score, items, mistakes };
  }

  // alertnessAbnormal and acuteChange come from the family member's answers;
  // speech cannot reliably judge alertness on its own.
  function total4AT({ alertnessAbnormal, amt4, months, acuteChange }) {
    const parts = {
      alertness: alertnessAbnormal ? 4 : 0,
      amt4: amt4.score,
      attention: months.score,
      acuteChange: acuteChange ? 4 : 0,
    };
    const total = parts.alertness + parts.amt4 + parts.attention + parts.acuteChange;
    const meaning = total >= 4 ? 'Possible delirium: contact a doctor or nurse today.'
      : total >= 1 ? 'Possible cognitive impairment; delirium less likely. Mention it to a doctor.'
        : 'No sign of delirium on this screen.';
    return { total, parts, meaning };
  }

  // Compares today's timing measures with the same person's earlier normal sessions.
  // Returns z-scores; positive means slower than usual. Needs at least 3 baseline sessions.
  function compareToBaseline(today, baseline) {
    if (!baseline || baseline.length < 3) return null;
    const out = {};
    for (const key of ['latencySec', 'meanGapSec', 'durationSec']) {
      const xs = baseline.map(b => b[key]).filter(v => typeof v === 'number');
      if (xs.length < 3 || typeof today[key] !== 'number') continue;
      const mean = xs.reduce((a, b) => a + b, 0) / xs.length;
      const sd = Math.sqrt(xs.reduce((a, b) => a + (b - mean) ** 2, 0) / (xs.length - 1)) || 0.25;
      out[key] = (today[key] - mean) / sd;
    }
    return out;
  }

  const api = { MONTHS, monthIndex, numbersIn, yearsIn, scoreMonthsBackwards, scoreAMT4, total4AT, compareToBaseline };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.FourAT = api;
})(typeof window !== 'undefined' ? window : globalThis);
