import { useEffect, useState } from 'react';
import { Platform } from 'react-native';
import { StatusBar } from 'expo-status-bar';
import AsyncStorage from '@react-native-async-storage/async-storage';

import CheckIn from './src/screens/CheckIn';
import FamilyHome from './src/screens/FamilyHome';
import SeniorHome from './src/screens/SeniorHome';
import Setup, { Role } from './src/screens/Setup';
import { Body, Screen } from './src/ui';

const KEY = 'checkin.setup';
// On the web there's often no reliable microphone, so the demo types answers
// unless EXPO_PUBLIC_WEB_MIC=1.
const TYPED = Platform.OS === 'web' && process.env.EXPO_PUBLIC_WEB_MIC !== '1';

type Saved = { role: Role; personId: string };

export default function App() {
  const [loaded, setLoaded] = useState(false);
  const [saved, setSaved] = useState<Saved | null>(null);
  const [checkingIn, setCheckingIn] = useState(false);

  useEffect(() => {
    AsyncStorage.getItem(KEY)
      .then((v) => v && setSaved(JSON.parse(v)))
      .finally(() => setLoaded(true));
  }, []);

  async function ready(role: Role, personId: string) {
    const s = { role, personId };
    await AsyncStorage.setItem(KEY, JSON.stringify(s));
    setSaved(s);
  }

  async function signOut() {
    await AsyncStorage.removeItem(KEY);
    setSaved(null);
  }

  let screen;
  if (!loaded) screen = <Screen><Body muted>Loading…</Body></Screen>;
  else if (!saved) screen = <Setup onReady={ready} />;
  else if (saved.role === 'family') screen = <FamilyHome personId={saved.personId} onSignOut={signOut} />;
  else if (checkingIn) screen = <CheckIn personId={saved.personId} typedMode={TYPED} onFinished={() => setCheckingIn(false)} />;
  else screen = <SeniorHome personId={saved.personId} onStart={() => setCheckingIn(true)} onSignOut={signOut} />;

  return (
    <>
      {screen}
      <StatusBar style="dark" />
    </>
  );
}
