// First run. A family member sets the senior up; the senior's phone then
// just needs the code shown at the end.

import { useState } from 'react';
import { StyleSheet, Text, View } from 'react-native';

import { api, Person, server } from '../api';
import { LogoFull, NodeLine } from '../graphics';
import { Rise } from '../motion';
import { colors, font, maxScale, radius, space, type } from '../theme';
import { BigButton, Body, BrandBar, Card, Choice, Field, Pick, QuietButton, Screen, Section, Title } from '../ui';

const TIMES = [
  { value: '08:00', label: '8 am' },
  { value: '09:00', label: '9 am' },
  { value: '10:00', label: '10 am' },
  { value: '11:00', label: '11 am' },
];

export type Role = 'senior' | 'family';

export default function Setup({ onReady }: { onReady: (role: Role, personId: string) => void }) {
  const [step, setStep] = useState<'choose' | 'family' | 'senior' | 'code' | 'server'>('choose');
  const [error, setError] = useState('');
  const [created, setCreated] = useState<Person | null>(null);
  const [code, setCode] = useState('');
  const [address, setAddress] = useState(server.get());
  const [form, setForm] = useState({
    name: '', birth_date: '', place: 'home', city: '', checkin_time: '09:00', family_name: '', family_phone: '',
  });
  const set = (k: keyof typeof form) => (v: string) => setForm({ ...form, [k]: v });

  async function create() {
    setError('');
    // Rejects dates like 1950-13-45 that only look right.
    const [y, m, d] = form.birth_date.split('-').map(Number);
    const born = new Date(y, m - 1, d);
    if (!/^\d{4}-\d{2}-\d{2}$/.test(form.birth_date) || born.getMonth() !== m - 1
        || born.getDate() !== d || born > new Date()) {
      setError('Birth date should look like 1944-03-14.');
      return;
    }
    try {
      const p = await api.createPerson({
        name: form.name.trim(),
        birth_date: form.birth_date,
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        checkin_time: form.checkin_time,
        place_keywords: [form.place, form.city].map((s) => s.trim()).filter(Boolean),
        family_name: form.family_name.trim() || undefined,
        family_phone: form.family_phone.trim() || null,
      });
      setCreated(p);
      setStep('code');
    } catch (e) {
      setError((e as Error).message);
    }
  }

  async function join() {
    setError('');
    try {
      const p = await api.getPerson(code.replace(/\s/g, ''));
      onReady('senior', p.id);
    } catch {
      setError("That code didn't work. Check it with your family.");
    }
  }

  async function saveServer() {
    setError('');
    try {
      setAddress(await server.set(address));
      setStep('choose');
    } catch (e) {
      setError((e as Error).message);
    }
  }

  if (step === 'server') {
    return (
      <Screen
        footer={
          <>
            <BigButton label="Save" onPress={saveServer} />
            <BigButton label="Back" kind="secondary" onPress={() => { setError(''); setAddress(server.get()); setStep('choose'); }} />
          </>
        }
      >
        <BrandBar />
        <Title>Server address</Title>
        <Body>Only change this if whoever runs your check-in server gave you an address.</Body>
        <Field label="Address" value={address} onChangeText={setAddress} autoCapitalize="none" autoCorrect={false} keyboardType="url" />
        {!!error && <Body>{error}</Body>}
      </Screen>
    );
  }
  if (step === 'choose') {
    return (
      <Screen backdrop="bright" footer={<QuietButton label="Server settings" onPress={() => setStep('server')} />}>
        <Rise style={styles.hero}>
          <LogoFull width={168} />
          <Text style={styles.tagline} maxFontSizeMultiplier={maxScale.heading}>
            A two-minute chat each day, so your family knows you're well.
          </Text>
          <NodeLine width={88} />
        </Rise>
        <Rise order={2}>
          <Section>Who is setting this up?</Section>
        </Rise>
        <Rise order={3}>
          <Choice
            title="I'm setting this up for a family member"
            detail="For a parent or grandparent. Takes about a minute."
            onPress={() => setStep('family')}
          />
        </Rise>
        <Rise order={4}>
          <Choice
            title="My family gave me a code"
            detail="Type in the code to connect this phone."
            onPress={() => setStep('senior')}
          />
        </Rise>
        <Body muted>Screening only, not a diagnosis.</Body>
      </Screen>
    );
  }
  if (step === 'senior') {
    return (
      <Screen
        footer={
          <>
            <BigButton label="Continue" onPress={join} disabled={!code.trim()} />
            <BigButton label="Back" kind="secondary" onPress={() => { setError(''); setStep('choose'); }} />
          </>
        }
      >
        <BrandBar />
        <Title>Enter your code</Title>
        <Body>Your family has a short code for you. Type it in the box.</Body>
        <Field label="Your code" big value={code} onChangeText={setCode} autoCapitalize="none" autoCorrect={false} autoFocus />
        {!!error && <Body>{error}</Body>}
      </Screen>
    );
  }
  if (step === 'code' && created) {
    return (
      <Screen
        footer={
          <>
            <BigButton label="Open the family view" onPress={() => onReady('family', created.id)} />
            <BigButton label="This is their phone: start check-ins" kind="secondary" onPress={() => onReady('senior', created.id)} />
          </>
        }
      >
        <BrandBar />
        <Rise><Title>{created.name} is set up</Title></Rise>
        <Body>On {created.name}'s phone, open Clari, tap "My family gave me a code" and type:</Body>
        <View style={styles.codeBox}>
          {/* In groups of four so it's easy to read out and type. */}
          <Text selectable style={styles.code} maxFontSizeMultiplier={maxScale.tight} accessibilityLabel={`Code: ${created.id.split('').join(' ')}`}>
            {created.id.match(/.{1,4}/g)?.join(' ')}
          </Text>
        </View>
        <Body muted>
          They'll get a reminder at {TIMES.find((t) => t.value === created.checkin_time)?.label ?? created.checkin_time} each
          day. If they haven't checked in 3 hours later, you'll get a text.
        </Body>
      </Screen>
    );
  }
  return (
    <Screen
      footer={
        <>
          <BigButton label="Create" onPress={create} disabled={!form.name.trim()} />
          <BigButton label="Back" kind="secondary" onPress={() => { setError(''); setStep('choose'); }} />
        </>
      }
    >
      <BrandBar label="Setup" />
      <Title>About them</Title>
      <Card>
        <Field label="What you call them (e.g. Mom, Grandpa Joe)" value={form.name} onChangeText={set('name')} />
        <Field label="Their date of birth (year-month-day)" value={form.birth_date} onChangeText={set('birth_date')} placeholder="1944-03-14" />
        <Field label="Their town or city" value={form.city} onChangeText={set('city')} />
        <Field label="Where they'll usually be when checking in" value={form.place} onChangeText={set('place')} />
        <Pick label="Daily reminder" options={TIMES} value={form.checkin_time} onChange={set('checkin_time')} />
      </Card>
      <Section>About you</Section>
      <Card>
        <Field label="Your first name" value={form.family_name} onChangeText={set('family_name')} />
        <Field label="Your mobile number, for missed check-in texts" value={form.family_phone} onChangeText={set('family_phone')} keyboardType="phone-pad" />
      </Card>
      <Body muted>
        Before starting, make sure they agree to daily check-ins and know their answers are recorded and shared
        with you.
      </Body>
      {!!error && <Body>{error}</Body>}
    </Screen>
  );
}

const styles = StyleSheet.create({
  hero: { alignItems: 'center', gap: space.m, marginBottom: space.s },
  tagline: { fontFamily: font.display, fontSize: type.big, lineHeight: 36, color: colors.text, textAlign: 'center', maxWidth: 420 },
  codeBox: { backgroundColor: colors.primarySoft, borderRadius: radius.l, borderWidth: 3, borderColor: colors.primary, paddingVertical: space.l, marginVertical: space.m, alignItems: 'center' },
  code: { fontFamily: font.display, fontSize: type.huge, letterSpacing: 2, color: colors.primary },
});
