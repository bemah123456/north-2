// The senior's daily check-in: the app reads each question aloud, shows it
// in large type, and listens. It moves on by itself after a few seconds of
// quiet, or when they tap "I'm finished". Before the first question it listens
// to the room for a few seconds and asks them to turn the TV down if it's
// loud, because background talk makes healthy answers get misheard. If the
// server can't make out an answer, the question is asked once more, and if
// two answers in a row had a TV talking behind them, it asks them to turn
// it off and asks again.

import { useEffect, useRef, useState } from 'react';
import { ActivityIndicator, Platform, StyleSheet, Text, View } from 'react-native';
import * as Speech from 'expo-speech';
import {
  RecordingPresets,
  requestRecordingPermissionsAsync,
  setAudioModeAsync,
  useAudioRecorder,
  useAudioRecorderState,
} from 'expo-audio';

import { Answer, Exercise, Session, api } from '../api';
import { colors, maxScale, type } from '../theme';
import { Badge, BigButton, Body, Field, Progress, Screen, Title } from '../ui';

const SPEAKING_DB = -40; // louder than this counts as talking
const QUIET_TO_FINISH_MS = 4000;
const SPEECH_RATE = 0.85;
// Typical room level above which we ask them to make it quieter. A guess
// from metering scales (quiet rooms read about -55 dB); tune on real phones.
const NOISY_ROOM_DB = -45;
const ROOM_CHECK_MS = 3000;

type Phase = 'loading' | 'roomcheck' | 'noisy' | 'tv' | 'checking' | 'speaking' | 'listening' | 'typing' | 'sending' | 'done' | 'error';

