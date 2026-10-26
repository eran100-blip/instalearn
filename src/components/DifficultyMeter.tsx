// A 0–3 meter for question difficulty.
// 0 = no questions for this course, 1 = easy, 2 = medium, 3 = hard.

import { Ionicons } from '@expo/vector-icons';
import React from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import { LEVEL_COLORS, LEVEL_LABELS, type QuestionLevel } from '../data/courses';

type Props = {
  value: QuestionLevel;
  onChange: (level: QuestionLevel) => void;
};

const LEVELS: QuestionLevel[] = [0, 1, 2, 3];

export default function DifficultyMeter({ value, onChange }: Props) {
  const color = LEVEL_COLORS[value];

  return (
    <View style={styles.container}>
      <View style={styles.track}>
        {LEVELS.map((level) => {
          const active = level === value;
          const filled = level > 0 && level <= value;
          return (
            <Pressable
              key={level}
              onPress={() => onChange(level)}
              hitSlop={6}
              style={styles.step}
              accessibilityRole="button"
              accessibilityLabel={`Questions: ${LEVEL_LABELS[level]}`}
              accessibilityState={{ selected: active }}>
              {level === 0 ? (
                <View style={[styles.offDot, active && { borderColor: color, backgroundColor: '#3a3a3c' }]}>
                  <Ionicons name="close" size={14} color={active ? '#fff' : '#8e8e93'} />
                </View>
              ) : (
                <View
                  style={[
                    styles.bar,
                    { height: 8 + level * 7 },
                    filled && { backgroundColor: color },
                    active && styles.barActive,
                  ]}
                />
              )}
              <Text style={[styles.num, active && { color: '#fff' }]}>{level}</Text>
            </Pressable>
          );
        })}
      </View>
      <View style={[styles.label, { borderColor: color }]}>
        <Text style={[styles.labelText, { color }]}>{LEVEL_LABELS[value]}</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flexDirection: 'row', alignItems: 'flex-end', justifyContent: 'space-between', gap: 12 },
  track: { flexDirection: 'row', alignItems: 'flex-end', gap: 14 },
  step: { alignItems: 'center', justifyContent: 'flex-end', minWidth: 26 },
  bar: { width: 18, borderRadius: 5, backgroundColor: '#3a3a3c' },
  barActive: { borderWidth: 2, borderColor: '#fff' },
  offDot: {
    width: 24,
    height: 24,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: '#3a3a3c',
    alignItems: 'center',
    justifyContent: 'center',
  },
  num: { color: '#8e8e93', fontSize: 11, fontWeight: '700', marginTop: 4 },
  label: { borderWidth: 1.5, borderRadius: 999, paddingHorizontal: 10, paddingVertical: 4, marginBottom: 16 },
  labelText: { fontSize: 12, fontWeight: '800' },
});
