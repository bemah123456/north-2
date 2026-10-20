import { ReactNode, useEffect, useRef } from 'react';
import { Animated, Easing, Platform, Pressable, ScrollView, StyleSheet, Text, TextInput, TextInputProps, View } from 'react-native';

import { colors, maxScale, radius, space, statusColor, statusSoft, statusSymbol, type } from './theme';

// One screen: content at the top, and the main action pinned to the bottom
// where a thumb can reach it without scrolling.
export function Screen({ children, footer, scroll = true }: { children: ReactNode; footer?: ReactNode; scroll?: boolean }) {
  const body = <View style={styles.inner}>{children}</View>;
  return (
    <View style={styles.screen}>
      {scroll ? <ScrollView contentContainerStyle={{ flexGrow: 1 }}>{body}</ScrollView> : <View style={{ flex: 1 }}>{body}</View>}
      {footer && <View style={styles.footer}>{footer}</View>}
    </View>
  );
}

export function Title({ children }: { children: ReactNode }) {
  return <Text style={styles.title} accessibilityRole="header" maxFontSizeMultiplier={maxScale.heading}>{children}</Text>;
}

export function Body({ children, muted, center }: { children: ReactNode; muted?: boolean; center?: boolean }) {
  return <Text style={[styles.body, muted && { color: colors.muted }, center && { textAlign: 'center' }]}>{children}</Text>;
}

export function Section({ children }: { children: ReactNode }) {
  return <Text style={styles.section} accessibilityRole="header">{children}</Text>;
}

export function BigButton({ label, hint, onPress, kind = 'primary', size = 'normal', disabled }: {
  label: string;
  hint?: string; // a second, smaller line, e.g. "About 2 minutes"
  onPress: () => void;
  kind?: 'primary' | 'secondary' | 'danger';
  size?: 'normal' | 'hero';
  disabled?: boolean;
}) {
  const bg = kind === 'primary' ? colors.primary : kind === 'danger' ? colors.red : colors.card;
  const fg = kind === 'secondary' ? colors.primary : colors.primaryText;
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityLabel={label}
      accessibilityHint={hint}
      accessibilityState={{ disabled }}
      disabled={disabled}
      onPress={onPress}
      style={({ pressed }) => [
        styles.button,
        size === 'hero' && styles.hero,
        { backgroundColor: kind === 'primary' && pressed ? colors.primaryPressed : bg, opacity: disabled ? 0.45 : 1 },
        kind === 'secondary' && { borderWidth: 3, borderColor: colors.primary },
        pressed && { transform: [{ scale: 0.98 }] },
      ]}
    >
      {/* Non-breaking hyphens keep "check-in" on one line at hero size. */}
      <Text maxFontSizeMultiplier={maxScale.button} style={[styles.buttonText, size === 'hero' && { fontSize: 30 }, { color: fg }]}>{size === 'hero' ? label.replace(/-/g, '\u2011') : label}</Text>
      {hint && <Text maxFontSizeMultiplier={maxScale.button} style={[styles.buttonHint, { color: fg }]}>{hint}</Text>}
    </Pressable>
  );
}

// For rarely used actions (settings, change setup), so they don't compete
// with the one main button. Still a full-size touch target.
export function QuietButton({ label, onPress }: { label: string; onPress: () => void }) {
  return (
    <Pressable accessibilityRole="button" accessibilityLabel={label} onPress={onPress} style={styles.quiet} hitSlop={8}>
      <Text style={styles.quietText}>{label}</Text>
    </Pressable>
  );
}

// A big choice with a title and a line of explanation, for picking a path.
export function Choice({ title, detail, onPress }: { title: string; detail: string; onPress: () => void }) {
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityLabel={title}
      accessibilityHint={detail}
      onPress={onPress}
      style={({ pressed }) => [styles.choice, pressed && { borderColor: colors.primary, backgroundColor: colors.primarySoft }]}
    >
      <View style={{ flex: 1 }}>
        <Text style={styles.choiceTitle} maxFontSizeMultiplier={maxScale.heading}>{title}</Text>
        <Text style={styles.choiceDetail}>{detail}</Text>
      </View>
      <Text style={styles.chevron} maxFontSizeMultiplier={maxScale.tight}>›</Text>
    </Pressable>
  );
}

