/**
 * Procedural additive breathing layer.
 * f(t) = sin(t * rate) scaled by exertion and emotion.
 * 
 * Returns per-bone additive Euler offsets for chest expansion.
 */
export interface BreathingParams {
  phase: number;       // accumulated time
  exertion: number;    // 0 = resting, 1 = max exertion
  emotionScale: number; // from EmotionModifiers.breatheScale
}

export interface BreathingOffsets {
  spine: { x: number; y: number; z: number };
  chest: { x: number; y: number; z: number };
  upperChest: { x: number; y: number; z: number };
  leftShoulder: { x: number; z: number };
  rightShoulder: { x: number; z: number };
}

export function computeBreathing({ phase, exertion, emotionScale }: BreathingParams): BreathingOffsets {
  // Base rate increases with exertion (resting ~1.5 Hz, max ~3.5 Hz)
  const rate = 1.5 + exertion * 2.0;
  // Amplitude scales with exertion and emotion
  const amp = (0.006 + exertion * 0.012) * emotionScale;
  
  const t = Math.sin(phase * rate);
  const chestExpand = t * amp * 2.0;

  return {
    spine: { x: t * amp, y: 0, z: 0 },
    chest: { x: t * amp * 1.5, y: 0, z: chestExpand * 0.3 },
    upperChest: { x: t * amp * 1.2, y: 0, z: 0 },
    leftShoulder: { x: -t * amp * 0.4, z: -chestExpand },
    rightShoulder: { x: -t * amp * 0.4, z: chestExpand },
  };
}
