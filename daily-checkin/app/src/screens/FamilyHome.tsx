// The family view: today at the top, then a month calendar where every day
// shows its score and colour. Tapping a day opens that day's digest: the
// result and why, the recorded conversation, what they said, and the
// family's own notes.

import { useCallback, useEffect, useState } from 'react';
import { AppState, Pressable, StyleSheet, Text, TextInput, View } from 'react-native';

import AsyncStorage from '@react-native-async-storage/async-storage';

import { Alert, api, DayRow, Person, Recording, Result, Suggestion } from '../api';
import { HowItWorks, TOUR_KEY } from '../tour';
import Messages from './Messages';
import { Calendar, TONE, TONE_SOFT, TONE_STRONG, toneOf } from '../calendar';
import { NowPlaying, useCheckinPlayer } from '../listen';
import { birthDate, Details, DetailsForm, detailsFrom, placesFrom, WhatClariChecks } from '../details';
import { Icon } from '../graphics';
import { Rise } from '../motion';
import { colors, font, maxScale, radius, space, type } from '../theme';
import { BigButton, Body, BrandBar, Card, QuietButton, Screen, Section, Title } from '../ui';

function niceDate(iso: string, long = false) {
  const d = new Date(`${iso}T12:00:00`);
  return d.toLocaleDateString(undefined, { weekday: 'long', month: long ? 'long' : 'short', day: 'numeric' });
}

// The day after `today` (YYYY-MM-DD). Pass the senior's today from the
// server's day rows, since the family may be in another time zone; this
// phone's local date is the fallback. Never toISOString, which is UTC.
function tomorrow(today?: string) {
  const d = today ? new Date(`${today}T12:00:00`) : new Date();
  d.setDate(d.getDate() + 1);
  const pad = (n: number) => String(n).padStart(2, '0');
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
}

// One short line under a day's headline: what its score means.
function bandLine(row: DayRow): string {
  if (row.status === 'missed') return 'No check-in this day';
  if (row.status === 'pending') return 'Not done yet';
  if (row.status === 'day_off') return 'Day off';
  if (row.status === 'possible_delirium') return '4 or more: call their doctor';
  if (row.status === 'possible_impairment') return row.score ? '1 to 3: keep an eye on it' : 'Some change from their usual';
  return row.unsure ? 'Some answers were hard to hear' : '0: their usual self';
}

const sentence = (r: string) => r.charAt(0).toUpperCase() + r.slice(1);

// The score in a big circle (or the day's icon when there's no score).
function ScoreBadge({ row, size = 76 }: { row: DayRow; size?: number }) {
  const tone = toneOf(row);
  return (
    <View style={[styles.scoreBadge, { width: size, height: size, borderRadius: size / 2, backgroundColor: TONE_STRONG[tone] }]}>
      {row.score != null ? (
        <Text style={[styles.scoreBadgeText, { fontSize: size * 0.46 }]} maxFontSizeMultiplier={maxScale.tight}>{row.score}</Text>
      ) : (
        <Icon name={TONE[tone].icon} size={size * 0.46} color="#FFFFFF" weight={3} />
      )}
    </View>
  );
}

// Clari's reasons as a tidy list, optionally only the first few.
function ReasonList({ reasons, max, more }: { reasons: string[]; max?: number; more?: () => void }) {
  const shown = max ? reasons.slice(0, max) : reasons;
  return (
    <View style={styles.reasons}>
      {shown.map((r) => (
        <View key={r} style={styles.reasonRow}>
          <View style={styles.reasonDot} />
          <Text style={styles.reasonText}>{sentence(r)}</Text>
        </View>
      ))}
      {max != null && reasons.length > max && more && (
        <QuietButton label={`${reasons.length - max} more in today's details`} onPress={more} />
      )}
    </View>
  );
}

