# Getting real delirium speech recordings: who to ask and what they need

Drafted 2026-10-20. **Nothing here has been sent.** Each email is a draft for the team to edit, sign and send from a real school or personal address. Fill in every `[bracket]` first.

## Who to contact

| Group | Person to email | Address | Why them | Source |
|---|---|---|---|---|
| Northwell / Feinstein Institutes (New York) | Dr Sunny X. Tang, Assistant Professor of Psychiatry | stang3@northwell.edu | First author of Tang et al. 2023 (33 inpatients aged 75+, 10 delirious; speech model AUC 0.90). Has an NIH R21 on speech biomarkers for delirium in hospitalized older adults ("IDOSA"), so the recordings are still being collected. Already shares a psychosis corpus on TalkBank, so she knows the data-sharing route. | Her ISCTM slides list the address and the R21: https://isctm.org/public_access/22nd_Annual/Presentation/Opler_Prize_Tang.pdf ; TalkBank Tang corpus: https://talkbank.org/psychosis/access/English/Tang.html |
| Northwell, second contact | Dr Liron Sinvani, geriatrician-hospitalist, leads Northwell's ED delirium detection program | Not found publicly. Ask Dr Tang to forward, or cc via the Northwell directory. | Clinical delirium lead; co-author on the speech work. | https://onlinelibrary.wiley.com/doi/10.1111/acem.70235 |
| Edinburgh Delirium Research Group | Prof Alasdair MacLullich, Professor of Geriatric Medicine, 4AT author | a.maclullich@ed.ac.uk | Senior author of Green et al. 2018 (45 inpatients, 15 delirious, audio-recorded conversation and Cookie Theft). Our app is a spoken 4AT, his test. | The 4AT contact page lists this address for permissions and questions: https://www.the4at.com/contact |
| Edinburgh / Glasgow, second contact | Dr Zoë Tieges, last author of Green et al. 2018 | Zoe.Tieges@glasgow.ac.uk | Ran the speech study day to day; works on smartphone attention tests for delirium. cc her on the MacLullich email. | https://www.gla.ac.uk/subjects/cms/staff/index.html/staffcontact/person/4cdde9ec8191 |
| DementiaBank (TalkBank, Carnegie Mellon) | Membership requests | talkbank@cmu.edu | Dementia, MCI and control speech with audio. No delirium, but good for "normal older voices" and the dementia-vs-delirium confusion. | https://talkbank.org/dementia/ and ground rules https://talkbank.org/share/rules.html |

## What each group will need from us

**Northwell and Edinburgh.** Neither paper's audio is public, and patient consent almost certainly did not cover handing raw recordings to an outside team. So the emails do not ask for the files. They ask for one of these, easiest first:
1. A short call for feedback on our approach.
2. Running our scoring code on their recordings inside their own systems, and sending back only the accuracy numbers. Nothing leaves their hospital.
3. Derived features or de-identified transcripts, if their ethics approval allows it.
4. Advice on building our own consented collection (the protocol, the consent form, the ethics route).

Expect them to ask for a supervising faculty member, what ethics approval we have (none yet), and a written plan. A student team with no school sponsor is unlikely to get data, but option 1 and 2 are realistic.

**DementiaBank** (quoted from the access page and ground rules):
- Register for TalkBank with the green Login button, read the Ground Rules, then email talkbank@cmu.edu with contact information, affiliation and "a brief statement about how you envision using the data".
- Access is "restricted to faculty members". Students must have a faculty advisor join as a member and request access for each student with start and end dates. "We will not respond to requests sent only by students."
- Data is CC BY-NC-SA 3.0: no commercial products, cannot be shared with anyone without a password, and cannot be built into a commercial model. Fine for research and the hackathon, but it can't become part of a product's training data later.
- The page notes the repository "is under review for potential modification", so terms may change.

That means the DementiaBank email has to come **from a teacher or professor**. Draft 3 is written for a student to send to that person, with the text they can forward to TalkBank.

## Draft 1: Northwell (Dr Sunny Tang)

**To:** stang3@northwell.edu
**Subject:** Student team building a home voice check for delirium: could we learn from your speech work?

