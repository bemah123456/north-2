// Clari's graphics, all flat solid colours: one family of rounded line
// icons, the logo's dots-and-lines motif, pale background shapes, and the
// animated pieces of the check-in (speaking, listening, done). Everything
// here is decoration or has a text label next to it, so it is hidden from
// screen readers.

import { useEffect, useRef } from 'react';
import { Animated, Easing, Image, StyleSheet, View } from 'react-native';
import Svg, { Circle, Path } from 'react-native-svg';

import { native, useBreath, useReducedMotion } from './motion';
import { brand, colors, motion } from './theme';

const hidden = { accessibilityElementsHidden: true, importantForAccessibility: 'no-hide-descendants' as const };

// ---------- icons ----------

export type IconName = 'check' | 'alert' | 'question' | 'dots' | 'dash' | 'mic' | 'speaker' | 'play' | 'stop'
  | 'chevronRight' | 'chevronLeft' | 'chevronDown' | 'chevronUp';

const ICONS: Record<IconName, string> = {
  check: 'M5 12.5l4.5 4.5L19 7.5',
  alert: 'M12 5.5v8.5M12 18.5v.01',
  question: 'M9 9a3 3 0 1 1 4.2 2.75c-.75.35-1.2 1.05-1.2 1.9v.85M12 18.5v.01',
  dots: 'M6.5 12h.01M12 12h.01M17.5 12h.01',
  dash: 'M6.5 12h11',
  mic: 'M12 4a3 3 0 0 0-3 3v5a3 3 0 0 0 6 0V7a3 3 0 0 0-3-3zM6 11.5a6 6 0 0 0 12 0M12 17.5V20',
  speaker: 'M4.5 9.5h3l4-3.5v12l-4-3.5h-3zM15.5 9a4 4 0 0 1 0 6M18 6.5a7.5 7.5 0 0 1 0 11',
  play: 'M8 5.5v13l10-6.5z',
  stop: 'M7 7h10v10H7z',
  chevronRight: 'M9.5 5.5L16 12l-6.5 6.5',
  chevronLeft: 'M14.5 5.5L8 12l6.5 6.5',
  chevronDown: 'M5.5 9.5L12 16l6.5-6.5',
  chevronUp: 'M5.5 14.5L12 8l6.5 6.5',
};

export function Icon({ name, size = 24, color = colors.text, weight = 2.4, filled = false }: {
  name: IconName; size?: number; color?: string; weight?: number; filled?: boolean;
}) {
  return (
    <Svg width={size} height={size} viewBox="0 0 24 24" {...hidden}>
      <Path d={ICONS[name]} stroke={color} strokeWidth={weight} strokeLinecap="round" strokeLinejoin="round"
        fill={filled ? color : 'none'} />
    </Svg>
  );
}

// A filled circle with an icon, so a status reads without colour.
export function StatusDot({ icon, color, size = 44 }: { icon: IconName; color: string; size?: number }) {
  return (
    <View {...hidden} style={{ width: size, height: size, borderRadius: size / 2, backgroundColor: color, alignItems: 'center', justifyContent: 'center' }}>
      <Icon name={icon} size={size * 0.62} color="#FFFFFF" weight={3} />
    </View>
  );
}

// ---------- brand ----------

export function LogoMark({ size = 56, breathe = false }: { size?: number; breathe?: boolean }) {
  const t = useBreath(motion.breathe, breathe);
  const scale = t.interpolate({ inputRange: [0, 1], outputRange: [1, 1.06] });
  return (
    <Animated.View {...hidden} style={{ width: size, height: size * 0.84, transform: [{ scale }] }}>
      <Image source={require('../assets/logo-mark.png')} style={{ width: '100%', height: '100%' }} resizeMode="contain" />
    </Animated.View>
  );
}

export function LogoFull({ width = 200 }: { width?: number }) {
  return (
    <Image
      source={require('../assets/logo-full.png')}
      style={{ width, height: width * 1.03 }}
      resizeMode="contain"
      accessibilityRole="image"
      accessibilityLabel="Clari"
    />
  );
}

