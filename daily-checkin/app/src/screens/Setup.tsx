// First run. A family member sets the senior up; the senior's phone then
// just needs the code shown at the end.

import { useState } from 'react';
import { Text } from 'react-native';

import { api, Person, server } from '../api';
import { colors, type } from '../theme';
import { BigButton, Body, Field, Screen, Title } from '../ui';

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
    if (!/^\d{4}-\d{2}-\d{2}$/.test(form.birth_date)) {
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
      const p = await api.getPerson(code.trim());
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
      <Screen>
        <Title>Server address</Title>
        <Body>Only change this if whoever runs your check-in server gave you an address.</Body>
        <Field label="Address" value={address} onChangeText={setAddress} autoCapitalize="none" autoCorrect={false} keyboardType="url" />
        {!!error && <Body>{error}</Body>}
        <BigButton label="Save" onPress={saveServer} />
        <BigButton label="Back" kind="secondary" onPress={() => { setError(''); setAddress(server.get()); setStep('choose'); }} />
      </Screen>
    );
  }
  if (step === 'choose') {
    return (
      <Screen>
        <Title>Daily check-in</Title>
        <Body>A 2-minute spoken check-in each day, so your family knows you're doing well.</Body>
        <BigButton label="I'm setting this up for a family member" onPress={() => setStep('family')} />
        <BigButton label="My family gave me a code" kind="secondary" onPress={() => setStep('senior')} />
        <Body muted>Screening only, not a diagnosis.</Body>
        <Text accessibilityRole="button" onPress={() => setStep('server')} style={{ fontSize: type.small, color: colors.muted, marginTop: 24 }}>
          Server: {server.get()} (change)
        </Text>
      </Screen>
    );
  }
  if (step === 'senior') {
    return (
      <Screen>
        <Title>Enter your code</Title>
        <Field label="Code from your family" value={code} onChangeText={setCode} autoCapitalize="none" />
        {!!error && <Body>{error}</Body>}
        <BigButton label="Continue" onPress={join} disabled={!code.trim()} />
        <BigButton label="Back" kind="secondary" onPress={() => setStep('choose')} />
      </Screen>
    );
  }
  if (step === 'code' && created) {
    return (
      <Screen>
        <Title>{created.name} is set up</Title>
        <Body>On {created.name}'s phone, open this app, tap "My family gave me a code" and enter:</Body>
        <Text selectable style={{ fontSize: type.huge, fontWeight: '700', color: colors.primary, marginVertical: 16 }}>
          {created.id}
        </Text>
        <Body muted>
          They'll get a reminder at {created.checkin_time} each day. If they haven't checked in 3 hours later,
          you'll get a text.
        </Body>
        <BigButton label="Open the family view" onPress={() => onReady('family', created.id)} />
        <BigButton label="This is their phone: start check-ins" kind="secondary" onPress={() => onReady('senior', created.id)} />
      </Screen>
    );
  }
  return (
    <Screen>
      <Title>About them</Title>
      <Field label="What you call them (e.g. Mom, Grandpa Joe)" value={form.name} onChangeText={set('name')} />
      <Field label="Their date of birth (YYYY-MM-DD)" value={form.birth_date} onChangeText={set('birth_date')} placeholder="1944-03-14" />
      <Field label="Where they'll usually be when checking in" value={form.place} onChangeText={set('place')} />
      <Field label="Their town or city" value={form.city} onChangeText={set('city')} />
      <Field label="Check-in time (24-hour)" value={form.checkin_time} onChangeText={set('checkin_time')} />
      <Field label="Your first name" value={form.family_name} onChangeText={set('family_name')} />
      <Field label="Your mobile number, for missed check-in texts" value={form.family_phone} onChangeText={set('family_phone')} keyboardType="phone-pad" />
      <Body muted>
        Before starting, make sure they agree to daily check-ins and know their answers are recorded and shared
        with you.
      </Body>
      {!!error && <Body>{error}</Body>}
      <BigButton label="Create" onPress={create} disabled={!form.name.trim()} />
      <BigButton label="Back" kind="secondary" onPress={() => setStep('choose')} />
    </Screen>
  );
}
