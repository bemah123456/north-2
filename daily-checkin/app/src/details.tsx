// The facts the family enters about the older person. Clari checks their
// spoken answers against these every day (age, birthday, where they are),
// so they have to be right: the birthday is picked as month, day and year
// rather than typed as one string, and the form shows the age it works out
// so a typo is easy to spot.

import { useState } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';

import { Person } from './api';
import { Icon } from './graphics';
import { colors, font, maxScale, radius, space, type } from './theme';
import { Body, Card, Field, Pick } from './ui';

export const MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September',
  'October', 'November', 'December'];

export const TIMES = [
  { value: '08:00', label: '8 am' },
  { value: '09:00', label: '9 am' },
  { value: '10:00', label: '10 am' },
  { value: '11:00', label: '11 am' },
];

export type Details = {
  name: string;
  month: number | null; // 1 to 12
  day: string;
  year: string;
  city: string;
  place: string;
  checkin_time: string;
};

export function emptyDetails(): Details {
  return { name: '', month: null, day: '', year: '', city: '', place: 'home', checkin_time: '09:00' };
}

// The form's values from a saved person, for "Change their details".
export function detailsFrom(p: Person): Details {
  const [y, m, d] = p.birth_date.split('-').map(Number);
  const [place = 'home', city = ''] = p.place_keywords;
  return { name: p.name, month: m, day: String(d), year: String(y), city, place, checkin_time: p.checkin_time };
}

const pad = (n: number) => String(n).padStart(2, '0');

// "1944-03-14", or null with a reason when it isn't a real past date.
export function birthDate(d: Details): { iso: string | null; problem: string | null } {
  const y = Number(d.year);
  const day = Number(d.day);
  if (!d.month || !d.day || !d.year) return { iso: null, problem: 'Pick the month, then type the day and the year.' };
  if (!/^\d{4}$/.test(d.year) || y < 1900) return { iso: null, problem: 'The year should have four digits, like 1944.' };
  const born = new Date(y, d.month - 1, day);
  if (!Number.isInteger(day) || born.getMonth() !== d.month - 1 || born.getDate() !== day) {
    return { iso: null, problem: `${MONTHS[d.month - 1]} doesn't have a day ${d.day}.` };
  }
  if (born > new Date()) return { iso: null, problem: "That date hasn't happened yet." };
  return { iso: `${y}-${pad(d.month)}-${pad(day)}`, problem: null };
}

export function ageOn(iso: string, today = new Date()) {
  const [y, m, d] = iso.split('-').map(Number);
  const hadBirthday = today.getMonth() + 1 > m || (today.getMonth() + 1 === m && today.getDate() >= d);
  return today.getFullYear() - y - (hadBirthday ? 0 : 1);
}

export function niceBirthday(iso: string) {
  const [y, m, d] = iso.split('-').map(Number);
  return `${MONTHS[m - 1]} ${d}, ${y}`;
}

export function placesFrom(d: Details) {
  return [d.place, d.city].map((s) => s.trim()).filter(Boolean);
}

