// The senior's daily reminder, scheduled on their own phone so it works
// even if the server is down. Missed check-in texts to the family come from
// the server's job, not from here.

import { Platform } from 'react-native';
import * as Notifications from 'expo-notifications';

export async function scheduleDailyReminder(checkinTime: string): Promise<boolean> {
  if (Platform.OS === 'web') return false;
  const perm = await Notifications.requestPermissionsAsync();
  if (!perm.granted) return false;
  const [hour, minute] = checkinTime.split(':').map(Number);
  await Notifications.cancelAllScheduledNotificationsAsync();
  await Notifications.scheduleNotificationAsync({
    content: { title: 'Daily check-in', body: 'Time for your daily check-in. It only takes 2 minutes.' },
    trigger: { type: Notifications.SchedulableTriggerInputTypes.DAILY, hour, minute },
  });
  return true;
}
