# Clari landing page

A one-page marketing site for Clari: `index.html`, `img/` (resized app screenshots), `media/` (the final demo video, re-encoded to about 4 MB) and `vendor/` (the built UI script and Arc UI's design tokens).

Serve the folder with any static server (for example `python3 -m http.server` inside `landing/`) and open it. The page loads `vendor/clari-ui.js` as a module, which browsers don't allow from `file://`. It isn't deployed anywhere yet; hosting and a domain wait on the team.

## Design tools

- **Arc UI** (`@arclux/arc-ui`): skip link, buttons, badge, results tabs, animated stat numbers, the "Where Clari is today" timeline, the video player and the FAQ accordion. Its tokens are remapped to the page's three colours with glows and gradients turned off (top of the `<style>` block).
- **Wired Elements**: the hand-drawn "fridge note" cards in the one-week story and beside the home screen.
- **thinking-orbs**: the dotted listening and comparing orbs, drawn with its framework-free engine and tinted ink.
- **Space UI** (`@usespaceui/squircle`): iOS-style smooth corners on panels and screenshots.
- **Componentry**: `AnnotatedText` (the circled and underlined words) and `GithubCalendar` (reworked as the five-week check-in calendar), ported from React to plain custom elements in `src/ui.js`.

## Colours

Two quiet colours and one loud one; everything else is a `color-mix()` tint of these:

- **Pine** `#173A33` (quiet): text, the dark bands, "their usual self".
- **Mist** `#EEF2EC` (quiet): the page.
- **Cobalt** `#2433E0` (loud): only the main buttons, the hand-drawn marks and anything that means "pay attention" (a cobalt ring for "Keep an eye on it", solid cobalt for "Call their doctor").

In the CSS they're `--ink`, `--paper` and `--signal`, so a new palette only changes those three values (plus the matching `-rgb` values). Dark mode swaps pine and mist and lifts the cobalt with mist (`#7F89E5`) so it still stands out. The nav logo is `img/logo-mark-cutout.png` used as a CSS mask, so it takes the text colour. The app screenshots and demo video still show the app's own navy and teal. Before and after screenshots of the 2026-11 restyle are in `screenshots/`.

## Rebuilding the script

```sh
cd landing
npm install
npm run build   # writes vendor/clari-ui.js and vendor/arc-tokens.css
```

The built files are committed, so the page works without a build.

## Content rules

Copy comes from the final pitch script and the app. It keeps the limits up front: screening aid, not a diagnosis, and not yet tested with people who have delirium. Statuses always show a symbol and a word as well as a colour, and body text keeps 7:1 contrast in light and dark themes (mist text on cobalt is 7:1). Stats are cited in the footer (Inouye 2014, Han 2009, Tieges 2021).

To refresh a screenshot, resize the new PNG from `daily-checkin/screenshots/clari/` to 520 px wide and save it as WebP under `img/`.
