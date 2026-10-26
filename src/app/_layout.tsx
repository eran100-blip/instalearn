import { DarkTheme, DefaultTheme, ThemeProvider } from 'expo-router';
import * as SplashScreen from 'expo-splash-screen';
import { ActivityIndicator, useColorScheme, View } from 'react-native';

import { AnimatedSplashOverlay } from '@/components/animated-icon';
import AppTabs from '@/components/app-tabs';
import AuthScreen from '@/components/AuthScreen';
import { AuthProvider, useAuth } from '@/context/auth';
import { ChatProvider } from '@/context/chat';
import { SettingsProvider } from '@/context/settings';

SplashScreen.preventAutoHideAsync();

// Signed in → the app. Signed out → the sign-in screen.
function Gate() {
  const { session, loading } = useAuth();
  if (loading) {
    return (
      <View style={{ flex: 1, backgroundColor: '#000', alignItems: 'center', justifyContent: 'center' }}>
        <ActivityIndicator color="#fff" />
      </View>
    );
  }
  return session ? <AppTabs /> : <AuthScreen />;
}

export default function TabLayout() {
  const colorScheme = useColorScheme();
  return (
    <ThemeProvider value={colorScheme === 'dark' ? DarkTheme : DefaultTheme}>
      <AuthProvider>
        <SettingsProvider>
          <ChatProvider>
            <AnimatedSplashOverlay />
            <Gate />
          </ChatProvider>
        </SettingsProvider>
      </AuthProvider>
    </ThemeProvider>
  );
}
