import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Share,
  Dimensions,
} from 'react-native';
import { router } from 'expo-router';
import Svg, { Circle, Path, Rect, Text as SvgText, G, Defs, RadialGradient, Stop } from 'react-native-svg';
import { useShotStore } from '../store/useShotStore';

const { width } = Dimensions.get('window');

const BALL_COLORS: Record<string, string> = {
  cue: '#FFFFFF',
  solid1: '#FFD700',
  solid2: '#0000FF',
  solid3: '#FF0000',
  solid4: '#800080',
  solid5: '#FFA500',
  solid6: '#008000',
  solid7: '#800000',
  solid8: '#111111',
  stripe9: '#0000FF',
  stripe10: '#FFD700',
  stripe11: '#FF0000',
  stripe12: '#800080',
  stripe13: '#FFA500',
  stripe14: '#008000',
  stripe15: '#800000',
};

export default function DiagramScreen() {
  const { capturedImage, shotData, detectedBalls, tableSize, reset } = useShotStore();

  if (!shotData || !capturedImage) {
    router.replace('/camera');
    return null;
  }

  const svgWidth = width - 32;
  const svgHeight = svgWidth * 0.5; // 2:1 aspect ratio

  const handleShare = async () => {
    try {
      await Share.share({
        message: `Pool Shot App recommendation: ${shotData.quality_description || `Ball ${shotData.target_ball_number} → ${shotData.target_pocket}`}\nPower: ${Math.round(shotData.power * 100)}% | Angle: ${shotData.angle}°`,
      });
    } catch (error) {
      console.error('Share failed:', error);
    }
  };

  const handleRetake = () => {
    reset();
    router.replace('/camera');
  };

  const { ghost_ball, cue_path, object_path, target_pocket, target_ball_number, power, english, angle, quality_description } = shotData;

  // Pocket positions (relative 0-1)
  const POCKET_POSITIONS: Record<string, [number, number]> = {
    top_left: [0.07, 0.07],
    top_right: [0.93, 0.07],
    middle_left: [0.0, 0.5],
    middle_right: [1.0, 0.5],
    bottom_left: [0.07, 0.93],
    bottom_right: [0.93, 0.93],
  };

  const pocketKey = target_pocket as string;
  const targetPocketPos = POCKET_POSITIONS[pocketKey] || [0.5, 0.5];

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.replace('/')}>
          <Text style={styles.homeButton}>🏠</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Shot Analysis</Text>
        <TouchableOpacity onPress={handleShare}>
          <Text style={styles.shareButton}>📤</Text>
        </TouchableOpacity>
      </View>

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {/* Shot Diagram */}
        <View style={styles.diagramContainer}>
          <Svg width={svgWidth} height={svgHeight} viewBox={`0 0 ${svgWidth} ${svgHeight}`}>
            <Defs>
              <RadialGradient id="ghostGrad" cx="30%" cy="30%" r="70%">
                <Stop offset="0%" stopColor="#8FCFFF" stopOpacity="0.6" />
                <Stop offset="100%" stopColor="#58A6FF" stopOpacity="0.3" />
              </RadialGradient>
            </Defs>

            {/* Table felt */}
            <Rect
              x="16"
              y="16"
              width={svgWidth - 32}
              height={svgHeight - 32}
              rx="8"
              fill="#0A4D2E"
              stroke="#4A3728"
              strokeWidth="8"
            />

            {/* Pockets */}
            {Object.values(POCKET_POSITIONS).map(([px, py], i) => (
              <Circle
                key={i}
                cx={px * svgWidth}
                cy={py * svgHeight}
                r={10}
                fill="#111111"
              />
            ))}

            {/* Cue path */}
            {cue_path && cue_path.length >= 2 && (
              <Path
                d={`M ${cue_path[0].x} ${cue_path[0].y} L ${cue_path[1].x} ${cue_path[1].y}`}
                fill="none"
                stroke="#F0F6FC"
                strokeWidth={3}
                strokeLinecap="round"
                opacity={0.9}
              />
            )}

            {/* Object path */}
            {object_path && object_path.length >= 2 && (
              <>
                <Path
                  d={`M ${object_path[0].x} ${object_path[0].y} L ${object_path[1].x} ${object_path[1].y}`}
                  fill="none"
                  stroke="#79C0FF"
                  strokeWidth={2.5}
                  strokeLinecap="round"
                  opacity={0.8}
                />
                {/* Target pocket highlight */}
                <Circle
                  cx={targetPocketPos[0] * svgWidth}
                  cy={targetPocketPos[1] * svgHeight}
                  r={16}
                  fill="none"
                  stroke="#D29922"
                  strokeWidth={2}
                  strokeDasharray="4,4"
                />
              </>
            )}

            {/* Ghost ball */}
            {ghost_ball && (
              <G>
                <Circle
                  cx={ghost_ball.x}
                  cy={ghost_ball.y}
                  r={16}
                  fill="url(#ghostGrad)"
                  stroke="#58A6FF"
                  strokeWidth={2}
                  strokeDasharray="6,4"
                />
              </G>
            )}

            {/* Balls */}
            {detectedBalls.map((ball, i) => {
              const isTarget = ball.number === target_ball_number;
              const ballColor = BALL_COLORS[ball.color] || '#FFFFFF';
              return (
                <G key={i}>
                  {isTarget && (
                    <Circle
                      cx={ball.x}
                      cy={ball.y}
                      r={14}
                      fill="none"
                      stroke="#D29922"
                      strokeWidth={2}
                      strokeDasharray="4,4"
                    />
                  )}
                  <Circle
                    cx={ball.x}
                    cy={ball.y}
                    r={10}
                    fill={ballColor}
                    stroke="white"
                    strokeWidth={0.5}
                  />
                  {ball.number && ball.number !== 8 && (
                    <SvgText
                      x={ball.x}
                      y={ball.y + 4}
                      fontSize={9}
                      fontWeight="bold"
                      fill={ballColor === '#FFFFFF' || ballColor === '#FFD700' ? '#000' : '#FFF'}
                      textAnchor="middle"
                    >
                      {ball.number}
                    </SvgText>
                  )}
                  {ball.number === 8 && (
                    <SvgText
                      x={ball.x}
                      y={ball.y + 4}
                      fontSize={9}
                      fontWeight="bold"
                      fill="#FFF"
                      textAnchor="middle"
                    >
                      8
                    </SvgText>
                  )}
                </G>
              );
            })}

            {/* Shot info label */}
            <SvgText
              x={20}
              y={30}
              fontSize={14}
              fontWeight="bold"
              fill="#F0F6FC"
            >
              Ball {target_ball_number} → {pocketKey.replace('_', ' ').toUpperCase()}
            </SvgText>
          </Svg>
        </View>

        {/* Shot Details */}
        <View style={styles.detailsCard}>
          <Text style={styles.qualityLabel}>
            {quality_description || 'Shot Analysis'}
          </Text>

          <View style={styles.metricsRow}>
            {/* Power */}
            <View style={styles.metric}>
              <Text style={styles.metricLabel}>Power</Text>
              <View style={styles.metricValueRow}>
                <View style={[styles.metricBar, { width: `${power * 100}%`, backgroundColor: getPowerColor(power) }]} />
              </View>
              <Text style={[styles.metricNumber, { color: getPowerColor(power) }]}>
                {Math.round(power * 100)}%
              </Text>
            </View>

            {/* Angle */}
            <View style={styles.metric}>
              <Text style={styles.metricLabel}>Angle</Text>
              <Text style={styles.metricNumber}>{angle}°</Text>
            </View>

            {/* English */}
            <View style={styles.metric}>
              <Text style={styles.metricLabel}>English</Text>
              <Text style={styles.metricNumber}>
                {Math.abs(english) < 0.1 ? 'Center' : english > 0 ? `R ${Math.round(english * 100)}%` : `L ${Math.round(Math.abs(english) * 100)}%`}
              </Text>
            </View>
          </View>
        </View>

        {/* Confidence */}
        <View style={styles.confidenceCard}>
          <Text style={styles.confidenceLabel}>Confidence</Text>
          <Text style={styles.confidenceValue}>{Math.round(shotData.confidence * 100)}%</Text>
          <Text style={styles.confidenceHint}>
            Based on angle, distance, and pocket selection
          </Text>
        </View>

        {/* Actions */}
        <View style={styles.actions}>
          <TouchableOpacity style={styles.retakeButton} onPress={handleRetake}>
            <Text style={styles.retakeText}>🔄 Retake</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.shareActionButton} onPress={handleShare}>
            <Text style={styles.shareActionText}>📤 Share</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </View>
  );
}

