import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, ActivityIndicator } from 'react-native';
import { router } from 'expo-router';
import { useShotStore } from '../store/useShotStore';
import { detectAndCalculate } from '../services/api';

export default function ProcessingScreen() {
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState('Analyzing table...');

  const {
    capturedImage,
    tableSize,
    gameType,
    skillLevel,
    setDetectedBalls,
    setCueBall,
    setShotData,
    setDiagramSvg,
  } = useShotStore();

  useEffect(() => {
    processImage();
  }, []);

  async function processImage() {
    if (!capturedImage) {
      router.replace('/camera');
      return;
    }

    try {
      // Simulate progress while processing
      const progressInterval = setInterval(() => {
        setProgress((p) => Math.min(p + 5, 90));
      }, 200);

      setStatus('Detecting balls...');
      setProgress(10);

      // Read the image as base64
      const response = await fetch(capturedImage);
      const blob = await response.blob();
      const base64 = await new Promise<string>((resolve) => {
        const reader = new FileReader();
        reader.onloadend = () => {
          const result = reader.result as string;
          resolve(result.split(',')[1]); // Remove data:image/jpeg;base64, prefix
        };
        reader.readAsDataURL(blob);
      });

      setStatus('Calculating shot...');
      setProgress(50);

      // Call the backend
      const result = await detectAndCalculate(
        base64,
        tableSize,
        gameType,
        skillLevel
      );

      clearInterval(progressInterval);
      setProgress(100);
      setStatus('Done!');

      // Store results
      setDetectedBalls(result.detection.balls);
      setCueBall(result.detection.cue_ball);
      setShotData(result.shot);
      setDiagramSvg(result.diagram_svg);

      // Navigate to diagram
      setTimeout(() => {
        router.replace('/diagram');
      }, 500);
    } catch (error) {
      console.error('Processing failed:', error);
      setStatus('Processing failed. Please try again.');
      setTimeout(() => {
        router.replace('/camera');
      }, 2000);
    }
  }

  return (
    <View style={styles.container}>
      <Text style={styles.logo}>🎱</Text>
      <Text style={styles.title}>Analyzing Your Shot</Text>

      <View style={styles.progressContainer}>
        <ActivityIndicator size="large" color="#58A6FF" />
        <View style={styles.progressBar}>
          <View style={[styles.progressFill, { width: `${progress}%` }]} />
        </View>
        <Text style={styles.progressText}>{progress}%</Text>
      </View>

      <Text style={styles.statusText}>{status}</Text>

      <Text style={styles.hint}>
        Ensure good lighting and a clear view of the table for best results.
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0D1117',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 32,
  },
  logo: {
    fontSize: 64,
    marginBottom: 24,
  },
  title: {
    fontSize: 24,
    fontWeight: '600',
    color: '#F0F6FC',
    marginBottom: 48,
  },
  progressContainer: {
    width: '100%',
    alignItems: 'center',
    marginBottom: 32,
  },
  progressBar: {
    width: '80%',
    height: 4,
    backgroundColor: '#161B22',
    borderRadius: 2,
    marginTop: 24,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#58A6FF',
    borderRadius: 2,
  },
  progressText: {
    marginTop: 12,
    fontSize: 14,
    color: '#8B949E',
    fontFamily: 'JetBrains Mono',
  },
  statusText: {
    fontSize: 16,
    color: '#F0F6FC',
    marginBottom: 24,
  },
  hint: {
    fontSize: 13,
    color: '#8B949E',
    textAlign: 'center',
    lineHeight: 20,
  },
});
