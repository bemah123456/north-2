import { ReactNode } from 'react';
import { Pressable, ScrollView, StyleSheet, Text, TextInput, TextInputProps, View } from 'react-native';

import { colors, type } from './theme';

export function Screen({ children, scroll = true }: { children: ReactNode; scroll?: boolean }) {
  const body = <View style={styles.inner}>{children}</View>;
  return (
    <View style={styles.screen}>
      {scroll ? <ScrollView contentContainerStyle={{ flexGrow: 1 }}>{body}</ScrollView> : body}
    </View>
  );
}

export function Title({ children }: { children: ReactNode }) {
  return <Text style={styles.title} accessibilityRole="header">{children}</Text>;
}

export function Body({ children, muted }: { children: ReactNode; muted?: boolean }) {
  return <Text style={[styles.body, muted && { color: colors.muted }]}>{children}</Text>;
}

export function BigButton({ label, onPress, kind = 'primary', disabled }: {
  label: string;
  onPress: () => void;
  kind?: 'primary' | 'secondary' | 'danger';
  disabled?: boolean;
}) {
  const bg = kind === 'primary' ? colors.primary : kind === 'danger' ? colors.red : colors.card;
  const fg = kind === 'secondary' ? colors.primary : colors.primaryText;
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityLabel={label}
      disabled={disabled}
      onPress={onPress}
      style={({ pressed }) => [
        styles.button,
        { backgroundColor: bg, opacity: disabled ? 0.5 : pressed ? 0.8 : 1 },
        kind === 'secondary' && { borderWidth: 2, borderColor: colors.primary },
      ]}
    >
      <Text style={[styles.buttonText, { color: fg }]}>{label}</Text>
    </Pressable>
  );
}

export function Field({ label, ...props }: TextInputProps & { label: string }) {
  return (
    <View style={{ marginBottom: 16 }}>
      <Text style={styles.label}>{label}</Text>
      <TextInput style={styles.input} placeholderTextColor={colors.muted} {...props} />
    </View>
  );
}

export function Card({ children, accent }: { children: ReactNode; accent?: string }) {
  return <View style={[styles.card, accent ? { borderLeftWidth: 8, borderLeftColor: accent } : null]}>{children}</View>;
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: colors.bg },
  inner: { flex: 1, padding: 24, paddingTop: 64, maxWidth: 640, width: '100%', alignSelf: 'center' },
  title: { fontSize: type.huge, fontWeight: '700', color: colors.text, marginBottom: 16 },
  body: { fontSize: type.body, lineHeight: 30, color: colors.text, marginBottom: 12 },
  button: { minHeight: 72, borderRadius: 16, justifyContent: 'center', alignItems: 'center', paddingHorizontal: 20, marginVertical: 8 },
  buttonText: { fontSize: type.big, fontWeight: '700' },
  label: { fontSize: type.small, color: colors.muted, marginBottom: 6 },
  input: { fontSize: type.body, backgroundColor: colors.card, borderWidth: 1, borderColor: colors.border, borderRadius: 12, padding: 14, color: colors.text },
  card: { backgroundColor: colors.card, borderRadius: 16, padding: 18, marginBottom: 12, borderWidth: 1, borderColor: colors.border },
});
