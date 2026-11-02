// Everything interactive on the Clari landing page, bundled into one file
// (vendor/clari-ui.js) so the page loads nothing from other sites.
//
//  - Arc UI (@arclux/arc-ui): skip link, buttons, tabs, animated numbers,
//    timeline, video player and the FAQ accordion.
//  - Wired Elements: the hand-drawn "fridge note" cards in the week story.
//  - thinking-orbs: the dotted listening orb (its framework-free engine).
//  - Space UI (@usespaceui/squircle): iOS-style smooth corners.
//  - Componentry: AnnotatedText and GithubCalendar, ported from React to
//    plain custom elements below (Componentry is copy-and-own by design).

import '@arclux/arc-ui/skip-link';
import '@arclux/arc-ui/button';
import '@arclux/arc-ui/badge';
import '@arclux/arc-ui/tabs';
import '@arclux/arc-ui/tab';
import '@arclux/arc-ui/animated-number';
import '@arclux/arc-ui/timeline';
import '@arclux/arc-ui/timeline-item';
import '@arclux/arc-ui/video';
import '@arclux/arc-ui/accordion';
import '@arclux/arc-ui/accordion-item';
import 'wired-elements/lib/wired-card.js';
import { MODE_FRAMES, resolvePreset, paintFrame } from 'thinking-orbs/engine';
import { initSquircle } from '@usespaceui/squircle';

try { initSquircle(); } catch { /* falls back to plain rounded corners */ }

const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');

function pageIsDark() {
  const t = document.documentElement.getAttribute('data-theme');
  if (t === 'dark') return true;
  if (t === 'light') return false;
  return matchMedia('(prefers-color-scheme: dark)').matches;
}

/* ---------- thinking-orbs: <clari-orb state="listening" size="240"> ---------- */
class ClariOrb extends HTMLElement {
  connectedCallback() {
    const size = Number(this.getAttribute('size') || 64);
    const state = this.getAttribute('state') || 'listening';
    const canvas = document.createElement('canvas');
    canvas.setAttribute('role', 'img');
    canvas.setAttribute('aria-label', this.getAttribute('label') || 'Clari is listening');
    canvas.style.cssText = `width:${size}px;height:${size}px;display:block;max-width:100%;height:auto;aspect-ratio:1`;
    this.replaceChildren(canvas);
    const dpr = Math.min(2, devicePixelRatio || 1);
    canvas.width = Math.round(size * dpr);
    canvas.height = Math.round(size * dpr);
    const ctx = canvas.getContext('2d');
    // Use the 64px preset's dot counts, drawn on a larger canvas.
    const { mode, speed, opts } = resolvePreset(state, 64);
    const frameFn = MODE_FRAMES[mode];
    const speedMul = Number(this.getAttribute('speed') || 1);
    const tintFor = () => {
      const c = getComputedStyle(this).color.match(/(\d+)\D+(\d+)\D+(\d+)/);
      return c ? { r: +c[1], g: +c[2], b: +c[3] } : undefined;
    };
    let tint = tintFor();
    let dark = pageIsDark();
    // Draw the 64px design and scale it up, so the dots grow with the orb.
    const k = dpr * size / 64;
    const draw = (t) => {
      ctx.setTransform(k, 0, 0, k, 0, 0);
      ctx.clearRect(0, 0, 64, 64);
      paintFrame(ctx, frameFn(64, t, opts), dark, tint);
    };
    let raf = 0, running = false, visible = true;
    const loop = () => { draw(performance.now() / 1000 * speed * speedMul); if (running) raf = requestAnimationFrame(loop); };
    const start = () => { if (running || reducedMotion.matches) return; running = true; raf = requestAnimationFrame(loop); };
    const stop = () => { running = false; cancelAnimationFrame(raf); };
    draw(0.6);
    this._io = new IntersectionObserver(([e]) => { visible = e.isIntersecting; visible && !document.hidden ? start() : stop(); });
    this._io.observe(canvas);
    this._vis = () => (document.hidden ? stop() : visible && start());
    document.addEventListener('visibilitychange', this._vis);
    this._theme = () => { dark = pageIsDark(); tint = tintFor(); if (!running) draw(0.6); };
    matchMedia('(prefers-color-scheme: dark)').addEventListener('change', this._theme);
    this._mo = new MutationObserver(this._theme);
    this._mo.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
    this._motion = () => { if (reducedMotion.matches) { stop(); draw(0.6); } else if (visible) start(); };
    reducedMotion.addEventListener('change', this._motion);
  }
  disconnectedCallback() {
    this._io?.disconnect(); this._mo?.disconnect();
    document.removeEventListener('visibilitychange', this._vis);
    reducedMotion.removeEventListener('change', this._motion);
  }
}
customElements.define('clari-orb', ClariOrb);

