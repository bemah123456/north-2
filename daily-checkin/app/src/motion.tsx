// Motion shared by every screen. Each animation means something (a new
// screen arriving, the app listening, a check-in finished), stays calm, and
// switches off when the phone asks for reduced motion.

import { ReactNode, useEffect, useRef, useState } from 'react';
import { AccessibilityInfo, Animated, Easing, Platform, StyleProp, ViewStyle } from 'react-native';

import { motion } from './theme';

export const native = Platform.OS !== 'web';

export function useReducedMotion() {
  const [reduced, setReduced] = useState(false);
  useEffect(() => {
    let alive = true;
    AccessibilityInfo.isReduceMotionEnabled().then((v) => alive && setReduced(v)).catch(() => {});
    const sub = AccessibilityInfo.addEventListener('reduceMotionChanged', setReduced);
    return () => {
      alive = false;
      sub.remove();
    };
  }, []);
  return reduced;
}

// Content that fades in and rises a little when it first appears. `order`
// staggers items in a list.
export function Rise({ children, order = 0, style }: { children: ReactNode; order?: number; style?: StyleProp<ViewStyle> }) {
  const reduced = useReducedMotion();
  const t = useRef(new Animated.Value(0)).current;
  useEffect(() => {
    if (reduced) {
      t.setValue(1);
      return;
    }
    Animated.timing(t, {
      toValue: 1,
      duration: motion.enter,
      delay: order * motion.stagger,
      easing: Easing.out(Easing.cubic),
      useNativeDriver: native,
    }).start();
  }, [reduced]);
  return (
    <Animated.View
      style={[style, {
        opacity: t,
        transform: [{ translateY: t.interpolate({ inputRange: [0, 1], outputRange: [14, 0] }) }],
      }]}
    >
      {children}
    </Animated.View>
  );
}

// A value that slowly goes 0 → 1 → 0 forever, for "breathing" graphics.
export function useBreath(period = motion.breathe, on = true) {
  const reduced = useReducedMotion();
  const t = useRef(new Animated.Value(0)).current;
  useEffect(() => {
    if (reduced || !on) {
      t.setValue(0);
      return;
    }
    const loop = Animated.loop(
      Animated.sequence([
        Animated.timing(t, { toValue: 1, duration: period / 2, easing: Easing.inOut(Easing.sin), useNativeDriver: native }),
        Animated.timing(t, { toValue: 0, duration: period / 2, easing: Easing.inOut(Easing.sin), useNativeDriver: native }),
      ]),
    );
    loop.start();
    return () => loop.stop();
  }, [reduced, on, period]);
  return t;
}
