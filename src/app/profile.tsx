// Profile: who you are, a few learning stats, edit details, sign out.

import { Ionicons } from '@expo/vector-icons';
import { Image } from 'expo-image';
import { useFocusEffect } from 'expo-router';
import React, { useCallback, useEffect, useState } from 'react';
import {
  ActivityIndicator,
  Pressable,
  ScrollView,
  StatusBar,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useAuth } from '../context/auth';
import { useSettings } from '../context/settings';
import { supabase } from '../lib/supabase';

export default function ProfileScreen() {
  const insets = useSafeAreaInsets();
  const { session, profile, updateProfile, signOut } = useAuth();
  const { settings } = useSettings();
  const [fullName, setFullName] = useState('');
  const [username, setUsername] = useState('');
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ ok: boolean; text: string } | null>(null);
  const [stats, setStats] = useState<Stats | null>(null);

  useEffect(() => {
    setFullName(profile?.full_name ?? '');
    setUsername(profile?.username ?? '');
  }, [profile]);

  // Stats and streaks from the attempts table (refreshed every time the tab opens).
  const uid = session?.user.id;
  useFocusEffect(
    useCallback(() => {
      if (!uid) return;
      supabase
        .from('attempts')
        .select('correct, created_at')
        .eq('user_id', uid)
        .order('created_at', { ascending: true })
        .then(({ data }) => setStats(computeStats(data ?? [])));
    }, [uid]),
  );

  const dirty =
    fullName !== (profile?.full_name ?? '') ||
    username !== (profile?.username ?? '');

  async function save() {
    const cleanUsername = username.trim().toLowerCase();
    if (cleanUsername && !/^[a-z0-9_.]{3,20}$/.test(cleanUsername)) {
      setMessage({ ok: false, text: 'Username: 3–20 letters, numbers, _ or .' });
      return;
    }
    setSaving(true);
    const err = await updateProfile({
      full_name: fullName.trim() || null,
      username: cleanUsername || null,
    });
    setSaving(false);
    setMessage(err ? { ok: false, text: err } : { ok: true, text: 'Saved' });
  }

  const initials = (profile?.full_name || session?.user.email || '?')
    .split(' ')
    .map((w) => w[0])
    .join('')
    .slice(0, 2)
    .toUpperCase();
  const accuracy = stats && stats.answered > 0 ? Math.round((stats.correct / stats.answered) * 100) : null;

  return (
    <View style={styles.screen}>
      <StatusBar barStyle="light-content" />
      <ScrollView
        contentContainerStyle={{ paddingTop: insets.top + 24, paddingBottom: insets.bottom + 120, paddingHorizontal: 16 }}
        keyboardShouldPersistTaps="handled">
        {/* Header */}
        <View style={styles.header}>
          {profile?.avatar_url ? (
            <Image source={{ uri: profile.avatar_url }} style={styles.avatar} />
          ) : (
            <View style={[styles.avatar, styles.avatarFallback]}>
              <Text style={styles.initials}>{initials}</Text>
            </View>
          )}
          <Text style={styles.name}>{profile?.full_name || 'Student'}</Text>
          {profile?.username ? <Text style={styles.username}>@{profile.username}</Text> : null}
          <Text style={styles.email}>{session?.user.email}</Text>
        </View>

        {/* Streaks */}
        <View style={styles.streakRow}>
          <Streak
            icon="flame"
            color="#ff9f0a"
            value={stats?.dayStreak ?? 0}
            unit={(stats?.dayStreak ?? 0) === 1 ? 'day' : 'days'}
            label="Daily streak"
            hint={stats?.answeredToday ? 'Answered today ✓' : 'Answer a question today'}
          />
          <Streak
            icon="trophy"
            color="#ffd60a"
            value={stats?.bestCorrect ?? 0}
            unit="in a row"
            label="Best correct streak"
            hint={`Current: ${stats?.currentCorrect ?? 0}`}
          />
        </View>

        {/* Stats */}
        <View style={styles.statsRow}>
          <Stat label="Courses" value={String(settings.selectedCourses.length)} />
          <Stat label="Answered" value={stats ? String(stats.answered) : '–'} />
          <Stat label="Accuracy" value={accuracy === null ? '–' : `${accuracy}%`} />
        </View>

        {/* Edit details */}
        <Text style={styles.sectionTitle}>Details</Text>
        <Field icon="person-outline" placeholder="Full name" value={fullName} onChangeText={setFullName} />
        <Field icon="at" placeholder="Username" value={username} onChangeText={setUsername} autoCapitalize="none" />
        {message && <Text style={[styles.message, { color: message.ok ? '#30d158' : '#ff453a' }]}>{message.text}</Text>}
        <Pressable
          style={({ pressed }) => [styles.saveButton, !dirty && styles.disabled, pressed && styles.pressed]}
          disabled={!dirty || saving}
          onPress={save}>
          {saving ? <ActivityIndicator color="#fff" /> : <Text style={styles.saveText}>Save changes</Text>}
        </Pressable>

        <Pressable style={({ pressed }) => [styles.signOut, pressed && styles.pressed]} onPress={signOut}>
          <Ionicons name="log-out-outline" size={20} color="#ff453a" />
          <Text style={styles.signOutText}>Sign out</Text>
        </Pressable>
      </ScrollView>
    </View>
  );
}

