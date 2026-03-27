import { create } from 'zustand';
import type { UserProfile } from '../services/supabase';

export type GameType = '8ball' | '9ball' | 'straight';
export type SkillLevel = 'beginner' | 'intermediate' | 'pro';
export type TableSize = '7ft' | '9ft';

export interface Ball {
  x: number;
  y: number;
  color: string;
  number: number | null;
  radius?: number;
}

export interface ShotData {
  ghost_ball: { x: number; y: number } | null;
  cue_path: Array<{ x: number; y: number }>;
  object_path: Array<{ x: number; y: number }>;
  target_pocket: string | null;
  target_ball_number: number | null;
  power: number;
  english: number;
  angle: number;
  distance: number;
  score: number;
  confidence: number;
  quality_description?: string;
}

interface ShotStore {
  // Auth
  user: any | null;
  profile: UserProfile | null;
  
  // Settings
  gameType: GameType;
  skillLevel: SkillLevel;
  tableSize: TableSize;
  
  // Session data
  capturedImage: string | null;
  detectedBalls: Ball[];
  cueBall: Ball | null;
  shotData: ShotData | null;
  diagramSvg: string | null;
  
  // Actions
  setUser: (user: any | null) => void;
  setProfile: (profile: UserProfile | null) => void;
  setGameType: (type: GameType) => void;
  setSkillLevel: (level: SkillLevel) => void;
  setTableSize: (size: TableSize) => void;
  setCapturedImage: (uri: string) => void;
  setDetectedBalls: (balls: Ball[]) => void;
  setCueBall: (ball: Ball | null) => void;
  setShotData: (data: ShotData) => void;
  setDiagramSvg: (svg: string) => void;
  reset: () => void;
}

export const useShotStore = create<ShotStore>((set) => ({
  // Defaults
  user: null,
  profile: null,
  gameType: '8ball',
  skillLevel: 'intermediate',
  tableSize: '9ft',
  capturedImage: null,
  detectedBalls: [],
  cueBall: null,
  shotData: null,
  diagramSvg: null,

  setUser: (user) => set({ user }),
  setProfile: (profile) => set({ profile }),
  setGameType: (type) => set({ gameType: type }),
  setSkillLevel: (level) => set({ skillLevel: level }),
  setTableSize: (size) => set({ tableSize: size }),
  setCapturedImage: (uri) => set({ capturedImage: uri }),
  setDetectedBalls: (balls) => set({ detectedBalls: balls }),
  setCueBall: (ball) => set({ cueBall: ball }),
  setShotData: (data) => set({ shotData: data }),
  setDiagramSvg: (svg) => set({ diagramSvg: svg }),
  reset: () => set({
    capturedImage: null,
    detectedBalls: [],
    cueBall: null,
    shotData: null,
    diagramSvg: null,
  }),
}));
