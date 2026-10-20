import { useCallback, useEffect, useState } from 'react';

import { api, Person } from '../api';
import { scheduleDailyReminder } from '../reminders';
import { BigButton, Body, Screen, Title } from '../ui';

export default function SeniorHome({ personId, onStart, onSignOut }: {
  personId: string;
  onStart: () => void;
  onSignOut: () => void;
}) {
  const [person, setPerson] = useState<Person | null>(null);
  const [done, setDone] = useState(false);
  const [error, setError] = useState('');

  const load = useCallback(async () => {
    try {
      const [p, today] = await Promise.all([api.getPerson(personId), api.today(personId)]);
      setPerson(p);
      setDone(today.already_done);
      await scheduleDailyReminder(p.checkin_time);
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
      {done ? (
        <>
          <Body>You've done today's check-in. Thank you!</Body>
          <Body muted>See you tomorrow.</Body>
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
