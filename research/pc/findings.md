# Findings (verified), spoken 4AT for delirium

## Official 4AT scoring (checked at https://www.the4at.com/userguide)
- Alertness: 0 normal (or <10 s mild sleepiness after waking); 4 clearly abnormal (marked drowsiness or agitation). Clinician observation.
- AMT4 (age, date of birth, place, year): 0 no mistakes; 1 one mistake; 2 two or more, or untestable. "The hospital" style answers accepted for place.
- Months backwards from December (one prompt allowed): 0 = 7+ correct; 1 = starts but <7, or refuses; 2 = untestable (cannot start because unwell, drowsy, inattentive).
- Acute change or fluctuation in the last 2 weeks, still evident in 24 h: 0 no, 4 yes (from informant, e.g. family).
- Total 4+ suggests delirium; 1-3 cognitive impairment; 0 unlikely. Hearing loss and language barriers must be considered.
- Evidence for months backwards alone: O'Regan et al. 2014, J Neurol Neurosurg Psychiatry 85(10):1122-31, doi 10.1136/jnnp-2013-307053 (265 inpatients; MOTYB was the most accurate single screen in older people).

## Speech measures worth extracting (Gemini round 2, filtered by me)
Usable and grounded:
- Per question: response latency, number of re-prompts, answer correctness (fuzzy match).
- Months backwards: longest correct run from December, omissions, reversals to forward order, perseverations, intrusions, total time, gaps between months.
- Whole session: pause-to-speech ratio, speech rate, disfluency and self-repair counts, loudness and pitch variability (monotone, trailing off).
- Change from the same person's own baseline (z-scores against 3+ normal recordings) is the strongest idea for a family app, since delirium is an acute change.

Treat as unvalidated (Gemini invented the numbers): the 10 s / -35 dBFS / 5.5 syll/s alertness cutoffs, 3000 ms month-gap threshold, 50% diurnal swing, z>3 rule, 0.35 similarity cutoff. Vowel space, jitter and shimmer need sustained vowels the 4AT does not elicit.

## Engineering notes
- Keep the 4AT scoring rule-based; use speech models only to extract answers and timing.
- Closed-grammar recognition (Vosk with month words) helps accuracy but can hide errors; also run an open pass or log confidence.
- "Untestable because of hearing" must stay separate from a low score.
- Licences: openSMILE is not free for commercial use; aubio is GPL. Silero VAD (MIT), Vosk (Apache 2.0), whisper.cpp (MIT) are fine.

## Training a detector: current blocker
No labelled delirium audio is public. Options, in order of value:
1. Collect our own recordings with consent and a clinician 4AT/CAM label (needs a clinical partner and ethics approval).
2. Ask the Tang (Northwell) or Green/MacLullich (Edinburgh) groups for data access.
3. Train proxy models on DementiaBank (cognitive impairment, not delirium); needs the user to apply for TalkBank membership.
4. Use the 6 public 3D-CAM videos only as a demo and test set (too few to train on, and no reuse licence).

## Round 2 literature (ChatGPT search, key items spot-checked by me)
Delirium-specific recorded speech beyond round 1 is almost all conference abstracts with no accuracy figures:
- Khan et al. 2020, JASA abstract 2pSCc11 (doi 10.1121/1.5147179): 16 thoracic surgery patients, daily "h-vowel-d" word recordings to track delirium; no results reported.
- Dappen et al. 2025, APAN poster: audio + intracranial EEG during delirium assessments in epilepsy patients; neural, not a voice classifier.
Best adjacent evidence (acute encephalopathy from liver disease, same brain mechanism family):
- Moon et al. 2022, Hepatology Communications (checked, PMC9512449): 43 participants, iPad + clip-on mic. Overt encephalopathy reading rate 48 wpm vs 151-164 in others; speech rate recovered as encephalopathy resolved. Strong support for "slowed speech + within-person recovery" as a signal.
- Bloom et al. 2024, Hepatology, HEAR-MHE (checked via news coverage, doi 10.1097/HEP.0000000000001086): 200 cirrhosis + 50 controls; 752 speech features (Winterlight); 3-feature model AUC 0.76 for minimal encephalopathy, 0.82 with age and MELD; speech rate <137 wpm linked to ~7x risk of later overt encephalopathy.
- Gazda et al. 2025, npj Digital Medicine (doi 10.1038/s41746-025-02276-9; not opened, paywall redirect): 93 participants, 15 s sustained vowels, XGBoost AUROC 0.81; model weights public on GitHub.
Digital (non-voice) delirium screening:
- Mulligan et al. 2022 (checked, PMC9675648): verbal vs tablet months-backwards correlate 0.77 overall; authors propose speech recognition as future work. Nobody has built it yet -> open gap for this project.
- UB-CAM app (Armstrong 2021 JAMIA Open; Marcantonio 2022 Ann Intern Med) and Chinese 3D-DST app (Wang 2024 JMIR Aging): clinician-entered, no voice capture.
- Jeffcock et al. 2023 HRI: robot CAM-ICU with speech recognition, role-played participants only.
Lead to follow: Ghezzi et al. 2021 TAVI protocol (Front Cardiovasc Med) planned iPad voice pitch measures to predict delirium; check whether results were published.

