// Holds the student's settings (chosen courses, question level per course,
// question frequency) and saves them on the device so they survive restarts.
// When the user is signed in, the settings are also synced to their account
// (table user_settings), so they follow them to any device.

import AsyncStorage from '@react-native-async-storage/async-storage';
import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import type { QuestionLevel } from '../data/courses';
import { supabase } from '../lib/supabase';
import { useAuth } from './auth';

// 0 = only when the student taps "Test yourself", otherwise a quiz card
// appears in the feed after every N videos.
export type QuestionFrequency = 0 | 1 | 2 | 3 | 5;

export type Settings = {
  selectedCourses: string[];
  levels: Record<string, QuestionLevel>; // courseId -> 0..3
  questionEvery: QuestionFrequency;
};

const DEFAULT_SETTINGS: Settings = {
  selectedCourses: [],
  levels: {},
  questionEvery: 3,
};

export const DEFAULT_LEVEL: QuestionLevel = 2;

const STORAGE_KEY = 'instalearn.settings.v1';

type SettingsContextValue = {
  settings: Settings;
  loaded: boolean;
  toggleCourse: (courseId: string) => void;
  setLevel: (courseId: string, level: QuestionLevel) => void;
  setQuestionEvery: (n: QuestionFrequency) => void;
  clearCourses: () => void;
  levelFor: (courseId: string) => QuestionLevel;
};

const SettingsContext = createContext<SettingsContextValue | null>(null);

export function SettingsProvider({ children }: { children: React.ReactNode }) {
  const [settings, setSettings] = useState<Settings>(DEFAULT_SETTINGS);
  const [loaded, setLoaded] = useState(false);

  // Load saved settings once when the app starts.
  useEffect(() => {
    AsyncStorage.getItem(STORAGE_KEY)
      .then((raw) => {
        if (raw) setSettings({ ...DEFAULT_SETTINGS, ...JSON.parse(raw) });
      })
      .catch(() => {})
      .finally(() => setLoaded(true));
  }, []);

  // Save every change (only after the first load, so we don't overwrite saved data).
  useEffect(() => {
    if (!loaded) return;
    AsyncStorage.setItem(STORAGE_KEY, JSON.stringify(settings)).catch(() => {});
  }, [settings, loaded]);

  // ---- Sync with the user's account --------------------------------------
  const { session } = useAuth();
  const userId = session?.user.id;
  const [synced, setSynced] = useState(false);

  // On sign-in: take the settings from the account. If the account has no
  // courses yet (first sign-in), keep what was chosen on this device.
  useEffect(() => {
    setSynced(false);
    if (!userId || !loaded) return;
    let cancelled = false;
    supabase
      .from('user_settings')
      .select('selected_courses, levels, question_every')
      .eq('user_id', userId)
      .maybeSingle()
      .then(({ data }) => {
        if (cancelled) return;
        if (data && data.selected_courses?.length > 0) {
          setSettings({
            selectedCourses: data.selected_courses,
            levels: data.levels ?? {},
            questionEvery: (data.question_every ?? 3) as QuestionFrequency,
          });
        }
        setSynced(true);
      });
    return () => {
      cancelled = true;
    };
  }, [userId, loaded]);

  // After that, save changes to the account (bundled, half a second after the last change).
  useEffect(() => {
    if (!userId || !synced) return;
    const t = setTimeout(() => {
      supabase
        .from('user_settings')
        .upsert({
          user_id: userId,
          selected_courses: settings.selectedCourses,
          levels: settings.levels,
          question_every: settings.questionEvery,
          updated_at: new Date().toISOString(),
        })
        .then(() => {});
    }, 500);
    return () => clearTimeout(t);
  }, [settings, userId, synced]);

  const toggleCourse = useCallback((courseId: string) => {
    setSettings((s) => {
      const isOn = s.selectedCourses.includes(courseId);
      return {
        ...s,
        selectedCourses: isOn
          ? s.selectedCourses.filter((id) => id !== courseId)
          : [...s.selectedCourses, courseId],
        levels: isOn || courseId in s.levels ? s.levels : { ...s.levels, [courseId]: DEFAULT_LEVEL },
      };
    });
  }, []);

  const setLevel = useCallback((courseId: string, level: QuestionLevel) => {
    setSettings((s) => ({ ...s, levels: { ...s.levels, [courseId]: level } }));
  }, []);

  const setQuestionEvery = useCallback((n: QuestionFrequency) => {
    setSettings((s) => ({ ...s, questionEvery: n }));
  }, []);

  const clearCourses = useCallback(() => {
    setSettings((s) => ({ ...s, selectedCourses: [] }));
  }, []);

  const levelFor = useCallback(
    (courseId: string) => settings.levels[courseId] ?? DEFAULT_LEVEL,
    [settings.levels],
  );

  const value = useMemo(
    () => ({ settings, loaded, toggleCourse, setLevel, setQuestionEvery, clearCourses, levelFor }),
    [settings, loaded, toggleCourse, setLevel, setQuestionEvery, clearCourses, levelFor],
  );

  return <SettingsContext.Provider value={value}>{children}</SettingsContext.Provider>;
}

export function useSettings() {
  const ctx = useContext(SettingsContext);
  if (!ctx) throw new Error('useSettings must be used inside <SettingsProvider>');
  return ctx;
}
