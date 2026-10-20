# How delirium sounds in speech: public clips and datasets

Compiled 2026-10-19. Every link below was checked by me (page or video title fetched) unless marked "unverified". ChatGPT (Codex CLI) and Gemini (agy CLI) were also asked; their raw answers are in `gpt_answer.md` and `gemini_answer.md` in this folder. ChatGPT's leads mostly checked out. Several of Gemini's papers and links did not and are listed at the end.

**Bottom line:** no open, downloadable corpus of delirious speech exists. The best free listening material is a set of labelled assessment interview videos (3D-CAM) and acted teaching vignettes. Real patient recordings exist only inside a few studies, which you would have to ask the authors for.

## 1. Best for hearing it: labelled assessment interviews

| Clip | What it shows | Access |
|---|---|---|
| 3D-CAM Patient 1, Day 1: https://vimeo.com/441329149/d683599b1b | Older inpatient answering the 3D-CAM questions (year, day, digits backwards, months backwards, confusion and hallucination questions). Answer key: no delirium, score 0/20. About 3 min. | Free to watch on Vimeo, posted by AGS CoCare and linked from Delirium Central. No stated reuse licence; the CAM form says "not to be reproduced without permission". |
| 3D-CAM Patient 1, Day 2: https://vimeo.com/441330711/eaad50f4b3 | Same patient. Answer key: inattention errors (digits, months backwards) and a hallucination "yes", score 5/20, but **not** delirium. Good example of a near-miss. | Same |
| 3D-CAM Patient 2, Day 1: https://vimeo.com/441331739/b56c5be375 | Answer key: no delirium, 1/20. | Same |
| 3D-CAM Patient 2, Day 2: https://vimeo.com/441333183/3c7e4466c5 | **Delirium present**, 13/20. Wrong year and place, fails digits, days and months backwards, sleepy, distracted, illogical flow of ideas, fluctuating attention. | Same |
| 3D-CAM Patient 3, Day 1: https://vimeo.com/441334168/d798c9082b | No delirium, 2/20 (one illogical answer). | Same |
| 3D-CAM Patient 3, Day 2: https://vimeo.com/441335048/880af7ecf4 | **Delirium present**, 6/20. Wrong year and place, fails digits and months backwards, sleepy. | Same |

Index page with Spanish-subtitled copies and the answer-key PDFs: https://www.deliriumcentral.org/delirium-instruments/

Why these matter: Patients 2 and 3 are each recorded on a day without and a day with delirium, which is exactly the "same person, before vs during" contrast a voice app would look for. The site does not say whether these are real patients or actors.

## 2. Acted teaching vignettes (good for intuition, not for training a model)

| Clip | What it shows | Access |
|---|---|---|
| Hypoactive Delirium: https://www.youtube.com/watch?v=db5-mMAyYcE | Acted vignette from QUT's "Learn Delirium" project | Free on YouTube |
| Hyperactive Delirium: https://www.youtube.com/watch?v=8ukWKPVj5xA | Acted vignette, same series | Free on YouTube |
| Hypoactive Delirium Superimposed on Dementia: https://www.youtube.com/watch?v=pEpnMtv0Dzc | Acted vignette, same series | Free on YouTube |
| Hyperactive Delirium Superimposed on Dementia: https://www.youtube.com/watch?v=OThAMJ4bUz4 | Acted vignette, same series | Free on YouTube |
| How to do the 4AT: 10-minute teaching video with 3 cases: https://youtu.be/cFZcBcmqEqY | Think Delirium (Prof. MacLullich, 4AT author) walking through 3 cases. Most relevant to the spoken-4AT plan. | Free on YouTube; 4AT site content is CC BY 4.0 unless stated otherwise |
| 4AT explained (under 3 min): https://youtu.be/ncbgH_Pnkqk | Quick 4AT overview, Think Delirium | Free on YouTube |
| Hyperactive Delirium Patient Experience: https://www.youtube.com/watch?v=RXBxEGgoC10 | Fictional first-person scenario of hyperactive delirium | Free on YouTube |
| Simulation Scenario: Delirium Care: https://www.youtube.com/watch?v=Ovik1yVzSt4 | Nursing simulation, Western Australian Clinical Training Network | Free on YouTube |
| CAM-ICU video series: https://vimeo.com/showcase/9768694 | 7 short CAM-ICU videos. The patient is simulated and **mechanically ventilated**, so there is almost no speech. | Free on Vimeo |
| ADHERe Delirium Care videos: https://www.adhere.org.au/delirium-care | 4AT in a nursing home, oncology clinic and acute hospital; CAM in hospital; 5-part patient journey | Page is free; video hosting and terms not stated |
| UB-CAM educational video: https://youtu.be/_tdv2nC5aF4 | Tutorial for the UB-CAM screen. Its "patient with delirium" case video is listed as coming soon. | Free on YouTube |
| 4AT written cases: https://www.the4at.com/4atcases | Six text-only cases describing speech (e.g. "incomprehensible", intermittent yes/no) | Free, CC BY 4.0 |
| Long CAM training video: https://www.deliriumcentral.org/delirium-instruments-application-form/ | Formal CAM training | Free but needs an application form (emailed in 24-48 h). I did not apply. |