// The logo's motif: three dots joined by a line. Used as a small divider.
export function NodeLine({ width = 96 }: { width?: number }) {
  const h = width * 0.25;
  return (
    <Svg width={width} height={h} viewBox="0 0 96 24" {...hidden}>
      <Path d="M8 18L40 8L60 14L88 6" stroke={brand.solid} strokeWidth={3} strokeLinecap="round" strokeLinejoin="round" fill="none" />
      <Circle cx={8} cy={18} r={5} fill={brand.solid} />
      <Circle cx={40} cy={8} r={5} fill={brand.solid} />
      <Circle cx={88} cy={6} r={5} fill={brand.solid} />
    </Svg>
  );
}

// Two large flat circles in pale tints behind a screen, drifting very slowly.
export function Backdrop({ tone = 'calm' }: { tone?: 'calm' | 'bright' }) {
  const reduced = useReducedMotion();
  const drift = useRef(new Animated.Value(0)).current;
  useEffect(() => {
    if (reduced) return;
    const loop = Animated.loop(
      Animated.sequence([
        Animated.timing(drift, { toValue: 1, duration: motion.ambient, easing: Easing.inOut(Easing.sin), useNativeDriver: native }),
        Animated.timing(drift, { toValue: 0, duration: motion.ambient, easing: Easing.inOut(Easing.sin), useNativeDriver: native }),
      ]),
    );
    loop.start();
    return () => loop.stop();
  }, [reduced]);
  const opacity = tone === 'bright' ? 1 : 0.7;
  const move = (dx: number, dy: number) => ({
    transform: [
      { translateX: drift.interpolate({ inputRange: [0, 1], outputRange: [0, dx] }) },
      { translateY: drift.interpolate({ inputRange: [0, 1], outputRange: [0, dy] }) },
    ],
  });
  const disc = (d: number, color: string) => ({ width: d, height: d, borderRadius: d / 2, backgroundColor: color, opacity });
  return (
    <View pointerEvents="none" style={StyleSheet.absoluteFill} {...hidden}>
      <Animated.View style={[{ position: 'absolute', top: -170, right: -150 }, disc(340, brand.wash), move(-20, 14)]} />
      <Animated.View style={[{ position: 'absolute', bottom: -210, left: -170 }, disc(380, colors.primarySoft), move(16, -12)]} />
    </View>
  );
}

// A circle in the logo's teal.
function Disc({ size }: { size: number }) {
  return <View style={[StyleSheet.absoluteFill, { borderRadius: size / 2, backgroundColor: brand.solid }]} />;
}

// ---------- check-in states ----------

// While the app reads a question aloud: gently moving sound bars.
export function Speaking({ size = 150 }: { size?: number }) {
  const reduced = useReducedMotion();
  const bars = useRef([0, 1, 2, 3, 4].map(() => new Animated.Value(0.4))).current;
  useEffect(() => {
    if (reduced) return;
    const loops = bars.map((b, i) =>
      Animated.loop(
        Animated.sequence([
          Animated.timing(b, { toValue: 1, duration: 420 + i * 70, easing: Easing.inOut(Easing.sin), useNativeDriver: native }),
          Animated.timing(b, { toValue: 0.35, duration: 420 + i * 70, easing: Easing.inOut(Easing.sin), useNativeDriver: native }),
        ]),
      ),
    );
    loops.forEach((l, i) => setTimeout(() => l.start(), i * 90));
    return () => loops.forEach((l) => l.stop());
  }, [reduced]);
  return (
    <View {...hidden} style={{ width: size, height: size, alignItems: 'center', justifyContent: 'center' }}>
      <Disc size={size} />
      <View style={{ position: 'relative', zIndex: 1, flexDirection: 'row', alignItems: 'center', gap: size * 0.045, height: size * 0.42 }}>
        {bars.map((b, i) => (
          <Animated.View
            key={i}
            style={{
              width: size * 0.07,
              height: size * (i === 2 ? 0.42 : i % 2 ? 0.32 : 0.22),
              borderRadius: size,
              backgroundColor: '#FFFFFF',
              transform: [{ scaleY: b }],
            }}
          />
        ))}
      </View>
    </View>
  );
}

