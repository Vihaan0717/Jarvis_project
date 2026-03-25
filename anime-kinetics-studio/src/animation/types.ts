export type EmotionType =
  | 'neutral' | 'happy' | 'angry' | 'sad' | 'surprised'
  | 'relaxed' | 'thinking' | 'serious'
  | 'sad_mild' | 'sad_moderate' | 'sad_severe'
  | 'fever' | 'cold';

export type PoseType =
  | 'idle' | 'walk' | 'run' | 'jump'
  | 'sit' | 'seiza' | 'agura'
  | 'dance' | 'wave' | 'bow'
  | 'think' | 'cry' | 'shiver' | 'hug_self'
  | 'gasp' | 'peace_sign' | 'peekaboo'
  | 'count_1' | 'count_2' | 'count_3' | 'count_4' | 'count_5';

export type Vowel = 'a' | 'i' | 'u' | 'e' | 'o' | 'silent';

export interface AnimationAPI {
  play: (pose: PoseType) => void;
  setEmotion: (emotion: EmotionType) => void;
  setExertion: (level: number) => void; // 0-1
  speakVowel: (vowel: Vowel) => void;
  setLookAt: (x: number, y: number) => void;
  setBlink: (v: number) => void;
  setMouthOpen: (v: number) => void;
}

export interface PoseDefinition {
  [boneName: string]: (phase: number) => { x: number; y: number; z: number };
}

export interface EmotionModifiers {
  shoulderHeightOffset: number;
  spineForwardLean: number;
  headTilt: number;
  breatheScale: number;
  /** 0-1: controls half-closed eyes for exhaustion/fever */
  eyeSquint?: number;
  /** 0-1: shiver intensity applied as skeleton jitter */
  shiverIntensity?: number;
}