export function Field({ label, big, ...props }: TextInputProps & { label: string; big?: boolean }) {
  return (
    <View style={{ marginBottom: space.m }}>
      <Text style={styles.label}>{label}</Text>
      <TextInput
        accessibilityLabel={label}
        style={[styles.input, big && styles.inputBig]}
        placeholderTextColor={colors.muted}
        {...props}
      />
    </View>
  );
}

// A row of options where exactly one is picked, e.g. the check-in time.
export function Pick<T extends string>({ label, options, value, onChange }: {
  label: string;
  options: { value: T; label: string }[];
  value: T;
  onChange: (v: T) => void;
}) {
  return (
    <View style={{ marginBottom: space.m }}>
      <Text style={styles.label}>{label}</Text>
      <View style={styles.pickRow} accessibilityRole="radiogroup">
        {options.map((o) => {
          const on = o.value === value;
          return (
            <Pressable
              key={o.value}
              accessibilityRole="radio"
              accessibilityState={{ checked: on }}
              accessibilityLabel={o.label}
              onPress={() => onChange(o.value)}
              style={[styles.pick, on && styles.pickOn]}
            >
              <Text maxFontSizeMultiplier={maxScale.button} style={[styles.pickText, on && { color: colors.primaryText }]}>{o.label}</Text>
            </Pressable>
          );
        })}
      </View>
    </View>
  );
}

export function Card({ children, accent, tint }: { children: ReactNode; accent?: string; tint?: string }) {
  return (
    <View style={[styles.card, accent ? { borderLeftWidth: 10, borderLeftColor: accent } : null, tint ? { backgroundColor: tint } : null]}>
      {children}
    </View>
  );
}

// A filled circle with a symbol, so a status reads without colour.
export function StatusIcon({ status, size = 44 }: { status: string; size?: number }) {
  return (
    <View
      accessibilityElementsHidden
      importantForAccessibility="no"
      style={{ width: size, height: size, borderRadius: size / 2, backgroundColor: statusColor[status], alignItems: 'center', justifyContent: 'center' }}
    >
      <Text maxFontSizeMultiplier={1} style={{ color: '#FFFFFF', fontSize: size * 0.55, fontWeight: '800', lineHeight: size * 0.7 }}>{statusSymbol[status]}</Text>
    </View>
  );
}

export function StatusPill({ status, label }: { status: string; label: string }) {
  return (
    <View style={[styles.pill, { backgroundColor: statusSoft[status], borderColor: statusColor[status] }]}>
      <Text style={[styles.pillText, { color: statusColor[status] }]}>{statusSymbol[status]}  {label}</Text>
    </View>
  );
}

// "Question 2 of 7" as a row of segments, so progress is visible at a glance.
export function Progress({ at, of }: { at: number; of: number }) {
  return (
    <View accessibilityLabel={`Question ${at} of ${of}`} style={{ marginBottom: space.l }}>
      <Text style={styles.progressText}>Question {at} of {of}</Text>
      <View style={styles.progressRow}>
        {Array.from({ length: of }, (_, i) => (
          <View key={i} style={[styles.segment, { backgroundColor: i < at ? colors.primary : colors.border }]} />
        ))}
      </View>
    </View>
  );
}

