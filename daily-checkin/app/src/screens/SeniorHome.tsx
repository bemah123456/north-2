// The senior's home screen: one big button and nothing else to think about.
// It refreshes itself when the app comes back to the front, so there's no
// Refresh button, and "Change setup" sits behind a confirm so a stray tap
// can't disconnect them from their family.

import { ReactNode, useCallback, useEffect, useState } from 'react';
import { Animated, AppState, StyleSheet, Text, View } from 'react-native';

import { api, Person, TodayPlan } from '../api';
import { scheduleDailyReminder } from '../reminders';
import { Done, LogoMark } from '../graphics';
import { Rise, useBreath } from '../motion';
import { brand, colors, font, maxScale, radius, space, type } from '../theme';
import { BigButton, Body, QuietButton, Screen, Title } from '../ui';

// The start button glows softly, like a slow breath, to show where to tap.
function Glowing({ children }: { children: ReactNode }) {
  const t = useBreath(2800);
  return (
    <View>
      <Animated.View
        pointerEvents="none"
        style={[styles.glow, {
          opacity: t.interpolate({ inputRange: [0, 1], outputRange: [0.25, 0.6] }),
          transform: [{ scaleX: t.interpolate({ inputRange: [0, 1], outputRange: [1, 1.035] }) },
            { scaleY: t.interpolate({ inputRange: [0, 1], outputRange: [1, 1.1] }) }],
        }]}
      />
      {children}
    </View>
  );
}

function niceTime(hhmm: string) {
  const [h, m] = hhmm.split(':').map(Number);
  const suffix = h < 12 ? 'am' : 'pm';
  const h12 = h % 12 || 12;
  return m ? `${h12}:${String(m).padStart(2, '0')} ${suffix}` : `${h12} ${suffix}`;
}

export default function SeniorHome({ personId, onStart, onSignOut }: {
  personId: string;
  onStart: () => void;
  onSignOut: () => void;
}) {
  const [person, setPerson] = useState<Person | null>(null);
  const [plan, setPlan] = useState<TodayPlan | null>(null);
  const [error, setError] = useState('');
  const [confirmSignOut, setConfirmSignOut] = useState(false);

  const load = useCallback(async () => {
    try {
      const [p, today] = await Promise.all([api.getPerson(personId), api.today(personId)]);
      setPerson(p);
      setPlan(today);
      setError('');
      await scheduleDailyReminder(p.checkin_time, p.evening_checkin ? p.evening_time : null);
    } catch (e) {
      setError((e as Error).message);
    }
  }, [personId]);

  useEffect(() => {
    load();
    const sub = AppState.addEventListener('change', (s) => s === 'active' && load());
    // A phone left open on this screen still notices the evening check-in opening.
    const timer = setInterval(load, 5 * 60 * 1000);
    return () => {
      sub.remove();
      clearInterval(timer);
    };
  }, [load]);

  if (confirmSignOut) {
    return (
      <Screen
        footer={
          <>
            <BigButton label="Keep things as they are" onPress={() => setConfirmSignOut(false)} />
            <BigButton label="Yes, change setup" kind="secondary" onPress={onSignOut} />
          </>
        }
      >
        <Title>Change setup?</Title>
        <Body>This disconnects this phone from {person?.family_name ? `${person.family_name}'s` : 'your family\'s'} check-ins. You'd need the code again to reconnect.</Body>
        <Body muted>If you're not sure, tap "Keep things as they are".</Body>
      </Screen>
    );
  }

  const now = new Date();
  const hour = now.getHours();
  const hello = hour < 12 ? 'Good morning' : hour < 18 ? 'Good afternoon' : 'Good evening';
  const today = now.toLocaleDateString(undefined, { weekday: 'long', month: 'long', day: 'numeric' });
  const evening = plan?.session === 'evening';

  let main;
  if (plan?.already_done) {
    main = (
      <View style={styles.centre}>
        <View style={{ alignItems: 'center' }}><Done size={130} /></View>
        <Text style={styles.doneTitle} maxFontSizeMultiplier={maxScale.heading}>All done for today</Text>
        <Body center>Thank you!</Body>
        <Body center muted>
          {plan.session === 'morning' && plan.evening_at
            ? `Your short evening check-in opens an hour before ${niceTime(plan.evening_at)}.`
            : 'See you tomorrow.'}
        </Body>
      </View>
    );
  } else {
    main = (
      <View style={styles.centre}>
        <Rise order={2} style={{ alignItems: 'center', marginBottom: space.m }}>
          <LogoMark size={128} breathe />
        </Rise>
        <Body center>
          {evening
            ? 'Time for your short evening check-in.'
            : "Time for today's check-in. I'll ask a few questions out loud and you answer by talking."}
        </Body>
      </View>
    );
  }

  return (
    <Screen
      backdrop="calm"
      footer={
        <>
          {!plan?.already_done && (
            <Glowing>
              <BigButton
                size="hero"
                icon="mic"
                label={evening ? 'Start my evening check-in' : 'Start my check-in'}
                hint={evening ? 'About 1 minute' : 'About 2 minutes'}
                onPress={onStart}
                disabled={!person}
              />
            </Glowing>
          )}
          <QuietButton label="Change setup" onPress={() => setConfirmSignOut(true)} />
        </>
      }
    >
      <Rise>
        <Text style={styles.date}>{today}</Text>
        <Title>{hello}{person ? `, ${person.name}` : ''}</Title>
      </Rise>
      {main}
      {!!error && (
        <View style={styles.error}>
          <Body>I can't connect right now. Check the internet is on, then try again.</Body>
          <BigButton label="Try again" kind="secondary" onPress={load} />
        </View>
      )}
      {person && !plan?.already_done && (
        <Body center muted>Your reminder is at {niceTime(person.checkin_time)} each day.</Body>
      )}
    </Screen>
  );
}

const styles = StyleSheet.create({
  date: { fontFamily: font.bodyBold, fontSize: type.body, color: colors.primary, marginBottom: space.xs },
  centre: { flex: 1, justifyContent: 'center', paddingVertical: space.l },
  doneTitle: { fontFamily: font.display, fontSize: type.huge, color: colors.green, textAlign: 'center', marginBottom: space.s },
  glow: { position: 'absolute', left: -6, right: -6, top: -8, bottom: -8, borderRadius: radius.xl + 8, backgroundColor: brand.glow },
  error: { backgroundColor: colors.amberSoft, borderRadius: 20, padding: space.m, marginBottom: space.m },
});
