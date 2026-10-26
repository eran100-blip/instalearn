// The InstaLearn graduation-cap symbol: a glowing badge that gently floats
// and pulses. Used as the "start learning" button and as the app's mark.

import { Ionicons } from '@expo/vector-icons';
import React, { useEffect, useRef } from 'react';
import { Animated, Easing, Pressable, StyleSheet, View } from 'react-native';

type Props = {
  size?: number;
  onPress?: () => void;
  animated?: boolean;
};

export default function GradCap({ size = 120, onPress, animated = true }: Props) {
  const pulse = useRef(new Animated.Value(0)).current;
  const float = useRef(new Animated.Value(0)).current;
  const press = useRef(new Animated.Value(1)).current;

  useEffect(() => {
    if (!animated) return;
    const pulseLoop = Animated.loop(
      Animated.timing(pulse, { toValue: 1, duration: 2200, easing: Easing.out(Easing.ease), useNativeDriver: true }),
    );
    const floatLoop = Animated.loop(
      Animated.sequence([
        Animated.timing(float, { toValue: 1, duration: 1600, easing: Easing.inOut(Easing.sin), useNativeDriver: true }),
        Animated.timing(float, { toValue: 0, duration: 1600, easing: Easing.inOut(Easing.sin), useNativeDriver: true }),
      ]),
    );
    pulseLoop.start();
    floatLoop.start();
    return () => {
      pulseLoop.stop();
      floatLoop.stop();
    };
  }, [animated, pulse, float]);

  const ringScale = pulse.interpolate({ inputRange: [0, 1], outputRange: [1, 1.55] });
  const ringOpacity = pulse.interpolate({ inputRange: [0, 0.7, 1], outputRange: [0.55, 0.1, 0] });
  const translateY = float.interpolate({ inputRange: [0, 1], outputRange: [0, -size * 0.06] });
  const rotate = float.interpolate({ inputRange: [0, 1], outputRange: ['-4deg', '4deg'] });

  const circle = { width: size, height: size, borderRadius: size / 2 };

  function pressIn() {
    Animated.spring(press, { toValue: 0.9, useNativeDriver: true }).start();
  }
  function pressOut() {
    Animated.spring(press, { toValue: 1, friction: 3, useNativeDriver: true }).start();
  }

  const badge = (
    <View style={[styles.wrap, { width: size * 1.6, height: size * 1.6 }]}>
      {/* Pulsing gold ring */}
      <Animated.View
        style={[styles.ring, circle, { opacity: ringOpacity, transform: [{ scale: ringScale }] }]}
      />
      <Animated.View style={{ transform: [{ translateY }, { scale: press }] }}>
        {/* Soft glow behind the badge */}
        <View style={[styles.glow, circle]} />
        {/* The badge itself: two layered circles for depth */}
        <View style={[styles.outer, circle]}>
          <View style={[styles.inner, { width: size * 0.82, height: size * 0.82, borderRadius: size * 0.41 }]}>
            <Animated.View style={{ transform: [{ rotate }] }}>
              <Ionicons name="school" size={size * 0.5} color="#fff" />
            </Animated.View>
          </View>
        </View>
        {/* Little gold tassel dot */}
        <View
          style={[
            styles.tassel,
            { width: size * 0.16, height: size * 0.16, borderRadius: size * 0.08, right: size * 0.1, top: size * 0.1 },
          ]}
        />
      </Animated.View>
    </View>
  );

  if (!onPress) return badge;

  return (
    <Pressable
      onPress={onPress}
      onPressIn={pressIn}
      onPressOut={pressOut}
      accessibilityRole="button"
      accessibilityLabel="Start learning">
      {badge}
    </Pressable>
  );
}

const styles = StyleSheet.create({
  wrap: { alignItems: 'center', justifyContent: 'center' },
  ring: { position: 'absolute', borderWidth: 3, borderColor: '#ffd60a' },
  glow: {
    position: 'absolute',
    backgroundColor: '#5e5ce6',
    opacity: 0.35,
    transform: [{ scale: 1.18 }],
  },
  outer: {
    backgroundColor: '#5e5ce6',
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 2,
    borderColor: 'rgba(255,255,255,0.35)',
    shadowColor: '#5e5ce6',
    shadowOpacity: 0.8,
    shadowRadius: 20,
    shadowOffset: { width: 0, height: 6 },
    elevation: 12,
  },
  inner: {
    backgroundColor: '#0a84ff',
    alignItems: 'center',
    justifyContent: 'center',
  },
  tassel: {
    position: 'absolute',
    backgroundColor: '#ffd60a',
    borderWidth: 2,
    borderColor: '#fff',
  },
});
