// Settings: pick your courses, set the question difficulty for each one
// (0 = no questions … 3 = hard), and choose how often quiz cards appear.
// Everything is saved automatically on the device.

import { Ionicons } from '@expo/vector-icons';
import { router } from 'expo-router';
import React, { useMemo, useState } from 'react';
import { Pressable, ScrollView, StatusBar, StyleSheet, Text, TextInput, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import DifficultyMeter from '../components/DifficultyMeter';
import GradCap from '../components/GradCap';
import { useSettings, type QuestionFrequency } from '../context/settings';
import { COURSES, FIELDS, type Course } from '../data/courses';

const FREQUENCIES: { value: QuestionFrequency; label: string }[] = [
  { value: 1, label: 'Every video' },
  { value: 2, label: 'Every 2' },
  { value: 3, label: 'Every 3' },
  { value: 5, label: 'Every 5' },
  { value: 0, label: 'Only when I tap' },
];

export default function SettingsScreen() {
  const insets = useSafeAreaInsets();
  const { settings, toggleCourse, setLevel, levelFor, setQuestionEvery, clearCourses } = useSettings();
  const [query, setQuery] = useState('');

  const selectedCount = settings.selectedCourses.length;

  // Search matches the English name, the Hebrew name, or the field name.
  const groups = useMemo(() => {
    const q = query.trim().toLowerCase();
    return FIELDS.map((field) => ({
      field,
      courses: COURSES.filter(
        (c) =>
          c.field === field.id &&
          (!q ||
            c.name.toLowerCase().includes(q) ||
            c.nameHe.includes(q) ||
            field.name.toLowerCase().includes(q) ||
            field.nameHe.includes(q)),
      ),
    })).filter((g) => g.courses.length > 0);
  }, [query]);

  function renderCourse(course: Course, color: string) {
    const selected = settings.selectedCourses.includes(course.id);
    return (
      <View key={course.id} style={[styles.courseCard, selected && { borderColor: color }]}>
        <Pressable
          style={styles.courseRow}
          onPress={() => toggleCourse(course.id)}
          accessibilityRole="checkbox"
          accessibilityState={{ checked: selected }}>
          <View style={[styles.checkbox, selected && { backgroundColor: color, borderColor: color }]}>
            {selected && <Ionicons name="checkmark" size={16} color="#fff" />}
          </View>
          <View style={{ flex: 1 }}>
            <Text style={styles.courseName}>{course.name}</Text>
            <Text style={styles.courseNameHe}>{course.nameHe}</Text>
          </View>
        </Pressable>

        {selected && !course.factsOnly && (
          <View style={styles.levelBox}>
            <Text style={styles.levelTitle}>Question difficulty</Text>
            <DifficultyMeter value={levelFor(course.id)} onChange={(l) => setLevel(course.id, l)} />
          </View>
        )}
        {selected && course.factsOnly && (
          <View style={styles.levelBox}>
            <Text style={styles.levelTitle}>Facts only · no questions</Text>
          </View>
        )}
      </View>
    );
  }

  return (
    <View style={styles.screen}>
      <StatusBar barStyle="light-content" />
      <ScrollView
        contentContainerStyle={{ paddingTop: insets.top + 12, paddingBottom: insets.bottom + 120 }}
        keyboardShouldPersistTaps="handled">
        {/* Header */}
        <View style={styles.header}>
          <GradCap size={72} />
          <Text style={styles.title}>My courses</Text>
          <Text style={styles.subtitle}>
            Pick what you study. Your feed will only show videos from these courses.
          </Text>
        </View>

        {/* Search */}
        <View style={styles.searchBox}>
          <Ionicons name="search" size={18} color="#8e8e93" />
          <TextInput
            value={query}
            onChangeText={setQuery}
            placeholder="Search courses… (e.g. Physics, אינפי)"
            placeholderTextColor="#8e8e93"
            style={styles.searchInput}
            autoCorrect={false}
            clearButtonMode="while-editing"
          />
          {query.length > 0 && (
            <Pressable onPress={() => setQuery('')} hitSlop={8}>
              <Ionicons name="close-circle" size={18} color="#8e8e93" />
            </Pressable>
          )}
        </View>

        <View style={styles.countRow}>
          <Text style={styles.countText}>
            {selectedCount === 0 ? 'No courses selected yet' : `${selectedCount} selected`}
          </Text>
          {selectedCount > 0 && (
            <Pressable onPress={clearCourses} hitSlop={8}>
              <Text style={styles.clearText}>Clear all</Text>
            </Pressable>
          )}
        </View>

        {/* Courses grouped by field */}
        {groups.map(({ field, courses }) => (
          <View key={field.id} style={styles.section}>
            <View style={styles.sectionHeader}>
              <View style={[styles.fieldIcon, { backgroundColor: field.color }]}>
                <Ionicons name={field.icon as keyof typeof Ionicons.glyphMap} size={16} color="#fff" />
              </View>
              <Text style={styles.sectionTitle}>{field.name}</Text>
              <Text style={styles.sectionTitleHe}>{field.nameHe}</Text>
            </View>
            {courses.map((c) => renderCourse(c, field.color))}
          </View>
        ))}

        {groups.length === 0 && (
          <Text style={styles.noResults}>No courses match “{query}”.</Text>
        )}

        {/* Question frequency */}
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <View style={[styles.fieldIcon, { backgroundColor: '#30d158' }]}>
              <Ionicons name="help" size={16} color="#fff" />
            </View>
            <Text style={styles.sectionTitle}>How often to quiz me</Text>
          </View>
          <Text style={styles.hint}>
            A question card appears in the feed after this many videos. Courses set to 0 never get
            questions.
          </Text>
          <View style={styles.freqWrap}>
            {FREQUENCIES.map((f) => {
              const active = settings.questionEvery === f.value;
              return (
                <Pressable
                  key={f.value}
                  onPress={() => setQuestionEvery(f.value)}
                  style={[styles.freqChip, active && styles.freqChipActive]}>
                  <Text style={[styles.freqText, active && styles.freqTextActive]}>{f.label}</Text>
                </Pressable>
              );
            })}
          </View>
        </View>

        <View style={styles.savedRow}>
          <Ionicons name="cloud-done-outline" size={16} color="#8e8e93" />
          <Text style={styles.savedText}>Saved automatically</Text>
        </View>

        {/* Go to the feed */}
        {selectedCount > 0 && (
          <Pressable style={styles.startButton} onPress={() => router.navigate('/')}>
            <Ionicons name="school" size={22} color="#fff" />
            <Text style={styles.startText}>Start learning</Text>
          </Pressable>
        )}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: '#000' },
  header: { alignItems: 'center', paddingHorizontal: 24, marginBottom: 8 },
  title: { color: '#fff', fontSize: 28, fontWeight: '800', marginTop: -6 },
  subtitle: { color: '#aeaeb2', fontSize: 15, textAlign: 'center', marginTop: 6, lineHeight: 21 },
  searchBox: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    backgroundColor: '#1c1c1e',
    marginHorizontal: 16,
    marginTop: 16,
    paddingHorizontal: 12,
    borderRadius: 12,
  },
  searchInput: { flex: 1, color: '#fff', fontSize: 16, paddingVertical: 12 },
  countRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginHorizontal: 20,
    marginTop: 12,
  },
  countText: { color: '#8e8e93', fontSize: 13, fontWeight: '600' },
  clearText: { color: '#ff453a', fontSize: 13, fontWeight: '700' },
  section: { marginTop: 22, paddingHorizontal: 16 },
  sectionHeader: { flexDirection: 'row', alignItems: 'center', gap: 8, marginBottom: 10 },
  fieldIcon: { width: 28, height: 28, borderRadius: 8, alignItems: 'center', justifyContent: 'center' },
  sectionTitle: { color: '#fff', fontSize: 18, fontWeight: '800' },
  sectionTitleHe: { color: '#8e8e93', fontSize: 14, marginLeft: 'auto' },
  courseCard: {
    backgroundColor: '#1c1c1e',
    borderRadius: 14,
    marginBottom: 8,
    borderWidth: 1.5,
    borderColor: 'transparent',
    overflow: 'hidden',
  },
  courseRow: { flexDirection: 'row', alignItems: 'center', gap: 12, padding: 14 },
  checkbox: {
    width: 24,
    height: 24,
    borderRadius: 7,
    borderWidth: 2,
    borderColor: '#48484a',
    alignItems: 'center',
    justifyContent: 'center',
  },
  courseName: { color: '#fff', fontSize: 16, fontWeight: '700' },
  courseNameHe: { color: '#aeaeb2', fontSize: 14, marginTop: 1 },
  levelBox: {
    borderTopWidth: StyleSheet.hairlineWidth,
    borderTopColor: '#3a3a3c',
    paddingHorizontal: 14,
    paddingTop: 10,
    paddingBottom: 12,
    backgroundColor: '#141416',
  },
  levelTitle: { color: '#8e8e93', fontSize: 12, fontWeight: '700', letterSpacing: 0.5, marginBottom: 8 },
  noResults: { color: '#8e8e93', textAlign: 'center', marginTop: 24, fontSize: 15 },
  hint: { color: '#8e8e93', fontSize: 13, lineHeight: 18, marginBottom: 12 },
  freqWrap: { flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
  freqChip: {
    paddingHorizontal: 14,
    paddingVertical: 9,
    borderRadius: 999,
    backgroundColor: '#1c1c1e',
    borderWidth: 1.5,
    borderColor: '#2c2c2e',
  },
  freqChipActive: { backgroundColor: '#12351d', borderColor: '#30d158' },
  freqText: { color: '#d1d1d6', fontSize: 14, fontWeight: '600' },
  freqTextActive: { color: '#fff' },
  savedRow: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 6, marginTop: 28 },
  savedText: { color: '#8e8e93', fontSize: 13 },
  startButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    backgroundColor: '#5e5ce6',
    marginHorizontal: 16,
    marginTop: 16,
    paddingVertical: 16,
    borderRadius: 16,
  },
  startText: { color: '#fff', fontSize: 17, fontWeight: '800' },
});