function getPowerColor(power: number): string {
  if (power < 0.33) return '#3FB950';
  if (power < 0.66) return '#D29922';
  return '#F85149';
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
  homeButton: {
    fontSize: 24,
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#F0F6FC',
  },
  shareButton: {
    fontSize: 24,
  },
  content: {
    flex: 1,
    paddingHorizontal: 16,
  },
  diagramContainer: {
    backgroundColor: '#161B22',
    borderRadius: 12,
    overflow: 'hidden',
    marginBottom: 16,
  },
  detailsCard: {
    backgroundColor: '#161B22',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
  },
  qualityLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#F0F6FC',
    marginBottom: 16,
  },
  metricsRow: {
    flexDirection: 'row',
    gap: 16,
  },
  metric: {
    flex: 1,
  },
  metricLabel: {
    fontSize: 11,
    color: '#8B949E',
    textTransform: 'uppercase',
    letterSpacing: 1,
    marginBottom: 6,
  },
  metricValueRow: {
    height: 4,
    backgroundColor: '#30363D',
    borderRadius: 2,
    marginBottom: 4,
  },
  metricBar: {
    height: '100%',
    borderRadius: 2,
  },
  metricNumber: {
    fontSize: 16,
    fontWeight: '600',
    color: '#F0F6FC',
    fontFamily: 'JetBrains Mono',
  },
  confidenceCard: {
    backgroundColor: '#161B22',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    alignItems: 'center',
  },
  confidenceLabel: {
    fontSize: 11,
    color: '#8B949E',
    textTransform: 'uppercase',
    letterSpacing: 1,
    marginBottom: 8,
  },
  confidenceValue: {
    fontSize: 36,
    fontWeight: '700',
    color: '#58A6FF',
    fontFamily: 'JetBrains Mono',
    marginBottom: 4,
  },
  confidenceHint: {
    fontSize: 12,
    color: '#8B949E',
  },
  actions: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 40,
  },
  retakeButton: {
    flex: 1,
    backgroundColor: '#161B22',
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#30363D',
  },
  retakeText: {
    fontSize: 16,
    color: '#F0F6FC',
  },
  shareActionButton: {
    flex: 1,
    backgroundColor: '#58A6FF',
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: 'center',
  },
  shareActionText: {
    fontSize: 16,
    color: '#FFFFFF',
    fontWeight: '600',
  },
});
