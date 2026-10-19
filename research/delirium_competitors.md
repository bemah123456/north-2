# Competing delirium and speech-cognition tools: where they fall short

Compiled 2026-10-19. Sources were checked unless marked "inferred".

**Bottom line:** nobody sells a voice-based delirium screener, and nobody sells a delirium tool for families at home. Delirium products are hospital-only (EEG, EHR models, clinician apps). Voice products target dementia/MCI for clinicians and drug trials, and they score a one-off snapshot, which misses delirium's defining feature: sudden change from that person's normal. The opening is a family app that tracks change against the person's own voice baseline.

## The landscape

| Product | What it does | Where it falls short |
|---|---|---|
| **Ceribell delirium monitor** ([FDA 510(k), Dec 2025](https://www.biospace.com/press-releases/ceribell-receives-fda-510k-clearance-for-first-of-its-kind-delirium-monitoring-solution)) | AI on bedside EEG headband, alerts on delirium patterns. First FDA-cleared delirium device. Validated on 225 adults. | ICU and ER only, needs EEG hardware and staff. No accuracy figures published in the release. Useless once the patient goes home. |
| **Mount Sinai AI model** ([press release, 2025](https://www.mountsinai.org/about/newsroom/2025/ai-model-improves-delirium-prediction-leading-to-better-health-outcomes-for-hospitalized-patients)) | EHR data plus NLP on nurses' notes flags high-risk inpatients. Detection rose from 4.4% to 17.2% of admissions across 32,000 patients. | Needs a hospital's records and a delirium team. Predicts risk, does not assess the patient. Single-site so far. |
| **UB-CAM app** ([App Store](https://apps.apple.com/us/app/-/id1591656740), [pilot](https://pmc.ncbi.nlm.nih.gov/articles/PMC8681914)) | Clinician taps through a 2-step CAM screen, about 90 seconds. Earlier version over 85% accurate. | Someone trained must ask and score the questions. No audio. Clinical audience. |
| **4AT app** ([App Store](https://apps.apple.com/us/app/-/id6450703321), Tactuum) | Free digital 4AT form, under 2 min. | Just a form; a clinician administers it. No voice, no tracking over time. |
| **FAM-CAM** ([Hebrew SeniorLife, Oct 2025](https://www.hebrewseniorlife.org/news/new-study-finds-family-and-caregivers-can-help-spot-post-surgery-delirium-early)) | Paper questionnaire for family. Agreed with researchers about 80% of the time in 817 surgical patients; at home, half the post-discharge delirium cases had been missed in hospital. | Paper, subjective, relies on the family remembering to use it. Only 133 of the families returned the home booklets. Strongest proof that families can catch delirium. |
| **Canary Speech** ([CHAI registry](https://registry.chai.org/canary-speech/canary-speech-vocal-biomarker-model-for-cognitive-)) | 40 s of conversation, flags MCI/Alzheimer's for clinicians, sits in Epic/Cerner. | Dementia, not delirium. Clinician tool, needs a quiet room and a set mic distance. No accuracy published on the registry page. |
| **Winterlight Labs** (bought by Cambridge Cognition, [2023, about £7m](https://pharmaphorum.com/news/cambridge-cognition-buys-vocal-biomarker-firm-winterlight)) | Speech-and-language markers of cognition. | Pivoted to pharma trial endpoints, not consumers. Shows the voice-cognition science works but there is no consumer path. |
| **Smart-home sensing research** ([JMIR 2026](https://formative.jmir.org/2026/1/e93258)) | Motion, door and sleep sensors flag "delirium-like" days in 13 people with dementia. | No real delirium labels, so accuracy is unknown. Cannot measure inattention, the core 4AT feature, which speech can. |
| **Academic speech models** (Tang 2023, Green 2018; see `delirium_speech_sources.md`) | Speech models hit 78% accuracy (AUC 0.90) in 33 inpatients. | Tiny samples, hospital-only, no product, no public data. |

## Common shortcomings

1. **Hospital-bound.** Every product with delirium in its label needs ICU hardware, an EHR or a trained clinician. Yet the FAM-CAM study found half of post-discharge cases were never caught in hospital.
2. **No personal baseline.** Delirium means a sudden change from this person's normal. Snapshot tools (Canary, 4AT, UB-CAM) compare a person to a population, so they confuse dementia or a person's usual speech with acute change.
3. **No voice for delirium.** Voice companies chase dementia because it has drug-trial money; delirium speech work stopped at small studies.
4. **Not built for families.** Nothing guides a worried relative through what to do, or produces a summary to show a doctor or call 111/911.
5. **Little published accuracy.** Ceribell and Canary publish no sensitivity or specificity in their public pages. Being transparent is an easy way to stand out.
6. **Lab-quality audio assumed.** Canary specifies 16 kHz, a quiet room and under 3 feet; real homes and older voices are noisy, which the Whisper fine-tune helps with.

## How the project can beat them

- **Baseline-and-change, not a one-off score.** Short daily voice check-ins while the person is well; flag sharp drops in attention (months backwards), orientation and coherence. No competitor does this, and the 3D-CAM Day 1 vs Day 2 videos show exactly that contrast.
- **Spoken 4AT plus FAM-CAM.** The app asks the patient the 4AT items by voice and asks the family member the FAM-CAM questions ("Is this sudden?"). That covers the 4AT's "acute change" item, which a voice-only test cannot see.
- **Target the moments of risk:** after surgery, after a hospital discharge, during an infection (UTI). That is where FAM-CAM proved families catch missed cases, and it is easy marketing ("going home after surgery? use this for 30 days").
- **Clear action output:** a traffic-light result, what to do next, and a shareable report with the recording for the doctor.
- **Data moat (inferred):** every consenting check-in that ends with a confirmed outcome becomes labelled delirium speech, which no one else has. That dataset is the long-term defensibility, and it is what Tang/Northwell and MacLullich/Edinburgh would want to partner on.
- **Regulation (inferred):** a screener that flags delirium is likely a medical device (FDA SaMD / UK MHRA). Framing an early version as a "wellness/change tracker that suggests contacting a clinician" lowers the bar, but claims must stay careful.
