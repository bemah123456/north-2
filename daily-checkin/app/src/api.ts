// Talks to the check-in server (server/checkin/api.py).
// Set EXPO_PUBLIC_API_URL to the server's address. On a phone that's your
// computer's LAN address (e.g. http://192.168.1.20:8000), not localhost.
// An installed build can also be pointed at another server from the setup
// screen; that address is saved on the phone and wins over the built-in one.

import { Platform } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

const DEFAULT_BASE = process.env.EXPO_PUBLIC_API_URL ?? 'http://localhost:8000';
const TOKEN = process.env.EXPO_PUBLIC_API_TOKEN;
const SERVER_KEY = 'checkin.server';
let BASE = DEFAULT_BASE;

export const server = {
  get: () => BASE,
  async load() {
    const saved = await AsyncStorage.getItem(SERVER_KEY);
    if (saved) BASE = saved;
    return BASE;
  },
  // Checks the address answers before saving it. An empty address goes back
  // to the built-in one.
  async set(url: string) {
    const next = url.trim().replace(/\/+$/, '') || DEFAULT_BASE;
    if (!/^https?:\/\//.test(next)) throw new Error('The address should start with https:// or http://');
    const res = await fetch(`${next}/health`).catch(() => null);
    if (!res?.ok) throw new Error("Couldn't reach a check-in server at that address.");
    BASE = next;
    if (next === DEFAULT_BASE) await AsyncStorage.removeItem(SERVER_KEY);
    else await AsyncStorage.setItem(SERVER_KEY, next);
    return BASE;
  },
};

export type Exercise = {
  id: string;
  part: 'alertness' | 'orientation' | 'attention';
  kind: string;
  prompt: string;
  listen_seconds: number;
  caption?: string; // shown instead of the prompt when the prompt gives the answer away
};

export type Session = 'morning' | 'evening';

export type TodayPlan = {
  date: string;
  session: Session;
  evening_at: string | null; // the evening check-in's time, when the family turned it on
  already_done: boolean;
  exercises: Exercise[];
};

export type Person = {
  id: string;
  name: string;
  birth_date: string;
  timezone: string;
  checkin_time: string;
  place_keywords: string[];
  family_name: string | null;
  family_phone: string | null;
  evening_checkin: boolean;
  evening_time: string;
  share_recordings: boolean; // send the family each check-in's recording when it's done
};

export type Change = {
  score: number; // 0 to 100: how far today is from their usual, all measures together
  level: 'usual' | 'some' | 'big';
  label: string;
  evidence: Record<string, number>;
  baseline_days: number;
};

export type Band = 'unlikely' | 'possible_impairment' | 'possible_delirium';

export type Result = {
  checkin_id: string;
  date: string;
  band: Band;
  headline: string;
  reasons: string[];
  total: number;
  parts: Record<string, number>;
  needs_review: number;
  voice: { measured: boolean; baseline_days: number; change_probability: number | null };
  change?: Change;
  drowsiness_signs?: string[];
  evening?: { checkin_id: string; fluctuation: 'none' | 'watch' | 'scored'; reasons: string[] };
  items: { exercise_id: string; prompt: string; transcript: string; correct?: boolean | null; correct_items?: number; out_of?: number | null; misheard?: boolean; one_month_dropped?: boolean; hard_to_hear?: boolean }[];
  disclaimer: string;
};

export type DayRow = {
  date: string;
  status: Band | 'missed' | 'pending' | 'day_off';
  headline: string;
  reasons: string[];
  checkin_id?: string;
  score?: number | null; // that day's 4AT total
  unsure?: boolean; // answers Clari wasn't sure of, or a noisy room
  note?: string; // the family's own note on the day
};

export type Alert = { date: string; kind: string; sent_at: string; delivered: number; message: string; was_real: number | null };

// A check-in to listen back to: every question in order, what the app
// heard, and the recording's path on the server (null when it was typed, or
// sharing is off).
export type Recording = {
  checkin_id: string;
  date: string;
  session: Session;
  shared: boolean;
  parts: { exercise_id: string; prompt: string; transcript: string; correct: boolean | null; correct_items: number | null; out_of: number | null; audio: string | null }[];
};

// Where the player should fetch a recording from. Phones send the token as
// a header; a web browser's audio element can't, so the clip is fetched
// first and played from memory.
export async function audioSource(path: string): Promise<string | { uri: string; headers?: Record<string, string> }> {
  const uri = `${BASE}${path}`;
  if (!TOKEN) return uri;
  if (Platform.OS === 'web') {
    const res = await fetch(uri, { headers: { Authorization: `Bearer ${TOKEN}` } });
    return URL.createObjectURL(await res.blob());
  }
  return { uri, headers: { Authorization: `Bearer ${TOKEN}` } };
}

// Ask Clari: the family's questions about the app, and its answers.
export type ChatTurn = { role: 'user' | 'assistant'; text: string };
export type Suggestion = {
  setting: 'evening_checkin' | 'evening_time' | 'checkin_time' | 'share_recordings' | 'day_off_tomorrow';
  value: string;
  label: string;
};
export type AskReply = { reply: string; suggestions: Suggestion[]; source: 'claude' | 'guide' };

// reason "unsure": the speech model itself doubted what it heard.
export type AnswerCheck = { ask_again: boolean; noisy: boolean; reason?: 'misheard' | 'one_month_dropped' | 'unsure' | null };

// One answer: a recording (phone) or typed text (web demo, or no mic).
export type Answer = { exerciseId: string; audioUri?: string; transcript?: string };

function appendAudio(form: FormData, field: string, uri: string, name: string) {
  return (async () => {
    if (Platform.OS === 'web') {
      const blob = await (await fetch(uri)).blob();
      form.append(field, blob, `${name}.webm`);
    } else {
      // React Native's FormData takes a file reference object.
      form.append(field, { uri, name: `${name}.m4a`, type: 'audio/m4a' } as unknown as Blob);
    }
  })();
}

async function call<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers: Record<string, string> = { ...(init.headers as Record<string, string>) };
  if (TOKEN) headers.Authorization = `Bearer ${TOKEN}`;
  if (init.body && typeof init.body === 'string') headers['Content-Type'] = 'application/json';
  const res = await fetch(`${BASE}${path}`, { ...init, headers });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      detail = (await res.json()).detail ?? detail;
    } catch {}
    throw new Error(typeof detail === 'string' ? detail : JSON.stringify(detail));
  }
  return res.json() as Promise<T>;
}