/* ---------- Componentry AnnotatedText: <clari-mark variant="circle"> ---------- */
function createRandom(seed) { let s = seed >>> 0; return () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; }
const shake = (r, a) => (r() - 0.5) * 2 * a;
const rnd = (v) => Math.round(v * 100) / 100;
function trace(points, close = false) {
  const [first, ...rest] = points;
  let d = `M${rnd(first.x)},${rnd(first.y)}`;
  rest.forEach((p, i) => {
    const n = rest[i + 1];
    d += n ? ` Q${rnd(p.x)},${rnd(p.y)} ${rnd((p.x + n.x) / 2)},${rnd((p.y + n.y) / 2)}` : ` L${rnd(p.x)},${rnd(p.y)}`;
  });
  return close ? d + ' Z' : d;
}
function stroke(from, to, { sag = 0, wobble = 0.55, steps = 12 }, r) {
  const pts = [];
  for (let i = 0; i <= steps; i++) {
    const t = i / steps, loose = i === 0 || i === steps ? 0 : 1;
    pts.push({ x: from.x + (to.x - from.x) * t + shake(r, wobble) * loose, y: from.y + (to.y - from.y) * t + Math.sin(t * Math.PI) * sag + shake(r, wobble) * loose });
  }
  return pts;
}
function arcPts(c, { rx, ry }, { from, to }, { wobble = 0.03, steps = 28 }, r) {
  const pts = [];
  for (let i = 0; i <= steps; i++) {
    const a = ((from + (to - from) * (i / steps)) * Math.PI) / 180, k = 1 + shake(r, wobble);
    pts.push({ x: c.x + Math.cos(a) * rx * k, y: c.y + Math.sin(a) * ry * k });
  }
  return pts;
}
const MARKS = {
  underline: { viewBox: '0 0 140 10', cls: 'mk-underline', strokes: (() => { const r = createRandom(23); return [{ d: trace(stroke({ x: 3, y: 6 }, { x: 137, y: 5 }, { sag: -2 }, r)) }]; })() },
  doubleUnderline: { viewBox: '0 0 140 16', cls: 'mk-double', strokes: (() => { const r = createRandom(41); return [
    { d: trace(stroke({ x: 3, y: 5 }, { x: 137, y: 4 }, { sag: -2 }, r)) },
    { d: trace(stroke({ x: 5, y: 12 }, { x: 135, y: 11 }, { sag: -1.2 }, r)), width: 1.8, opacity: 0.75 }]; })() },
  circle: { viewBox: '0 0 220 64', cls: 'mk-circle', strokes: (() => { const r = createRandom(101); return [
    { d: trace(arcPts({ x: 110, y: 32 }, { rx: 100, ry: 27 }, { from: 150, to: 520 }, { wobble: 0.035 }, r)), width: 3 },
    { d: trace(arcPts({ x: 110, y: 32 }, { rx: 95, ry: 24 }, { from: 165, to: 480 }, { wobble: 0.03 }, r)), width: 1.5, opacity: 0.55 }]; })() },
  highlight: { viewBox: '0 0 170 26', cls: 'mk-highlight', behind: true, strokes: (() => { const r = createRandom(163); return [{ fill: true, d: trace([
    ...stroke({ x: 5, y: 6 }, { x: 165, y: 5 }, { sag: -2, steps: 10 }, r), ...stroke({ x: 165, y: 5 }, { x: 165, y: 21 }, { steps: 3 }, r),
    ...stroke({ x: 165, y: 21 }, { x: 5, y: 22 }, { sag: 2, steps: 10 }, r), ...stroke({ x: 5, y: 22 }, { x: 5, y: 6 }, { steps: 3 }, r)], true) }]; })() },
};
class ClariMark extends HTMLElement {
  connectedCallback() {
    if (this._done) return; this._done = true;
    const mark = MARKS[this.getAttribute('variant') || 'underline'];
    const NS = 'http://www.w3.org/2000/svg';
    const svg = document.createElementNS(NS, 'svg');
    svg.setAttribute('viewBox', mark.viewBox); svg.setAttribute('fill', 'none');
    svg.setAttribute('preserveAspectRatio', 'none'); svg.setAttribute('aria-hidden', 'true');
    svg.setAttribute('class', 'mk ' + mark.cls);
    const paths = mark.strokes.map((s) => {
      const p = document.createElementNS(NS, 'path');
      p.setAttribute('d', s.d); p.setAttribute('pathLength', '1');
      if (s.fill) { p.setAttribute('fill', 'currentColor'); }
      else { p.setAttribute('stroke', 'currentColor'); p.setAttribute('stroke-width', String(s.width ?? 2.4)); p.setAttribute('stroke-linecap', 'round'); p.setAttribute('stroke-linejoin', 'round'); p.setAttribute('vector-effect', 'non-scaling-stroke'); }
      if (s.opacity) p.setAttribute('opacity', String(s.opacity));
      p.dataset.reveal = s.fill ? 'reveal' : 'stroke';
      svg.append(p); return p;
    });
    if (mark.behind) { const w = document.createElement('span'); w.className = 'mk-text'; w.append(...this.childNodes); this.append(w); this.prepend(svg); }
    else this.append(svg);
    if (reducedMotion.matches) return;
    const delay = Number(this.getAttribute('delay') || 0) * 1000;
    const anims = paths.map((p, i) => {
      const op = Number(p.getAttribute('opacity') ?? 1);
      const a = p.animate(p.dataset.reveal === 'reveal'
        ? [{ clipPath: 'inset(0 100% 0 0)' }, { clipPath: 'inset(0 0% 0 0)' }]
        : [{ strokeDasharray: '1', strokeDashoffset: '1', opacity: 0, offset: 0 }, { strokeDasharray: '1', strokeDashoffset: '0.999', opacity: op, offset: 0.001 }, { strokeDasharray: '1', strokeDashoffset: '0', opacity: op, offset: 1 }],
        { duration: 750, delay: delay + i * 160, easing: 'cubic-bezier(0.22, 0.61, 0.36, 1)', fill: 'backwards' });
      a.pause(); return a;
    });
    const io = new IntersectionObserver(([e]) => { if (e.isIntersecting) { anims.forEach((a) => a.play()); io.disconnect(); } }, { threshold: 0.25 });
    io.observe(this);
  }
}
customElements.define('clari-mark', ClariMark);

