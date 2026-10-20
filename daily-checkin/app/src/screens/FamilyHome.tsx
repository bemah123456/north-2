// The family view: one row per day, newest first, with what to do and why.

import { useCallback, useEffect, useState } from 'react';
import { AppState, Pressable, StyleSheet, Text, View } from 'react-native';

import { Alert, api, DayRow, Person, Result } from '../api';
import { colors, maxScale, statusColor, statusSoft, type } from '../theme';
import { BigButton, Body, Card, QuietButton, Screen, Section, StatusIcon, StatusPill, Title } from '../ui';

function niceDate(iso: string) {
  const d = new Date(`${iso}T12:00:00`);
  return d.toLocaleDateString(undefined, { weekday: 'long', month: 'short', day: 'numeric' });
}

function tomorrow() {
  const d = new Date();
  d.setDate(d.getDate() + 1);
  return d.toISOString().slice(0, 10);
}

export default function FamilyHome({ personId, onSignOut }: { personId: string; onSignOut: () => void }) {
  const [person, setPerson] = useState<Person | null>(null);
  const [days, setDays] = useState<DayRow[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [open, setOpen] = useState<string | null>(null);
  const [detail, setDetail] = useState<Result | null>(null);
  const [error, setError] = useState('');
  const [showAll, setShowAll] = useState(false);

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

  async function setEvening(on: boolean) {
    setPerson(await api.updatePerson(personId, { evening_checkin: on }));
  }

  async function report(different: boolean) {
    if (!detail) return;
    setDetail(await api.familyReport(detail.checkin_id, different));
    load();
  }

  const latest = days[0];
  const week = days.slice(0, 7).reverse();
  return (
    <Screen>
      <Text style={styles.brand}>Family view</Text>
      <Title>{person?.name ?? 'Check-ins'}</Title>
      {!!error && (
        <Card tint={colors.amberSoft}>
          <Body>Can't reach the server right now.</Body>
          <BigButton label="Try again" kind="secondary" onPress={load} />
        </Card>
      )}
      {latest && (
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
        </Card>
      )}

      {week.length > 1 && (
        <View style={styles.week} accessibilityLabel="The last week at a glance">
          {week.map((row) => (
            <View key={row.date} style={styles.weekDay}>
              <StatusIcon status={row.status} size={36} />
              <Text style={styles.weekLabel} maxFontSizeMultiplier={maxScale.tight}>{new Date(`${row.date}T12:00:00`).toLocaleDateString(undefined, { weekday: 'short' })}</Text>
            </View>
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
              <Text style={styles.chevron}>{open === row.date ? '⌃' : '⌄'}</Text>
            </View>
            {open === row.date && (
              <View style={{ marginTop: 12 }}>
                {row.reasons.map((r) => (
                  <Body key={r}>• {r}</Body>
                ))}
                {detail && detail.date === row.date && <Detail result={detail} onReport={report} />}
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
      <Card>
        <Text style={styles.settingTitle}>Away tomorrow?</Text>
        <Body muted>A day off means no reminders and no missed check-in text.</Body>
        <BigButton
          label="Mark tomorrow as a day off"
          kind="secondary"
          onPress={async () => {
            await api.dayOff(personId, tomorrow(), true);
            load();
          }}
        />
      </Card>
      <Body muted>Screening only, not a diagnosis. If you're worried, call their doctor.</Body>
      <QuietButton label="Refresh" onPress={load} />
      <QuietButton label="Change setup" onPress={onSignOut} />
    </Screen>
  );
}

function Detail({ result, onReport }: { result: Result; onReport: (different: boolean) => void }) {
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
          <Body>
            {result.change.label} ({result.change.score} of 100)
          </Body>
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
      {result.items.map((it) => (
        <View key={it.exercise_id} style={{ marginBottom: 10 }}>
          <Text style={styles.q}>{it.prompt}</Text>
          <Text style={styles.a}>
            "{it.transcript || '(no answer)'}"
            {it.correct === true ? '  ✓' : it.correct === false ? '  ✗' : ''}
            {it.out_of ? `  (${it.correct_items} of ${it.out_of})` : ''}
            {it.one_month_dropped
              ? '  (one month may have been misheard)'
              : it.misheard ? "  (couldn't make this out)" : ''}
          </Text>
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
  brand: { fontSize: type.small, fontWeight: '800', color: colors.primary, textTransform: 'uppercase', letterSpacing: 1, marginBottom: 4 },
  smallCaps: { fontSize: type.small, fontWeight: '700', color: colors.muted, textTransform: 'uppercase', letterSpacing: 1 },
  todayRow: { flexDirection: 'row', alignItems: 'center', gap: 14, marginVertical: 10 },
  headline: { flex: 1, fontSize: type.big, lineHeight: 34, fontWeight: '800' },
  week: { flexDirection: 'row', justifyContent: 'space-between', backgroundColor: colors.card, borderRadius: 24, borderWidth: 1, borderColor: colors.border, paddingVertical: 14, paddingHorizontal: 10, marginBottom: 4 },
  weekDay: { alignItems: 'center', gap: 6, flex: 1 },
  weekLabel: { fontSize: type.small, fontWeight: '700', color: colors.muted },
  section: { fontSize: type.body, fontWeight: '800', color: colors.text, marginTop: 16, marginBottom: 8 },
  row: { flexDirection: 'row', alignItems: 'center', gap: 12 },
  pair: { flexDirection: 'row', gap: 12 },
  chevron: { fontSize: 32, color: colors.primary, fontWeight: '700' },
  date: { fontSize: type.body, fontWeight: '700', color: colors.text, marginBottom: 6 },
  settingTitle: { fontSize: type.body, fontWeight: '800', color: colors.text, marginBottom: 6 },
  q: { fontSize: type.small, color: colors.muted },
  a: { fontSize: type.body, color: colors.text },
});