Conclusion after round 2: an automated, voice-scored 4AT / months-backwards test for delirium has not been published. That is the project's opening.

## Round 3: data strategy, regulation, speech recognition (GPT + Gemini, checked by me where noted)
Data and training (GPT, round3_gpt_data_strategy.md):
- Labels: clinician 4AT/CAM within 15-60 min of the recording, as in McCartney et al. 2025 Age Ageing 54(6):afaf166 (checked: 120 delirious inpatients, 4AT sensitivity 0.94-0.96 at repeat assessments for tracking recovery).
- Record daily through onset and recovery; a baseline before illness (e.g. planned surgery) is what makes "change from usual" possible. Split train/test by person.
- Consent: proxy/consultee routes and deferred consent have published delirium precedents (Green 2018, Shenkin 2019 4AT study); needs local ethics approval.
- Pilot target (GPT's proposal, not from a paper): 100-150 people, 30-50 with confirmed delirium, 4-7 days of recordings each.
- Acted delirium speech: no evidence it helps real detection; use only for testing the app. Dementia (DementiaBank) or liver encephalopathy data may help pretraining but transfer is unproven.
- Trainable now with no delirium audio: elderly-speech recognition tuning (Mozilla Common Voice, CC0, has optional age labels), the months/AMT4 parser (done, rule-based), latency and noise checks. SeniorTalk (checked: 202 Mandarin speakers aged 75-85, 55.5 h, CC BY-NC-SA, non-commercial) is not usable for an English commercial app.
- Partners: Tang/Sinvani/Liberman (Northwell + Penn), MacLullich/Tieges (Edinburgh, 4AT authors), Moon/Haley/Jacks (UNC, encephalopathy speech), CUHK elderly ASR group.
Regulation (Gemini, round3_gemini_reg_asr.md, partly corrected):
- A voice delirium screen sold to families is very likely a medical device (software as a medical device), not "general wellness". FDA's existing category for app cognitive screening is product code PKQ, "computerized cognitive assessment aid", Class II, 21 CFR 882.1470 (checked; Gemini's codes QLM/QNP were wrong). Precedents: Cognivue via De Novo DEN130033, CANTAB Mobile K161328. No voice-based delirium device is cleared.
- EU MDR Rule 11: at least Class IIa, possibly IIb. UK: MHRA, rules in transition.
- Privacy: HIPAA usually not for a direct-to-consumer app, but FTC Health Breach Notification Rule applies; GDPR health data needs explicit consent and a DPIA; Illinois BIPA if voiceprints are stored. Safer design: extract measures on the device and do not keep raw audio unless the user opts in.
- Until cleared, describe it as tracking speech and attention exercises to share with a clinician, not "detects delirium". Renaming alone does not change intended use.
Speech recognition (Gemini, unverified estimates): whisper.cpp base on device, Vosk with a month grammar as fallback; Web Speech API is fine for a prototype but sends audio to the browser vendor. Our own scorer (prototype/scorer.js) replaces Gemini's buggy scoring code.

## Prototype (built 2026-10-19)
prototype/index.html + scorer.js: family answers alertness and acute-change items, phone asks AMT4 and months backwards by voice, scores per official 4AT, measures latency and gaps between months, and compares with the person's own saved normal days. 15/15 unit tests pass (node --test); full flow checked in a browser with simulated speech.
