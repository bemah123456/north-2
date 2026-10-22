// The Messages tab: texts Clari sent the family, then "Ask Clari", a chat
// where the family can ask what anything means or how to set Clari up for
// them. Clari can suggest a settings change as a button; nothing changes
// until they tap it. The chat is kept on this phone.

import { ReactNode, useEffect, useState } from 'react';
import { Pressable, StyleSheet, Text, TextInput, View } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

import { Alert, api, ChatTurn, DayRow, Person, Suggestion } from '../api';
import { Icon, LogoMark } from '../graphics';
import { Rise } from '../motion';
import { colors, font, maxScale, radius, space, type } from '../theme';
import { BigButton, Body, BrandBar, Card, QuietButton, Screen, Section, Title } from '../ui';

type ChatMessage = ChatTurn & { suggestions?: Suggestion[]; done?: string[] };

const STARTERS = [
  'What is the 4AT?',
  'What do the colours mean?',
  'Should I turn on the evening check-in?',
  'How do the recordings work?',
];

function niceDate(iso: string) {
  return new Date(`${iso}T12:00:00`).toLocaleDateString(undefined, { weekday: 'long', month: 'short', day: 'numeric' });
}

export default function Messages({ personId, person, days, alerts, tabBar, onFeedback, onOpenDay, onApply }: {
  personId: string;
  person: Person | null;
  days: DayRow[];
  alerts: Alert[];
  tabBar: ReactNode;
  onFeedback: (a: Alert, real: boolean) => void;
  onOpenDay: (row: DayRow) => void;
  onApply: (s: Suggestion) => Promise<string>; // returns what changed, e.g. "The evening check-in is on."
}) {
  const key = `clari.chat.${personId}`;
  const [chat, setChat] = useState<ChatMessage[]>([]);
  const [draft, setDraft] = useState('');
  const [waiting, setWaiting] = useState(false);
  const toFamily = alerts.filter((a) => !a.kind.startsWith('reminder'));
  const name = person?.name ?? 'them';

  useEffect(() => {
    AsyncStorage.getItem(key).then((v) => v && setChat(JSON.parse(v))).catch(() => {});
  }, [key]);

  function save(next: ChatMessage[]) {
    const kept = next.slice(-40);
    setChat(kept);
    AsyncStorage.setItem(key, JSON.stringify(kept)).catch(() => {});
  }

  async function send(text: string) {
    const message = text.trim();
    if (!message || waiting) return;
    setDraft('');
    const history: ChatTurn[] = chat.map(({ role, text: t }) => ({ role, text: t }));
    const withQuestion = [...chat, { role: 'user' as const, text: message }];
    save(withQuestion);
    setWaiting(true);
    try {
      const r = await api.ask(personId, message, history);
      save([...withQuestion, { role: 'assistant', text: r.reply, suggestions: r.suggestions }]);
    } catch {
      save([...withQuestion, { role: 'assistant', text: "Sorry, I can't reach the server right now. Try again in a moment." }]);
    } finally {
      setWaiting(false);
    }
  }

  async function apply(i: number, s: Suggestion) {
    try {
      const said = await onApply(s);
      const next = chat.map((m, j) => (j === i ? { ...m, done: [...(m.done ?? []), s.label] } : m));
      save([...next, { role: 'assistant', text: `Done. ${said}` }]);
    } catch (e) {
      save([...chat, { role: 'assistant', text: `That didn't work: ${(e as Error).message}` }]);
    }
  }

  const composer = (
    <View style={styles.composer}>
      <TextInput
        accessibilityLabel="Ask Clari a question"
        style={styles.input}
        value={draft}
        onChangeText={setDraft}
        placeholder="Ask Clari a question"
        placeholderTextColor={colors.muted}
        onSubmitEditing={() => send(draft)}
        returnKeyType="send"
        maxLength={1000}
      />
      <Pressable
        accessibilityRole="button"
        accessibilityLabel="Send"
        disabled={!draft.trim() || waiting}
        onPress={() => send(draft)}
        style={({ pressed }) => [styles.send, (!draft.trim() || waiting) && { opacity: 0.4 }, pressed && { opacity: 0.7 }]}
      >
        <Icon name="chevronRight" size={28} color={colors.primaryText} weight={3} />
      </Pressable>
    </View>
  );

  return (
    <Screen key="messages" backdrop="calm" scrollToEndOn={chat.length + (waiting ? 0.5 : 0)} footer={<>{composer}{tabBar}</>}>
      <BrandBar label="Messages" />
      <Title center>Messages</Title>

      {toFamily.length > 0 && (
        <>
          <Section center>Texts from Clari</Section>
          {toFamily.slice(0, 10).map((a, i) => (
            <Rise key={`${a.date}${a.kind}`} order={i}>
              <Card>
                <Text style={styles.date}>{niceDate(a.date)}</Text>
                <Body center>
                  {a.message}
                  {a.delivered ? '' : ' (not sent: test mode)'}
                </Body>
                {a.kind.startsWith('missed') &&
                  (a.was_real === null ? (
                    <>
                      <Body muted center>Was this a real concern?</Body>
                      <View style={styles.pair}>
                        <View style={{ flex: 1 }}><BigButton label="Yes" kind="secondary" onPress={() => onFeedback(a, true)} /></View>
                        <View style={{ flex: 1 }}><BigButton label="No, all fine" kind="secondary" onPress={() => onFeedback(a, false)} /></View>
                      </View>
                    </>
                  ) : (
                    <Body muted center>You said: {a.was_real ? 'a real concern' : 'all fine'}.</Body>
                  ))}
                {a.kind.endsWith('recording') && days.find((d) => d.date === a.date)?.checkin_id && (
                  <QuietButton label="Open that day" onPress={() => { const d = days.find((r) => r.date === a.date); if (d) onOpenDay(d); }} />
                )}
              </Card>
            </Rise>
          ))}
        </>
      )}

      <Section center>Ask Clari</Section>
      <Bubble from="clari">
        Hi, I'm Clari. Ask me what anything in the app means, or how to set Clari up for {name}.
      </Bubble>
      {chat.length === 0 && (
        <View style={styles.starters}>
          {STARTERS.map((q) => (
            <Pressable key={q} accessibilityRole="button" onPress={() => send(q)} style={({ pressed }) => [styles.starter, pressed && { opacity: 0.7 }]}>
              <Text style={styles.starterText}>{q}</Text>
            </Pressable>
          ))}
        </View>
      )}
      {chat.map((m, i) => (
        <View key={i}>
          <Bubble from={m.role === 'user' ? 'you' : 'clari'}>{m.text}</Bubble>
          {m.suggestions?.map((s) => {
            const done = m.done?.includes(s.label);
            return (
              <View key={s.label} style={styles.suggestion}>
                <BigButton label={done ? 'Done' : s.label} icon={done ? 'check' : undefined} kind="secondary" disabled={done}
                  onPress={() => apply(i, s)} />
              </View>
            );
          })}
        </View>
      ))}
      {waiting && <Bubble from="clari">…</Bubble>}
      <Text style={styles.small}>Clari explains the app. It isn't medical advice. In an emergency, call 911.</Text>
    </Screen>
  );
}