Dear Dr Tang,

We are [names], a student team at [school] building a free phone app that helps families notice delirium at home. An older person answers the 4AT questions out loud each day (name, age, place, year, months backwards), and the app compares their answers and voice with their own normal days.

Your 2023 paper in the Journal of Psychiatry and Neuroscience is the closest work to ours, and the reason we think speech can do this at all. So far we have only tested on healthy and synthetic voices. The answer scoring holds up well, but we have no way to know how it does on people who actually have delirium.

We are not asking for your recordings. We would be very grateful for any of these:
- 20 minutes on a call to tell us what we are getting wrong.
- If your approvals allow, running our open-source scoring code on your recordings yourselves and telling us only how it did.
- Advice on how a small team could collect consented recordings properly.

Our code and results are here: https://github.com/bemah123456/north-2 [check this is public, or send a summary instead]. Our supervising teacher is [name, email]. Thank you for reading.

Best wishes,
[name], [school], [email]

## Draft 2: Edinburgh (Prof MacLullich, cc Dr Tieges)

**To:** a.maclullich@ed.ac.uk
**Cc:** Zoe.Tieges@glasgow.ac.uk
**Subject:** A spoken 4AT for families at home: student project asking for advice

Dear Professor MacLullich and Dr Tieges,

We are [names], a student team at [school]. We are building a free phone app that reads the 4AT items aloud to an older person at home, scores their spoken answers, and asks a family member whether any change was sudden. It also compares each day with that person's own usual days. We credit the 4AT under its CC BY 4.0 licence.

Green et al. (2018) shaped our design: shorter utterances and less relevant content were exactly the signals we try to pick up. Our scoring works well on healthy and synthetic voices, but we have never tested it on people with delirium, so we cannot claim it works.

We would be very grateful for:
- Your view on whether a spoken 4AT at home is sound, and what would make it unsafe.
- If your study's approvals ever allow it, running our open-source scoring on your recordings in your own environment and sharing only the results.
- Any guidance on the right way to collect consented recordings ourselves.

Code and results: https://github.com/bemah123456/north-2 [check this is public, or send a summary instead]. Our supervising teacher is [name, email].

With thanks,
[name], [school], [email]

## Draft 3: DementiaBank (student to faculty sponsor, then sponsor to TalkBank)

**Part A: student to teacher or professor**

**To:** [teacher or professor]
**Subject:** Could you sponsor our DementiaBank access for a delirium project?

Hi [name],

Our team is building a phone app that checks older people's speech for signs of delirium at home. To test it on real older voices we need DementiaBank, a research speech collection run by Carnegie Mellon. It is free, but they only accept requests from faculty, who then add students and take responsibility for how we use it (no sharing the files, no commercial use, research only).

Would you be willing to send the email below from your school address? It takes about five minutes: register at talkbank.org, then send it. I'm happy to handle everything else.

Thanks,
[name]

**Part B: sponsor to TalkBank**

**To:** talkbank@cmu.edu
**Subject:** DementiaBank membership request: [name], [school]

Hello,

I am [name, title] at [school, department], [email, phone]. I have registered on TalkBank and read the Ground Rules. I'd like to request DementiaBank membership for myself and access for these students, from [start date] to [end date]: [student names and emails].

Planned use: the students are building a non-commercial research prototype that screens older adults' speech for sudden cognitive change (delirium) at home. We would use the Pitt and other control and dementia recordings to (1) check how well speech recognition handles older voices, and (2) make sure the tool does not mistake ordinary dementia speech for delirium. The data will stay on our own machines, will not be shared or posted, and will not be uploaded to services that store it. We will cite DementiaBank as the Ground Rules require.

I accept responsibility for the students' use of the data.

Thank you,
[name]

## Before sending

- Decide who signs (names, school, a supervising teacher). None of this is in the project yet.
- The repo bemah123456/north-2 may be private. Either make it public first (a separate decision) or replace the link with a one-paragraph summary.
- Send the Northwell and Edinburgh emails from a school address if possible; researchers answer those more often.
- If no reply in two weeks, send one short follow-up, then stop.
