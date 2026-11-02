# Clari landing page

A one-page marketing site for Clari: `index.html`, `img/` (resized app screenshots), `media/` (the final demo video, re-encoded to about 4 MB) and `vendor/` (the built UI script and Arc UI's design tokens).

Serve the folder with any static server (for example `python3 -m http.server` inside `landing/`) and open it. The page loads `vendor/clari-ui.js` as a module, which browsers don't allow from `file://`. It isn't deployed anywhere yet; hosting and a domain wait on the team.

## Design tools

- **Arc UI** (`@arclux/arc-ui`): skip link, buttons, badge, results tabs, animated stat numbers, the "Where Clari is today" timeline, the video player and the FAQ accordion. Its tokens are remapped to Clari's navy and teal with glows and gradients turned off (top of the `<style>` block).
- **Wired Elements**: the hand-drawn "fridge note" cards in the one-week story and beside the home screen.
- **thinking-orbs**: the dotted listening and comparing orbs, drawn with its framework-free engine and tinted teal.
- **Space UI** (`@usespaceui/squircle`): iOS-style smooth corners on panels and screenshots.
- **Componentry**: `AnnotatedText` (the circled and underlined words) and `GithubCalendar` (reworked as the five-week check-in calendar), ported from React to plain custom elements in `src/ui.js`.

## Rebuilding the script

```sh
cd landing
npm install
npm run build   # writes vendor/clari-ui.js and vendor/arc-tokens.css
```

The built files are committed, so the page works without a build.

## Content rules

Copy comes from the final pitch script and the app. It keeps the limits up front: screening aid, not a diagnosis, and not yet tested with people who have delirium. Statuses always show a symbol and a word as well as a colour, and text keeps 7:1 contrast in light and dark themes. Stats are cited in the footer (Inouye 2014, Han 2009, Tieges 2021).

To refresh a screenshot, resize the new PNG from `daily-checkin/screenshots/clari/` to 520 px wide and save it as WebP under `img/`.
