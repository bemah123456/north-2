// The senior's daily reminder, scheduled on their own phone so it works
// even if the server is down. Missed check-in texts to the family come from
// the server's job, not from here.

import { Platform } from 'react-native';
import * as Notifications from 'expo-notifications';

export async function scheduleDailyReminder(checkinTime: string, eveningTime: string | null = null): Promise<boolean> {
  if (Platform.OS === 'web') return false;
  const perm = await Notifications.requestPermissionsAsync();
  if (!perm.granted) return false;
  const [hour, minute] = checkinTime.split(':').map(Number);
  await Notifications.cancelAllScheduledNotificationsAsync();
  await Notifications.scheduleNotificationAsync({
    content: { title: 'Clari', body: 'Time for your daily check-in. It only takes 2 minutes.' },
    trigger: { type: Notifications.SchedulableTriggerInputTypes.DAILY, hour, minute },
  });
  if (eveningTime) {
    const [eh, em] = eveningTime.split(':').map(Number);
    await Notifications.scheduleNotificationAsync({
      content: { title: 'Evening check-in', body: 'Time for your short evening check-in. It takes about a minute.' },
      trigger: { type: Notifications.SchedulableTriggerInputTypes.DAILY, hour: eh, minute: em },
    });
  }
  return true;
}
