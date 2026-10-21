# Daily Check-in: Pitch Script

> Copy of the live Claude Doc at https://claude.ai/artifact/CVy5eqNcaKWJTkT1Qtn5bJ (saved 2026-10-21). Edit the live doc; refresh this copy after.

A word-for-word script for the 8-minute pitch video, timed at about 7 minutes 15 seconds when read at a calm pace, which leaves room for pauses. Record it by Oct 24, 2026 so there's a day to redo it. Swap in your own words wherever they feel stiff; the timings matter more than the wording.

| Slide | Speaker | Time | Running total |
| --- | --- | --- | --- |
| 1. Team and vault | Pitch lead | 0:30 | 0:30 |
| 2. Problem | Pitch lead | 1:00 | 1:30 |
| 3. Heist plan | Pitch lead | 0:50 | 2:20 |
| 4. How it works | Technical lead | 1:20 | 3:40 |
| 5. Technical challenges | Technical lead | 1:10 | 4:50 |
| 6. Market | Business lead | 1:00 | 5:50 |
| 7. Impact and sustainability | Business lead | 0:55 | 6:45 |
| 8. Close | Pitch lead | 0:30 | 7:15 |

## 1. Team and vault (0:30)

"We're [team name], and we're cracking the Health Tech vault. Our heist is about time: the days between the morning an older parent starts to get confused and the moment someone notices. We built Daily Check-in, a two-minute spoken check-in that helps families catch delirium early, so their parents can keep living safely at home."

## 2. Problem (1:00)

"Delirium is a sudden change in thinking. One day someone is themselves; the next they're muddled about the year, can't follow a conversation, or are just unusually sleepy. It affects up to half of older adults in hospital, and it costs the US over 164 billion dollars a year. And 30 to 40 percent of cases can be prevented.

The hard part is noticing. The most common kind in older adults is the quiet kind: sleepy and withdrawn. It looks like a bad day. If you live two states away and call your mom on Sundays, you can miss it for most of a week.

So the problem we're cracking is simple to say: nobody is checking every day, in a way that would catch a change."

## 3. Heist plan (0:50)

"Our plan has three steps.

First, they talk. Every day, the app reads a few short questions aloud, and your parent answers out loud. No typing, no menus.

Second, we compare. The answers are scored with the 4AT, a validated delirium screen that clinicians use at the bedside. And their voice is compared with their own normal days, not with anyone else.

Third, the family knows. You get one plain result with the reasons. And if your parent doesn't open the app at all, you get a text, because withdrawal is a warning sign too."

## 4. How it works (1:20)

"Here's the senior's screen. Big type, one question at a time. The app speaks the question, listens, and moves on by itself after a few seconds of quiet.

The questions cover all four parts of the 4AT. Alertness: are they answering, and how quickly? Orientation: their age, birthday, where they are and what year it is. Attention: months of the year backwards, a rotating version like counting down from twenty, or repeating a short string of digits. And acute change: is today different from their usual?

The wording and order change every day, so nobody can memorize the answers.

On the family's side, there are three possible results: 'Looks like their usual self', 'Keep an eye on it', or 'Call their doctor today'. Each comes with plain reasons, like 'got the year wrong' or 'slower to answer than usual'. Tap a day and you can see exactly what they said.

This is a working app, not a mock-up: an Expo app for iPhone, Android and the web, and a Python server that transcribes, scores and sends the alerts. Families can add an evening check-in too, because confusion often gets worse late in the day, and a change score from 0 to 100 shows how far today is from their usual."

## 5. Technical challenges (1:10)

"Three things made this hard.

First, there's no public dataset of delirious speech. So instead of one model for everyone, we compare each person with their own baseline. Their pace, their pauses and how long they take to answer are compared with their own normal days.

Second, speech recognition mishears older voices. We compared eight speech models, then tested the best ones on real recordings of speakers over sixty. We found the patterns that make a healthy answer look wrong, like 'eighty too' instead of eighty-two, and fixed them. With those fixes and a hint listing the months, Whisper small marked no right answers wrong in a quiet room, and two percent with background noise. If the app hears speech but can't make out the answer, it asks the question once more, and if it still can't tell, a person checks it instead of the app counting it wrong.

Third, a TV in the background makes every model struggle. So before the first question, the app listens to the room and asks them to turn it down. If it hears another voice behind their answers, it asks once whether a TV is on and repeats the question. We tuned that check on real recordings so it comes up in fewer than two percent of quiet check-ins.

It has 84 automated tests, and we've been honest about the limits. It's a screening tool, not a diagnosis, and the voice model has only seen simulated data so far."

## 6. Market (1:00)

"We start where the risk is highest: the weeks after a hospital stay. Adults over 65 have about 13 million hospital stays a year in the US, and that's when delirium is most likely.

Our users are older adults living at home and the adult children who worry about them from a distance.

Our customers are the organizations that lose money when delirium is missed: hospital-at-home programs, home-care agencies and Medicare Advantage plans. A missed case means a longer stay, a readmission, or a move to a nursing home. We'd charge them per patient per month, and families could also subscribe directly.

The way in is the discharge desk. When a parent leaves the hospital, the family is paying attention, and that's the moment to set up the app."

## 7. Impact and sustainability (0:55)

"The impact is days. Families call the doctor the day thinking changes, not days later. Seniors keep their independence with a two-minute routine. Clinicians get a daily trend instead of a single snapshot.

It also gets better the more it's used. Each person's baseline sharpens with every check-in. With consent, those daily recordings become a dataset that doesn't exist anywhere today. And every senior comes with relatives who see the value every single day.

Our next step is a pilot with families after discharge, comparing our results with clinicians' own 4AT scores."

## 8. Close (0:30)

"Delirium is common, costly and often preventable, and the quiet kind slips past families every day. Daily Check-in gives them two minutes a day of attention, so they notice sooner. We're [team name]. Thank you."

## Recording tips

- Record each slide as its own take, then join them, so one stumble doesn't mean starting over.
- Read a little slower than feels natural. Older-adult health is a topic where calm sounds credible.
- Keep slide 4 on screen while the demo walkthrough plays in the separate demo video; don't play the video inside the pitch, because the demo has its own 5-minute slot.
- If you run long, cut from slide 5 first: the judges will see the technical detail in the demo and the repo.

## Sources for the numbers

- Up to 50% of hospitalized seniors, $164 billion a year, 30 to 40% preventable, hypoactive form most common in older adults: [Inouye, Westendorp & Saczynski, "Delirium in elderly people", The Lancet, 2014](https://pmc.ncbi.nlm.nih.gov/articles/PMC4120864)
- About 13 million hospital stays a year by adults 65+: [AHRQ HCUP Statistical Brief 180, 2012](https://hcup-us.ahrq.gov/reports/statbriefs/sb180-Hospitalizations-United-States-2012.pdf) (9.7 million at ages 65 to 84 plus 3.0 million at 85+)
- 8 speech models compared; on real speakers aged 60+, Whisper small with the month hint marked 0% of right answers wrong in quiet and 2% with noise; the TV question on 1.7% of real check-ins with no TV known: the project's own speech model comparison (real older speakers from Common Voice plus synthetic voices, not patients)
