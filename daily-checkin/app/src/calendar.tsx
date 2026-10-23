// The family's month calendar: one square per day with that day's score,
// coloured by how it went. Red is concerning, yellow is "keep an eye on it"
// or uncertain (a missed day, answers Clari wasn't sure of), green is their
// usual self, grey is no check-in. Each colour also has an icon, so it reads
// without colour too.

import { useMemo, useState } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';

import { DayRow } from './api';
import { Icon, IconName } from './graphics';
import { colors, font, maxScale, radius, space, type } from './theme';

export type Tone = 'red' | 'yellow' | 'green' | 'grey';

export function toneOf(row: DayRow | undefined): Tone {
  if (!row) return 'grey';
  if (row.status === 'possible_delirium') return 'red';
  if (row.status === 'possible_impairment' || row.status === 'missed') return 'yellow';
  if (row.status === 'unlikely') return row.unsure ? 'yellow' : 'green';
  return 'grey'; // not done yet, day off
}

export const TONE: Record<Tone, { bg: string; fg: string; icon: IconName; label: string }> = {
  red: { bg: colors.red, fg: '#FFFFFF', icon: 'alert', label: 'Concerning' },
  yellow: { bg: '#FDEBBE', fg: colors.amber, icon: 'question', label: 'Keep an eye / unsure' },
  green: { bg: colors.greenSoft, fg: colors.green, icon: 'check', label: 'Usual self' },
  grey: { bg: colors.greySoft, fg: colors.grey, icon: 'dash', label: 'No check-in' },
};

// The same colours for cards and badges outside the calendar: a strong one
// for icons, badges and headlines (7:1 on its soft tint), and a soft one for
// backgrounds.
export const TONE_STRONG: Record<Tone, string> = { red: colors.red, yellow: colors.amber, green: colors.green, grey: colors.grey };
export const TONE_SOFT: Record<Tone, string> = { red: colors.redSoft, yellow: '#FDEBBE', green: colors.greenSoft, grey: colors.greySoft };

const WEEKDAYS = ['S', 'M', 'T', 'W', 'T', 'F', 'S'];
const pad = (n: number) => String(n).padStart(2, '0');
const iso = (y: number, m: number, d: number) => `${y}-${pad(m + 1)}-${pad(d)}`;

