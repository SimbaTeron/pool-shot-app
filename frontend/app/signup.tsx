import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  SafeAreaView,
  KeyboardAvoidingView,
  Platform,
  Alert,
  ScrollView,
} from 'react-native';
import { router } from 'expo-router';
import { signUp } from '../services/authService';
import { useShotStore } from '../store/useShotStore';

export default function SignUpScreen() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const { setUser } = useShotStore();

  async function handleSignUp() {
    if (!email || !password || !confirmPassword) {
      Alert.alert('Error', 'Please fill in all fields');
      return;
    }
    if (password !== confirmPassword) {
      Alert.alert('Error', 'Passwords do not match');
      return;
    }
    if (password.length < 6) {
      Alert.alert('Error', 'Password must be at least 6 characters');
      return;
    }

    setLoading(true);
    const { user, error } = await signUp(email, password);
    setLoading(false);

    if (error) {
      Alert.alert('Sign Up Failed', error);
      return;
    }

    Alert.alert(
      'Check your email!',
      'We sent a confirmation link. Please verify before signing in.',
      [{ text: 'OK', onPress: () => router.replace('/signin') }]
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.content}
      >
        <ScrollView contentContainerStyle={styles.scroll}>
          {/* Header */}
          <View style={styles.header}>
            <Text style={styles.logo}>🎱</Text>
            <Text style={styles.title}>Create Account</Text>
            <Text style={styles.subtitle}>Start with 3 free shots per day</Text>
          </View>

          {/* Form */}
          <View style={styles.form}>
            <View style={styles.inputGroup}>
              <Text style={styles.label}>Email</Text>
              <TextInput
                style={styles.input}
                value={email}
                onChangeText={setEmail}
                placeholder="you@example.com"
                placeholderTextColor="#484F58"
                keyboardType="email-address"
                autoCapitalize="none"
                autoCorrect={false}
              />
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.label}>Password</Text>
              <TextInput
                style={styles.input}
                value={password}
                onChangeText={setPassword}
                placeholder="Min. 6 characters"
                placeholderTextColor="#484F58"
                secureTextEntry
              />
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.label}>Confirm Password</Text>
              <TextInput
                style={styles.input}
                value={confirmPassword}
                onChangeText={setConfirmPassword}
                placeholder="Repeat password"
                placeholderTextColor="#484F58"
                secureTextEntry
              />
            </View>

            <TouchableOpacity
              style={[styles.button, loading && styles.buttonDisabled]}
              onPress={handleSignUp}
              disabled={loading}
            >
              <Text style={styles.buttonText}>
                {loading ? 'Creating account...' : 'Create Account'}
              </Text>
            </TouchableOpacity>

            {/* Pricing */}
            <View style={styles.pricing}>
              <Text style={styles.pricingTitle}>Free Tier</Text>
              <Text style={styles.pricingDesc}>3 shots/day • All game types • Basic diagrams</Text>
              <View style={styles.pricingSeparator} />
              <Text style={styles.pricingTitle}>Pro — $7.99/mo</Text>
              <Text style={styles.pricingDesc}>Unlimited shots • AI-generated overlays • Priority support</Text>
              <View style={styles.pricingSeparator} />
              <Text style={styles.pricingTitle}>Pool Hall — $14.99/mo</Text>
              <Text style={styles.pricingDesc}>5 devices • Team management • Analytics dashboard</Text>
            </View>

            <TouchableOpacity
              style={styles.linkButton}
              onPress={() => router.push('/signin')}
            >
              <Text style={styles.linkText}>
                Already have an account? <Text style={styles.linkBold}>Sign in</Text>
              </Text>
            </TouchableOpacity>
          </View>
        </ScrollView>

        {/* Back */}
        <TouchableOpacity
          style={styles.backButton}
          onPress={() => router.back()}
        >
          <Text style={styles.backText}>← Back</Text>
        </TouchableOpacity>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0D1117',
  },
  content: {
    flex: 1,
  },
  scroll: {
    flexGrow: 1,
    paddingHorizontal: 32,
    paddingTop: 80,
    paddingBottom: 40,
    justifyContent: 'center',
  },
  header: {
    alignItems: 'center',
    marginBottom: 40,
  },
  logo: {
    fontSize: 56,
    marginBottom: 12,
  },
  title: {
    fontSize: 28,
    fontWeight: '700',
    color: '#F0F6FC',
  },
  subtitle: {
    fontSize: 16,
    color: '#8B949E',
    marginTop: 4,
  },
  form: {
    width: '100%',
  },
  inputGroup: {
    marginBottom: 20,
  },
  label: {
    fontSize: 13,
    fontWeight: '600',
    color: '#F0F6FC',
    marginBottom: 8,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  input: {
    backgroundColor: '#161B22',
    borderWidth: 1,
    borderColor: '#30363D',
    borderRadius: 10,
    paddingHorizontal: 16,
    paddingVertical: 14,
    fontSize: 16,
    color: '#F0F6FC',
  },
  button: {
    backgroundColor: '#58A6FF',
    borderRadius: 10,
    paddingVertical: 16,
    alignItems: 'center',
    marginTop: 8,
  },
  buttonDisabled: {
    opacity: 0.6,
  },
  buttonText: {
    fontSize: 17,
    fontWeight: '600',
    color: '#FFFFFF',
  },
  pricing: {
    marginTop: 32,
    backgroundColor: '#161B22',
    borderRadius: 12,
    padding: 20,
    borderWidth: 1,
    borderColor: '#30363D',
  },
  pricingTitle: {
    fontSize: 14,
    fontWeight: '700',
    color: '#F0F6FC',
    marginBottom: 4,
  },
  pricingDesc: {
    fontSize: 13,
    color: '#8B949E',
    lineHeight: 18,
  },
  pricingSeparator: {
    height: 1,
    backgroundColor: '#30363D',
    marginVertical: 12,
  },
  linkButton: {
    marginTop: 24,
    alignItems: 'center',
  },
  linkText: {
    fontSize: 14,
    color: '#8B949E',
  },
  linkBold: {
    color: '#58A6FF',
    fontWeight: '600',
  },
  backButton: {
    position: 'absolute',
    top: 60,
    left: 24,
    padding: 8,
  },
  backText: {
    fontSize: 16,
    color: '#8B949E',
  },
});
