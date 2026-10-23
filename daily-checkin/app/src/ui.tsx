import { ReactNode, useEffect, useRef, useState } from 'react';
import { Animated, Easing, Pressable, ScrollView, StyleSheet, Text, TextInput, TextInputProps, View } from 'react-native';

import { Backdrop, Icon, IconName, LogoMark, StatusDot } from './graphics';
import { useReducedMotion } from './motion';
import { brand, colors, font, maxScale, motion, radius, space, statusColor, statusIcon, statusSoft, type } from './theme';

// One screen: content at the top, and the main action pinned to the bottom
// where a thumb can reach it without scrolling. `backdrop` adds the soft
// brand shapes behind it.
export function Screen({ children, footer, scroll = true, backdrop }: {
  children: ReactNode;
  footer?: ReactNode;
  scroll?: boolean;
  backdrop?: 'calm' | 'bright';
}) {
  const body = <View style={styles.inner}>{children}</View>;
  return (
    <View style={styles.screen}>
      {backdrop && <Backdrop tone={backdrop} />}
      {scroll ? <ScrollView contentContainerStyle={{ flexGrow: 1 }}>{body}</ScrollView> : <View style={{ flex: 1 }}>{body}</View>}
      {footer && <View style={styles.footer}>{footer}</View>}
    </View>
  );
}

// The small Clari mark and name at the top of a screen.
export function BrandBar({ label }: { label?: string }) {
  return (
    <View style={styles.brandBar}>
      <LogoMark size={40} />
      <Text style={styles.brandName} maxFontSizeMultiplier={maxScale.tight}>Clari</Text>
      {label && <Text style={styles.brandLabel} maxFontSizeMultiplier={maxScale.tight}>{label}</Text>}
    </View>
  );
}

export function Title({ children, center }: { children: ReactNode; center?: boolean }) {
  return (
    <Text style={[styles.title, center && { textAlign: 'center' }]} accessibilityRole="header" maxFontSizeMultiplier={maxScale.heading}>
      {children}
    </Text>
  );
}

export function Body({ children, muted, center }: { children: ReactNode; muted?: boolean; center?: boolean }) {
  return <Text style={[styles.body, muted && { color: colors.muted }, center && { textAlign: 'center' }]}>{children}</Text>;
}

export function Section({ children, center }: { children: ReactNode; center?: boolean }) {
  return (
    <Text style={[styles.section, center && { textAlign: 'center' }]} accessibilityRole="header" maxFontSizeMultiplier={maxScale.heading}>
      {children}
    </Text>
  );
}

// Presses dip slightly and quickly, without moving anything around them.
function usePress() {
  const reduced = useReducedMotion();
  const s = useRef(new Animated.Value(1)).current;
  const to = (v: number) => () => {
    if (reduced) return;
    Animated.timing(s, { toValue: v, duration: motion.press, easing: Easing.out(Easing.quad), useNativeDriver: true }).start();
  };
  return { scale: s, onPressIn: to(0.97), onPressOut: to(1) };
}

export function BigButton({ label, hint, onPress, kind = 'primary', size = 'normal', disabled, icon }: {
  label: string;
  hint?: string; // a second, smaller line, e.g. "About 2 minutes"
  onPress: () => void;
  kind?: 'primary' | 'secondary' | 'danger';
  size?: 'normal' | 'hero';
  disabled?: boolean;
  icon?: IconName;
}) {
  const press = usePress();
  const fg = kind === 'secondary' ? colors.primary : colors.primaryText;
  const fill = kind === 'primary' ? colors.primary : kind === 'danger' ? colors.red : null;
  const content = (
    <>
      <View style={[styles.buttonRow, size === 'hero' && icon && styles.heroStack]}>
        {icon && <Icon name={icon} size={size === 'hero' ? 30 : 24} color={fg} weight={2.6} filled={icon === 'play' || icon === 'stop'} />}
        {/* Non-breaking hyphens keep "check-in" on one line at hero size. */}
        <Text maxFontSizeMultiplier={maxScale.button} style={[styles.buttonText, size === 'hero' && styles.heroText, { color: fg }]}>
          {size === 'hero' ? label.replace(/-/g, '‑') : label}
        </Text>
      </View>
      {hint && <Text maxFontSizeMultiplier={maxScale.button} style={[styles.buttonHint, { color: fg }]}>{hint}</Text>}
    </>
  );
  return (
    <Animated.View style={{ transform: [{ scale: press.scale }], opacity: disabled ? 0.45 : 1 }}>
      <Pressable
        accessibilityRole="button"
        accessibilityLabel={label}
        accessibilityHint={hint}
        accessibilityState={{ disabled }}
        disabled={disabled}
        onPress={onPress}
        onPressIn={press.onPressIn}
        onPressOut={press.onPressOut}
        style={[styles.buttonShell, size === 'hero' && styles.heroShell]}
      >
        {({ pressed }) =>
          fill ? (
            <View style={[styles.button, size === 'hero' && styles.hero, { backgroundColor: pressed ? colors.primaryPressed : fill }]}>
              {content}
            </View>
          ) : (
            <View style={[styles.button, styles.secondary, pressed && { backgroundColor: colors.primarySoft }]}>{content}</View>
          )
        }
      </Pressable>
    </Animated.View>
  );
}

