import React, { useState, useRef } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Dimensions,
  ActivityIndicator,
} from 'react-native';
import { CameraView, useCameraPermissions } from 'expo-camera';
import { router } from 'expo-router';
import { useShotStore } from '../store/useShotStore';
import * as ImagePicker from 'expo-image-picker';

const { width, height } = Dimensions.get('window');

export default function CameraScreen() {
  const [permission, requestPermission] = useCameraPermissions();
  const [angle, setAngle] = useState<number>(45); // Simulated angle
  const [isCapturing, setIsCapturing] = useState(false);
  const cameraRef = useRef<CameraView>(null);

  const {
    tableSize,
    setTableSize,
    setCapturedImage,
    setDetectedBalls,
    setCueBall,
    setShotData,
    setDiagramSvg,
    gameType,
    skillLevel,
  } = useShotStore();

  const isAngleGood = angle >= 30 && angle <= 90;

  const takePicture = async () => {
    if (!cameraRef.current || !isAngleGood) return;

    setIsCapturing(true);
    try {
      const photo = await cameraRef.current.takePictureAsync({
        base64: true,
        quality: 0.8,
      });

      if (photo?.base64) {
        setCapturedImage(photo.uri);
        
        // Navigate to processing
        router.push('/processing');
      }
    } catch (error) {
      console.error('Failed to take picture:', error);
    } finally {
      setIsCapturing(false);
    }
  };

  if (!permission) {
    return (
      <View style={styles.container}>
        <ActivityIndicator size="large" color="#58A6FF" />
      </View>
    );
  }

  if (!permission.granted) {
    return (
      <View style={styles.permissionContainer}>
        <Text style={styles.permissionText}>
          📷 Camera access is needed to photograph your pool table
        </Text>
        <TouchableOpacity style={styles.permissionButton} onPress={requestPermission}>
          <Text style={styles.permissionButtonText}>Grant Permission</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Camera */}
      <CameraView
        ref={cameraRef}
        style={styles.camera}
        facing="back"
      >
        {/* Angle Overlay */}
        <AngleOverlay angle={angle} isGood={isAngleGood} />

        {/* Top Controls */}
        <View style={styles.topControls}>
          {/* Close */}
          <TouchableOpacity
            style={styles.closeButton}
            onPress={() => router.back()}
          >
            <Text style={styles.closeText}>✕</Text>
          </TouchableOpacity>

          {/* Angle Indicator */}
          <View style={[styles.angleBadge, isAngleGood ? styles.angleGood : styles.angleBad]}>
            <Text style={styles.angleText}>{angle}°</Text>
          </View>

          {/* Flash Toggle */}
          <TouchableOpacity style={styles.flashButton}>
            <Text style={styles.flashText}>⚡</Text>
          </TouchableOpacity>
        </View>

        {/* Table Size Selector */}
        <View style={styles.tableSizeContainer}>
          <Text style={styles.tableSizeLabel}>Table Size</Text>
          <View style={styles.tableSizeOptions}>
            {(['7ft', '9ft'] as const).map((size) => (
              <TouchableOpacity
                key={size}
                style={[
                  styles.tableSizeOption,
                  tableSize === size && styles.tableSizeSelected,
                ]}
                onPress={() => setTableSize(size)}
              >
                <Text
                  style={[
                    styles.tableSizeOptionText,
                    tableSize === size && styles.tableSizeOptionTextSelected,
                  ]}
                >
                  {size === '7ft' ? 'Bar 7ft' : 'Regulation 9ft'}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* Bottom Controls */}
        <View style={styles.bottomControls}>
          {/* Gallery Pick */}
          <TouchableOpacity
            style={styles.galleryButton}
            onPress={async () => {
              const result = await ImagePicker.launchImageLibraryAsync({
                mediaTypes: ImagePicker.MediaTypeOptions.Images,
                allowsEditing: true,
                quality: 0.8,
                base64: true,
              });
              if (!result.canceled && result.assets[0]?.base64) {
                setCapturedImage(result.assets[0].uri);
                router.push('/processing');
              }
            }}
          >
            <Text style={styles.galleryIcon}>🖼</Text>
          </TouchableOpacity>

          {/* Capture Button */}
          <TouchableOpacity
            style={[
              styles.captureButton,
              !isAngleGood && styles.captureButtonDisabled,
            ]}
            onPress={takePicture}
            disabled={!isAngleGood || isCapturing}
          >
            {isCapturing ? (
              <ActivityIndicator color="#FFFFFF" />
            ) : (
              <View style={styles.captureInner} />
            )}
          </TouchableOpacity>

          {/* Flip Camera */}
          <TouchableOpacity style={styles.flipButton}>
            <Text style={styles.flipText}>🔄</Text>
          </TouchableOpacity>
        </View>
      </CameraView>
    </View>
  );
}

// --- Sub-components ---

function AngleOverlay({ angle, isGood }: { angle: number; isGood: boolean }) {
  return (
    <View style={styles.angleOverlay}>
      {/* Corner brackets */}
      <View style={[styles.corner, styles.topLeft]} />
      <View style={[styles.corner, styles.topRight]} />
      <View style={[styles.corner, styles.bottomLeft]} />
      <View style={[styles.corner, styles.bottomRight]} />

      {/* Angle feedback tint */}
      <View
        style={[
          styles.angleTint,
          isGood ? styles.angleTintGood : styles.angleTintBad,
        ]}
      />

      {/* Instruction */}
      <View style={styles.instructionContainer}>
        <Text style={styles.instructionText}>
          {isGood
            ? '✅ Good angle — hold steady'
            : angle < 30
            ? '📐 Raise your camera (too low)'
            : '📐 Lower your camera (too high)'}
        </Text>
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0D1117',
  },
  camera: {
    flex: 1,
  },
  permissionContainer: {
    flex: 1,
    backgroundColor: '#0D1117',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 32,
  },
  permissionText: {
    fontSize: 18,
    color: '#F0F6FC',
    textAlign: 'center',
    marginBottom: 24,
  },
  permissionButton: {
    backgroundColor: '#58A6FF',
    paddingVertical: 14,
    paddingHorizontal: 32,
    borderRadius: 8,
  },
  permissionButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
  angleOverlay: {
    ...StyleSheet.absoluteFillObject,
  },
  corner: {
    position: 'absolute',
    width: 40,
    height: 40,
    borderColor: '#58A6FF',
    borderWidth: 3,
  },
  topLeft: {
    top: 100,
    left: 24,
    borderRightWidth: 0,
    borderBottomWidth: 0,
  },
  topRight: {
    top: 100,
    right: 24,
    borderLeftWidth: 0,
    borderBottomWidth: 0,
  },
  bottomLeft: {
    bottom: 180,
    left: 24,
    borderRightWidth: 0,
    borderTopWidth: 0,
  },
  bottomRight: {
    bottom: 180,
    right: 24,
    borderLeftWidth: 0,
    borderTopWidth: 0,
  },
  angleTint: {
    ...StyleSheet.absoluteFillObject,
    opacity: 0.08,
  },
  angleTintGood: {
    backgroundColor: '#3FB950',
  },
  angleTintBad: {
    backgroundColor: '#F85149',
  },
  instructionContainer: {
    position: 'absolute',
    top: 160,
    left: 0,
    right: 0,
    alignItems: 'center',
  },
  instructionText: {
    color: '#FFFFFF',
    fontSize: 14,
    backgroundColor: 'rgba(0,0,0,0.6)',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    overflow: 'hidden',
  },
  topControls: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingTop: 60,
    paddingHorizontal: 24,
  },
  closeButton: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  closeText: {
    color: '#FFFFFF',
    fontSize: 20,
    fontWeight: '300',
  },
  angleBadge: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
  },
  angleGood: {
    backgroundColor: '#3FB950',
  },
  angleBad: {
    backgroundColor: '#F85149',
  },
  angleText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
    fontFamily: 'JetBrains Mono',
  },
  flashButton: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  flashText: {
    fontSize: 20,
  },
  tableSizeContainer: {
    position: 'absolute',
    top: 200,
    right: 24,
  },
  tableSizeLabel: {
    color: '#8B949E',
    fontSize: 10,
    textTransform: 'uppercase',
    letterSpacing: 1,
    marginBottom: 8,
    textAlign: 'right',
  },
  tableSizeOptions: {
    gap: 8,
  },
  tableSizeOption: {
    backgroundColor: 'rgba(0,0,0,0.6)',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 6,
    borderWidth: 1,
    borderColor: '#30363D',
  },
  tableSizeSelected: {
    backgroundColor: '#58A6FF',
    borderColor: '#58A6FF',
  },
  tableSizeOptionText: {
    color: '#8B949E',
    fontSize: 12,
  },
  tableSizeOptionTextSelected: {
    color: '#FFFFFF',
  },
  bottomControls: {
    position: 'absolute',
    bottom: 40,
    left: 0,
    right: 0,
    flexDirection: 'row',
    justifyContent: 'space-around',
    alignItems: 'center',
    paddingHorizontal: 32,
  },
  galleryButton: {
    width: 50,
    height: 50,
    borderRadius: 12,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  galleryIcon: {
    fontSize: 24,
  },
  captureButton: {
    width: 72,
    height: 72,
    borderRadius: 36,
    backgroundColor: '#FFFFFF',
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 4,
    borderColor: '#F0F6FC',
  },
  captureButtonDisabled: {
    backgroundColor: '#8B949E',
    borderColor: '#8B949E',
  },
  captureInner: {
    width: 58,
    height: 58,
    borderRadius: 29,
    backgroundColor: '#F85149',
  },
  flipButton: {
    width: 50,
    height: 50,
    borderRadius: 12,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  flipText: {
    fontSize: 24,
  },
});
