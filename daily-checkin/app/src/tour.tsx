// "How Clari works": a short tour for the family, shown once after setup
// and any time from Settings. Five cards, one idea each.

import { ReactNode, useState } from 'react';
import { StyleSheet, Text, View } from 'react-native';

import { TONE, Tone } from './calendar';
import { Done, Icon, LogoMark, Speaking } from './graphics';
import { Rise } from './motion';
import { colors, font, maxScale, radius, space, type } from './theme';
import { BigButton, QuietButton, Screen } from './ui';

export const TOUR_KEY = (personId: string) => `clari.tour.${personId}`;

const FOUR_AT = [
  ['Alertness', 'Are they awake and answering normally?'],
  ['Orientation', 'Their age, birthday, where they are, and the year.'],
  ['Attention', 'The months of the year, backwards.'],
  ['Sudden change', 'Different from their usual days?'],
];

export function HowItWorks({ name, onDone }: { name: string; onDone: () => void }) {
  const [step, setStep] = useState(0);
  const slides: { art: ReactNode; title: string; body: ReactNode }[] = [
    {
      art: <Speaking size={110} />,
      title: 'A 2-minute chat each day',
      body: <Text style={styles.body}>{name} taps one big button and answers a few questions out loud. Clari reads each question for them.</Text>,
    },
    {
      art: <LogoMark size={110} />,
      title: 'Questions from the 4AT',
      body: (
        <>
          <Text style={styles.body}>The 4AT is a short test hospitals use to spot delirium. Clari asks about the same four things:</Text>
          <View style={styles.list}>
            {FOUR_AT.map(([t, d]) => (
              <View key={t} style={styles.row}>
                <Icon name="check" size={22} color={colors.primary} weight={3} />
                <Text style={styles.rowText}><Text style={styles.bold}>{t}.</Text> {d}</Text>
              </View>
            ))}
          </View>
        </>
      ),
    },
    {
      art: <View style={styles.legendArt}>{(['red', 'yellow', 'green'] as Tone[]).map((k) => (
        <View key={k} style={[styles.swatch, { backgroundColor: TONE[k].bg }]}><Icon name={TONE[k].icon} size={26} color={TONE[k].fg} weight={3} /></View>
      ))}</View>,
      title: 'What the colours mean',
      body: (
        <View style={styles.list}>
          {([['red', 'Call their doctor', '4 or more'], ['yellow', 'Keep an eye on it', '1 to 3, a missed day, or hard to hear'], ['green', 'Their usual self', '0']] as [Tone, string, string][]).map(([k, t, d]) => (
            <View key={k} style={styles.row}>
              <View style={[styles.dot, { backgroundColor: TONE[k].bg }]} />
              <Text style={styles.rowText}><Text style={styles.bold}>{t}</Text> · {d}</Text>
            </View>
          ))}
        </View>
      ),
    },
    {
      art: <Icon name="calendar" size={96} color={colors.primary} weight={1.8} />,
      title: 'Every day, at a glance',
      body: <Text style={styles.body}>Tap any day on the calendar to see its score, hear the conversation, and add your own notes for their doctor.</Text>,
    },
    {
      art: <Done size={96} />,
      title: 'If a day turns red',
      body: (
        <Text style={styles.body}>
          Call their doctor. Clari is a screening aid, not a diagnosis. In an emergency, call 911.{'\n\n'}
          Questions? Ask Clari any time in Messages.
        </Text>
      ),
    },
  ];
  const s = slides[step];
  const last = step === slides.length - 1;
  return (
    <Screen
      backdrop="bright"
      footer={
        <>
          <BigButton label={last ? 'Start using Clari' : 'Next'} onPress={() => (last ? onDone() : setStep(step + 1))} />
          <View style={styles.footRow}>
            {step > 0 ? <QuietButton label="Back" onPress={() => setStep(step - 1)} /> : <View />}
            {!last && <QuietButton label="Skip" onPress={onDone} />}
          </View>
        </>
      }
    >
      <Text style={styles.eyebrow} accessibilityLabel={`How Clari works, ${step + 1} of ${slides.length}`}>How Clari works</Text>
      <View style={styles.dots}>
        {slides.map((_, i) => <View key={i} style={[styles.pip, i === step && styles.pipOn]} />)}
      </View>
      <Rise key={step} style={styles.slide}>
        <View style={styles.art}>{s.art}</View>
        <Text style={styles.title} accessibilityRole="header" maxFontSizeMultiplier={maxScale.heading}>{s.title}</Text>
        {s.body}
      </Rise>
    </Screen>
  );
}

const styles = StyleSheet.create({
  eyebrow: { fontFamily: font.bodyBold, fontSize: type.small, color: colors.muted, textAlign: 'center', textTransform: 'uppercase', letterSpacing: 1.2 },
  dots: { flexDirection: 'row', justifyContent: 'center', gap: 8, marginVertical: space.m },
  pip: { width: 10, height: 10, borderRadius: 5, backgroundColor: colors.border },
  pipOn: { width: 28, backgroundColor: colors.primary },
  slide: { alignItems: 'center', gap: space.m },
  art: { minHeight: 150, alignItems: 'center', justifyContent: 'center' },
  title: { fontFamily: font.display, fontSize: type.huge, lineHeight: 42, color: colors.text, textAlign: 'center' },
  body: { fontFamily: font.body, fontSize: type.body, lineHeight: 32, color: colors.text, textAlign: 'center' },
  list: { alignSelf: 'stretch', backgroundColor: colors.card, borderRadius: radius.l, borderWidth: 1, borderColor: colors.border, padding: space.m, gap: 12 },
  row: { flexDirection: 'row', alignItems: 'flex-start', gap: 10 },
  rowText: { flex: 1, fontFamily: font.body, fontSize: type.small, lineHeight: 26, color: colors.text },
  bold: { fontFamily: font.bodyBold },
  dot: { width: 22, height: 22, borderRadius: 6, marginTop: 2 },
  legendArt: { flexDirection: 'row', gap: 12 },
  swatch: { width: 64, height: 64, borderRadius: 16, alignItems: 'center', justifyContent: 'center' },
  footRow: { flexDirection: 'row', justifyContent: 'space-between' },
});