// For rarely used actions (settings, change setup), so they don't compete
// with the one main button. Still a full-size touch target.
export function QuietButton({ label, onPress, icon }: { label: string; onPress: () => void; icon?: IconName }) {
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityLabel={label}
      onPress={onPress}
      hitSlop={8}
      style={({ pressed }) => [styles.quiet, pressed && { opacity: 0.6 }]}
    >
      {icon && <Icon name={icon} size={20} color={colors.primary} filled={icon === 'play' || icon === 'stop'} />}
      <Text style={styles.quietText}>{label}</Text>
    </Pressable>
  );
}

// A big choice with a title and a line of explanation, for picking a path.
export function Choice({ title, detail, onPress }: { title: string; detail: string; onPress: () => void }) {
  const press = usePress();
  return (
    <Animated.View style={{ transform: [{ scale: press.scale }] }}>
      <Pressable
        accessibilityRole="button"
        accessibilityLabel={title}
        accessibilityHint={detail}
        onPress={onPress}
        onPressIn={press.onPressIn}
        onPressOut={press.onPressOut}
        style={({ pressed }) => [styles.choice, pressed && { borderColor: colors.primary, backgroundColor: colors.primarySoft }]}
      >
        <View style={{ flex: 1 }}>
          <Text style={styles.choiceTitle} maxFontSizeMultiplier={maxScale.heading}>{title}</Text>
          <Text style={styles.choiceDetail}>{detail}</Text>
        </View>
        <View style={styles.choiceArrow}>
          <Icon name="chevronRight" size={26} color={colors.primary} weight={2.8} />
        </View>
      </Pressable>
    </Animated.View>
  );
}

export function Field({ label, big, ...props }: TextInputProps & { label: string; big?: boolean }) {
  const [focused, setFocused] = useState(false);
  return (
    <View style={{ marginBottom: space.m }}>
      <Text style={styles.label}>{label}</Text>
      <TextInput
        {...props}
        accessibilityLabel={label}
        style={[styles.input, big && styles.inputBig, focused && styles.inputFocused]}
        placeholderTextColor={colors.muted}
        onFocus={(e) => { setFocused(true); props.onFocus?.(e); }}
        onBlur={(e) => { setFocused(false); props.onBlur?.(e); }}
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
    <View style={[styles.card, tint ? { backgroundColor: tint, borderColor: 'transparent' } : null]}>
      {accent && <View style={[styles.cardAccent, { backgroundColor: accent }]} />}
      {children}
    </View>
  );
}

// A filled circle with an icon, so a status reads without colour.
export function StatusIcon({ status, size = 44 }: { status: string; size?: number }) {
  return <StatusDot icon={statusIcon[status]} color={statusColor[status]} size={size} />;
}

export function StatusPill({ status, label }: { status: string; label: string }) {
  return (
    <View style={[styles.pill, { backgroundColor: statusSoft[status] }]}>
      <Icon name={statusIcon[status]} size={20} color={statusColor[status]} weight={3} />
      <Text style={[styles.pillText, { color: statusColor[status] }]}>{label}</Text>
    </View>
  );
}

