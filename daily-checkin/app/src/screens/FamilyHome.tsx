// The family view: today at the top, then a month calendar where every day
// shows its score and colour. Tapping a day opens that day's digest: the
// result and why, the recorded conversation, what they said, and the
// family's own notes.

import { useCallback, useEffect, useState } from 'react';
import { AppState, StyleSheet, Text, TextInput, View } from 'react-native';

import { Alert, api, DayRow, Person, Recording, Result } from '../api';
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

export default function FamilyHome({ personId, onSignOut }: { personId: string; onSignOut: () => void }) {
  const [person, setPerson] = useState<Person | null>(null);
  const [days, setDays] = useState<DayRow[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const player = useCheckinPlayer();
  const [day, setDay] = useState<DayRow | null>(null); // the day whose digest is open
  const [detail, setDetail] = useState<Result | null>(null);
  const [error, setError] = useState('');
  const [showAll, setShowAll] = useState(false);
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
  return (
    <Screen backdrop="calm">
      <BrandBar label="Family view" />
      <Title center>{person?.name ?? 'Check-ins'}</Title>
      {!!error && (
        <Card tint={colors.amberSoft}>
          <Body center>Can't reach the server right now.</Body>
          <BigButton label="Try again" kind="secondary" onPress={load} />
        </Card>
      )}
      {latest && (
        <Rise>
          <View style={[styles.today, { backgroundColor: TONE_SOFT[latestTone], borderColor: TONE_STRONG[latestTone] }]}>
            <Text style={styles.smallCaps}>Today</Text>
            <View style={[styles.scoreBadge, { width: 64, height: 64, backgroundColor: TONE_STRONG[latestTone] }]}>
              <Icon name={TONE[latestTone].icon} size={36} color="#FFFFFF" weight={3} />
            </View>
            <Text style={[styles.headline, { color: TONE_STRONG[latestTone] }]} maxFontSizeMultiplier={maxScale.heading}>
              {latest.headline}
            </Text>
            {latest.score != null && <Text style={styles.scoreLine}>Score {latest.score}</Text>}
            {(showAll ? latest.reasons : latest.reasons.slice(0, 3)).map((r) => (
              <Text key={r} style={styles.reason}>{r}</Text>
            ))}
            {latest.reasons.length > 3 && (
              <QuietButton
                label={showAll ? 'Show fewer reasons' : `Show all ${latest.reasons.length} reasons`}
                onPress={() => setShowAll(!showAll)}
              />
            )}
            {latest.checkin_id && person?.share_recordings && alerts.some((a) => a.date === latest.date && a.kind === 'recording') && (
              <View style={{ alignSelf: 'stretch' }}>
                <ListenButton checkinId={latest.checkin_id} now={player.now} onPlay={player.play} onStop={player.stop} label="Listen to today's check-in" />
              </View>
            )}
            {latest.checkin_id && <QuietButton label="Open today's digest" onPress={() => openDay(latest)} />}
          </View>
        </Rise>
      )}

      <Section center>Every day</Section>
      <Body muted center>Tap a day to see how it went, hear it, and add your notes.</Body>
      <Rise order={2}>
        <Calendar rows={days} onSelect={openDay} />
      </Rise>

      {alerts.length > 0 && (
        <>
          <Section center>Messages sent to you</Section>
          {alerts.slice(0, 5).map((a) => (
            <Card key={`${a.date}${a.kind}`}>
              <Text style={[styles.date, styles.center]}>{niceDate(a.date)}</Text>
              <Body center>
                {a.message}
                {a.delivered ? '' : ' (not sent: test mode)'}
              </Body>
              {a.kind.startsWith('missed') &&
                (a.was_real === null ? (
                  <>
                    <Body muted center>Was this a real concern?</Body>
                    <View style={styles.pair}>
                      <View style={{ flex: 1 }}>
                        <BigButton label="Yes" kind="secondary" onPress={() => api.alertFeedback(personId, a.date, a.kind, true).then(load)} />
                      </View>
                      <View style={{ flex: 1 }}>
                        <BigButton label="No, all fine" kind="secondary" onPress={() => api.alertFeedback(personId, a.date, a.kind, false).then(load)} />
                      </View>
                    </View>
                  </>
                ) : (
                  <Body muted center>You said: {a.was_real ? 'a real concern' : 'all fine'}.</Body>
                ))}
            </Card>
          ))}
        </>
      )}

      <Section center>Settings</Section>
      {person && (
        <Card>
          <Text style={styles.settingTitle}>Their details</Text>
          <WhatClariChecks person={person} />
          <Body muted center>Code for their phone, if it ever needs connecting again:</Body>
          <Text selectable style={styles.code} maxFontSizeMultiplier={maxScale.tight}
            accessibilityLabel={`Code: ${person.id.split('').join(' ')}`}>
            {person.id.match(/.{1,4}/g)?.join(' ')}
          </Text>
          <BigButton label="Change their details" kind="secondary" onPress={() => setEditing(detailsFrom(person))} />
        </Card>
      )}
      {person && (
        <Card>
          <Text style={styles.settingTitle}>Evening check-in: {person.evening_checkin ? `on, at ${person.evening_time}` : 'off'}</Text>
          <Body muted center>
            A one-minute second check-in in the evening, compared with the morning. Delirium often comes and goes
            during the day, so a worse evening can show what one check-in misses.
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
          <Text style={styles.settingTitle}>Check-in recordings: {person.share_recordings ? 'sent to you' : 'off'}</Text>
          <Body muted center>
            When {person.name} finishes a check-in, you get a message and can listen to it: each question, then their answer.
            Only with their OK.
          </Body>
          <BigButton
            label={person.share_recordings ? 'Stop sending recordings' : 'Send me the recordings'}
            kind="secondary"
            onPress={() => setSharing(!person.share_recordings)}
          />
        </Card>
      )}
      <Card>
        <Text style={styles.settingTitle}>Away tomorrow?</Text>
        <Body muted center>A day off means no reminders and no missed check-in text.</Body>
        <BigButton
          label={dayOff ? 'Undo the day off' : 'Mark tomorrow as a day off'}
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
      <Body muted center>Screening only, not a diagnosis. If you're worried, call their doctor.</Body>
      <QuietButton label="Refresh" onPress={load} />
      <QuietButton label="Change setup" onPress={onSignOut} />
    </Screen>
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
          <View style={[styles.scoreBadge, { backgroundColor: strong }]}>
            {row.score != null ? (
              <Text style={styles.scoreBadgeText} maxFontSizeMultiplier={maxScale.tight}>{row.score}</Text>
            ) : (
              <Icon name={tone.icon} size={34} color="#FFFFFF" weight={3} />
            )}
          </View>
          <Text style={[styles.headline, { color: strong }]} maxFontSizeMultiplier={maxScale.heading}>{row.headline}</Text>
          {row.score != null && (
            <Text style={styles.scoreExplain}>Score {row.score}. 0 is their usual, 1 to 3 keep an eye on it, 4 or more call their doctor.</Text>
          )}
          {row.unsure && row.status === 'unlikely' && (
            <Text style={styles.scoreExplain}>Some answers were hard to hear or need checking, so this day is marked yellow.</Text>
          )}
        </View>
      </Rise>

      {row.checkin_id && row.reasons.length > 0 && (
        <>
          <Section center>Clari's notes</Section>
          {row.reasons.map((r) => <Text key={r} style={styles.reason}>{r}</Text>)}
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
            Hearing an answer that sounds fine doesn't cancel the result. Confusion can come and go, so if you're worried,
            call their doctor.
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
            ? `Voice compared with their last ${result.voice.baseline_days} usual days.`
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
  scoreLine: { fontFamily: font.bodyBold, fontSize: type.small, color: colors.text },
  reason: { fontFamily: font.body, fontSize: type.body, lineHeight: 30, color: colors.text, textAlign: 'center', marginBottom: 6 },
  scoreBadge: { width: 76, height: 76, borderRadius: 38, alignItems: 'center', justifyContent: 'center' },
  scoreBadgeText: { fontFamily: font.display, fontSize: 36, color: '#FFFFFF' },
  scoreExplain: { fontFamily: font.body, fontSize: type.small, lineHeight: 26, color: colors.text, textAlign: 'center' },
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
  noteBox: { fontFamily: font.body, fontSize: type.body, minHeight: 120, textAlignVertical: 'top', backgroundColor: colors.card, borderWidth: 2, borderColor: colors.border, borderRadius: radius.m, padding: 16, color: colors.text, marginBottom: space.s },
});