function Bubble({ from, children }: { from: 'clari' | 'you'; children: ReactNode }) {
  const mine = from === 'you';
  return (
    <View style={[styles.bubbleRow, mine && { justifyContent: 'flex-end' }]}>
      {!mine && <View style={styles.avatar}><LogoMark size={30} /></View>}
      <View style={[styles.bubble, mine ? styles.mine : styles.theirs]}>
        <Text style={[styles.bubbleText, mine && { color: colors.primaryText }]} maxFontSizeMultiplier={maxScale.heading}>{children}</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  date: { fontFamily: font.bodyBold, fontSize: type.body, color: colors.text, marginBottom: 6, textAlign: 'center' },
  pair: { flexDirection: 'row', gap: 12 },
  starters: { gap: 8, marginBottom: space.s, marginLeft: 44 },
  starter: { alignSelf: 'flex-start', borderWidth: 2, borderColor: colors.primary, borderRadius: radius.round, paddingVertical: 10, paddingHorizontal: 16, backgroundColor: colors.card },
  starterText: { fontFamily: font.bodyBold, fontSize: type.small, color: colors.primary },
  bubbleRow: { flexDirection: 'row', alignItems: 'flex-end', gap: 8, marginBottom: 10 },
  avatar: { width: 36, height: 36, borderRadius: 18, backgroundColor: colors.card, borderWidth: 1, borderColor: colors.border, alignItems: 'center', justifyContent: 'center' },
  bubble: { maxWidth: '82%', borderRadius: 20, paddingVertical: 12, paddingHorizontal: 16 },
  theirs: { backgroundColor: colors.card, borderWidth: 1, borderColor: colors.border, borderBottomLeftRadius: 6 },
  mine: { backgroundColor: colors.primary, borderBottomRightRadius: 6 },
  bubbleText: { fontFamily: font.body, fontSize: type.small, lineHeight: 26, color: colors.text },
  suggestion: { marginLeft: 44, marginBottom: 10 },
  small: { fontFamily: font.body, fontSize: 15, color: colors.muted, textAlign: 'center', marginTop: space.s },
  composer: { flexDirection: 'row', gap: 8, alignItems: 'center' },
  input: { flex: 1, fontFamily: font.body, fontSize: type.small, minHeight: 56, backgroundColor: colors.card, borderWidth: 2, borderColor: colors.border, borderRadius: radius.round, paddingHorizontal: 18, color: colors.text },
  send: { width: 56, height: 56, borderRadius: 28, backgroundColor: colors.primary, alignItems: 'center', justifyContent: 'center' },
});
