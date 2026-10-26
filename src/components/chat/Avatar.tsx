// Round avatar: photo, initials, or a group icon.

import { Ionicons } from '@expo/vector-icons';
import { Image } from 'expo-image';
import React from 'react';
import { StyleSheet, Text, View } from 'react-native';

const COLORS = ['#5e5ce6', '#0a84ff', '#30d158', '#ff9f0a', '#ff375f', '#bf5af2', '#64d2ff'];

function colorFor(seed: string) {
  let h = 0;
  for (let i = 0; i < seed.length; i++) h = (h * 31 + seed.charCodeAt(i)) | 0;
  return COLORS[Math.abs(h) % COLORS.length];
}

type Props = { name?: string | null; url?: string | null; size?: number; group?: boolean; seed?: string };

export default function Avatar({ name, url, size = 48, group, seed }: Props) {
  const box = { width: size, height: size, borderRadius: size / 2 };
  if (url) return <Image source={{ uri: url }} style={box} />;
  const bg = colorFor(seed || name || '?');
  if (group) {
    return (
      <View style={[box, styles.center, { backgroundColor: bg }]}>
        <Ionicons name="people" size={size * 0.5} color="#fff" />
      </View>
    );
  }
  const initials = (name || '?')
    .replace('@', '')
    .split(' ')
    .filter(Boolean)
    .map((w) => w[0])
    .join('')
    .slice(0, 2)
    .toUpperCase();
  return (
    <View style={[box, styles.center, { backgroundColor: bg }]}>
      <Text style={[styles.initials, { fontSize: size * 0.38 }]}>{initials}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  center: { alignItems: 'center', justifyContent: 'center' },
  initials: { color: '#fff', fontWeight: '800' },
});
