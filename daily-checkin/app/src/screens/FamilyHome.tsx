// The family view: one row per day, newest first, with what to do and why.

import { useCallback, useEffect, useState } from 'react';
import { AppState, Pressable, StyleSheet, Text, View } from 'react-native';

import { Alert, api, DayRow, Person, Recording, Result } from '../api';
import { NowPlaying, useCheckinPlayer } from '../listen';
import { birthDate, Details, DetailsForm, detailsFrom, placesFrom, WhatClariChecks } from '../details';
import { Icon } from '../graphics';
import { Rise } from '../motion';
import { colors, font, maxScale, statusColor, statusSoft, type } from '../theme';
import { BigButton, Body, BrandBar, Card, QuietButton, Screen, Section, StatusIcon, StatusPill, Title } from '../ui';

function niceDate(iso: string) {
  const d = new Date(`${iso}T12:00:00`);
  return d.toLocaleDateString(undefined, { weekday: 'long', month: 'short', day: 'numeric' });
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
  const [open, setOpen] = useState<string | null>(null);
  const [detail, setDetail] = useState<Result | null>(null);
  const [error, setError] = useState('');
  const [showAll, setShowAll] = useState(false);
  const [dayOff, setDayOff] = useState<string | null>(null);
  const [editing, setEditing] = useState<Details | null>(null);
  const [editError, setEditError] = useState('');

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


  const load = useCallback(async () => {
    try {
      const r = await api.days(personId);
      setPerson(r.person);
      setDays(r.days);
      setAlerts(r.alerts);
      setError('');
    } catch (e) {
      setError((e as Error).message);
    }
  }, [personId]);

  useEffect(() => {
    load();
    const sub = AppState.addEventListener('change', (s) => s === 'active' && load());
    return () => sub.remove();
  }, [load]);

  async function toggle(row: DayRow) {
    if (open === row.date) {
      setOpen(null);
      return;
    }
    setOpen(row.date);
    setDetail(row.checkin_id ? await api.checkin(row.checkin_id) : null);
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
    load();
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
        <Title>Change their details</Title>
        <Body muted>Clari checks their answers against these, so fixing a mistake here stops right answers being marked wrong.</Body>
        <DetailsForm value={editing} onChange={setEditing} />
        {!!editError && <Body>{editError}</Body>}
      </Screen>
    );
  }

  const latest = days[0];
  const week = days.slice(0, 7).reverse();
  return (
    <Screen backdrop="calm">
      <BrandBar label="Family view" />
      <Title>{person?.name ?? 'Check-ins'}</Title>
      {!!error && (
        <Card tint={colors.amberSoft}>
          <Body>Can't reach the server right now.</Body>
          <BigButton label="Try again" kind="secondary" onPress={load} />
        </Card>
      )}
      {latest && (
        <Rise>
        <Card tint={statusSoft[latest.status]} accent={statusColor[latest.status]}>
          <Text style={styles.smallCaps}>Today</Text>
          <View style={styles.todayRow}>
            <StatusIcon status={latest.status} size={56} />
            <Text style={[styles.headline, { color: statusColor[latest.status] }]}>{latest.headline}</Text>
          </View>
          {(showAll ? latest.reasons : latest.reasons.slice(0, 3)).map((r) => (
            <Body key={r}>• {r}</Body>
          ))}
          {latest.reasons.length > 3 && (
            <QuietButton
              label={showAll ? 'Show fewer reasons' : `Show all ${latest.reasons.length} reasons`}
              onPress={() => setShowAll(!showAll)}
            />
          )}
          {latest.checkin_id && person?.share_recordings && alerts.some((a) => a.date === latest.date && a.kind === 'recording') && (
            <ListenButton checkinId={latest.checkin_id} now={player.now} onPlay={player.play} onStop={player.stop} label="Listen to today's check-in" />
          )}
        </Card>
        </Rise>
      )}

      {week.length > 1 && (
        <View style={styles.week} accessibilityLabel="The last week at a glance">
          {week.map((row, i) => (
            <Rise key={row.date} order={3 + i} style={styles.weekDay}>
              <StatusIcon status={row.status} size={36} />
              <Text style={styles.weekLabel} maxFontSizeMultiplier={maxScale.tight}>{new Date(`${row.date}T12:00:00`).toLocaleDateString(undefined, { weekday: 'short' })}</Text>
            </Rise>
          ))}
        </View>
      )}

      <Section>Recent days</Section>
      <Body muted>Tap a day for its answers and details.</Body>
      {days.map((row) => (
        <Pressable
          key={row.date}
          onPress={() => toggle(row)}
          accessibilityRole="button"
          accessibilityState={{ expanded: open === row.date }}
          accessibilityLabel={`${niceDate(row.date)}: ${row.headline}`}
        >
          <Card accent={statusColor[row.status]}>
            <View style={styles.row}>
              <View style={{ flex: 1 }}>
                <Text style={styles.date}>{niceDate(row.date)}</Text>
                <StatusPill status={row.status} label={row.headline} />
              </View>
              <Icon name={open === row.date ? 'chevronUp' : 'chevronDown'} size={30} color={colors.primary} weight={2.8} />
            </View>
            {open === row.date && (
              <View style={{ marginTop: 12 }}>
                {row.reasons.map((r) => (
                  <Body key={r}>• {r}</Body>
                ))}
                {detail && detail.date === row.date && (
                  <Detail result={detail} onReport={report} player={player} sharing={!!person?.share_recordings} />
                )}
              </View>
            )}
          </Card>
        </Pressable>
      ))}

      {alerts.length > 0 && (
        <>
          <Section>Alerts sent to you</Section>
          {alerts.slice(0, 5).map((a) => (
            <Card key={`${a.date}${a.kind}`}>
              <Text style={styles.date}>{niceDate(a.date)}</Text>
              <Body>
                {a.message}
                {a.delivered ? '' : ' (not sent: test mode)'}
              </Body>
              {a.kind.startsWith('missed') &&
                (a.was_real === null ? (
                  <>
                    <Body muted>Was this a real concern?</Body>
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
                  <Body muted>You said: {a.was_real ? 'a real concern' : 'all fine'}.</Body>
                ))}
            </Card>
          ))}
        </>
      )}

      <Section>Settings</Section>
      {person && (
        <Card>
          <Text style={styles.settingTitle}>Their details</Text>
          <WhatClariChecks person={person} />
          <Body muted>Code for their phone, if it ever needs connecting again:</Body>
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
          <Body muted>
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
          <Body muted>
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
        <Body muted>A day off means no reminders and no missed check-in text.</Body>
        <BigButton
          label={dayOff ? 'Undo the day off' : 'Mark tomorrow as a day off'}
          kind="secondary"
          onPress={async () => {
            const day = dayOff ?? tomorrow(days[0]?.date);
            await api.dayOff(personId, day, !dayOff);
            setDayOff(dayOff ? null : day);
            load();
          }}
        />
        {!!dayOff && <Body>{niceDate(dayOff)} is a day off.</Body>}
      </Card>
      <Body muted>Screening only, not a diagnosis. If you're worried, call their doctor.</Body>
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
      <Text style={styles.section}>Did they seem different from their usual self?</Text>
      <View style={styles.pair}>
        <View style={{ flex: 1 }}>
          <BigButton label="Yes" kind={result.parts.acute_change && result.reasons.includes('family says they seem different today') ? 'danger' : 'secondary'} onPress={() => onReport(true)} />
        </View>
        <View style={{ flex: 1 }}>
          <BigButton label="No" kind="secondary" onPress={() => onReport(false)} />
        </View>
      </View>
      {result.change && (
        <>
          <Text style={styles.section}>Compared with their usual</Text>
          <Body>{result.change.label}</Body>
          <Body muted>
            {result.change.baseline_days >= 2
              ? `Answers, timing, voice and alertness together, against their last ${result.change.baseline_days} usual days.`
              : 'Still learning what their usual is (needs 2 check-ins).'}
          </Body>
        </>
      )}
      {result.evening && (
        <>
          <Text style={styles.section}>Evening check-in</Text>
          <Body>
            {result.evening.fluctuation === 'none'
              ? 'About the same as the morning.'
              : result.evening.reasons.join('; ')}
          </Body>
        </>
      )}
      <Text style={styles.section}>What they said</Text>
      {recorded.size > 0 && (
        <>
          <ListenButton checkinId={result.checkin_id} now={player.now} onPlay={player.play} onStop={player.stop} label="Play the whole check-in" />
          <Body muted>
            Hearing an answer that sounds fine doesn't cancel the result. Confusion can come and go, so if you're worried,
            call their doctor.
          </Body>
        </>
      )}
      {result.items.map((it) => (
        <View key={it.exercise_id} style={[styles.answer, playingHere === it.exercise_id && styles.answerOn]}>
          <Text style={styles.q}>{it.prompt}</Text>
          <Text style={styles.a}>
            "{it.transcript || '(no answer)'}"
            {it.correct === true ? '  (right)' : it.correct === false ? '  (wrong)' : ''}
            {it.out_of ? `  (${it.correct_items} of ${it.out_of})` : ''}
            {it.one_month_dropped
              ? '  (one month may have been misheard)'
              : it.misheard ? "  (couldn't make this out)" : ''}
          </Text>
          {recorded.has(it.exercise_id) && (
            <QuietButton
              icon={playingHere === it.exercise_id ? 'stop' : 'play'}
              label={playingHere === it.exercise_id ? 'Stop' : 'Hear their answer'}
              onPress={() => (playingHere === it.exercise_id ? player.stop() : player.play(result.checkin_id, { only: it.exercise_id }))}
            />
          )}
        </View>
      ))}
      <Body muted>
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
  smallCaps: { fontFamily: font.bodyBold, fontSize: type.small, color: colors.muted, textTransform: 'uppercase', letterSpacing: 1.2 },
  todayRow: { flexDirection: 'row', alignItems: 'center', gap: 14, marginVertical: 10 },
  headline: { flex: 1, fontFamily: font.display, fontSize: type.big, lineHeight: 34 },
  week: { flexDirection: 'row', justifyContent: 'space-between', backgroundColor: colors.card, borderRadius: 24, borderWidth: 1, borderColor: colors.border, paddingVertical: 14, paddingHorizontal: 10, marginBottom: 4 },
  weekDay: { alignItems: 'center', gap: 6, flex: 1 },
  weekLabel: { fontFamily: font.bodyBold, fontSize: type.small, color: colors.muted },
  section: { fontFamily: font.display, fontSize: type.body, color: colors.text, marginTop: 16, marginBottom: 8 },
  row: { flexDirection: 'row', alignItems: 'center', gap: 12 },
  pair: { flexDirection: 'row', gap: 12 },
  date: { fontFamily: font.bodyBold, fontSize: type.body, color: colors.text, marginBottom: 6 },
  code: { fontFamily: font.display, fontSize: type.big, letterSpacing: 2, color: colors.primary, marginBottom: 8 },
  settingTitle: { fontFamily: font.display, fontSize: type.body, color: colors.text, marginBottom: 6 },
  q: { fontFamily: font.body, fontSize: type.small, color: colors.muted },
  a: { fontFamily: font.bodyBold, fontSize: type.body, color: colors.text },
  answer: { marginBottom: 10, paddingLeft: 10, borderLeftWidth: 4, borderLeftColor: 'transparent' },
  answerOn: { borderLeftColor: colors.primary },
});