export default function FamilyHome({ personId, onSignOut }: { personId: string; onSignOut: () => void }) {
  const [person, setPerson] = useState<Person | null>(null);
  const [days, setDays] = useState<DayRow[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const player = useCheckinPlayer();
  const [tab, setTab] = useState<Tab>('home');
  const [tourOpen, setTourOpen] = useState(false);
  const [day, setDay] = useState<DayRow | null>(null); // the day whose digest is open
  const [detail, setDetail] = useState<Result | null>(null);
  const [error, setError] = useState('');
  const [dayOff, setDayOff] = useState<string | null>(null);
  const [editing, setEditing] = useState<Details | null>(null);
  const [editError, setEditError] = useState('');

  const load = useCallback(async () => {
    try {
      const r = await api.days(personId);
      setPerson(r.person);
      setDays(r.days);
      setAlerts(r.alerts);
      setError('');
      return r.days;
    } catch (e) {
      setError((e as Error).message);
      return null;
    }
  }, [personId]);

  useEffect(() => {
    load();
    const sub = AppState.addEventListener('change', (s) => s === 'active' && load());
    return () => sub.remove();
  }, [load]);

  // The tour shows once, the first time this phone opens the family view.
  useEffect(() => {
    AsyncStorage.getItem(TOUR_KEY(personId)).then((seen) => !seen && setTourOpen(true)).catch(() => {});
  }, [personId]);

  function finishTour() {
    setTourOpen(false);
    AsyncStorage.setItem(TOUR_KEY(personId), '1').catch(() => {});
  }

  // A settings change Ask Clari suggested and the family tapped.
  async function applySuggestion(s: Suggestion): Promise<string> {
    switch (s.setting) {
      case 'evening_checkin':
        setPerson(await api.updatePerson(personId, { evening_checkin: s.value === 'on' }));
        return s.value === 'on' ? 'The evening check-in is on.' : 'The evening check-in is off.';
      case 'evening_time':
        setPerson(await api.updatePerson(personId, { evening_checkin: true, evening_time: s.value }));
        return `The evening check-in is on, at ${s.value}.`;
      case 'checkin_time':
        setPerson(await api.updatePerson(personId, { checkin_time: s.value }));
        return `The daily reminder is now at ${s.value}.`;
      case 'share_recordings':
        await setSharing(s.value === 'on');
        return s.value === 'on' ? 'Recordings are on.' : 'Recordings are off.';
      case 'day_off_tomorrow': {
        const d = tomorrow(days[0]?.date);
        await api.dayOff(personId, d, true);
        setDayOff(d);
        load();
        return `${niceDate(d)} is a day off.`;
      }
    }
  }

  async function openDay(row: DayRow) {
    setDay(row);
    setDetail(null);
    if (row.checkin_id) setDetail(await api.checkin(row.checkin_id));
  }

  function closeDay() {
    player.stop();
    setDay(null);
    setDetail(null);
  }

  async function saveDetails() {
    if (!editing) return;
    const born = birthDate(editing);
    if (!editing.name.trim() || !born.iso) {
      setEditError(born.problem ?? 'Add the name they go by.');
      return;
    }
    try {
      setPerson(await api.updatePerson(personId, {
        name: editing.name.trim(),
        birth_date: born.iso,
        place_keywords: placesFrom(editing),
        checkin_time: editing.checkin_time,
      }));
      setEditing(null);
      setEditError('');
    } catch (e) {
      setEditError((e as Error).message);
    }
  }

  async function setSharing(on: boolean) {
    if (!on) player.stop();
    setPerson(await api.updatePerson(personId, { share_recordings: on }));
  }

  async function setEvening(on: boolean) {
    setPerson(await api.updatePerson(personId, { evening_checkin: on }));
  }

  async function report(different: boolean) {
    if (!detail) return;
    setDetail(await api.familyReport(detail.checkin_id, different));
    const rows = await load();
    const fresh = rows?.find((r) => r.date === day?.date);
    if (fresh) setDay(fresh);
  }

  async function saveNote(text: string) {
    if (!day) return;
    await api.setNote(personId, day.date, text);
    const rows = await load();
    const fresh = rows?.find((r) => r.date === day.date);
    if (fresh) setDay(fresh);
  }

  if (tourOpen) {
    return <HowItWorks name={person?.name ?? 'Your relative'} onDone={finishTour} />;
  }

  if (editing) {
    return (
      <Screen
        footer={
          <>
            <BigButton label="Save" onPress={saveDetails} />
            <BigButton label="Cancel" kind="secondary" onPress={() => { setEditing(null); setEditError(''); }} />
          </>
        }
      >
        <BrandBar label="Their details" />
        <Title center>Change their details</Title>
        <Body muted center>Clari checks their answers against these, so fixing a mistake here stops right answers being marked wrong.</Body>
        <DetailsForm value={editing} onChange={setEditing} />
        {!!editError && <Body center>{editError}</Body>}
      </Screen>
    );
  }

  if (day) {
    return (
      <DayDigest
        row={day}
        result={detail}
        name={person?.name ?? 'They'}
        sharing={!!person?.share_recordings}
        player={player}
        onReport={report}
        onSaveNote={saveNote}
        onBack={closeDay}
      />
    );
  }

  const latest = days[0];
  const latestTone = toneOf(latest);
  // Only what was sent to the family; reminders to the older person stay out.
  const toFamily = alerts.filter((a) => !a.kind.startsWith('reminder'));
  const unanswered = alerts.filter((a) => a.kind.startsWith('missed') && a.was_real === null).length;
  const tabBar = <TabBar tab={tab} onTab={setTab} badges={{ messages: unanswered }} />;
  const errorCard = !!error && (
    <Card tint={colors.amberSoft}>
      <Body center>Can't reach the server right now.</Body>
      <BigButton label="Try again" kind="secondary" onPress={load} />
    </Card>
  );

  if (tab === 'messages') {
    return (
      <Messages
        personId={personId}
        person={person}
        days={days}
        alerts={alerts}
        tabBar={tabBar}
        onFeedback={(a, real) => api.alertFeedback(personId, a.date, a.kind, real).then(load)}
        onOpenDay={openDay}
        onApply={applySuggestion}
      />
    );
  }

  if (tab === 'settings') {
    return (
      <Screen key="settings" backdrop="calm" footer={tabBar}>
        <BrandBar label="Settings" />
        <Title center>Settings</Title>
        {errorCard}
        {person && (
          <>
            <Section center>Their details</Section>
            <Body muted center>Clari checks their answers against these.</Body>
            <WhatClariChecks person={person} />
            <Card>
              <Text style={styles.settingTitle}>Code for their phone</Text>
              <Body muted center>If their phone ever needs connecting again, they type:</Body>
              <Text selectable style={styles.code} maxFontSizeMultiplier={maxScale.tight}
                accessibilityLabel={`Code: ${person.id.split('').join(' ')}`}>
                {person.id.match(/.{1,4}/g)?.join(' ')}
              </Text>
              <BigButton label="Edit their details" kind="secondary" onPress={() => setEditing(detailsFrom(person))} />
            </Card>
            <Section center>Check-ins</Section>
          </>
        )}
        {person && (
          <Card>
            <Text style={styles.settingTitle}>Evening check-in: {person.evening_checkin ? `on, at ${person.evening_time}` : 'off'}</Text>
            <Body muted center>
              A one-minute check-in each evening, to catch changes during the day.
            </Body>
            <BigButton
              label={person.evening_checkin ? 'Turn it off' : 'Turn it on'}
              kind="secondary"
              onPress={() => setEvening(!person.evening_checkin)}
            />
          </Card>
        )}
        {person && (
          <Card>
            <Text style={styles.settingTitle}>Recordings: {person.share_recordings ? 'on' : 'off'}</Text>
            <Body muted center>
              Hear each check-in once it's done. Only with their OK.
            </Body>
            <BigButton
              label={person.share_recordings ? 'Turn them off' : 'Turn them on'}
              kind="secondary"
              onPress={() => setSharing(!person.share_recordings)}
            />
          </Card>
        )}
        <Card>
          <Text style={styles.settingTitle}>Away tomorrow?</Text>
          <Body muted center>No reminders or texts that day.</Body>
          <BigButton
            label={dayOff ? 'Undo the day off' : 'Make tomorrow a day off'}
            kind="secondary"
            onPress={async () => {
              const d = dayOff ?? tomorrow(days[0]?.date);
              await api.dayOff(personId, d, !dayOff);
              setDayOff(dayOff ? null : d);
              load();
            }}
          />
          {!!dayOff && <Body center>{niceDate(dayOff)} is a day off.</Body>}
        </Card>
        <Section center>Help</Section>
        <Card>
          <Text style={styles.settingTitle}>New to Clari?</Text>
          <Body muted center>A one-minute tour, or ask Clari what anything means.</Body>
          <BigButton label="How Clari works" kind="secondary" onPress={() => setTourOpen(true)} />
          <BigButton label="Ask Clari a question" kind="secondary" onPress={() => setTab('messages')} />
        </Card>
        <Body muted center>Screening only, not a diagnosis. If you're worried, call their doctor.</Body>
        <QuietButton label="Change setup" onPress={onSignOut} />
      </Screen>
    );
  }

  return (
    <Screen key="home" backdrop="calm" footer={tabBar}>
      <BrandBar label="Family view" />
      <Title center>{person?.name ?? 'Check-ins'}</Title>
      {errorCard}
      {latest && (
        <Rise>
          <View style={[styles.today, { backgroundColor: TONE_SOFT[latestTone], borderColor: TONE_STRONG[latestTone] }]}>
            <Text style={styles.smallCaps}>Today</Text>
            <ScoreBadge row={latest} />
            <Text style={[styles.headline, { color: TONE_STRONG[latestTone] }]} maxFontSizeMultiplier={maxScale.heading}>
              {latest.headline}
            </Text>
            <Text style={styles.band}>{bandLine(latest)}</Text>
            {latest.checkin_id && latest.reasons.length > 0 && (
              <ReasonList reasons={latest.reasons} max={2} more={() => openDay(latest)} />
            )}
            {latest.checkin_id && person?.share_recordings && alerts.some((a) => a.date === latest.date && a.kind === 'recording') && (
              <View style={{ alignSelf: 'stretch' }}>
                <ListenButton checkinId={latest.checkin_id} now={player.now} onPlay={player.play} onStop={player.stop} label="Listen to today's check-in" />
              </View>
            )}
            {latest.checkin_id && (
              <View style={{ alignSelf: 'stretch' }}>
                <BigButton label="See today's details" kind="secondary" onPress={() => openDay(latest)} />
              </View>
            )}
          </View>
        </Rise>
      )}
      <Section center>Every day</Section>
      <Body muted center>Tap a day for its details.</Body>
      <Rise order={2}>
        <Calendar rows={days} onSelect={openDay} />
      </Rise>
    </Screen>
  );
}

type Tab = 'messages' | 'home' | 'settings';

const TABS: { key: Tab; label: string; icon: 'home' | 'message' | 'gear' }[] = [
  { key: 'messages', label: 'Messages', icon: 'message' },
  { key: 'home', label: 'Home', icon: 'home' },
  { key: 'settings', label: 'Settings', icon: 'gear' },
];

// Always on screen at the bottom: Messages on the left, Home (today and the
// calendar) in the middle as a raised circle, Settings (including their
// details) on the right. A number shows messages waiting for an answer.
function TabBar({ tab, onTab, badges }: { tab: Tab; onTab: (t: Tab) => void; badges: Partial<Record<Tab, number>> }) {
  return (
    <View style={styles.tabBar} accessibilityRole="tablist">
      {TABS.map((t) => {
        const on = tab === t.key;
        const badge = badges[t.key] ?? 0;
        if (t.key === 'home') {
          return (
            <Pressable
              key={t.key}
              accessibilityRole="tab"
              accessibilityState={{ selected: on }}
              accessibilityLabel={t.label}
              onPress={() => onTab(t.key)}
              style={({ pressed }) => [styles.homeTab, pressed && { transform: [{ scale: 0.96 }] }]}
            >
              <View style={[styles.homeCircle, !on && styles.homeCircleOff]}>
                <Icon name="home" size={34} color={on ? colors.primaryText : colors.primary} weight={2.6} />
              </View>
              <Text style={[styles.tabLabel, { color: colors.primary }]} maxFontSizeMultiplier={maxScale.tight}>{t.label}</Text>
            </Pressable>
          );
        }
        return (
          <Pressable
            key={t.key}
            accessibilityRole="tab"
            accessibilityState={{ selected: on }}
            accessibilityLabel={badge ? `${t.label}, ${badge} waiting` : t.label}
            onPress={() => onTab(t.key)}
            style={({ pressed }) => [styles.tab, on && styles.tabOn, pressed && { opacity: 0.7 }]}
          >
            <View>
              <Icon name={t.icon} size={28} color={on ? colors.primary : colors.muted} weight={on ? 2.6 : 2.2} />
              {badge > 0 && (
                <View style={styles.badge}>
                  <Text style={styles.badgeText} maxFontSizeMultiplier={1}>{badge}</Text>
                </View>
              )}
            </View>
            <Text style={[styles.tabLabel, on && { color: colors.primary }]} numberOfLines={1} maxFontSizeMultiplier={maxScale.tight}>
              {t.label}
            </Text>
          </Pressable>
        );
      })}
    </View>
  );
}

type Player = ReturnType<typeof useCheckinPlayer>;

// Play or stop one check-in. While it plays, says which part is on.
function ListenButton({ checkinId, now, onPlay, onStop, label }: {
  checkinId: string;
  now: NowPlaying;
  onPlay: Player['play'];
  onStop: () => void;
  label: string;
}) {
  const playing = now?.checkinId === checkinId;
  return (
    <View style={{ marginTop: 12 }}>
      <BigButton
        icon={playing ? 'stop' : 'play'}
        label={playing ? 'Stop' : label}
        kind={playing ? 'secondary' : 'primary'}
        onPress={() => (playing ? onStop() : onPlay(checkinId))}
      />
      {playing && <Body muted center>{now.step === 'question' ? 'Reading the question…' : 'Playing their answer…'}</Body>}
    </View>
  );
}

// One day, in full: the result and why, the conversation, and your notes.
function DayDigest({ row, result, name, sharing, player, onReport, onSaveNote, onBack }: {
  row: DayRow;
  result: Result | null;
  name: string;
  sharing: boolean;
  player: Player;
  onReport: (different: boolean) => void;
  onSaveNote: (text: string) => Promise<void>;
  onBack: () => void;
}) {
  const toneKey = toneOf(row);
  const tone = TONE[toneKey];
  const strong = TONE_STRONG[toneKey];
  const [note, setNote] = useState(row.note ?? '');
  const [saved, setSaved] = useState(false);
  useEffect(() => {
    setNote(row.note ?? '');
    setSaved(false);
  }, [row.date]);
  return (
    <Screen footer={<BigButton label="Back to the calendar" kind="secondary" onPress={onBack} />}>
      <BrandBar label="Day digest" />
      <Rise>
        <Text style={[styles.smallCaps, styles.center]}>{niceDate(row.date, true)}</Text>
        <View style={[styles.today, { backgroundColor: TONE_SOFT[toneKey], borderColor: strong }]}>
          <ScoreBadge row={row} />
          <Text style={[styles.headline, { color: strong }]} maxFontSizeMultiplier={maxScale.heading}>{row.headline}</Text>
          <Text style={styles.band}>{bandLine(row)}</Text>
        </View>
      </Rise>

      {row.checkin_id && row.reasons.length > 0 && (
        <>
          <Section center>Clari's notes</Section>
          <ReasonList reasons={row.reasons} />
        </>
      )}

      {result && <Detail result={result} onReport={onReport} player={player} sharing={sharing} />}
      {!row.checkin_id && (
        <Body muted center>
          {row.status === 'day_off' ? 'This was a day off.' : row.status === 'pending' ? `${name} hasn't checked in yet today.` : `${name} didn't check in this day.`}
        </Body>
      )}

      <Section center>Your notes</Section>
      <Body muted center>Anything worth remembering, like a fall, a new medicine or a bad night. Useful to show their doctor.</Body>
      <TextInput
        accessibilityLabel="Your notes for this day"
        style={styles.noteBox}
        multiline
        value={note}
        onChangeText={(t) => { setNote(t); setSaved(false); }}
        placeholder="Add a note for this day"
        placeholderTextColor={colors.muted}
      />
      <BigButton
        label={saved ? 'Saved' : 'Save note'}
        kind="secondary"
        icon={saved ? 'check' : undefined}
        onPress={async () => { await onSaveNote(note); setSaved(true); }}
      />
    </Screen>
  );
}

// Right, wrong, how many in order, or "needs a person to check", with an
// icon and colour so it reads at a glance, plus any doubt about the hearing.
function Verdict({ item }: { item: Result['items'][number] }) {
  const doubt = item.one_month_dropped
    ? 'one month may have been misheard'
    : item.misheard ? "couldn't make this out" : item.hard_to_hear ? 'hard to hear' : '';
  let icon: 'check' | 'alert' | 'question' | null = null;
  let color: string = colors.muted;
  let text = '';
  if (item.out_of) {
    text = `${item.correct_items} of ${item.out_of} in order`;
  } else if (item.correct === true) {
    [icon, color, text] = ['check', colors.green, 'Right'];
  } else if (item.correct === false) {
    [icon, color, text] = ['alert', colors.red, 'Wrong'];
  } else if (item.correct === null) {
    [icon, color, text] = ['question', colors.amber, 'Needs a person to check'];
  }
  if (!text && !doubt) return null;
  return (
    <View style={styles.verdictRow}>
      {icon && <Icon name={icon} size={20} color={color} weight={3} />}
      <Text style={[styles.verdict, { color }]}>{[text, doubt].filter(Boolean).join(' · ')}</Text>
    </View>
  );
}

function Detail({ result, onReport, player, sharing }: {
  result: Result;
  onReport: (different: boolean) => void;
  player: Player;
  sharing: boolean;
}) {
  const [rec, setRec] = useState<Recording | null>(null);
  useEffect(() => {
    setRec(null);
    if (sharing) player.load(result.checkin_id).then(setRec).catch(() => setRec(null));
  }, [result.checkin_id, sharing]);
  const recorded = new Set(rec?.parts.filter((p) => p.audio).map((p) => p.exercise_id));
  const playingHere = player.now?.checkinId === result.checkin_id ? player.now.exerciseId : null;
  return (
    <View>
      {recorded.size > 0 && (
        <>
          <Section center>The conversation</Section>
          <ListenButton checkinId={result.checkin_id} now={player.now} onPlay={player.play} onStop={player.stop} label="Play the whole check-in" />
          <Body muted center>
            An answer that sounds fine doesn't cancel the result.
          </Body>
        </>
      )}
      <Section center>What they said</Section>
      {result.items.map((it) => (
        <View key={it.exercise_id} style={[styles.answer, playingHere === it.exercise_id && styles.answerOn]}>
          <Text style={styles.q}>{it.prompt}</Text>
          <Text style={styles.a}>"{it.transcript || '(no answer)'}"</Text>
          <Verdict item={it} />
          {recorded.has(it.exercise_id) && (
            <QuietButton
              icon={playingHere === it.exercise_id ? 'stop' : 'play'}
              label={playingHere === it.exercise_id ? 'Stop' : 'Hear their answer'}
              onPress={() => (playingHere === it.exercise_id ? player.stop() : player.play(result.checkin_id, { only: it.exercise_id }))}
            />
          )}
        </View>
      ))}
      {result.change && (
        <>
          <Section center>Compared with their usual</Section>
          <Body center>{result.change.label}</Body>
          <Body muted center>
            {result.change.baseline_days >= 2
              ? `Answers, timing, voice and alertness together, against their last ${result.change.baseline_days} usual days.`
              : 'Still learning what their usual is (needs 2 check-ins).'}
          </Body>
        </>
      )}
      {result.evening && (
        <>
          <Section center>Evening check-in</Section>
          <Body center>
            {result.evening.fluctuation === 'none' ? 'About the same as the morning.' : result.evening.reasons.join('; ')}
          </Body>
        </>
      )}
      <Section center>Did they seem different from their usual self?</Section>
      <View style={styles.pair}>
        <View style={{ flex: 1 }}>
          <BigButton label="Yes" kind={result.parts.acute_change && result.reasons.includes('family says they seem different today') ? 'danger' : 'secondary'} onPress={() => onReport(true)} />
        </View>
        <View style={{ flex: 1 }}>
          <BigButton label="No" kind="secondary" onPress={() => onReport(false)} />
        </View>
      </View>
      <Body muted center>
        {result.voice.measured
          ? result.voice.baseline_days >= 2
            ? `Compared with their last ${result.voice.baseline_days} usual days.`
            : 'Still learning their usual voice (needs 2 check-ins).'
          : 'Typed answers, so voice was not measured.'}
        {result.needs_review ? ` ${result.needs_review} answer(s) need a person to check.` : ''}
      </Body>
    </View>
  );
}

const styles = StyleSheet.create({
  center: { textAlign: 'center' },
  smallCaps: { fontFamily: font.bodyBold, fontSize: type.small, color: colors.muted, textTransform: 'uppercase', letterSpacing: 1.2 },
  today: { alignItems: 'center', gap: 10, borderRadius: radius.l, borderWidth: 2, padding: space.m, marginBottom: space.s },
  headline: { fontFamily: font.display, fontSize: type.big, lineHeight: 34, textAlign: 'center' },
  scoreBadge: { width: 76, height: 76, borderRadius: 38, alignItems: 'center', justifyContent: 'center' },
  scoreBadgeText: { fontFamily: font.display, fontSize: 36, color: '#FFFFFF' },
  band: { fontFamily: font.bodyBold, fontSize: type.small, color: colors.text, textAlign: 'center' },
  reasons: { alignSelf: 'stretch', backgroundColor: 'rgba(255,255,255,0.7)', borderRadius: radius.m, paddingVertical: 10, paddingHorizontal: 14, gap: 8 },
  reasonRow: { flexDirection: 'row', alignItems: 'flex-start', gap: 10 },
  reasonDot: { width: 8, height: 8, borderRadius: 4, backgroundColor: colors.muted, marginTop: 9 },
  reasonText: { flex: 1, fontFamily: font.body, fontSize: type.small, lineHeight: 26, color: colors.text },
  pair: { flexDirection: 'row', gap: 12 },
  date: { fontFamily: font.bodyBold, fontSize: type.body, color: colors.text, marginBottom: 6 },
  settingTitle: { fontFamily: font.display, fontSize: type.body, color: colors.text, marginBottom: 6, textAlign: 'center' },
  code: { fontFamily: font.display, fontSize: type.big, letterSpacing: 2, color: colors.primary, marginBottom: 8, textAlign: 'center' },
  answer: { alignItems: 'center', gap: 2, paddingVertical: 12, borderTopWidth: 1, borderTopColor: colors.border, borderRadius: 12 },
  answerOn: { backgroundColor: colors.primarySoft },
  q: { fontFamily: font.body, fontSize: type.small, color: colors.muted, textAlign: 'center' },
  a: { fontFamily: font.bodyBold, fontSize: type.body, color: colors.text, textAlign: 'center' },
  verdictRow: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 6, flexWrap: 'wrap' },
  verdict: { fontFamily: font.bodyBold, fontSize: type.small, textAlign: 'center' },
  empty: { alignItems: 'center', gap: 12, paddingVertical: space.xl },
  tabBar: { flexDirection: 'row', alignItems: 'flex-end', backgroundColor: colors.card, borderRadius: radius.l, borderWidth: 1, borderColor: colors.border, padding: 6, gap: 4, marginTop: 30,
    shadowColor: colors.text, shadowOpacity: 0.08, shadowRadius: 12, shadowOffset: { width: 0, height: 4 }, elevation: 4 },
  homeTab: { flex: 1, alignItems: 'center', gap: 4, marginTop: -36 },
  homeCircle: { width: 76, height: 76, borderRadius: 38, backgroundColor: colors.primary, alignItems: 'center', justifyContent: 'center',
    borderWidth: 5, borderColor: colors.bg, shadowColor: colors.primary, shadowOpacity: 0.3, shadowRadius: 10, shadowOffset: { width: 0, height: 4 }, elevation: 6 },
  homeCircleOff: { backgroundColor: colors.primarySoft },
  tab: { flex: 1, minHeight: 64, alignItems: 'center', justifyContent: 'center', gap: 4, borderRadius: radius.m, paddingHorizontal: 2 },
  tabOn: { backgroundColor: colors.primarySoft },
  tabLabel: { fontFamily: font.bodyBold, fontSize: 14, color: colors.muted, textAlign: 'center' },
  badge: { position: 'absolute', top: -6, right: -12, minWidth: 22, height: 22, borderRadius: 11, backgroundColor: colors.red, alignItems: 'center', justifyContent: 'center', paddingHorizontal: 5 },
  badgeText: { fontFamily: font.bodyBold, fontSize: 13, color: '#FFFFFF' },
  noteBox: { fontFamily: font.body, fontSize: type.body, minHeight: 120, textAlignVertical: 'top', backgroundColor: colors.card, borderWidth: 2, borderColor: colors.border, borderRadius: radius.m, padding: 16, color: colors.text, marginBottom: space.s },
});
