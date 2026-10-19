# North 2

Shared project repository for North 2: a voice check-in that helps families catch delirium in older relatives early.

## What's in here

- `daily-checkin/`: the hackathon app. A Python scoring server (`server/`), an Expo phone app (`app/`), the Supabase schema (`supabase/`), screenshots, the demo recording script (`tools/`) and the submitted demo video (`submission/`). Its own README explains how to run it.
- `research/delirium_speech_sources.md`: public clips, studies and datasets on how delirium sounds in speech.
- `research/delirium_competitors.md`: existing delirium and speech-cognition tools and where they fall short.
- `research/cloud-4at-asr/`: eight speech models compared on spoken 4AT answers, how often each makes a healthy person look impaired, and transcript fixes that halve those false alarms.

Some work also happens in the Claude project's shared files before it lands here. The copies in this repository are the ones to review and build on; new work from the project is brought in through pull requests.

## Getting started

Each contributor should clone the repository and open their own working copy:

```sh
git clone https://github.com/bemah123456/north-2.git
cd north-2
claude
```

Add project-specific setup instructions here when the app's stack and tooling are known.

## Working together

Each person should use their own clone and create a branch for their work. Push the branch to GitHub and open a pull request to merge it into `main`. Pull the latest `main` before starting new work. GitHub is the shared source of truth; Claude Code works on the files in the local clone.

To give teammates access, add them as collaborators in the repository settings.
