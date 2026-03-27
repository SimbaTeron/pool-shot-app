import { View, Text, TouchableOpacity, StyleSheet, SafeAreaView } from 'react-native';
import { router } from 'expo-router';
import { useShotStore } from '../store/useShotStore';
import { signOut } from '../services/authService';
import { getQuotaRemaining } from '../services/authService';

export default function HomeScreen() {
  const { user, profile, setUser, setProfile } = useShotStore();

  const handleStart = () => {
    if (!user) {
      router.push('/signin');
      return;
    }
    router.push('/camera');
  };

  async function handleSignOut() {
    await signOut();
    setUser(null);
    setProfile(null);
  }

  const quotaLeft = getQuotaRemaining(profile);
  const isFree = profile?.subscription_tier === 'free' || !user;

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.content}>
        {/* Logo / Title */}
        <View style={styles.header}>
          <Text style={styles.logo}>🎱</Text>
          <Text style={styles.title}>Pool Shot App</Text>
          <Text style={styles.tagline}>AI-powered shot coach</Text>
        </View>

        {/* User / Quota info */}
        {user ? (
          <View style={styles.userBanner}>
            <Text style={styles.userEmail}>{user.email}</Text>
            {isFree && (
              <Text style={styles.quotaText}>
                {quotaLeft > 0
                  ? `${quotaLeft} free shot${quotaLeft !== 1 ? 's' : ''} remaining today`
                  : 'Daily shots exhausted — upgrade to Pro!'}
              </Text>
            )}
            {profile?.subscription_tier !== 'free' && profile?.subscription_tier && (
              <Text style={styles.tierBadge}>
                {profile.subscription_tier === 'pro' ? '⭐ Pro' : '🏆 Pool Hall'}
              </Text>
            )}
          </View>
        ) : (
          <View style={styles.userBanner}>
            <Text style={styles.quotaText}>Sign in to track your shots</Text>
          </View>
        )}

        {/* Quick Settings */}
        <View style={styles.settings}>
          <GameTypeSelector />
          <SkillLevelSelector />
        </View>

        {/* CTA */}
        <TouchableOpacity style={styles.ctaButton} onPress={handleStart}>
          <Text style={styles.ctaText}>
            {user ? 'Take a Shot' : 'Sign In to Start'}
          </Text>
        </TouchableOpacity>

        {/* Auth buttons */}
        {user ? (
          <TouchableOpacity style={styles.authButton} onPress={handleSignOut}>
            <Text style={styles.authButtonText}>Sign Out</Text>
          </TouchableOpacity>
        ) : (
          <TouchableOpacity
            style={styles.authButton}
            onPress={() => router.push('/signup')}
          >
            <Text style={styles.authButtonText}>Create Account — Free</Text>
          </TouchableOpacity>
        )}

        {/* Footer */}
        <TouchableOpacity
          style={styles.settingsGear}
          onPress={() => router.push('/settings')}
        >
          <Text style={styles.gearIcon}>⚙️</Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
}

// --- Sub-components ---

function GameTypeSelector() {
  const { gameType, setGameType } = useShotStore();

  const options = [
    { value: '8ball', label: '8-Ball' },
    { value: '9ball', label: '9-Ball' },
    { value: 'straight', label: 'Straight' },
  ];

  return (
    <View style={styles.selector}>
      <Text style={styles.selectorLabel}>Game</Text>
      <View style={styles.optionRow}>
        {options.map((opt) => (
          <TouchableOpacity
            key={opt.value}
            style={[
              styles.option,
              gameType === opt.value && styles.optionSelected,
            ]}
            onPress={() => setGameType(opt.value as any)}
          >
            <Text
              style={[
                styles.optionText,
                gameType === opt.value && styles.optionTextSelected,
              ]}
            >
              {opt.label}
            </Text>
          </TouchableOpacity>
        ))}
      </View>
    </View>
  );
}

function SkillLevelSelector() {
  const { skillLevel, setSkillLevel } = useShotStore();

  const options = [
    { value: 'beginner', label: 'Beginner' },
    { value: 'intermediate', label: 'Intermediate' },
    { value: 'pro', label: 'Pro' },
  ];

  return (
    <View style={styles.selector}>
      <Text style={styles.selectorLabel}>Skill Level</Text>
      <View style={styles.optionRow}>
        {options.map((opt) => (
          <TouchableOpacity
            key={opt.value}
            style={[
              styles.option,
              skillLevel === opt.value && styles.optionSelected,
            ]}
            onPress={() => setSkillLevel(opt.value as any)}
          >
            <Text
              style={[
                styles.optionText,
                skillLevel === opt.value && styles.optionTextSelected,
              ]}
            >
              {opt.label}
            </Text>
          </TouchableOpacity>
        ))}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0D1117',
  },
  content: {
    flex: 1,
    paddingHorizontal: 32,
    justifyContent: 'center',
    alignItems: 'center',
  },
  header: {
    alignItems: 'center',
    marginBottom: 32,
  },
  logo: {
    fontSize: 72,
    marginBottom: 16,
  },
  title: {
    fontSize: 36,
    fontWeight: '700',
    color: '#F0F6FC',
    letterSpacing: -1,
  },
  tagline: {
    fontSize: 16,
    color: '#8B949E',
    marginTop: 4,
  },
  userBanner: {
    width: '100%',
    backgroundColor: '#161B22',
    borderRadius: 10,
    paddingVertical: 12,
    paddingHorizontal: 16,
    marginBottom: 24,
    borderWidth: 1,
    borderColor: '#30363D',
    alignItems: 'center',
  },
  userEmail: {
    fontSize: 13,
    color: '#8B949E',
    marginBottom: 2,
  },
  quotaText: {
    fontSize: 13,
    color: '#D29922',
    fontWeight: '500',
  },
  tierBadge: {
    fontSize: 13,
    color: '#58A6FF',
    fontWeight: '600',
    marginTop: 2,
  },
  settings: {
    width: '100%',
    marginBottom: 32,
  },
  selector: {
    marginBottom: 20,
  },
  selectorLabel: {
    fontSize: 12,
    color: '#8B949E',
    marginBottom: 8,
    textTransform: 'uppercase',
    letterSpacing: 1,
  },
  optionRow: {
    flexDirection: 'row',
    gap: 8,
  },
  option: {
    flex: 1,
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 8,
    backgroundColor: '#161B22',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#30363D',
  },
  optionSelected: {
    backgroundColor: '#58A6FF',
    borderColor: '#58A6FF',
  },
  optionText: {
    fontSize: 14,
    fontWeight: '500',
    color: '#8B949E',
  },
  optionTextSelected: {
    color: '#FFFFFF',
  },
  ctaButton: {
    backgroundColor: '#58A6FF',
    paddingVertical: 18,
    paddingHorizontal: 64,
    borderRadius: 12,
    width: '100%',
    marginBottom: 12,
  },
  ctaText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#FFFFFF',
    textAlign: 'center',
  },
  authButton: {
    paddingVertical: 12,
    width: '100%',
    alignItems: 'center',
  },
  authButtonText: {
    fontSize: 14,
    color: '#58A6FF',
    fontWeight: '500',
  },
  settingsGear: {
    position: 'absolute',
    top: 60,
    right: 24,
    padding: 8,
  },
  gearIcon: {
    fontSize: 24,
  },
});