// While the app listens: a microphone on the logo's teal, with rings
// that swell when it hears their voice, so they can see it's working.
export function Listening({ level, size = 150 }: { level: number | undefined; size?: number }) {
  const reduced = useReducedMotion();
  const loud = useRef(new Animated.Value(0)).current;
  const pulse = useBreath(1800);
  // Metering is in dB: about -60 when quiet, -20 when speaking up close.
  const target = level === undefined ? 0 : Math.max(0, Math.min(1, (level + 55) / 35));
  useEffect(() => {
    Animated.spring(loud, { toValue: reduced ? 0 : target, speed: 18, bounciness: 2, useNativeDriver: native }).start();
  }, [target, reduced]);
  // Visible even in silence, then swelling with their voice.
  const ring = (rest: number, swell: number, opacity: number) => ({
    position: 'absolute' as const,
    width: size,
    height: size,
    borderRadius: size / 2,
    backgroundColor: brand.glow,
    opacity: Animated.add(loud.interpolate({ inputRange: [0, 1], outputRange: [opacity * 0.7, opacity] }),
      pulse.interpolate({ inputRange: [0, 1], outputRange: [0, 0.1] })),
    transform: [{ scale: Animated.add(loud.interpolate({ inputRange: [0, 1], outputRange: [rest, swell] }),
      pulse.interpolate({ inputRange: [0, 1], outputRange: [0, 0.05] })) }],
  });
  return (
    <View {...hidden} style={{ width: size * 1.7, height: size * 1.7, alignItems: 'center', justifyContent: 'center' }}>
      <Animated.View style={ring(1.34, 1.66, 0.4)} />
      <Animated.View style={ring(1.16, 1.34, 0.7)} />
      <View style={{ width: size, height: size, alignItems: 'center', justifyContent: 'center' }}>
        <Disc size={size} />
        {/* Its own layer, so browsers paint it above the disc as phones do. */}
        <View style={{ position: 'relative', zIndex: 1 }}>
          <Icon name="mic" size={size * 0.46} color="#FFFFFF" weight={2.2} />
        </View>
      </View>
    </View>
  );
}

// A check-in finished: the teal circle grows in, the tick pops in, and
// three dots like the logo's float out around it.
export function Done({ size = 150 }: { size?: number }) {
  const reduced = useReducedMotion();
  const grow = useRef(new Animated.Value(reduced ? 1 : 0)).current;
  const tick = useRef(new Animated.Value(reduced ? 1 : 0)).current;
  const dots = useRef([0, 1, 2].map(() => new Animated.Value(reduced ? 1 : 0))).current;
  useEffect(() => {
    if (reduced) {
      [grow, tick, ...dots].forEach((v) => v.setValue(1));
      return;
    }
    Animated.sequence([
      Animated.spring(grow, { toValue: 1, speed: 12, bounciness: 5, useNativeDriver: native }),
      Animated.spring(tick, { toValue: 1, speed: 14, bounciness: 9, useNativeDriver: native }),
      Animated.stagger(110, dots.map((d) =>
        Animated.timing(d, { toValue: 1, duration: 520, easing: Easing.out(Easing.back(1.6)), useNativeDriver: native }))),
    ]).start();
  }, [reduced]);
  const box = size * 1.55;
  const spots = [
    { x: -0.62, y: 0.32, r: 0.075, color: brand.solid },
    { x: -0.5, y: -0.55, r: 0.055, color: brand.solid },
    { x: 0.62, y: -0.36, r: 0.085, color: brand.solid },
  ];
  return (
    <View {...hidden} style={{ width: box, height: box, alignItems: 'center', justifyContent: 'center' }}>
      {spots.map((p, i) => {
        const d = size * p.r * 2;
        return (
          <Animated.View
            key={i}
            style={{
              position: 'absolute',
              width: d,
              height: d,
              borderRadius: d / 2,
              backgroundColor: p.color,
              left: box / 2 + p.x * size - d / 2,
              top: box / 2 + p.y * size - d / 2,
              opacity: dots[i],
              transform: [
                { scale: dots[i] },
                { translateY: dots[i].interpolate({ inputRange: [0, 1], outputRange: [size * 0.12, 0] }) },
              ],
            }}
          />
        );
      })}
      <Animated.View style={{ width: size, height: size, alignItems: 'center', justifyContent: 'center', transform: [{ scale: grow }] }}>
        <Disc size={size} />
        <Animated.View style={{ position: 'relative', zIndex: 1, opacity: tick, transform: [{ scale: tick.interpolate({ inputRange: [0, 1], outputRange: [0.4, 1] }) }] }}>
          <Icon name="check" size={size * 0.58} color="#FFFFFF" weight={3} />
        </Animated.View>
      </Animated.View>
    </View>
  );
}

// Waiting: the logo mark, breathing.
export function Waiting({ size = 120 }: { size?: number }) {
  return <LogoMark size={size} breathe />;
}
