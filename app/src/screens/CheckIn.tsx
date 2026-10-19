// The senior's daily check-in: the app reads each question aloud, shows it
// in large type, and listens. It moves on by itself after a few seconds of
// quiet, or when they tap "I'm done".

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

import { Answer, Exercise, api } from '../api';
import { colors, type } from '../theme';
import { BigButton, Body, Field, Screen, Title } from '../ui';

const SPEAKING_DB = -40; // louder than this counts as talking
const QUIET_TO_FINISH_MS = 4000;
const SPEECH_RATE = 0.85;

type Phase = 'loading' | 'speaking' | 'listening' | 'typing' | 'sending' | 'done' | 'error';

export default function CheckIn({ personId, typedMode, onFinished }: {
  personId: string;
  typedMode: boolean;
  onFinished: () => void;
}) {
  const [exercises, setExercises] = useState<Exercise[]>([]);
  const [index, setIndex] = useState(0);
  const [phase, setPhase] = useState<Phase>('loading');
  const [error, setError] = useState('');
  const [typed, setTyped] = useState('');
  const [useTyping, setUseTyping] = useState(typedMode);
  const answers = useRef<Answer[]>([]);

  const recorder = useAudioRecorder({ ...RecordingPresets.HIGH_QUALITY, isMeteringEnabled: true });
  const state = useAudioRecorderState(recorder, 250);
  const heardSpeech = useRef(false);
  const quietSince = useRef<number | null>(null);
  const timeLimit = useRef<ReturnType<typeof setTimeout> | null>(null);
  const finishing = useRef(false);
  const askId = useRef(0);

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
        setExercises(plan.exercises);
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
    if (exercises.length) ask(exercises[index]);
  }, [exercises, index]);

  // Move on after a stretch of quiet once they've said something.
  useEffect(() => {
    if (phase !== 'listening' || state.metering === undefined) return;
    const now = Date.now();
    if (state.metering > SPEAKING_DB) {
      heardSpeech.current = true;
      quietSince.current = null;
    } else if (heardSpeech.current) {
      quietSince.current ??= now;
      if (now - quietSince.current > QUIET_TO_FINISH_MS) finishAnswer();
    }
  }, [state.metering, phase]);

  function ask(ex: Exercise) {
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
    Speech.speak(ex.prompt, { rate: SPEECH_RATE, onDone: begin, onStopped: () => {}, onError: begin });
    // Some browsers never report the end of speech.
    setTimeout(begin, 1500 + ex.prompt.split(' ').length * 450);
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

  async function finishAnswer() {
    if (finishing.current) return;
    finishing.current = true;
    if (timeLimit.current) clearTimeout(timeLimit.current);
    await recorder.stop();
    answers.current.push({ exerciseId: exercises[index].id, audioUri: recorder.uri ?? undefined });
    next();
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
      await api.submit(personId, answers.current);
      setPhase('done');
      Speech.speak('All done. Thank you, see you tomorrow!', { rate: SPEECH_RATE });
    } catch (e) {
      setError(String((e as Error).message));
      setPhase('error');
    }
  }

  if (phase === 'loading' || phase === 'sending') {
    return (
      <Screen>
        <View style={styles.center}>
          <ActivityIndicator size="large" color={colors.primary} />
          <Body muted>{phase === 'sending' ? 'Saving your answers…' : 'Getting ready…'}</Body>
        </View>
      </Screen>
    );
  }
  if (phase === 'done') {
    return (
      <Screen>
        <Title>All done. Thank you!</Title>
        <Body>See you tomorrow.</Body>
        <BigButton label="Back" onPress={onFinished} />
      </Screen>
    );
  }
  if (phase === 'error') {
    return (
      <Screen>
        <Title>Something went wrong</Title>
        <Body>{error}</Body>
        <BigButton label="Back" onPress={onFinished} />
      </Screen>
    );
  }

  const ex = exercises[index];
  return (
    <Screen scroll={false}>
      <Text style={styles.step}>Question {index + 1} of {exercises.length}</Text>
      <Text style={styles.prompt}>{ex.prompt}</Text>
      {phase === 'listening' && (
        <View style={styles.listening} accessibilityLiveRegion="polite">
          <View style={[styles.dot, { opacity: (state.metering ?? -60) > SPEAKING_DB ? 1 : 0.35 }]} />
          <Text style={styles.listeningText}>Listening… take your time</Text>
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
      <View style={{ flex: 1 }} />
      {phase === 'listening' && <BigButton label="I'm done" onPress={finishAnswer} />}
      {phase === 'typing' && <BigButton label="Next" onPress={submitTyped} />}
      <BigButton label="Say that again" kind="secondary" onPress={repeatQuestion} />
      {Platform.OS === 'web' && !useTyping && <Body muted>Speak into your computer's microphone.</Body>}
    </Screen>
  );
}

const styles = StyleSheet.create({
  center: { flex: 1, justifyContent: 'center', alignItems: 'center', gap: 16 },
  step: { fontSize: type.small, color: colors.muted, marginBottom: 12 },
  prompt: { fontSize: type.huge, lineHeight: 46, fontWeight: '600', color: colors.text, marginBottom: 32 },
  listening: { flexDirection: 'row', alignItems: 'center', gap: 14 },
  dot: { width: 28, height: 28, borderRadius: 14, backgroundColor: colors.red },
  listeningText: { fontSize: type.big, color: colors.text },
});