// The form itself. Used when setting up and when changing details later.
export function DetailsForm({ value, onChange }: { value: Details; onChange: (d: Details) => void }) {
  const set = <K extends keyof Details>(k: K) => (v: Details[K]) => onChange({ ...value, [k]: v });
  const born = birthDate(value);
  const started = value.month || value.day || value.year;
  return (
    <>
      <Card>
        <Field label="What you call them (e.g. Mom, Grandpa Joe)" value={value.name} onChangeText={set('name')} />
        <Text style={styles.label}>Their birthday</Text>
        <View style={styles.months} accessibilityRole="radiogroup" accessibilityLabel="Birth month">
          {[0, 3, 6, 9].map((row) => (
            <View key={row} style={styles.monthRow}>
              {MONTHS.slice(row, row + 3).map((m, j) => {
                const n = row + j + 1;
                const on = value.month === n;
                return (
                  <Pressable
                    key={m}
                    accessibilityRole="radio"
                    accessibilityState={{ checked: on }}
                    accessibilityLabel={m}
                    onPress={() => set('month')(n)}
                    style={[styles.month, on && styles.monthOn]}
                  >
                    <Text maxFontSizeMultiplier={maxScale.button} style={[styles.monthText, on && { color: colors.primaryText }]}>
                      {m.slice(0, 3)}
                    </Text>
                  </Pressable>
                );
              })}
            </View>
          ))}
        </View>
        <View style={styles.dayYear}>
          <View style={{ flex: 1 }}>
            <Field label="Day" value={value.day} onChangeText={(t) => set('day')(t.replace(/\D/g, '').slice(0, 2))}
              keyboardType="number-pad" placeholder="14" maxLength={2} />
          </View>
          <View style={{ flex: 1.4 }}>
            <Field label="Year" value={value.year} onChangeText={(t) => set('year')(t.replace(/\D/g, '').slice(0, 4))}
              keyboardType="number-pad" placeholder="1944" maxLength={4} />
          </View>
        </View>
        {born.iso ? (
          <View style={styles.ok} accessibilityLiveRegion="polite">
            <Icon name="check" size={22} color={colors.green} weight={3} />
            <Text style={styles.okText}>{niceBirthday(born.iso)}, so they're {ageOn(born.iso)} now.</Text>
          </View>
        ) : started ? (
          <Body muted>{born.problem}</Body>
        ) : null}
        <Field label="Their town or city" value={value.city} onChangeText={set('city')} />
        <Field label="Where they'll usually be when checking in" value={value.place} onChangeText={set('place')} />
        <Pick label="Daily reminder" options={TIMES} value={value.checkin_time} onChange={set('checkin_time')} />
      </Card>
    </>
  );
}

// What Clari will expect when it asks its questions, so the family can see
// it has the right answers.
export function WhatClariChecks({ person }: { person: Pick<Person, 'name' | 'birth_date' | 'place_keywords'> }) {
  const rows: [string, string][] = [
    ['How old are you?', `${ageOn(person.birth_date)}`],
    ['When is your birthday?', niceBirthday(person.birth_date)],
    ['Where are you right now?', person.place_keywords.length ? person.place_keywords.join(' or ') : 'not set'],
    ['What year is it?', `${new Date().getFullYear()}`],
  ];
  return (
    <View style={styles.checks}>
      <Text style={styles.checksTitle} maxFontSizeMultiplier={maxScale.heading}>What Clari checks</Text>
      <Text style={styles.checksNote}>Clari asks {person.name} these each day and compares the answers with:</Text>
      {rows.map(([q, a]) => (
        <View key={q} style={styles.checkRow}>
          <Text style={styles.checkQ}>{q}</Text>
          <Text style={styles.checkA}>{a}</Text>
        </View>
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  label: { fontFamily: font.bodyBold, fontSize: type.small, color: colors.text, marginBottom: space.xs },
  months: { gap: 8, marginBottom: space.s },
  monthRow: { flexDirection: 'row', gap: 8 },
  month: { flex: 1, minHeight: 52, borderRadius: radius.m, borderWidth: 2, borderColor: colors.primary, backgroundColor: colors.card, alignItems: 'center', justifyContent: 'center' },
  monthOn: { backgroundColor: colors.primary },
  monthText: { fontFamily: font.display, fontSize: type.small + 1, color: colors.primary },
  dayYear: { flexDirection: 'row', gap: space.s },
  ok: { flexDirection: 'row', alignItems: 'center', gap: 8, backgroundColor: colors.greenSoft, borderRadius: radius.m, padding: space.s, marginBottom: space.m },
  okText: { flex: 1, fontFamily: font.bodyBold, fontSize: type.small, color: colors.green },
  checks: { backgroundColor: colors.primarySoft, borderRadius: radius.l, padding: space.m, marginVertical: space.s, gap: 4 },
  checksTitle: { fontFamily: font.display, fontSize: type.body, color: colors.text },
  checksNote: { fontFamily: font.body, fontSize: type.small, lineHeight: 26, color: colors.muted, marginBottom: space.xs },
  checkRow: { flexDirection: 'row', flexWrap: 'wrap', justifyContent: 'space-between', gap: 8, paddingVertical: 8, borderTopWidth: 1, borderTopColor: colors.border },
  checkQ: { fontFamily: font.body, fontSize: type.small, color: colors.muted, flexShrink: 1 },
  checkA: { fontFamily: font.bodyBold, fontSize: type.small, color: colors.text, textAlign: 'right' },
});
