# Daily Check-in: Executive Summary

> Copy of the live Claude Doc at https://claude.ai/artifact/C9ZRMchkCXuRyZsPstwZ8x (saved 2026-10-21). Edit the live doc; refresh this copy after.

**The Heist Hackathon, Health Tech vault** (Aging in Place: safety and monitoring) · Team: [Team name]

## Problem

Delirium is a sudden change in thinking that affects up to 50% of hospitalized older adults, costs over $164 billion a year in the US, and is preventable or treatable in many cases when caught early (Inouye et al., The Lancet, 2014). The quiet form, where someone is sleepy and withdrawn, is the most common in older adults and is easy to mistake for a bad day. At home, nobody is checking every day, so it can go unnoticed for days.

## Solution

Daily Check-in is a phone app that gives an older adult a 2-minute spoken check-in each day. It reads a few questions aloud, listens to the answers, scores them with the rules of the 4AT (a validated, free delirium screen), and compares their voice with their own usual days. The family sees one plain result with the reasons: "Looks like their usual self", "Keep an eye on it" or "Call their doctor today". If the check-in is skipped, the family gets a text, because withdrawal is itself a warning sign.

## Key features

- Spoken questions and spoken answers, with large type and no typing for the senior
- All four 4AT parts: alertness, orientation (age, birthday, place, year), attention (months backwards, a rotating version, or repeating digits) and acute change
- Questions change order and wording every day so they can't be memorized
- A personal voice baseline: response time, speaking pace, pauses and hesitations compared with that person's normal
- Missed check-in alerts: reminders first, a family text after 3 hours, and a pattern flag after 2 missed days; families can mark days off
- An optional evening check-in for late-day confusion, a drowsiness check, and a 0–100 change score showing how far today is from the person's usual
- An AI judge only for unclear answers, and a person can always override the score

## Target user

Older adults living at home, especially in the weeks after a hospital stay, and the adult children who look out for them from a distance. Paying customers would be hospital-at-home programs, home-care agencies and Medicare Advantage plans (per patient per month), with a family subscription as a second route. US adults 65+ have about 13 million hospital stays a year (AHRQ HCUP, 2012). Pricing is a hypothesis to test in a pilot.

## What's built

A working prototype: an Expo app (iPhone, Android and web) and a Python server that transcribes recordings, scores the 4AT, builds each person's voice baseline and sends reminders and family alerts. It has 84 automated tests. Common speech-to-text slips are fixed before scoring, and an answer the app can't make out is asked again. On real speakers aged 60+, the recommended speech model with these fixes marked no right answers wrong in a quiet room (2% with background noise). The app checks the room before starting and asks once if a TV is on. Texts and AI scoring are switched off in the demo. Limits: this is screening, not diagnosis; the voice model has only been trained on simulated data; it has not yet been compared with clinicians.

## Team roles

- Name: Technical lead
- Name: Business lead
- Name: Pitch lead

## Links

- Pitch deck: https://claude.ai/artifact/NSYfpvN1PXQqLioYZnZRzV
- Demo: [demo video or app link]
- Code: [repo link]