export function Calendar({ rows, onSelect }: { rows: DayRow[]; onSelect: (row: DayRow) => void }) {
  const byDate = useMemo(() => new Map(rows.map((r) => [r.date, r])), [rows]);
  const newest = rows[0]?.date ?? new Date().toISOString().slice(0, 10);
  const oldest = rows[rows.length - 1]?.date ?? newest;
  const [y0, m0] = newest.split('-').map(Number);
  const [month, setMonth] = useState({ y: y0, m: m0 - 1 });
  const first = new Date(month.y, month.m, 1);
  const daysIn = new Date(month.y, month.m + 1, 0).getDate();
  const cells: (number | null)[] = [...Array(first.getDay()).fill(null), ...Array.from({ length: daysIn }, (_, i) => i + 1)];
  while (cells.length % 7) cells.push(null);
  const weeks = Array.from({ length: cells.length / 7 }, (_, i) => cells.slice(i * 7, i * 7 + 7));
  const monthKey = month.y * 12 + month.m;
  const [oy, om] = oldest.split('-').map(Number);
  const canBack = monthKey > oy * 12 + om - 1;
  const canNext = monthKey < y0 * 12 + m0 - 1;
  const title = first.toLocaleDateString(undefined, { month: 'long', year: 'numeric' });
  const shift = (n: number) => {
    const k = monthKey + n;
    setMonth({ y: Math.floor(k / 12), m: k % 12 });
  };

  return (
    <View style={styles.wrap}>
      <View style={styles.head}>
        <Pressable accessibilityRole="button" accessibilityLabel="Previous month" disabled={!canBack}
          onPress={() => shift(-1)} style={[styles.nav, !canBack && { opacity: 0.3 }]} hitSlop={6}>
          <Icon name="chevronLeft" size={26} color={colors.primary} weight={2.8} />
        </Pressable>
        <Text style={styles.month} maxFontSizeMultiplier={maxScale.heading} accessibilityRole="header">{title}</Text>
        <Pressable accessibilityRole="button" accessibilityLabel="Next month" disabled={!canNext}
          onPress={() => shift(1)} style={[styles.nav, !canNext && { opacity: 0.3 }]} hitSlop={6}>
          <Icon name="chevronRight" size={26} color={colors.primary} weight={2.8} />
        </Pressable>
      </View>
      <View style={styles.row}>
        {WEEKDAYS.map((w, i) => (
          <Text key={i} style={styles.weekday} maxFontSizeMultiplier={maxScale.tight}>{w}</Text>
        ))}
      </View>
      {weeks.map((week, wi) => (
        <View key={wi} style={styles.row}>
          {week.map((d, di) => {
            if (!d) return <View key={di} style={styles.cell} />;
            const date = iso(month.y, month.m, d);
            const row = byDate.get(date);
            const tone = toneOf(row);
            const t = TONE[tone];
            const isToday = date === newest;
            const label = new Date(`${date}T12:00:00`).toLocaleDateString(undefined, { weekday: 'long', month: 'long', day: 'numeric' });
            return (
              <Pressable
                key={di}
                disabled={!row}
                onPress={() => row && onSelect(row)}
                accessibilityRole="button"
                accessibilityLabel={row ? `${label}: ${row.headline}${row.score != null ? `, score ${row.score}` : ''}` : `${label}: no check-in`}
                style={({ pressed }) => [styles.cell, styles.day, { backgroundColor: row ? t.bg : 'transparent' },
                  isToday && styles.today, pressed && { opacity: 0.7 }]}
              >
                <Text style={[styles.dayNum, { color: row ? t.fg : colors.border }]} maxFontSizeMultiplier={maxScale.tight}>{d}</Text>
                {row && (row.score != null ? (
                  <Text style={[styles.score, { color: t.fg }]} maxFontSizeMultiplier={maxScale.tight}>{row.score}</Text>
                ) : (
                  <Icon name={t.icon} size={16} color={t.fg} weight={3} />
                ))}
              </Pressable>
            );
          })}
        </View>
      ))}
      <View style={styles.legend}>
        {(['red', 'yellow', 'green', 'grey'] as Tone[]).map((k) => (
          <View key={k} style={styles.legendItem}>
            <View style={[styles.swatch, { backgroundColor: TONE[k].bg }]}>
              <Icon name={TONE[k].icon} size={14} color={TONE[k].fg} weight={3} />
            </View>
            <Text style={styles.legendText}>{TONE[k].label}</Text>
          </View>
        ))}
      </View>
      <Text style={styles.hint}>The number is that day's score: 0 is their usual, 1 to 3 keep an eye on it, 4 or more call their doctor.</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { backgroundColor: colors.card, borderRadius: radius.l, borderWidth: 1, borderColor: colors.border, padding: 10, gap: 6, marginBottom: space.s },
  head: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', marginBottom: 4 },
  nav: { width: 48, height: 48, borderRadius: 24, backgroundColor: colors.primarySoft, alignItems: 'center', justifyContent: 'center' },
  month: { fontFamily: font.display, fontSize: type.body, color: colors.text, textAlign: 'center', flex: 1 },
  row: { flexDirection: 'row', gap: 4 },
  weekday: { flex: 1, textAlign: 'center', fontFamily: font.bodyBold, fontSize: 14, color: colors.muted },
  cell: { flex: 1, minHeight: 52 },
  day: { borderRadius: 12, alignItems: 'center', justifyContent: 'center', paddingVertical: 4 },
  today: { borderWidth: 3, borderColor: colors.primary },
  dayNum: { fontFamily: font.bodyBold, fontSize: 13 },
  score: { fontFamily: font.display, fontSize: 18, lineHeight: 22 },
  legend: { flexDirection: 'row', flexWrap: 'wrap', justifyContent: 'center', gap: 10, marginTop: 8 },
  legendItem: { flexDirection: 'row', alignItems: 'center', gap: 6 },
  swatch: { width: 24, height: 24, borderRadius: 7, alignItems: 'center', justifyContent: 'center' },
  legendText: { fontFamily: font.bodyBold, fontSize: 15, color: colors.text },
  hint: { fontFamily: font.body, fontSize: 15, lineHeight: 21, color: colors.muted, textAlign: 'center', marginTop: 4 },
});
