// Plays a check-in back for the family the way it happened: the phone reads
// each question aloud, then their recorded answer plays. One check-in plays
// at a time, and starting another stops the first.

import { useCallback, useEffect, useRef, useState } from 'react';
import { Platform } from 'react-native';
import * as Speech from 'expo-speech';
import { AudioPlayer, createAudioPlayer, setAudioModeAsync } from 'expo-audio';

import { api, audioSource, Recording } from './api';

const SPEECH_RATE = 0.9;
// If a clip never reports that it finished (a dropped connection), move on.
const CLIP_TIMEOUT_MS = 90_000;

export type NowPlaying = { checkinId: string; exerciseId: string; step: 'question' | 'answer' } | null;

export function useCheckinPlayer() {
  const [now, setNow] = useState<NowPlaying>(null);
  const run = useRef(0); // bumped on every start or stop, so an old run stops itself
  const player = useRef<AudioPlayer | null>(null);
  const cache = useRef(new Map<string, Recording>());

  const release = () => {
    player.current?.remove();
    player.current = null;
  };

  const stop = useCallback(() => {
    run.current += 1;
    Speech.stop();
    release();
    setNow(null);
  }, []);

  useEffect(() => stop, [stop]);

  const load = useCallback(async (checkinId: string) => {
    const hit = cache.current.get(checkinId);
    if (hit) return hit;
    const rec = await api.recording(checkinId);
    cache.current.set(checkinId, rec);
    return rec;
  }, []);

  function say(text: string, id: number) {
    return new Promise<void>((resolve) => {
      if (id !== run.current) return resolve();
      Speech.speak(text, { rate: SPEECH_RATE, onDone: () => resolve(), onStopped: () => resolve(), onError: () => resolve() });
    });
  }

  async function playClip(path: string, id: number) {
    if (id !== run.current) return;
    release();
    const p = createAudioPlayer(await audioSource(path));
    if (id !== run.current) {
      p.remove();
      return;
    }
    player.current = p;
    await new Promise<void>((resolve) => {
      const timer = setTimeout(resolve, CLIP_TIMEOUT_MS);
      const sub = p.addListener('playbackStatusUpdate', (s) => {
        if (s.didJustFinish) {
          clearTimeout(timer);
          sub.remove();
          resolve();
        }
      });
      p.play();
    });
  }

  // Plays from `fromExercise` (or the start) to the end. With `only`, plays
  // just that one answer, without reading the question.
  const play = useCallback(async (checkinId: string, opts: { fromExercise?: string; only?: string } = {}) => {
    stop();
    const id = run.current;
    try {
      if (Platform.OS !== 'web') await setAudioModeAsync({ playsInSilentMode: true, allowsRecording: false });
      const rec = await load(checkinId);
      let parts = rec.parts.filter((p) => p.audio); // typed answers have nothing to hear
      if (opts.only) parts = parts.filter((p) => p.exercise_id === opts.only);
      else if (opts.fromExercise) parts = parts.slice(Math.max(0, parts.findIndex((p) => p.exercise_id === opts.fromExercise)));
      for (const part of parts) {
        if (id !== run.current) return;
        if (!opts.only) {
          setNow({ checkinId, exerciseId: part.exercise_id, step: 'question' });
          await say(part.prompt, id);
        }
        if (part.audio) {
          setNow({ checkinId, exerciseId: part.exercise_id, step: 'answer' });
          await playClip(part.audio, id);
        }
      }
    } finally {
      if (id === run.current) {
        release();
        setNow(null);
      }
    }
  }, [load, stop]);

  return { now, play, stop, load };
}
