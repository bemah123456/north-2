// The family view: one row per day, newest first, with what to do and why.

import { useCallback, useEffect, useState } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';

import { Alert, api, DayRow, Person, Result } from '../api';
import { colors, statusColor, type } from '../theme';
import { BigButton, Body, Card, Screen, Title } from '../ui';

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
  }, [load]);

  async function toggle(row: DayRow) {
    if (open === row.date) {
      setOpen(null);
      return;
    }
    setOpen(row.date);
    setDetail(row.checkin_id ? await api.checkin(row.checkin_id) : null);
  }

  async function report(different: boolean) {
    if (!detail) return;
    setDetail(await api.familyReport(detail.checkin_id, different));
    load();
  }

  const latest = days[0];
  return (
    <Screen>
      <Title>{person?.name ?? 'Check-ins'}</Title>
      {!!error && <Body muted>Can't reach the server: {error}</Body>}
      {latest && (
        <Card accent={statusColor[latest.status]}>
          <Text style={styles.smallCaps}>Today</Text>
          <Text style={[styles.headline, { color: statusColor[latest.status] }]}>{latest.headline}</Text>
          {latest.reasons.map((r) => (
            <Body key={r}>• {r}</Body>
          ))}
        </Card>
      )}

      <Text style={styles.section}>Recent days</Text>
      {days.map((row) => (
        <Pressable key={row.date} onPress={() => toggle(row)} accessibilityRole="button">
          <Card accent={statusColor[row.status]}>
            <View style={styles.row}>
              <Text style={styles.date}>{niceDate(row.date)}</Text>
              <Text style={[styles.status, { color: statusColor[row.status] }]}>{row.headline}</Text>
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
          <Text style={styles.section}>Alerts</Text>
          {alerts.slice(0, 5).map((a) => (
            <Body key={`${a.date}${a.kind}`} muted>
              {niceDate(a.date)}: {a.message}
              {a.delivered ? '' : ' (not sent: test mode)'}
            </Body>
          ))}
        </>
      )}

      <BigButton label="Refresh" onPress={load} />
      <BigButton
        label="Mark tomorrow as a day off"
        kind="secondary"
        onPress={async () => {
          await api.dayOff(personId, tomorrow(), true);
          load();
        }}
      />
      <Body muted>Screening only, not a diagnosis. If you're worried, call their doctor.</Body>
      <BigButton label="Change setup" kind="secondary" onPress={onSignOut} />
    </Screen>
  );
}

function Detail({ result, onReport }: { result: Result; onReport: (different: boolean) => void }) {
  return (
    <View>
      <Text style={styles.section}>Did they seem different from their usual self?</Text>
      <View style={styles.row}>
        <View style={{ flex: 1, marginRight: 6 }}>
          <BigButton label="Yes" kind={result.parts.acute_change && result.reasons.includes('family says they seem different today') ? 'danger' : 'secondary'} onPress={() => onReport(true)} />
        </View>
        <View style={{ flex: 1, marginLeft: 6 }}>
          <BigButton label="No" kind="secondary" onPress={() => onReport(false)} />
        </View>
      </View>
      <Text style={styles.section}>What they said</Text>
      {result.items.map((it) => (
        <View key={it.exercise_id} style={{ marginBottom: 10 }}>
          <Text style={styles.q}>{it.prompt}</Text>
          <Text style={styles.a}>
            "{it.transcript || '(no answer)'}"
            {it.correct === true ? '  ✓' : it.correct === false ? '  ✗' : ''}
            {it.out_of ? `  (${it.correct_items} of ${it.out_of})` : ''}
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
  smallCaps: { fontSize: type.small, color: colors.muted, textTransform: 'uppercase', letterSpacing: 1 },
  headline: { fontSize: type.big, fontWeight: '700', marginVertical: 6 },
  section: { fontSize: type.body, fontWeight: '700', color: colors.text, marginTop: 16, marginBottom: 8 },
  row: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap' },
  date: { fontSize: type.body, color: colors.text },
  status: { fontSize: type.body, fontWeight: '700' },
  q: { fontSize: type.small, color: colors.muted },
  a: { fontSize: type.body, color: colors.text },
});
