# Clari landing page

A one-page marketing site for Clari: `index.html` plus `img/` (resized app screenshots) and `media/` (the final demo video, re-encoded to about 4 MB). Plain HTML and CSS, no build step and no dependencies; fonts come from Google Fonts.

Open `index.html` in a browser to view it. It isn't deployed anywhere yet; hosting and a domain wait on the team.

- Copy comes from the final pitch script and the app. It keeps the limits up front: screening aid, not a diagnosis, and not yet tested with people who have delirium.
- Design follows the app's look (`daily-checkin/app/src/theme.ts`): navy text and buttons, teal graphics only, Nunito and Atkinson Hyperlegible, 7:1 text contrast, statuses always shown as symbol + word + colour, light and dark themes, reduced-motion support.
- Section order and wording were checked against suggestions from ChatGPT and Gemini (say "adapted from the 4AT", no accuracy claims, missed days never look good, a short FAQ).
- Stats in the "Why it matters" section are cited in the footer (Inouye 2014, Han 2009, Tieges 2021).

To refresh a screenshot, resize the new PNG from `daily-checkin/screenshots/clari/` to 520 px wide and save it as WebP under `img/`.