type Stats = {
  answered: number;
  correct: number;
  bestCorrect: number; // longest run of correct answers in a row
  currentCorrect: number; // current run of correct answers
  dayStreak: number; // days in a row with at least one answer
  answeredToday: boolean;
};

// Local calendar day, e.g. "2026-10-07".
function dayKey(d: Date) {
  return `${d.getFullYear()}-${d.getMonth() + 1}-${d.getDate()}`;
}

function computeStats(rows: { correct: boolean; created_at: string }[]): Stats {
  let best = 0;
  let run = 0;
  for (const r of rows) {
    run = r.correct ? run + 1 : 0;
    best = Math.max(best, run);
  }
  const days = new Set(rows.map((r) => dayKey(new Date(r.created_at))));
  const today = new Date();
  const answeredToday = days.has(dayKey(today));
  // The streak counts back from today (or from yesterday, if today has no answer yet).
  const cursor = new Date(today);
  if (!answeredToday) cursor.setDate(cursor.getDate() - 1);
  let dayStreak = 0;
  while (days.has(dayKey(cursor))) {
    dayStreak++;
    cursor.setDate(cursor.getDate() - 1);
  }
  return {
    answered: rows.length,
    correct: rows.filter((r) => r.correct).length,
    bestCorrect: best,
    currentCorrect: run,
    dayStreak,
    answeredToday,
  };
}

type StreakProps = {
  icon: keyof typeof Ionicons.glyphMap;
  color: string;
  value: number;
  unit: string;
  label: string;
  hint: string;
};

function Streak({ icon, color, value, unit, label, hint }: StreakProps) {
  return (
    <View style={styles.streak}>
      <View style={[styles.streakIcon, { backgroundColor: color + '26' }]}>
        <Ionicons name={icon} size={22} color={color} />
      </View>
      <View style={styles.streakValueRow}>
        <Text style={styles.streakValue}>{value}</Text>
        <Text style={styles.streakUnit}>{unit}</Text>
      </View>
      <Text style={styles.streakLabel}>{label}</Text>
      <Text style={styles.streakHint}>{hint}</Text>
    </View>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <View style={styles.stat}>
      <Text style={styles.statValue}>{value}</Text>
      <Text style={styles.statLabel}>{label}</Text>
    </View>
  );
}

function Field({ icon, ...input }: React.ComponentProps<typeof TextInput> & { icon: keyof typeof Ionicons.glyphMap }) {
  return (
    <View style={styles.field}>
      <Ionicons name={icon} size={19} color="#8e8e93" />
      <TextInput {...input} style={styles.input} placeholderTextColor="#8e8e93" autoCorrect={false} />
    </View>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: '#000' },
  header: { alignItems: 'center', marginBottom: 20 },
  avatar: { width: 96, height: 96, borderRadius: 48 },
  avatarFallback: { backgroundColor: '#5e5ce6', alignItems: 'center', justifyContent: 'center' },
  initials: { color: '#fff', fontSize: 34, fontWeight: '800' },
  name: { color: '#fff', fontSize: 24, fontWeight: '800', marginTop: 12 },
  username: { color: '#64d2ff', fontSize: 15, fontWeight: '600', marginTop: 2 },
  email: { color: '#8e8e93', fontSize: 14, marginTop: 4 },
  streakRow: { flexDirection: 'row', gap: 10, marginBottom: 10 },
  streak: { flex: 1, backgroundColor: '#1c1c1e', borderRadius: 16, padding: 14 },
  streakIcon: { width: 38, height: 38, borderRadius: 12, alignItems: 'center', justifyContent: 'center', marginBottom: 10 },
  streakValueRow: { flexDirection: 'row', alignItems: 'baseline', gap: 6 },
  streakValue: { color: '#fff', fontSize: 30, fontWeight: '900' },
  streakUnit: { color: '#8e8e93', fontSize: 13, fontWeight: '700' },
  streakLabel: { color: '#fff', fontSize: 14, fontWeight: '700', marginTop: 2 },
  streakHint: { color: '#8e8e93', fontSize: 12, marginTop: 2 },
  statsRow: { flexDirection: 'row', gap: 10, marginBottom: 24 },
  stat: { flex: 1, backgroundColor: '#1c1c1e', borderRadius: 14, paddingVertical: 14, alignItems: 'center' },
  statValue: { color: '#fff', fontSize: 22, fontWeight: '800' },
  statLabel: { color: '#8e8e93', fontSize: 12, fontWeight: '600', marginTop: 2 },
  sectionTitle: { color: '#fff', fontSize: 18, fontWeight: '800', marginBottom: 10 },
  field: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    backgroundColor: '#1c1c1e',
    borderRadius: 12,
    paddingHorizontal: 14,
    marginBottom: 10,
  },
  input: { flex: 1, color: '#fff', fontSize: 16, paddingVertical: 13 },
  message: { fontSize: 14, marginBottom: 8 },
  saveButton: { backgroundColor: '#5e5ce6', borderRadius: 12, height: 48, alignItems: 'center', justifyContent: 'center', marginTop: 4 },
  saveText: { color: '#fff', fontSize: 16, fontWeight: '700' },
  disabled: { opacity: 0.4 },
  signOut: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    marginTop: 28,
    paddingVertical: 14,
    borderRadius: 12,
    backgroundColor: '#1c1c1e',
  },
  signOutText: { color: '#ff453a', fontSize: 16, fontWeight: '700' },
  pressed: { opacity: 0.7 },
});
