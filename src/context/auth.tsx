// Who is signed in, their profile, and the sign-in / sign-up / sign-out actions.

import type { Session } from '@supabase/supabase-js';
import * as Linking from 'expo-linking';
import * as WebBrowser from 'expo-web-browser';
import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { isSupabaseConfigured, supabase } from '../lib/supabase';

WebBrowser.maybeCompleteAuthSession();

export type Profile = {
  id: string;
  full_name: string | null;
  username: string | null;
  university: string | null;
  avatar_url: string | null;
};

type AuthContextValue = {
  session: Session | null;
  profile: Profile | null;
  loading: boolean;
  configured: boolean;
  signInWithEmail: (email: string, password: string) => Promise<string | null>;
  signUpWithEmail: (name: string, email: string, password: string) => Promise<string | null>;
  signInWithGoogle: () => Promise<string | null>;
  signOut: () => Promise<void>;
  updateProfile: (changes: Partial<Omit<Profile, 'id'>>) => Promise<string | null>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

// Turn Supabase error messages into short, friendly ones.
function friendly(message: string): string {
  const m = message.toLowerCase();
  if (m.includes('invalid login credentials')) return 'Wrong email or password.';
  if (m.includes('email not confirmed')) return 'Please confirm your email first (check your inbox).';
  if (m.includes('already registered')) return 'This email already has an account. Try signing in.';
  if (m.includes('password should be')) return 'Password must be at least 6 characters.';
  if (m.includes('duplicate key') && m.includes('username')) return 'This username is taken.';
  return message;
}

// Read access_token / refresh_token (or a PKCE code) from the redirect URL.
async function createSessionFromUrl(url: string) {
  const params: Record<string, string> = {};
  const parts = url.split(/[?#]/).slice(1).join('&');
  parts.split('&').forEach((pair) => {
    const [k, v] = pair.split('=');
    if (k) params[decodeURIComponent(k)] = decodeURIComponent(v ?? '');
  });
  if (params.error_description) throw new Error(params.error_description);
  if (params.code) {
    const { error } = await supabase.auth.exchangeCodeForSession(params.code);
    if (error) throw error;
    return;
  }
  if (params.access_token && params.refresh_token) {
    const { error } = await supabase.auth.setSession({
      access_token: params.access_token,
      refresh_token: params.refresh_token,
    });
    if (error) throw error;
  }
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [session, setSession] = useState<Session | null>(null);
  const [profile, setProfile] = useState<Profile | null>(null);
  const [loading, setLoading] = useState(true);

  // Restore the saved session and listen for sign-in / sign-out.
  useEffect(() => {
    if (!isSupabaseConfigured) {
      setLoading(false);
      return;
    }
    supabase.auth.getSession().then(({ data }) => {
      setSession(data.session);
      setLoading(false);
    });
    const { data: sub } = supabase.auth.onAuthStateChange((_event, s) => setSession(s));
    return () => sub.subscription.unsubscribe();
  }, []);

  // Load the profile whenever the signed-in user changes.
  const userId = session?.user.id;
  useEffect(() => {
    if (!userId) {
      setProfile(null);
      return;
    }
    supabase
      .from('profiles')
      .select('id, full_name, username, university, avatar_url')
      .eq('id', userId)
      .single()
      .then(({ data }) => setProfile((data as Profile) ?? null));
  }, [userId]);

  const signInWithEmail = useCallback(async (email: string, password: string) => {
    const { error } = await supabase.auth.signInWithPassword({ email: email.trim(), password });
    return error ? friendly(error.message) : null;
  }, []);

  const signUpWithEmail = useCallback(async (name: string, email: string, password: string) => {
    const { data, error } = await supabase.auth.signUp({
      email: email.trim(),
      password,
      options: { data: { full_name: name.trim() } },
    });
    if (error) return friendly(error.message);
    if (!data.session) return 'CHECK_EMAIL'; // email confirmation is turned on
    return null;
  }, []);

  const signInWithGoogle = useCallback(async () => {
    try {
      const redirectTo = Linking.createURL('auth-callback');
      const { data, error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: { redirectTo, skipBrowserRedirect: true },
      });
      if (error) return friendly(error.message);
      const res = await WebBrowser.openAuthSessionAsync(data?.url ?? '', redirectTo);
      if (res.type === 'success') await createSessionFromUrl(res.url);
      return null;
    } catch (e: any) {
      return friendly(e?.message ?? 'Google sign-in failed.');
    }
  }, []);

  const signOut = useCallback(async () => {
    await supabase.auth.signOut();
  }, []);

  const updateProfile = useCallback(
    async (changes: Partial<Omit<Profile, 'id'>>) => {
      if (!userId) return 'Not signed in.';
      const { data, error } = await supabase
        .from('profiles')
        .update({ ...changes, updated_at: new Date().toISOString() })
        .eq('id', userId)
        .select('id, full_name, username, university, avatar_url')
        .single();
      if (error) return friendly(error.message);
      setProfile(data as Profile);
      return null;
    },
    [userId],
  );

  const value = useMemo(
    () => ({
      session,
      profile,
      loading,
      configured: isSupabaseConfigured,
      signInWithEmail,
      signUpWithEmail,
      signInWithGoogle,
      signOut,
      updateProfile,
    }),
    [session, profile, loading, signInWithEmail, signUpWithEmail, signInWithGoogle, signOut, updateProfile],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>');
  return ctx;
}
