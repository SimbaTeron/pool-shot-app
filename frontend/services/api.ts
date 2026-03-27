const API_BASE = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000';

export interface DetectResponse {
  balls: Array<{
    x: number;
    y: number;
    color: string;
    number: number | null;
  }>;
  table_corners: Array<{ x: number; y: number }>;
  cue_ball: { x: number; y: number } | null;
  detection_confidence: number;
}

export interface ShotResponse {
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
  error?: string;
}

export interface DetectAndCalculateResponse {
  detection: DetectResponse;
  shot: ShotResponse;
  shot_quality: string | null;
  diagram_svg: string;
}

export async function detectAndCalculate(
  imageBase64: string,
  tableSize: '7ft' | '9ft',
  gameType: '8ball' | '9ball' | 'straight',
  skillLevel: 'beginner' | 'intermediate' | 'pro'
): Promise<DetectAndCalculateResponse> {
  const response = await fetch(`${API_BASE}/detect-and-calculate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      image_base64: imageBase64,
      table_size: tableSize,
    }),
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  return response.json();
}
