import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { View, StyleSheet } from 'react-native';
import { useEffect } from 'react';
import { getCurrentUser, getProfile } from '../services/authService';
import { useShotStore } from '../store/useShotStore';

export default function RootLayout() {
  const { setUser, setProfile } = useShotStore();

  // Check auth state on app start
  useEffect(() => {
    async function loadUser() {
      const user = await getCurrentUser();
      if (user) {
        setUser(user);
        const { profile } = await getProfile(user.id);
        setProfile(profile);
      }
    }
    loadUser();
  }, []);

  return (
    <View style={styles.container}>
      <StatusBar style="light" />
      <Stack
        screenOptions={{
          headerShown: false,
          contentStyle: { backgroundColor: '#0D1117' },
          animation: 'slide_from_right',
        }}
      >
        <Stack.Screen name="index" />
        <Stack.Screen name="camera" />
        <Stack.Screen name="processing" />
        <Stack.Screen name="diagram" />
        <Stack.Screen name="settings" />
        <Stack.Screen name="signin" />
        <Stack.Screen name="signup" />
      </Stack>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0D1117',
  },
});
