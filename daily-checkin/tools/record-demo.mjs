import { chromium } from '/opt/node-tools/node_modules/playwright/index.mjs';
import fs from 'fs';
const [OUT, DEMO] = process.argv.slice(2);
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
const ctx = await browser.newContext({ viewport: { width: 420, height: 900 }, deviceScaleFactor: 1,
  recordVideo: { dir: OUT, size: { width: 420, height: 900 } } });
const page = await ctx.newPage();
const t0 = Date.now();
const caps = [];
const cap = (text) => { const t = (Date.now() - t0) / 1000; if (caps.length) caps[caps.length - 1].end = t; caps.push({ start: t, text }); console.log(t.toFixed(1), text); };
const wait = (ms) => page.waitForTimeout(ms);
page.setDefaultTimeout(20000);
const errors = [];
page.on('pageerror', e => errors.push(String(e)));

cap('TITLE');
await page.goto('http://localhost:8081');
await page.getByText("I'm setting this up for a family member").waitFor();
await wait(5000);
cap('A family member sets it up on their own phone. It takes about a minute.');
await wait(1500);
await page.getByText("I'm setting this up for a family member").click();
await wait(1200);
const fill = async (label, v) => { const i = page.locator(`text=${label}`).locator('xpath=following-sibling::input[1]'); await i.click(); await i.pressSequentially(v, { delay: 60 }); await wait(400); };
await fill('What you call them', 'Dad');
await fill('Their date of birth', '1950-06-02');
await fill('Their town or city', 'Rochester');
await fill('Your first name', 'Sam');
await wait(800);
await page.getByRole('button', { name: 'Create' }).click();
await page.getByText('Dad is set up').waitFor();
cap('They get a short code to enter on Dad\'s phone, and a daily reminder time.');
await wait(6000);
await page.getByRole('button', { name: 'This is their phone: start check-ins' }).click();
cap('On Dad\'s phone there is one big button. No menus, no typing.');
await wait(5000);
await page.getByRole('button', { name: 'Start my check-in' }).click();
// Typed answers can't hear the digit span, so read its numbers from the plan.
const personId = await page.evaluate(() => JSON.parse(localStorage.getItem('checkin.setup')).personId);
const plan = await (await fetch(`http://localhost:8000/people/${personId}/today`)).json();
cap('The app reads each question aloud and records the spoken answer. For this video the answers are typed.');
const answerFor = (q) => {
  if (/how old|age/i.test(q)) return "I'm seventy six";
  if (/birth/i.test(q)) return 'June second nineteen fifty';
  if (/where|place/i.test(q)) return "I'm at home in Rochester";
  if (/months/i.test(q)) return 'December November October September August July June May';
  if (/days of the week/i.test(q)) return 'Sunday Saturday Friday Thursday Wednesday Tuesday Monday';
  if (/count/i.test(q)) return '20 19 18 17 16 15 14 13 12 11 10 9 8';
  if (/year/i.test(q)) return 'twenty twenty six';
  return 'Pretty good, I slept well and I am going for a walk later';
};
const captionsFor = [
  null,
  'Questions follow the 4AT, a validated delirium screen: age, birthday, place and year.',
  null,
  'Order and wording change every day, so the answers can\'t be memorized.',
  null,
  'An attention task: months backwards, or a rotating version like counting down.',
];
const n = plan.exercises.length;
for (let i = 0; i < n; i++) {
  await page.getByText(`Question ${i + 1} of ${n}`).waitFor();
  const input = page.locator('input');
  await input.waitFor();
  if (captionsFor[i]) cap(captionsFor[i]);
  await wait(1800);
  const text = await page.locator('body').innerText();
  const line = text.split('\n').find(l => l.endsWith('?') || l.endsWith('.')) || '';
  await input.click();
  const ex = plan.exercises[i];
  const answer = ex.kind === 'digit_span' ? ex.expect.split('').join(' ') : answerFor(line);
  await input.pressSequentially(answer, { delay: 45 });
  await wait(900);
  await page.getByRole('button', { name: 'Next' }).click();
}
await page.getByText('All done. Thank you!').waitFor();
cap('Done in about two minutes. A quick 1 to 5 rating tells us if it felt easy.');
await wait(3500);
await page.getByRole('button', { name: '5', exact: true }).click();
await page.getByText('See you tomorrow.').waitFor();
await wait(2500);

await page.evaluate((id) => localStorage.setItem('checkin.setup', JSON.stringify({ role: 'family', personId: id })), DEMO);
await page.reload();
await page.getByText('Recent days').waitFor();
cap('Now the family view for Rose, who has used it for a week. Today she seems confused.');
await wait(6000);
cap('The result follows the 4AT bands, with plain reasons: wrong year, struggled with months backwards, slower and more hesitant than her usual.');
await wait(8000);
cap('Her voice is compared with her own normal days, not with other people.');
await page.mouse.wheel(0, 500);
await wait(4500);
cap('Days she skipped show up too. If she doesn\'t open the app, she gets reminders, then the family gets a text.');
await page.mouse.wheel(0, 600);
await wait(6500);
await page.mouse.wheel(0, -2000);
await wait(1200);
cap('Tapping a day shows exactly what she said and why it was scored that way.');
await page.getByText('Call their doctor today').nth(1).click();
await page.getByText('What they said').waitFor();
await wait(4500);
await page.mouse.wheel(0, 500);
await wait(4000);
cap('If the family knows something the app doesn\'t, they can say so and it counts toward the score.');
await page.mouse.wheel(0, 600);
await wait(6000);
cap('END');
await wait(7000);
caps[caps.length - 1].end = (Date.now() - t0) / 1000;
fs.writeFileSync(`${OUT}/captions.json`, JSON.stringify(caps, null, 1));
console.log('errors', JSON.stringify(errors));
await ctx.close();
await browser.close();
