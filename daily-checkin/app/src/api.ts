// Talks to the check-in server (server/checkin/api.py).
// Set EXPO_PUBLIC_API_URL to the server's address. On a phone that's your
// computer's LAN address (e.g. http://192.168.1.20:8000), not localhost.

import { Platform } from 'react-native';

const BASE = process.env.EXPO_PUBLIC_API_URL ?? 'http://localhost:8000';
const TOKEN = process.env.EXPO_PUBLIC_API_TOKEN;

export type Exercise = {
  id: string;
  part: 'alertness' | 'orientation' | 'attention';
  kind: string;
  prompt: string;
  listen_seconds: number;
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
  items: { exercise_id: string; prompt: string; transcript: string; correct?: boolean | null; correct_items?: number; out_of?: number | null; misheard?: boolean; one_month_dropped?: boolean }[];
  disclaimer: string;
};

export type DayRow = {
  date: string;
  status: Band | 'missed' | 'pending' | 'day_off';
  headline: string;
  reasons: string[];
  checkin_id?: string;
};

export type Alert = { date: string; kind: string; sent_at: string; delivered: number; message: string; was_real: number | null };

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
  createPerson: (p: Omit<Person, 'id' | 'family_name'> & { family_name?: string }) =>
    call<Person>('/people', { method: 'POST', body: JSON.stringify(p) }),
  getPerson: (id: string) => call<Person>(`/people/${id}`),
  updatePerson: (id: string, changes: Partial<Person> & { senior_push_token?: string; family_push_token?: string }) =>
    call<Person>(`/people/${id}`, { method: 'PATCH', body: JSON.stringify(changes) }),
  today: (id: string) => call<{ date: string; already_done: boolean; exercises: Exercise[] }>(`/people/${id}/today`),
  days: (id: string) => call<{ person: Person; days: DayRow[]; alerts: Alert[] }>(`/people/${id}/days`),
  checkin: (checkinId: string) => call<Result>(`/checkins/${checkinId}`),
  familyReport: (checkinId: string, different: boolean) =>
    call<Result>(`/checkins/${checkinId}/family-report`, { method: 'POST', body: JSON.stringify({ different }) }),
  dayOff: (id: string, date: string, off: boolean) =>
    call(`/people/${id}/days-off`, { method: 'POST', body: JSON.stringify({ date, off }) }),

  ease: (checkinId: string, rating: number) =>
    call(`/checkins/${checkinId}/ease`, { method: 'POST', body: JSON.stringify({ rating }) }),
  alertFeedback: (id: string, date: string, kind: string, wasReal: boolean) =>
    call(`/people/${id}/alerts/feedback`, { method: 'POST', body: JSON.stringify({ date, kind, was_real: wasReal }) }),

  async submit(id: string, answers: Answer[], durationS: number): Promise<Result> {
    const form = new FormData();
    form.append('duration_s', String(Math.round(durationS)));
    const typed = answers.filter((a) => a.transcript !== undefined && !a.audioUri);
    form.append('answers', JSON.stringify(typed.map((a) => ({ exercise_id: a.exerciseId, transcript: a.transcript }))));
    for (const a of answers) {
      if (a.audioUri) await appendAudio(form, `audio_${a.exerciseId}`, a.audioUri, a.exerciseId);
    }
    return call<Result>(`/people/${id}/checkins`, { method: 'POST', body: form });
  },

  // Whether one recorded answer couldn't be made out, so the question
  // should be asked again. Any failure or a slow server means "no".
  async shouldAskAgain(id: string, exerciseId: string, audioUri: string, timeoutMs = 10000): Promise<boolean> {
    const form = new FormData();
    form.append('exercise_id', exerciseId);
    await appendAudio(form, 'audio', audioUri, exerciseId);
    const check = call<{ ask_again: boolean }>(`/people/${id}/answers/check`, { method: 'POST', body: form });
    const late = new Promise<{ ask_again: boolean }>((resolve) => setTimeout(() => resolve({ ask_again: false }), timeoutMs));
    try {
      return (await Promise.race([check, late])).ask_again;
    } catch {
      return false;
    }
  },
};
