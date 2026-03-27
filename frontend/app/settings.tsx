import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, Linking } from 'react-native';
import { router } from 'expo-router';
import { useShotStore } from '../store/useShotStore';

export default function SettingsScreen() {
  const { gameType, skillLevel, tableSize, setGameType, setSkillLevel, setTableSize } = useShotStore();

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()}>
          <Text style={styles.backButton}>←</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Settings</Text>
        <View style={{ width: 30 }} />
      </View>

      <ScrollView style={styles.content}>
        {/* Game Settings */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Game Defaults</Text>

          <Text style={styles.settingLabel}>Game Type</Text>
          <View style={styles.optionRow}>
            {(['8ball', '9ball', 'straight'] as const).map((type) => (
              <TouchableOpacity
                key={type}
                style={[styles.option, gameType === type && styles.optionSelected]}
                onPress={() => setGameType(type)}
              >
                <Text style={[styles.optionText, gameType === type && styles.optionTextSelected]}>
                  {type === '8ball' ? '8-Ball' : type === '9ball' ? '9-Ball' : 'Straight'}
                </Text>
              </TouchableOpacity>
            ))}
          </View>

          <Text style={styles.settingLabel}>Skill Level</Text>
          <View style={styles.optionRow}>
            {(['beginner', 'intermediate', 'pro'] as const).map((level) => (
              <TouchableOpacity
                key={level}
                style={[styles.option, skillLevel === level && styles.optionSelected]}
                onPress={() => setSkillLevel(level)}
              >
                <Text style={[styles.optionText, skillLevel === level && styles.optionTextSelected]}>
                  {level.charAt(0).toUpperCase() + level.slice(1)}
                </Text>
              </TouchableOpacity>
            ))}
          </View>

          <Text style={styles.settingLabel}>Default Table Size</Text>
          <View style={styles.optionRow}>
            {(['7ft', '9ft'] as const).map((size) => (
              <TouchableOpacity
                key={size}
                style={[styles.option, tableSize === size && styles.optionSelected]}
                onPress={() => setTableSize(size)}
              >
                <Text style={[styles.optionText, tableSize === size && styles.optionTextSelected]}>
                  {size === '7ft' ? 'Bar 7ft' : 'Regulation 9ft'}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* Subscription */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Subscription</Text>
          <View style={styles.subscriptionCard}>
            <View style={styles.subscriptionHeader}>
              <Text style={styles.subscriptionTitle}>Free Tier</Text>
              <Text style={styles.subscriptionBadge}>Current</Text>
            </View>
            <Text style={styles.subscriptionDesc}>3 shots per day</Text>
            <TouchableOpacity style={styles.upgradeButton}>
              <Text style={styles.upgradeButtonText}>Upgrade to Pro — $7.99/mo</Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* About */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>About</Text>
          <Text style={styles.aboutText}>Pool Shot App v1.0.0</Text>
          <Text style={styles.aboutText}>AI-powered pool shot coach</Text>
          <Text style={styles.aboutText}>Built with React Native + OpenCV</Text>
        </View>

        {/* Links */}
        <View style={styles.section}>
          <TouchableOpacity style={styles.linkRow}>
            <Text style={styles.linkText}>Privacy Policy</Text>
            <Text style={styles.linkArrow}>→</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.linkRow}>
            <Text style={styles.linkText}>Terms of Service</Text>
            <Text style={styles.linkArrow}>→</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.linkRow}>
            <Text style={styles.linkText}>Support</Text>
            <Text style={styles.linkArrow}>→</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0D1117',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingTop: 60,
    paddingHorizontal: 20,
    paddingBottom: 16,
  },
  backButton: {
    fontSize: 28,
    color: '#F0F6FC',
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#F0F6FC',
  },
  content: {
    flex: 1,
    paddingHorizontal: 20,
  },
  section: {
    marginBottom: 32,
  },
  sectionTitle: {
    fontSize: 12,
    color: '#8B949E',
    textTransform: 'uppercase',
    letterSpacing: 1,
    marginBottom: 16,
  },
  settingLabel: {
    fontSize: 14,
    color: '#F0F6FC',
    marginBottom: 8,
  },
  optionRow: {
    flexDirection: 'row',
    gap: 8,
    marginBottom: 16,
  },
  option: {
    flex: 1,
    paddingVertical: 12,
    paddingHorizontal: 12,
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
    fontSize: 13,
    color: '#8B949E',
  },
  optionTextSelected: {
    color: '#FFFFFF',
    fontWeight: '600',
  },
  subscriptionCard: {
    backgroundColor: '#161B22',
    borderRadius: 12,
    padding: 16,
    borderWidth: 1,
    borderColor: '#30363D',
  },
  subscriptionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  subscriptionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#F0F6FC',
  },
  subscriptionBadge: {
    fontSize: 11,
    color: '#58A6FF',
    backgroundColor: 'rgba(88,166,255,0.1)',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
  },
  subscriptionDesc: {
    fontSize: 14,
    color: '#8B949E',
    marginBottom: 16,
  },
  upgradeButton: {
    backgroundColor: '#58A6FF',
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: 'center',
  },
  upgradeButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#FFFFFF',
  },
  aboutText: {
    fontSize: 14,
    color: '#8B949E',
    marginBottom: 4,
  },
  linkRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#161B22',
    paddingVertical: 16,
    paddingHorizontal: 16,
    borderRadius: 8,
    marginBottom: 8,
  },
  linkText: {
    fontSize: 15,
    color: '#F0F6FC',
  },
  linkArrow: {
    fontSize: 16,
    color: '#8B949E',
  },
});
