// Scores recognised probe answers with the prototype's own 4AT scorer, so the comparison
// uses exactly the rules the app uses. stdin: [{kind, transcript}], stdout: [{judgedHealthy}]
const S = require('../prototype/scorer.js');

const truth = { age: 84, birth: { day: 4, month: 5, year: 1942 }, year: 2026, placeWords: ['home', 'house'] };
const input = JSON.parse(require('fs').readFileSync(0, 'utf8').replace(/^﻿/, ''));

const out = input.map(({ kind, transcript }) => {
  if (kind === 'months') {
    const words = transcript.split(/\s+/).filter(Boolean).map((text, i) => ({ text, t: i }));
    const r = S.scoreMonthsBackwards(words);
    return { judgedHealthy: r.score === 0 ? true : r.askAgain ? null : false };
  }
  const r = S.scoreAMT4({ [kind]: transcript }, truth);
  return { judgedHealthy: r.items[kind] };
});
process.stdout.write(JSON.stringify(out));