export default function CheckIn({ personId, typedMode, onFinished }: {
  personId: string;
  typedMode: boolean;
  onFinished: () => void;
}) {
  const [exercises, setExercises] = useState<Exercise[]>([]);
  const [session, setSession] = useState<Session>('morning');
  const [index, setIndex] = useState(0);
  const [phase, setPhase] = useState<Phase>('loading');
  const [error, setError] = useState('');
  const [typed, setTyped] = useState('');
  const [useTyping, setUseTyping] = useState(typedMode);
  const answers = useRef<Answer[]>([]);
  const startedAt = useRef(Date.now());
  const [checkinId, setCheckinId] = useState('');
  const [rated, setRated] = useState(false);
  const [started, setStarted] = useState(false);

  const recorder = useAudioRecorder({ ...RecordingPresets.HIGH_QUALITY, isMeteringEnabled: true });
  const state = useAudioRecorderState(recorder, 250);
  const heardSpeech = useRef(false);
  const quietSince = useRef<number | null>(null);
  const timeLimit = useRef<ReturnType<typeof setTimeout> | null>(null);
  const finishing = useRef(false);
  const askId = useRef(0);
  const askedAgain = useRef(new Set<string>());
  const lastWasNoisy = useRef(false);
  const tvWarned = useRef(false);
  const pendingUri = useRef<string | undefined>(undefined);

  useEffect(() => {
    (async () => {
      try {
        const plan = await api.today(personId);
        if (plan.already_done) {
          setPhase('done');
          return;
        }
        if (!useTyping) {
          const perm = await requestRecordingPermissionsAsync();
          if (!perm.granted) setUseTyping(true);
          else await setAudioModeAsync({ allowsRecording: true, playsInSilentMode: true });
        }
        setSession(plan.session);
        setExercises(plan.exercises);
        if (useTyping) setStarted(true);
      } catch (e) {
        setError(String((e as Error).message));
        setPhase('error');
      }
    })();
    return () => {
      Speech.stop();
    };
  }, [personId]);

  useEffect(() => {
    if (!exercises.length) return;
    if (started) ask(exercises[index]);
    else if (useTyping) setStarted(true);
    else checkRoom();
  }, [exercises, index, started]);

  // A few seconds of the room's normal level, before anyone speaks.
  async function checkRoom() {
    setPhase('roomcheck');
    try {
      await recorder.prepareToRecordAsync();
      recorder.record();
      const levels: number[] = [];
      const t0 = Date.now();
      while (Date.now() - t0 < ROOM_CHECK_MS) {
        await new Promise((r) => setTimeout(r, 250));
        if (level.current !== undefined) levels.push(level.current);
      }
      await recorder.stop();
      levels.sort((a, b) => a - b);
      const typical = levels.length ? levels[Math.floor(levels.length / 2)] : -160;
      if (typical > NOISY_ROOM_DB) {
        setPhase('noisy');
        Speech.speak("It's a bit noisy. Could you turn down the TV, or go somewhere quieter?", { rate: SPEECH_RATE });
        return;
      }
    } catch {
      // A failed check never blocks the check-in.
    }
    setStarted(true);
  }

  // Move on after a stretch of quiet once they've said something. This polls
  // rather than reacting to level changes: steady silence reports the same
  // level over and over, which would never re-trigger an effect.
  const level = useRef<number | undefined>(undefined);
  level.current = state.metering;
  useEffect(() => {
    if (phase !== 'listening') return;
    const timer = setInterval(() => {
      if (level.current === undefined) return;
      const now = Date.now();
      if (level.current > SPEAKING_DB) {
        heardSpeech.current = true;
        quietSince.current = null;
      } else if (heardSpeech.current) {
        quietSince.current ??= now;
        if (now - quietSince.current > QUIET_TO_FINISH_MS) finishRef.current();
      }
    }, 250);
    return () => clearInterval(timer);
  }, [phase]);

  function ask(ex: Exercise, preface = '') {
    setTyped('');
    setPhase('speaking');
    const myAsk = ++askId.current;
    const begin = () => {
      // Only the latest reading of the question may start the microphone.
      if (askId.current !== myAsk) return;
      askId.current++;
      if (useTyping) setPhase('typing');
      else startListening(ex);
    };
    const said = preface ? `${preface} ${ex.prompt}` : ex.prompt;
    Speech.speak(said, { rate: SPEECH_RATE, onDone: begin, onStopped: () => {}, onError: begin });
    // Some browsers never report the end of speech.
    setTimeout(begin, 1500 + said.split(' ').length * 450);
  }

  async function startListening(ex: Exercise) {
    heardSpeech.current = false;
    quietSince.current = null;
    finishing.current = false;
    await recorder.prepareToRecordAsync();
    recorder.record();
    setPhase('listening');
    timeLimit.current = setTimeout(finishAnswer, ex.listen_seconds * 1000);
  }

  const finishRef = useRef<() => void>(() => {});
  finishRef.current = finishAnswer;

  async function finishAnswer() {
    if (finishing.current) return;
    finishing.current = true;
    if (timeLimit.current) clearTimeout(timeLimit.current);
    await recorder.stop();
    const ex = exercises[index];
    const uri = recorder.uri ?? undefined;
    if (uri && !askedAgain.current.has(ex.id)) {
      setPhase('checking');
      const check = await api.checkAnswer(personId, ex.id, uri, session);
      // One noisy clip can be a fluke; two in a row means something is on.
      const tvOn = check.noisy && lastWasNoisy.current && !tvWarned.current;
      lastWasNoisy.current = check.noisy;
      if (tvOn) {
        tvWarned.current = true;
        askedAgain.current.add(ex.id);
        pendingUri.current = uri;
        setPhase('tv');
        Speech.speak('It sounds like a TV or radio is on. Could you turn it off?', { rate: SPEECH_RATE });
        return;
      }
      if (check.ask_again) {
        askedAgain.current.add(ex.id);
        ask(ex, "Sorry, I didn't quite catch that. Let's try once more.");
        return;
      }
    }
    answers.current.push({ exerciseId: ex.id, audioUri: uri });
    next();
  }

  function afterTv(turnedOff: boolean) {
    lastWasNoisy.current = false;
    if (turnedOff) {
      ask(exercises[index], "Thank you. Let's try that one again.");
    } else {
      answers.current.push({ exerciseId: exercises[index].id, audioUri: pendingUri.current });
      next();
    }
  }

  async function repeatQuestion() {
    if (phase === 'listening') {
      finishing.current = true;
      if (timeLimit.current) clearTimeout(timeLimit.current);
      await recorder.stop();
    }
    Speech.stop();
    ask(exercises[index]);
  }

  function submitTyped() {
    answers.current.push({ exerciseId: exercises[index].id, transcript: typed });
    next();
  }

  async function next() {
    if (index + 1 < exercises.length) {
      setIndex(index + 1);
      return;
    }
    setPhase('sending');
    try {
      const result = await api.submit(personId, answers.current, (Date.now() - startedAt.current) / 1000, session);
      setCheckinId(result.checkin_id);
      setPhase('done');
      Speech.speak('All done. Thank you! Was that easy or hard?', { rate: SPEECH_RATE });
    } catch (e) {
      setError(String((e as Error).message));
      setPhase('error');
    }
  }

  if (phase === 'roomcheck' || phase === 'checking' || phase === 'loading' || phase === 'sending') {
    const words = {
      roomcheck: 'Getting ready to listen…',
      checking: 'One moment…',
      loading: 'Getting ready…',
      sending: 'Saving your answers…',
    }[phase];
    return (
      <Screen>
        <View style={styles.center}>
          <ActivityIndicator size="large" color={colors.primary} style={{ transform: [{ scale: 1.6 }] }} />
          <Text style={styles.wait}>{words}</Text>
        </View>
      </Screen>
    );
  }
  if (phase === 'noisy') {
    return (
      <Screen
        footer={
          <>
            <BigButton label="It's quieter now" onPress={checkRoom} />
            <BigButton label="Start anyway" kind="secondary" onPress={() => setStarted(true)} />
          </>
        }
      >
        <Title>It's a bit noisy</Title>
        <Body>Could you turn down the TV or radio, or go somewhere quieter?</Body>
        <Body muted>Background voices make it hard to hear your answers.</Body>
      </Screen>
    );
  }
  if (phase === 'tv') {
    return (
      <Screen
        footer={
          <>
            <BigButton label="It's off now" onPress={() => afterTv(true)} />
            <BigButton label="Keep going" kind="secondary" onPress={() => afterTv(false)} />
          </>
        }
      >
        <Title>Is a TV or radio on?</Title>
        <Body>It sounds like someone else is talking in the background. Could you turn it off so I can hear you clearly?</Body>
      </Screen>
    );
  }
  if (phase === 'done') {
    const asking = !!checkinId && !rated;
    return (
      <Screen
        footer={
          asking ? (
            // Three plain choices instead of a 1 to 5 scale, stored on the same scale.
            ([['Easy', 5], ['OK', 3], ['Hard', 1]] as const).map(([label, n]) => (
              <BigButton
                key={label}
                label={label}
                kind="secondary"
                onPress={() => {
                  setRated(true);
                  api.ease(checkinId, n).catch(() => {});
                }}
              />
            ))
          ) : (
            <BigButton label="Back to home" onPress={onFinished} />
          )
        }
      >
        <View style={styles.center}>
          <Badge mode="done" />
          <Title>All done. Thank you!</Title>
          <Body center>{asking ? 'Was that easy or hard?' : 'See you tomorrow.'}</Body>
        </View>
      </Screen>
    );
  }
  if (phase === 'error') {
    return (
      <Screen footer={<BigButton label="Back to home" onPress={onFinished} />}>
        <Title>Sorry, something went wrong</Title>
        <Body>Your family can still see that you tried today. You can try again later.</Body>
        <Body muted>{error}</Body>
      </Screen>
    );
  }

  const ex = exercises[index];
  const listening = phase === 'listening';
  return (
    <Screen
      footer={
        <>
          {listening && <BigButton label="I'm finished" onPress={finishAnswer} />}
          {phase === 'typing' && <BigButton label="Next" onPress={submitTyped} />}
          <BigButton label="Hear it again" kind="secondary" onPress={repeatQuestion} />
        </>
      }
    >
      <Progress at={index + 1} of={exercises.length} />
      <Text style={styles.prompt} maxFontSizeMultiplier={maxScale.heading}>{ex.caption || ex.prompt}</Text>
      {phase === 'speaking' && (
        <View style={styles.status} accessibilityLiveRegion="polite">
          <Badge mode="speaking" />
          <Text style={styles.statusText}>Listen…</Text>
        </View>
      )}
      {listening && (
        <View style={styles.status} accessibilityLiveRegion="polite">
          <Badge mode="listening" active={(state.metering ?? -60) > SPEAKING_DB} />
          <Text style={styles.statusText}>I'm listening</Text>
          <Text style={styles.statusHint}>Take your time</Text>
        </View>
      )}
      {phase === 'typing' && (
        <Field
          label="Type the answer"
          value={typed}
          onChangeText={setTyped}
          autoFocus
          onSubmitEditing={submitTyped}
          returnKeyType="next"
        />
      )}
      {Platform.OS === 'web' && !useTyping && <Body muted center>Speak into your computer's microphone.</Body>}
    </Screen>
  );
}

const styles = StyleSheet.create({
  center: { flex: 1, justifyContent: 'center', alignItems: 'center', gap: 16 },
  wait: { fontSize: type.big, fontWeight: '700', color: colors.text, textAlign: 'center', marginTop: 24 },
  prompt: { fontSize: type.huge, lineHeight: 48, fontWeight: '700', color: colors.text, marginBottom: 16 },
  status: { flex: 1, alignItems: 'center', justifyContent: 'center' },
  statusText: { fontSize: type.big, fontWeight: '800', color: colors.text },
  statusHint: { fontSize: type.body, color: colors.muted, marginTop: 4 },
});