## 3. Studies that recorded real delirious patients

| Study | What was recorded | Data access |
|---|---|---|
| Tang et al. 2023, J Psychiatry Neurosci, "Characterizing and detecting delirium with clinical and computational measures of speech and language disturbance": https://pmc.ncbi.nlm.nih.gov/articles/PMC10322161/ | 33 inpatients aged 75+ in New York (10 delirious). Narratives, picture description, paragraph reading, fluency. Speech-based model reached 78% accuracy (AUC 0.90). Delirium showed more incoherence and lower category fluency. | No public audio. Contact authors (Northwell / Feinstein Institutes). Closest existing work to this project. |
| Green et al. 2018, PLoS ONE, "Investigating speech and language impairments in delirium": https://pmc.ncbi.nlm.nih.gov/articles/PMC6261049/ | 45 Edinburgh inpatients (15 delirium, 15 dementia, 15 controls). Conversation and Cookie Theft picture description, audio-recorded. Delirium gave shorter utterances and less relevant content. | Only a small anonymised CSV of scores is public (also on figshare: https://figshare.com/articles/dataset/Investigating_speech_and_language_impairments_in_delirium_A_preliminary_case-control_study/7383131/1). No audio or transcripts. Same group as the 4AT (MacLullich). |
| Maybrier et al. 2018, BMJ Open, delirium assessment reliability: https://pmc.ncbi.nlm.nih.gov/articles/PMC6252643/ | Videos of 9 real postoperative patients aged 60+ (3 CAM-positive) in St Louis | Password-protected Vimeo; paper says data "can be made available upon request" |
| Shaw et al. 2022, Int J Nurs Stud, "Nurse Talk" elderspeak study: https://experts.umn.edu/en/publications/characteristics-of-elderspeak-communication-in-hospital-dementia-/ | 88 audio-recorded nurse-patient encounters, 16 patients with dementia, some with delirium. Focus is nurse speech. | No public audio found |
| Khan et al. 2020, Acoustical Society abstract on speech after lobectomy or esophagectomy (unverified: PDF too large to open) https://acousticalsociety.org/wp-content/uploads/2020/10/PAS_148_4.pdf | Daily postoperative speech recordings aimed at delirium-related change | No public audio found |
| Tate et al. 2013, J Gerontol Nurs: https://pmc.ncbi.nlm.nih.gov/articles/PMC4006194/ | Video of ICU patients, 43% delirious at some point, but all **intubated and nonspeaking** | Not useful for voice |

## 4. Related speech datasets (no delirium labels)

| Dataset | Contents | Access |
|---|---|---|
| DementiaBank / TalkBank: https://talkbank.org/dementia/access/ | Audio and transcripts for dementia, MCI, PPA and controls (Pitt, Delaware, Baycrest, Kempler, Lu, WLS and others). No delirium corpus. Standard comparison data for cognitive speech models. | Research membership via TalkBank; free for researchers but password protected |
| Bridge2AI-Voice: https://physionet.org/content/b2ai-voice/ | NIH voice-biomarker dataset, 833 adults in v3.1.0, including neurological conditions | PhysioNet credentialed access gives derived features only. Raw audio needs a Synapse request with institutional sign-off. |

## 5. What I could not confirm (mostly from Gemini)

- "Gurlitt et al. 2021", "Sultana et al.", "Voigt et al. 2020" delirium speech papers: Gemini gave no real citation and admitted the DOI was approximate. Treat as made up.
- YouTube video `1o-8TjEw5mI` ("Think Delirium 4AT in Practice"): does not resolve. The real 4AT videos are listed in section 2.
- `icudelirium.org/.../cam-icu-training-videos`: returns 404. The site's monitoring page lists CAM-ICU videos but the links are empty placeholders.
- First 4AT search hit `youtube.com/watch?v=hJiTxbJWKKc`: does not resolve (likely replaced by `cFZcBcmqEqY`).
- Gemini's claims that Stanford Medicine 25, BGS and Geeky Medics host delirium speech demos: not checked; links were generic home pages.

## What this means for the project

1. There is no off-the-shelf dataset to train a delirium voice model. The project will need its own recordings, which fits the spoken-4AT plan: record the 4AT tasks (name, age, place, year, months backwards) and score them.
2. The 3D-CAM Day 1 vs Day 2 videos for Patients 2 and 3 are the best free material for designing features and demoing the idea.
3. The two research groups worth contacting are Tang / Sinvani (Northwell) and MacLullich / Tieges (Edinburgh, also the 4AT authors).
4. Watching these videos is fine. Downloading or training on them needs permission from the owners; none has an open reuse licence except the 4AT site text.
