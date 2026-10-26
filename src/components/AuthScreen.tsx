// Sign in / create account screen (email + password, or Google).

import { Ionicons } from '@expo/vector-icons';
import React, { useState } from 'react';
import {
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
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
import GradCap from './GradCap';

type Mode = 'signin' | 'signup';

export default function AuthScreen() {
  const insets = useSafeAreaInsets();
  const { configured, signInWithEmail, signUpWithEmail, signInWithGoogle } = useAuth();
  const [mode, setMode] = useState<Mode>('signin');
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [busy, setBusy] = useState<'email' | 'google' | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [info, setInfo] = useState<string | null>(null);

  const isSignup = mode === 'signup';

  async function submit() {
    setError(null);
    setInfo(null);
    if (isSignup && name.trim().length < 2) return setError('Please enter your name.');
    if (!email.includes('@')) return setError('Please enter a valid email.');
    if (password.length < 6) return setError('Password must be at least 6 characters.');
    setBusy('email');
    const err = isSignup ? await signUpWithEmail(name, email, password) : await signInWithEmail(email, password);
    setBusy(null);
    if (err === 'CHECK_EMAIL') {
      setInfo('Almost there! We sent you a confirmation email. Open the link, then sign in.');
      setMode('signin');
    } else if (err) setError(err);
  }

  async function google() {
    setError(null);
    setBusy('google');
    const err = await signInWithGoogle();
    setBusy(null);
    if (err) setError(err);
  }

  if (!configured) {
    return (
      <View style={[styles.screen, styles.center, { padding: 28 }]}>
        <GradCap size={80} />
        <Text style={styles.title}>Connect Supabase</Text>
        <Text style={styles.subtitle}>
          Create the file .env.local in the project folder with your Supabase URL and key (see
          supabase/SETUP.md), then restart with: npx expo start -c
        </Text>
      </View>
    );
  }

  return (
    <KeyboardAvoidingView style={styles.screen} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
      <StatusBar barStyle="light-content" />
      <ScrollView
        contentContainerStyle={[styles.content, { paddingTop: insets.top + 30, paddingBottom: insets.bottom + 30 }]}
        keyboardShouldPersistTaps="handled">
        <View style={styles.header}>
          <GradCap size={84} />
          <Text style={styles.brand}>InstaLearn</Text>
          <Text style={styles.subtitle}>Short lessons. Real courses. Learn while you scroll.</Text>
        </View>

        {/* Sign in / Create account switch */}
        <View style={styles.switch}>
          {(['signin', 'signup'] as Mode[]).map((m) => (
            <Pressable
              key={m}
              style={[styles.switchItem, mode === m && styles.switchItemActive]}
              onPress={() => {
                setMode(m);
                setError(null);
              }}>
              <Text style={[styles.switchText, mode === m && styles.switchTextActive]}>
                {m === 'signin' ? 'Sign in' : 'Create account'}
              </Text>
            </Pressable>
          ))}
        </View>

        {isSignup && (
          <Field icon="person-outline" placeholder="Full name" value={name} onChangeText={setName} autoCapitalize="words" />
        )}
        <Field
          icon="mail-outline"
          placeholder="Email"
          value={email}
          onChangeText={setEmail}
          keyboardType="email-address"
          autoCapitalize="none"
          autoComplete="email"
        />
        <Field
          icon="lock-closed-outline"
          placeholder="Password"
          value={password}
          onChangeText={setPassword}
          secureTextEntry={!showPassword}
          autoCapitalize="none"
          right={
            <Pressable onPress={() => setShowPassword(!showPassword)} hitSlop={8}>
              <Ionicons name={showPassword ? 'eye-off-outline' : 'eye-outline'} size={20} color="#8e8e93" />
            </Pressable>
          }
        />

        {error && <Text style={styles.error}>{error}</Text>}
        {info && <Text style={styles.info}>{info}</Text>}

        <Pressable
          style={({ pressed }) => [styles.primary, pressed && styles.pressed]}
          onPress={submit}
          disabled={busy !== null}>
          {busy === 'email' ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.primaryText}>{isSignup ? 'Create account' : 'Sign in'}</Text>
          )}
        </Pressable>

        <View style={styles.dividerRow}>
          <View style={styles.dividerLine} />
          <Text style={styles.dividerText}>or</Text>
          <View style={styles.dividerLine} />
        </View>

        <Pressable
          style={({ pressed }) => [styles.google, pressed && styles.pressed]}
          onPress={google}
          disabled={busy !== null}>
          {busy === 'google' ? (
            <ActivityIndicator color="#000" />
          ) : (
            <>
              <Ionicons name="logo-google" size={20} color="#000" />
              <Text style={styles.googleText}>Continue with Google</Text>
            </>
          )}
        </Pressable>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

type FieldProps = React.ComponentProps<typeof TextInput> & {
  icon: keyof typeof Ionicons.glyphMap;
  right?: React.ReactNode;
};

function Field({ icon, right, ...input }: FieldProps) {
  return (
    <View style={styles.field}>
      <Ionicons name={icon} size={20} color="#8e8e93" />
      <TextInput {...input} style={styles.input} placeholderTextColor="#8e8e93" autoCorrect={false} />
      {right}
    </View>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: '#000' },
  center: { alignItems: 'center', justifyContent: 'center' },
  content: { paddingHorizontal: 24 },
  header: { alignItems: 'center', marginBottom: 24 },
  brand: { color: '#fff', fontSize: 32, fontWeight: '900', marginTop: -8 },
  title: { color: '#fff', fontSize: 24, fontWeight: '800', marginTop: 8 },
  subtitle: { color: '#aeaeb2', fontSize: 15, textAlign: 'center', marginTop: 6, lineHeight: 21 },
  switch: { flexDirection: 'row', backgroundColor: '#1c1c1e', borderRadius: 12, padding: 4, marginBottom: 18 },
  switchItem: { flex: 1, paddingVertical: 10, borderRadius: 9, alignItems: 'center' },
  switchItemActive: { backgroundColor: '#3a3a3c' },
  switchText: { color: '#8e8e93', fontSize: 15, fontWeight: '700' },
  switchTextActive: { color: '#fff' },
  field: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    backgroundColor: '#1c1c1e',
    borderRadius: 12,
    paddingHorizontal: 14,
    marginBottom: 10,
  },
  input: { flex: 1, color: '#fff', fontSize: 16, paddingVertical: 14 },
  error: { color: '#ff453a', fontSize: 14, marginTop: 2, marginBottom: 8 },
  info: { color: '#30d158', fontSize: 14, marginTop: 2, marginBottom: 8, lineHeight: 20 },
  primary: {
    backgroundColor: '#5e5ce6',
    borderRadius: 14,
    height: 52,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 8,
  },
  primaryText: { color: '#fff', fontSize: 17, fontWeight: '800' },
  dividerRow: { flexDirection: 'row', alignItems: 'center', gap: 10, marginVertical: 20 },
  dividerLine: { flex: 1, height: StyleSheet.hairlineWidth, backgroundColor: '#3a3a3c' },
  dividerText: { color: '#8e8e93', fontSize: 13 },
  google: {
    flexDirection: 'row',
    gap: 10,
    backgroundColor: '#fff',
    borderRadius: 14,
    height: 52,
    alignItems: 'center',
    justifyContent: 'center',
  },
  googleText: { color: '#000', fontSize: 16, fontWeight: '700' },
  pressed: { opacity: 0.7 },
});
