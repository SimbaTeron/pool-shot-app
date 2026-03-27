import { View, Text, TouchableOpacity, StyleSheet, SafeAreaView } from 'react-native';
import { router } from 'expo-router';
import { useShotStore } from '../store/useShotStore';

export default function HomeScreen() {
  const { setGameType, setSkillLevel } = useShotStore();

  const handleStart = () => {
    router.push('/camera');
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.content}>
        {/* Logo / Title */}
        <View style={styles.header}>
          <Text style={styles.logo}>🎱</Text>
          <Text style={styles.title}>Pool Shot App</Text>
          <Text style={styles.tagline}>AI-powered shot coach</Text>
        </View>

        {/* Quick Settings */}
        <View style={styles.settings}>
          <GameTypeSelector />
          <SkillLevelSelector />
        </View>

        {/* CTA */}
        <TouchableOpacity style={styles.ctaButton} onPress={handleStart}>
          <Text style={styles.ctaText}>Take a Shot</Text>
        </TouchableOpacity>

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
    marginBottom: 48,
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
  settings: {
    width: '100%',
    marginBottom: 48,
  },
  selector: {
    marginBottom: 24,
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
  },
  ctaText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#FFFFFF',
    textAlign: 'center',
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
