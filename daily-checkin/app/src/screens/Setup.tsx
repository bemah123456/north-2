// First run. A family member sets the senior up; the senior's phone then
// just needs the code shown at the end.

import { useState } from 'react';
import { StyleSheet, Text, View } from 'react-native';

import { api, Person, server } from '../api';
import { birthDate, DetailsForm, emptyDetails, placesFrom, TIMES, WhatClariChecks } from '../details';
import { LogoFull, NodeLine } from '../graphics';
import { Rise } from '../motion';
import { colors, font, maxScale, radius, space, type } from '../theme';
import { BigButton, Body, BrandBar, Card, Choice, Field, QuietButton, Screen, Section, Title } from '../ui';

export type Role = 'senior' | 'family';

export default function Setup({ onReady }: { onReady: (role: Role, personId: string) => void }) {
  const [step, setStep] = useState<'choose' | 'family' | 'senior' | 'code' | 'server'>('choose');
  const [error, setError] = useState('');
  const [created, setCreated] = useState<Person | null>(null);
  const [code, setCode] = useState('');
  const [address, setAddress] = useState(server.get());
  const [details, setDetails] = useState(emptyDetails());
  const [you, setYou] = useState({ family_name: '', family_phone: '' });

  async function create() {
    setError('');
    const born = birthDate(details);
    if (!born.iso) {
      setError(born.problem ?? 'Check their birthday.');
      return;
    }
    try {
      const p = await api.createPerson({
        name: details.name.trim(),
        birth_date: born.iso,
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        checkin_time: details.checkin_time,
        place_keywords: placesFrom(details),
        family_name: you.family_name.trim() || undefined,
        family_phone: you.family_phone.trim() || null,
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
          That's all they need to type. They'll get a reminder at {TIMES.find((t) => t.value === created.checkin_time)?.label ?? created.checkin_time} each
          day. If they haven't checked in 3 hours later, you'll get a text.
        </Body>
        <WhatClariChecks person={created} />
        <Body muted>If anything here is wrong, change it later in the family view under "Their details".</Body>
      </Screen>
    );
  }
  return (
    <Screen
      footer={
        <>
          <BigButton label="Create" onPress={create} disabled={!details.name.trim() || !birthDate(details).iso} />
          <BigButton label="Back" kind="secondary" onPress={() => { setError(''); setStep('choose'); }} />
        </>
      }
    >
      <BrandBar label="Setup" />
      <Title>About them</Title>
      <Body muted>
        You fill this in, not them. Clari checks their answers against it each day, so their birthday and where they live
        need to be right. All they'll do is type a code.
      </Body>
      <DetailsForm value={details} onChange={setDetails} />
      <Section>About you</Section>
      <Card>
        <Field label="Your first name" value={you.family_name} onChangeText={(t) => setYou({ ...you, family_name: t })} />
        <Field label="Your mobile number with country code (e.g. +1 555 123 4567), for texts" value={you.family_phone}
          onChangeText={(t) => setYou({ ...you, family_phone: t })} keyboardType="phone-pad" />
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