/* ---------- Componentry GithubCalendar, as a check-in calendar ---------- */
// Data: one letter per day, oldest first. g = their usual self, y = keep an eye
// on it, r = call their doctor, m = missed, . = no check-in scheduled yet.
const LEVEL = {
  g: { cls: 'cal-g', word: 'Their usual self', icon: 'check' },
  y: { cls: 'cal-y', word: 'Keep an eye on it', icon: 'q' },
  r: { cls: 'cal-r', word: 'Call their doctor', icon: 'bang' },
  m: { cls: 'cal-m', word: 'Missed check-in, family texted', icon: 'q' },
};
const ICONS = {
  check: '<path d="M5 12.5l4.5 4.5L19 7.5" fill="none" stroke="currentColor" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"/>',
  q: '<path d="M9 9.2a3 3 0 1 1 4.2 2.8c-.8.4-1.2 1-1.2 1.9v.6" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"/><circle cx="12" cy="18.3" r="1.7" fill="currentColor"/>',
  bang: '<path d="M12 5v9" stroke="currentColor" stroke-width="3.4" stroke-linecap="round"/><circle cx="12" cy="18.6" r="1.9" fill="currentColor"/>',
};
class ClariCalendar extends HTMLElement {
  connectedCallback() {
    if (this._done) return; this._done = true;
    const days = (this.getAttribute('days') || '').replace(/\s/g, '').split('');
    const end = new Date(this.getAttribute('end') || '2026-10-21T12:00:00');
    const fmt = new Intl.DateTimeFormat('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
    const grid = document.createElement('div');
    grid.className = 'cal-grid';
    grid.setAttribute('role', 'list');
    const tip = document.createElement('div');
    tip.className = 'cal-tip'; tip.hidden = true; tip.setAttribute('aria-hidden', 'true');
    // Pad the start so each column is one week, Monday at the top.
    const first = new Date(end); first.setDate(end.getDate() - (days.length - 1));
    const pad = (first.getDay() + 6) % 7;
    for (let i = 0; i < pad; i++) { const s = document.createElement('span'); s.className = 'cal-cell cal-pad'; s.setAttribute('aria-hidden', 'true'); grid.append(s); }
    days.forEach((code, i) => {
      const L = LEVEL[code]; const date = new Date(first); date.setDate(first.getDate() + i);
      const cell = document.createElement('span');
      cell.className = 'cal-cell squircle ' + (L ? L.cls : 'cal-none');
      cell.style.setProperty('--i', String(i));
      cell.setAttribute('role', 'listitem');
      const label = `${fmt.format(date)}: ${L ? L.word : 'no check-in'}`;
      cell.setAttribute('aria-label', label);
      if (L && code !== 'g') cell.innerHTML = `<svg viewBox="0 0 24 24" aria-hidden="true">${ICONS[L.icon]}</svg>`;
      const show = () => {
        tip.textContent = label; tip.hidden = false;
        const g = grid.getBoundingClientRect(), c = cell.getBoundingClientRect();
        tip.style.left = `${c.left - g.left + c.width / 2}px`; tip.style.top = `${c.top - g.top}px`;
      };
      cell.tabIndex = 0;
      cell.addEventListener('mouseenter', show); cell.addEventListener('focus', show);
      cell.addEventListener('mouseleave', () => (tip.hidden = true)); cell.addEventListener('blur', () => (tip.hidden = true));
      grid.append(cell);
    });
    const wrap = document.createElement('div'); wrap.className = 'cal-wrap';
    wrap.append(grid, tip);
    this.replaceChildren(wrap);
  }
}
customElements.define('clari-calendar', ClariCalendar);