// "Question 2 of 7" as a bar that fills smoothly, so progress is visible at a glance.
export function Progress({ at, of }: { at: number; of: number }) {
  const reduced = useReducedMotion();
  const fill = useRef(new Animated.Value(Math.max(0, at - 1) / of)).current;
  useEffect(() => {
    if (reduced) fill.setValue(at / of);
    else Animated.timing(fill, { toValue: at / of, duration: motion.enter, easing: Easing.out(Easing.cubic), useNativeDriver: false }).start();
  }, [at, of, reduced]);
  return (
    <View accessibilityLabel={`Question ${at} of ${of}`} style={{ marginBottom: space.l }}>
      <Text style={styles.progressText}>Question {at} of {of}</Text>
      <View style={styles.progressTrack}>
        <Animated.View style={[styles.progressFill, { width: fill.interpolate({ inputRange: [0, 1], outputRange: ['0%', '100%'] }) }]} />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: colors.bg, overflow: 'hidden' },
  inner: { flex: 1, padding: space.l, paddingTop: 60, maxWidth: 640, width: '100%', alignSelf: 'center' },
  footer: { paddingHorizontal: space.l, paddingTop: space.s, paddingBottom: space.l, maxWidth: 640, width: '100%', alignSelf: 'center', gap: space.s },
  brandBar: { flexDirection: 'row', alignItems: 'center', gap: 10, marginBottom: space.m },
  brandName: { fontFamily: font.display, fontSize: 26, color: colors.primary, letterSpacing: 0.2 },
  brandLabel: { fontFamily: font.bodyBold, fontSize: type.small, color: colors.muted, marginLeft: 'auto' },
  title: { fontFamily: font.display, fontSize: type.huge, lineHeight: 42, color: colors.text, marginBottom: space.m },
  body: { fontFamily: font.body, fontSize: type.body, lineHeight: 32, color: colors.text, marginBottom: space.s },
  section: { fontFamily: font.display, fontSize: type.big - 3, color: colors.text, marginTop: space.l, marginBottom: space.s },
  buttonShell: { borderRadius: radius.l },
  heroShell: { borderRadius: radius.xl, shadowColor: colors.primary, shadowOpacity: 0.28, shadowRadius: 18, shadowOffset: { width: 0, height: 8 }, elevation: 6 },
  button: { minHeight: 76, borderRadius: radius.l, justifyContent: 'center', alignItems: 'center', paddingHorizontal: space.m, paddingVertical: space.s },
  secondary: { backgroundColor: colors.card, borderWidth: 3, borderColor: colors.primary },
  hero: { minHeight: 132, borderRadius: radius.xl },
  buttonRow: { flexDirection: 'row', alignItems: 'center', gap: 12 },
  heroStack: { flexDirection: 'column', gap: 6 },
  buttonText: { fontFamily: font.display, fontSize: type.big, textAlign: 'center', flexShrink: 1 },
  heroText: { fontSize: 31 },
  buttonHint: { fontFamily: font.bodyBold, fontSize: type.small, marginTop: 4, opacity: 0.92 },
  quiet: { minHeight: 56, flexDirection: 'row', gap: 8, justifyContent: 'center', alignItems: 'center' },
  quietText: { fontFamily: font.bodyBold, fontSize: type.small, color: colors.primary, textDecorationLine: 'underline' },
  choice: { flexDirection: 'row', alignItems: 'center', backgroundColor: colors.card, borderWidth: 2, borderColor: colors.border, borderRadius: radius.l, padding: space.m, marginBottom: space.s, minHeight: 112, gap: space.s },
  choiceTitle: { fontFamily: font.display, fontSize: type.big - 2, lineHeight: 32, color: colors.text },
  choiceDetail: { fontFamily: font.body, fontSize: type.small, lineHeight: 26, color: colors.muted, marginTop: 4 },
  choiceArrow: { width: 48, height: 48, borderRadius: 24, backgroundColor: colors.primarySoft, alignItems: 'center', justifyContent: 'center' },
  label: { fontFamily: font.bodyBold, fontSize: type.small, color: colors.text, marginBottom: space.xs },
  input: { fontFamily: font.body, fontSize: type.body, backgroundColor: colors.card, borderWidth: 2, borderColor: colors.border, borderRadius: radius.m, padding: 16, minHeight: 60, color: colors.text },
  inputFocused: { borderColor: colors.primary, borderWidth: 3, padding: 15 },
  inputBig: { fontFamily: font.display, fontSize: type.huge, letterSpacing: 4, textAlign: 'center', minHeight: 84 },
  pickRow: { flexDirection: 'row', flexWrap: 'wrap', gap: space.s },
  pick: { minHeight: 56, minWidth: 88, paddingHorizontal: space.m, borderRadius: radius.m, borderWidth: 2, borderColor: colors.primary, backgroundColor: colors.card, justifyContent: 'center', alignItems: 'center' },
  pickOn: { backgroundColor: colors.primary },
  pickText: { fontFamily: font.display, fontSize: type.body, color: colors.primary },
  card: { backgroundColor: colors.card, borderRadius: radius.l, padding: space.m, marginBottom: space.s, borderWidth: 1, borderColor: colors.border, overflow: 'hidden' },
  cardAccent: { position: 'absolute', left: 0, top: 0, bottom: 0, width: 8 },
  pill: { flexDirection: 'row', alignItems: 'center', gap: 6, borderRadius: radius.round, paddingHorizontal: 12, paddingVertical: 6, alignSelf: 'flex-start' },
  pillText: { fontFamily: font.bodyBold, fontSize: type.small },
  progressText: { fontFamily: font.bodyBold, fontSize: type.small, color: colors.muted, marginBottom: space.xs },
  progressTrack: { height: 12, borderRadius: 6, backgroundColor: colors.border, overflow: 'hidden' },
  progressFill: { height: '100%', borderRadius: 6, backgroundColor: brand.solid },
});