export const api = {
  createPerson: (p: Omit<Person, 'id' | 'family_name' | 'evening_checkin' | 'evening_time' | 'share_recordings'> & { family_name?: string }) =>
    call<Person>('/people', { method: 'POST', body: JSON.stringify(p) }),
  getPerson: (id: string) => call<Person>(`/people/${id}`),
  updatePerson: (id: string, changes: Partial<Person> & { senior_push_token?: string; family_push_token?: string }) =>
    call<Person>(`/people/${id}`, { method: 'PATCH', body: JSON.stringify(changes) }),
  today: (id: string) => call<TodayPlan>(`/people/${id}/today`),
  days: (id: string) => call<{ person: Person; days: DayRow[]; alerts: Alert[] }>(`/people/${id}/days`),
  checkin: (checkinId: string) => call<Result>(`/checkins/${checkinId}`),
  recording: (checkinId: string) => call<Recording>(`/checkins/${checkinId}/recording`),
  familyReport: (checkinId: string, different: boolean) =>
    call<Result>(`/checkins/${checkinId}/family-report`, { method: 'POST', body: JSON.stringify({ different }) }),
  ask: (id: string, message: string, history: ChatTurn[]) =>
    call<AskReply>(`/people/${id}/ask`, { method: 'POST', body: JSON.stringify({ message, history: history.slice(-12) }) }),
  setNote: (id: string, date: string, text: string) =>
    call<{ date: string; note: string }>(`/people/${id}/notes/${date}`, { method: 'PUT', body: JSON.stringify({ text }) }),
  dayOff: (id: string, date: string, off: boolean) =>
    call(`/people/${id}/days-off`, { method: 'POST', body: JSON.stringify({ date, off }) }),

  ease: (checkinId: string, rating: number) =>
    call(`/checkins/${checkinId}/ease`, { method: 'POST', body: JSON.stringify({ rating }) }),
  alertFeedback: (id: string, date: string, kind: string, wasReal: boolean) =>
    call(`/people/${id}/alerts/feedback`, { method: 'POST', body: JSON.stringify({ date, kind, was_real: wasReal }) }),

  // planDate is the day the questions were for, so a check-in that runs
  // past midnight is still scored against them.
  async submit(id: string, answers: Answer[], durationS: number, session: Session = 'morning', planDate?: string): Promise<Result> {
    const form = new FormData();
    form.append('duration_s', String(Math.round(durationS)));
    form.append('session', session);
    if (planDate) form.append('plan_date', planDate);
    const typed = answers.filter((a) => a.transcript !== undefined && !a.audioUri);
    form.append('answers', JSON.stringify(typed.map((a) => ({ exercise_id: a.exerciseId, transcript: a.transcript }))));
    for (const a of answers) {
      if (a.audioUri) await appendAudio(form, `audio_${a.exerciseId}`, a.audioUri, a.exerciseId);
    }
    return call<Result>(`/people/${id}/checkins`, { method: 'POST', body: form });
  },

  // Whether one recorded answer couldn't be made out, so the question
  // should be asked again, and whether a TV seemed to be on behind it.
  // Any failure or a slow server means "no" to both.
  async checkAnswer(id: string, exerciseId: string, audioUri: string, session: Session = 'morning', planDate?: string, timeoutMs = 10000): Promise<AnswerCheck> {
    const form = new FormData();
    form.append('exercise_id', exerciseId);
    form.append('session', session);
    if (planDate) form.append('plan_date', planDate);
    await appendAudio(form, 'audio', audioUri, exerciseId);
    const fine: AnswerCheck = { ask_again: false, noisy: false };
    const check = call<AnswerCheck>(`/people/${id}/answers/check`, { method: 'POST', body: form });
    const late = new Promise<AnswerCheck>((resolve) => setTimeout(() => resolve(fine), timeoutMs));
    try {
      return await Promise.race([check, late]);
    } catch {
      return fine;
    }
  },
};
