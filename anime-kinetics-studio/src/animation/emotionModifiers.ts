import { EmotionType, EmotionModifiers } from './types';

const EMOTION_MODIFIERS: Record<EmotionType, EmotionModifiers> = {
  neutral: {
    shoulderHeightOffset: 0,
    spineForwardLean: 0,
    headTilt: 0,
    breatheScale: 1.0,
  },
  happy: {
    shoulderHeightOffset: -0.03,
    spineForwardLean: -0.02,
    headTilt: 0.04,
    breatheScale: 1.2,
  },
  sad: {
    shoulderHeightOffset: 0.05,
    spineForwardLean: 0.06,
    headTilt: -0.08,
    breatheScale: 0.7,
  },
  // ─── Sadness hierarchy ────────────────────────────────────────────
  sad_mild: {
    shoulderHeightOffset: 0.02,
    spineForwardLean: 0.02,
    headTilt: -0.04,
    breatheScale: 0.85,
  },
  sad_moderate: {
    shoulderHeightOffset: 0.08,
    spineForwardLean: 0.1,
    headTilt: -0.52,       // ~30° down
    breatheScale: 0.6,
  },
  sad_severe: {
    shoulderHeightOffset: 0.12,
    spineForwardLean: 0.15,
    headTilt: -0.35,
    breatheScale: 1.4,     // sobbing = heavier breathing
  },
  angry: {
    shoulderHeightOffset: -0.04,
    spineForwardLean: -0.03,
    headTilt: -0.03,
    breatheScale: 1.5,
  },
  surprised: {
    shoulderHeightOffset: -0.06,
    spineForwardLean: -0.04,
    headTilt: 0.06,
    breatheScale: 1.3,
  },
  relaxed: {
    shoulderHeightOffset: 0.02,
    spineForwardLean: 0.02,
    headTilt: 0.02,
    breatheScale: 0.8,
  },
  thinking: {
    shoulderHeightOffset: 0.01,
    spineForwardLean: 0.03,
    headTilt: -0.04,
    breatheScale: 0.9,
  },
  serious: {
    shoulderHeightOffset: -0.02,
    spineForwardLean: -0.02,
    headTilt: -0.02,
    breatheScale: 1.0,
  },
  // ─── Illness states ───────────────────────────────────────────────
  fever: {
    shoulderHeightOffset: 0.06,
    spineForwardLean: 0.08,
    headTilt: -0.1,
    breatheScale: 1.6,
    eyeSquint: 0.6,         // half-closed exhausted eyes
    shiverIntensity: 0.7,
  },
  cold: {
    shoulderHeightOffset: 0.1,
    spineForwardLean: 0.12,
    headTilt: -0.06,
    breatheScale: 1.3,
    eyeSquint: 0.3,
    shiverIntensity: 0.3,
  },
};

export function getEmotionModifiers(emotion: EmotionType): EmotionModifiers {
  return EMOTION_MODIFIERS[emotion] ?? EMOTION_MODIFIERS.neutral;
}