// A big round badge: a tick when something is done, a gently pulsing ring
// while the app is listening, a speaker while it is talking.
export function Badge({ mode, active = true }: { mode: 'done' | 'listening' | 'speaking'; active?: boolean }) {
  const pulse = useRef(new Animated.Value(0)).current;
  useEffect(() => {
    if (mode === 'done') return;
    const loop = Animated.loop(
      Animated.timing(pulse, { toValue: 1, duration: 1400, easing: Easing.out(Easing.ease), useNativeDriver: Platform.OS !== 'web' }),
    );
    loop.start();
    return () => loop.stop();
  }, [mode]);
  const color = mode === 'listening' ? colors.red : colors.primary;
  const symbol = mode === 'done' ? '✓' : mode === 'listening' ? '●' : '♪';
  return (
    <View style={styles.badgeWrap} accessibilityElementsHidden importantForAccessibility="no">
      {mode !== 'done' && (
        <Animated.View
          style={[
            styles.badgeRing,
            { borderColor: color, opacity: pulse.interpolate({ inputRange: [0, 1], outputRange: [active ? 0.6 : 0.2, 0] }) },
            { transform: [{ scale: pulse.interpolate({ inputRange: [0, 1], outputRange: [1, 1.45] }) }] },
          ]}
        />
      )}
      <View style={[styles.badge, { backgroundColor: mode === 'done' ? colors.green : color }]}>
        <Text style={styles.badgeText} maxFontSizeMultiplier={1}>{symbol}</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: colors.bg },
  inner: { flex: 1, padding: space.l, paddingTop: 64, maxWidth: 640, width: '100%', alignSelf: 'center' },
  footer: { paddingHorizontal: space.l, paddingTop: space.s, paddingBottom: space.l, maxWidth: 640, width: '100%', alignSelf: 'center' },
  title: { fontSize: type.huge, lineHeight: 44, fontWeight: '800', color: colors.text, marginBottom: space.m },
  body: { fontSize: type.body, lineHeight: 32, color: colors.text, marginBottom: space.s },
  section: { fontSize: type.body, fontWeight: '800', color: colors.text, marginTop: space.l, marginBottom: space.s },
  button: { minHeight: 76, borderRadius: radius.l, justifyContent: 'center', alignItems: 'center', paddingHorizontal: space.m, paddingVertical: space.s, marginVertical: space.xs },
  hero: { minHeight: 132, borderRadius: 32, shadowColor: '#000', shadowOpacity: 0.18, shadowRadius: 12, shadowOffset: { width: 0, height: 6 }, elevation: 4 },
  buttonText: { fontSize: type.big, fontWeight: '800', textAlign: 'center' },
  buttonHint: { fontSize: type.small, fontWeight: '600', marginTop: 4, opacity: 0.9 },
  quiet: { minHeight: 56, justifyContent: 'center', alignItems: 'center', marginTop: space.xs },
  quietText: { fontSize: type.small, color: colors.muted, fontWeight: '600', textDecorationLine: 'underline' },
  choice: { flexDirection: 'row', alignItems: 'center', backgroundColor: colors.card, borderWidth: 3, borderColor: colors.border, borderRadius: radius.l, padding: space.m, marginBottom: space.s, minHeight: 112 },
  choiceTitle: { fontSize: type.big, fontWeight: '800', color: colors.text },
  choiceDetail: { fontSize: type.small, lineHeight: 26, color: colors.muted, marginTop: 4 },
  chevron: { fontSize: 48, color: colors.primary, marginLeft: space.s, fontWeight: '300' },
  label: { fontSize: type.small, fontWeight: '700', color: colors.text, marginBottom: space.xs },
  input: { fontSize: type.body, backgroundColor: colors.card, borderWidth: 2, borderColor: colors.border, borderRadius: radius.m, padding: 16, minHeight: 60, color: colors.text },
  inputBig: { fontSize: type.huge, fontWeight: '700', letterSpacing: 4, textAlign: 'center', minHeight: 84 },
  pickRow: { flexDirection: 'row', flexWrap: 'wrap', gap: space.s },
  pick: { minHeight: 56, minWidth: 88, paddingHorizontal: space.m, borderRadius: radius.m, borderWidth: 2, borderColor: colors.primary, backgroundColor: colors.card, justifyContent: 'center', alignItems: 'center' },
  pickOn: { backgroundColor: colors.primary },
  pickText: { fontSize: type.body, fontWeight: '700', color: colors.primary },
  card: { backgroundColor: colors.card, borderRadius: radius.l, padding: space.m, marginBottom: space.s, borderWidth: 1, borderColor: colors.border },
  pill: { borderRadius: radius.round, borderWidth: 2, paddingHorizontal: 14, paddingVertical: 6, alignSelf: 'flex-start' },
  pillText: { fontSize: type.small, fontWeight: '800' },
  progressText: { fontSize: type.small, fontWeight: '700', color: colors.muted, marginBottom: space.xs },
  progressRow: { flexDirection: 'row', gap: 6 },
  segment: { flex: 1, height: 10, borderRadius: 5 },
  badgeWrap: { width: 160, height: 160, alignItems: 'center', justifyContent: 'center', alignSelf: 'center', marginVertical: space.m },
  badgeRing: { position: 'absolute', width: 140, height: 140, borderRadius: 70, borderWidth: 10 },
  badge: { width: 120, height: 120, borderRadius: 60, alignItems: 'center', justifyContent: 'center' },
  badgeText: { color: '#FFFFFF', fontSize: 60, fontWeight: '800', lineHeight: 72 },
});
