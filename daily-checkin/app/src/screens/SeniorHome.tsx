import { useCallback, useEffect, useState } from 'react';

import { api, Person, TodayPlan } from '../api';
import { scheduleDailyReminder } from '../reminders';
import { BigButton, Body, Screen, Title } from '../ui';

export default function SeniorHome({ personId, onStart, onSignOut }: {
  personId: string;
  onStart: () => void;
  onSignOut: () => void;
}) {
  const [person, setPerson] = useState<Person | null>(null);
  const [plan, setPlan] = useState<TodayPlan | null>(null);
  const [error, setError] = useState('');

  const load = useCallback(async () => {
    try {
      const [p, today] = await Promise.all([api.getPerson(personId), api.today(personId)]);
      setPerson(p);
      setPlan(today);
      await scheduleDailyReminder(p.checkin_time, p.evening_checkin ? p.evening_time : null);
    } catch (e) {
      setError((e as Error).message);
    }
  }, [personId]);

  useEffect(() => {
    load();
  }, [load]);

  const hour = new Date().getHours();
  const hello = hour < 12 ? 'Good morning' : hour < 18 ? 'Good afternoon' : 'Good evening';

  return (
    <Screen>
      <Title>{hello}{person ? `, ${person.name}` : ''}!</Title>
      {plan?.already_done ? (
        <>
          <Body>You've done today's check-in. Thank you!</Body>
          <Body muted>
            {plan.session === 'morning' && plan.evening_at
              ? `Your short evening check-in opens an hour before ${plan.evening_at}.`
              : 'See you tomorrow.'}
          </Body>
        </>
      ) : plan?.session === 'evening' ? (
        <>
          <Body>Time for your short evening check-in. It takes about a minute.</Body>
          <BigButton label="Start my evening check-in" onPress={onStart} disabled={!person} />
        </>
      ) : (
        <>
          <Body>Your daily check-in takes about 2 minutes. I'll ask a few questions out loud.</Body>
          <BigButton label="Start my check-in" onPress={onStart} disabled={!person} />
        </>
      )}
      {!!error && <Body muted>Can't reach the server: {error}</Body>}
      <BigButton label="Refresh" kind="secondary" onPress={load} />
      <BigButton label="Change setup" kind="secondary" onPress={onSignOut} />
    </Screen>
  );
}
