/**
 * VRMAnimationManager — Single-file facade for the entire VRM animation system.
 *
 * Usage:
 *   import { VRMAnimationManager } from '@/animation/VRMAnimationManager';
 *
 *   const manager = new VRMAnimationManager();
 *   manager.attach(vrm);
 *
 *   // Simple API
 *   manager.playAction('wave');
 *   manager.setEmotion('thinking');
 *   manager.setPosture('seiza');
 *   manager.speakVowel('a');
 *   manager.setLookAt(0.5, -0.2);
 *   manager.setExertion(0.7);
 *
 *   // Call every frame
 *   manager.update(delta);
 */

import * as THREE from 'three';
import { VRM, VRMHumanBoneName, VRMExpressionPresetName } from '@pixiv/three-vrm';
import { POSE_LIBRARY, ALL_BONE_NAMES } from './poses';
import { getEmotionModifiers } from './emotionModifiers';
import { computeBreathing } from './breathing';
import { EyeController } from './eyeController';
import { LipSyncController } from './lipSync';
import { initializeSpringBones, updateSpringBones } from './springBoneDamper';

// ── Re-export types so consumers only need this one file ────────────────
export type { AnimationAPI, PoseDefinition, EmotionModifiers } from './types';
export type { EmotionType, PoseType, Vowel } from './types';

// ── Constants ───────────────────────────────────────────────────────────
const TRANSITION_SPEED = 2; // 0.5s crossfade

const ARM_DOWN_DEFAULTS: Record<string, { x: number; y: number; z: number }> = {
  leftUpperArm:  { x: 0, y: 0, z: 1.35 },
  rightUpperArm: { x: 0, y: 0, z: -1.35 },
  leftLowerArm:  { x: -0.15, y: 0, z: 0 },
  rightLowerArm: { x: -0.15, y: 0, z: 0 },
  leftHand:      { x: -0.1, y: 0, z: 0 },
  rightHand:     { x: -0.1, y: 0, z: 0 },
  leftShoulder:  { x: 0, y: 0, z: 0 },
  rightShoulder: { x: 0, y: 0, z: 0 },
};
const ARM_BONE_NAMES = new Set(Object.keys(ARM_DOWN_DEFAULTS));

const WAVE_BONES = new Set(['rightShoulder', 'rightUpperArm', 'rightLowerArm', 'rightHand']);

// ── Helpers ─────────────────────────────────────────────────────────────
function getVRMBone(vrm: VRM, name: string): THREE.Object3D | null {
  return vrm.humanoid?.getNormalizedBoneNode(name as VRMHumanBoneName)
    ?? vrm.humanoid?.getRawBoneNode(name as VRMHumanBoneName)
    ?? null;
}

function getWaveOverrideEuler(bone: string, phase: number): { x: number; y: number; z: number } | null {
  const w = Math.sin(phase * 5);
  switch (bone) {
    case 'rightShoulder':  return { x: -0.1, y: 0, z: 0.26 };
    case 'rightUpperArm':  return { x: -0.57, y: 0, z: 0.44 };
    case 'rightLowerArm':  return { x: -1.57, y: w * 0.52, z: 0 };
    case 'rightHand':      return { x: 0.1, y: w * 0.18, z: 0.05 };
    default: return null;
  }
}

const POSE_EXERTION: Partial<Record<string, number>> = {
  run: 0.7, walk: 0.3, dance: 0.5, jump: 0.8, cry: 0.3, peekaboo: 0.2,
};

const POSE_AUTO_EMOTION: Partial<Record<string, string>> = {
  think: 'thinking', cry: 'sad_severe',
  hug_self: 'cold', gasp: 'surprised', peace_sign: 'happy',
  peekaboo: 'surprised',
};

const EMOTION_TO_PRESET: Record<string, VRMExpressionPresetName | null> = {
  neutral: null, happy: 'happy', angry: 'angry', sad: 'sad',
  sad_mild: 'sad', sad_moderate: 'sad', sad_severe: 'sad',
  surprised: 'surprised', relaxed: 'relaxed',
  thinking: 'neutral', serious: 'neutral', fever: 'neutral', cold: 'neutral',
};

const STATIC_POSES = new Set(['idle', 'sit', 'seiza', 'agura', 'think', 'hug_self']);

// ═══════════════════════════════════════════════════════════════════════
// ██  VRMAnimationManager  ██
// ═══════════════════════════════════════════════════════════════════════

export class VRMAnimationManager {
  private vrm: VRM | null = null;
  private currentPose: string = 'idle';
  private currentEmotion: string = 'neutral';
  private exertion = 0;
  private phase = 0;
  private transitionProgress = 1;

  public readonly eye = new EyeController();
  public readonly lip = new LipSyncController();

  // Track the current LookAt coordinates to apply to head/neck
  private currentHeadTarget = { yaw: 0, pitch: 0 };

  // ── Lifecycle ─────────────────────────────────────────────────────────

  /** Attach a loaded VRM model. Call once after loading. */
  attach(vrm: VRM): void {
    this.vrm = vrm;
    initializeSpringBones(vrm);
  }

  /** Detach the current model. */
  detach(): void {
    this.vrm = null;
  }

  /** Whether a VRM is currently attached. */
  get isAttached(): boolean {
    return this.vrm !== null;
  }

  // ── Public API ────────────────────────────────────────────────────────

  /**
   * Play an action/pose.
   * Actions: 'idle' | 'walk' | 'run' | 'jump' | 'sit' | 'seiza' | 'agura'
   *        | 'dance' | 'wave' | 'bow' | 'think' | 'cry'
   *        | 'hug_self' | 'gasp' | 'peace_sign'
   */
  playAction(action: string): void {
    if (action === this.currentPose) return;
    this.transitionProgress = 0;
    this.currentPose = action;
    this.exertion = POSE_EXERTION[action] ?? 0;

    const autoEmotion = POSE_AUTO_EMOTION[action];
    if (autoEmotion) this.setEmotion(autoEmotion);
  }

  private targetExpressions: Record<string, number> = {};
  private currentExpressions: Record<string, number> = {};

  /**
   * Set the character's emotional expression.
   * Emotions: 'neutral' | 'happy' | 'angry' | 'sad' | 'surprised'
   *         | 'relaxed' | 'thinking' | 'serious'
   *         | 'sad_mild' | 'sad_moderate' | 'sad_severe'
   *         | 'fever' | 'cold'
   */
  setEmotion(emotion: string): void {
    this.currentEmotion = emotion;
    if (!this.vrm?.expressionManager) return;

    // Reset all major targets to 0
    const presets: VRMExpressionPresetName[] = ['happy', 'angry', 'sad', 'surprised', 'relaxed', 'neutral'];
    presets.forEach(p => {
      this.targetExpressions[p] = 0;
    });

    // Set the specific preset target to 1
    const preset = EMOTION_TO_PRESET[emotion];
    if (preset && preset !== 'neutral') {
      this.targetExpressions[preset] = 1;
    }

    // Initialize current value if missing
    presets.forEach(p => {
      if (this.currentExpressions[p] === undefined) {
        this.currentExpressions[p] = 0;
      }
    });
  }

  /**
   * Set a seated/standing posture (convenience alias for playAction).
   * Postures: 'idle' | 'sit' | 'seiza' | 'agura'
   */
  setPosture(posture: string): void {
    this.playAction(posture);
  }

  /** Set exertion level (0-1). Affects breathing rate and amplitude. */
  setExertion(level: number): void {
    this.exertion = Math.max(0, Math.min(1, level));
  }

  /** Trigger a lip-sync vowel: 'a' | 'i' | 'u' | 'e' | 'o' | 'silent' */
  speakVowel(vowel: string): void {
    this.lip.setVowel(vowel as any);
  }

  /** Set eye-tracking and head tracking targets. Values are normalized via yaw/pitch. */
  setLookAt(headYaw: number, headPitch: number, eyeYaw: number, eyePitch: number): void {
    this.eye.setLookAt(eyeYaw, eyePitch);
    this.currentHeadTarget = { yaw: headYaw, pitch: headPitch };
  }

  /** Override blink amount (0-1). */
  setBlink(v: number): void {
    this.eye.setBlinkOverride(v);
  }

  /** Set exact blind signals tracked by backend */
  setBlinkExact(left?: number, right?: number): void {
    this.eye.setBlinkExact(left, right);
  }

  /** Set mouth-open amount (0-1). */
  setMouthOpen(v: number): void {
    this.lip.setManualAmplitude(v);
  }

  // ── Getters ───────────────────────────────────────────────────────────

  get action(): string { return this.currentPose; }
  get emotion(): string { return this.currentEmotion; }

  // ── Frame update ──────────────────────────────────────────────────────

  /** Call every frame with delta time in seconds. */
  update(delta: number): void {
    if (!this.vrm) return;

    // Clamp delta to prevent massive physics explosions on frame drops (max ~30fps equivalent)
    const safeDelta = Math.min(delta, 0.033);

    this.phase += safeDelta;

    // Transition progress
    const isTransitioning = this.transitionProgress < 1;
    if (isTransitioning) {
      this.transitionProgress = Math.min(1, this.transitionProgress + safeDelta * TRANSITION_SPEED);
    }

    // Spring bone physics should ignore abnormal spikes caused by frame stalls
    if (delta < 0.05) {
      updateSpringBones(this.vrm, safeDelta, isTransitioning, STATIC_POSES.has(this.currentPose));
    }

    // Emotion modifiers
    const emotionMod = getEmotionModifiers(this.currentEmotion as any);

    // Breathing
    const breathing = computeBreathing({
      phase: this.phase,
      exertion: this.exertion,
      emotionScale: emotionMod.breatheScale,
    });

    // Pose definition
    const poseDef = (POSE_LIBRARY as any)[this.currentPose] ?? POSE_LIBRARY.idle;

    // Per-bone update
    ALL_BONE_NAMES.forEach(boneName => {
      const node = getVRMBone(this.vrm!, boneName);
      if (!node) return;

      // Resolve euler: pose def → arm defaults → zero
      const poseFn = poseDef[boneName];
      let euler: { x: number; y: number; z: number };
      if (poseFn) {
        euler = poseFn(this.phase);
      } else if (ARM_BONE_NAMES.has(boneName)) {
        euler = { ...ARM_DOWN_DEFAULTS[boneName] };
      } else {
        euler = { x: 0, y: 0, z: 0 };
      }

      // Wave override
      const isWaveBone = this.currentPose === 'wave' && WAVE_BONES.has(boneName);
      if (isWaveBone) {
        const we = getWaveOverrideEuler(boneName, this.phase);
        if (we) euler = we;
      }

      let ex = euler.x, ey = euler.y, ez = euler.z;

      // Emotion modifiers (skip wave bones)
      if (!isWaveBone) {
        if (boneName === 'spine') ex += emotionMod.spineForwardLean;
        if (boneName === 'head') ex += emotionMod.headTilt;
        if (boneName === 'leftShoulder' || boneName === 'rightShoulder') {
          ex += emotionMod.shoulderHeightOffset;
        }

        // Breathing additive
        const breathKey = boneName as keyof typeof breathing;
        if (breathKey in breathing) {
          const b = breathing[breathKey] as { x: number; y?: number; z: number };
          ex += b.x;
          if ('y' in b && b.y !== undefined) ey += b.y;
          ez += b.z;
        }

        // Apply robust Head and Neck tracking via Euler interpolation
        if (boneName === 'head' || boneName === 'neck') {
          // Increase horizontal rotation scale by 300% to allow proper imitation
          const rotationFactor = boneName === 'head' ? 0.85 : 0.5;
          
          // Negative x because screen-left is positive space
          const yawLimit = Math.PI / 4; 
          const targetYaw = -Math.max(-2, Math.min(2, this.currentHeadTarget.yaw)) * yawLimit * rotationFactor;
          
          const pitchLimit = Math.PI / 6;
          // Negative y means look down relative to screen coords
          const targetPitch = Math.max(-2, Math.min(2, this.currentHeadTarget.pitch)) * pitchLimit * rotationFactor;

          // Add to base Euler (ex=pitch, ey=yaw)
          ey += targetYaw;
          ex -= targetPitch; // Adjust pitch inversion if needed
        }
      }

      // Apply manual eye tracking using Euler rotations
      if (boneName === 'leftEye' || boneName === 'rightEye') {
        // currentX = yaw (left/right), currentY = pitch (up/down)
        // Adjust these to match the coordinate system of the VRM bones
        const eyeYaw = -this.eye.currentX * 1.5;
        const eyePitch = -this.eye.currentY * 1.5;
        
        ey += eyeYaw;
        ex -= eyePitch;
      }

      const targetQ = new THREE.Quaternion().setFromEuler(new THREE.Euler(ex, ey, ez));

      const slerpFactor = isWaveBone
        ? 0.3
        : isTransitioning
          ? Math.min(1, safeDelta * TRANSITION_SPEED * 2)
          : (1.0 - Math.exp(-15 * safeDelta));
      node.quaternion.slerp(targetQ, slerpFactor);
    });

    // --- Smooth Expression Lerping ---
    if (this.vrm.expressionManager) {
      const presets: VRMExpressionPresetName[] = ['happy', 'angry', 'sad', 'surprised', 'relaxed', 'neutral'];
      const lerpFactor = Math.min(1, safeDelta * 5.0); // Smooth 0.2s transition
      
      presets.forEach(p => {
        const target = this.targetExpressions[p] ?? 0;
        let current = this.currentExpressions[p] ?? 0;
        
        current += (target - current) * lerpFactor;
        this.currentExpressions[p] = current;
        this.vrm!.expressionManager!.setValue(p, current);
      });

      // Special case for eyeSquint (blending with blink)
      if (emotionMod.eyeSquint && emotionMod.eyeSquint > 0) {
        const val = emotionMod.eyeSquint;
        if (this.vrm.expressionManager.getExpression('blink')) {
          this.vrm.expressionManager.setValue('blink', Math.max(val, this.vrm.expressionManager.getValue('blink') ?? 0));
        } else {
          this.vrm.expressionManager.setValue('blinkLeft', Math.max(val, this.vrm.expressionManager.getValue('blinkLeft') ?? 0));
          this.vrm.expressionManager.setValue('blinkRight', Math.max(val, this.vrm.expressionManager.getValue('blinkRight') ?? 0));
        }
      }
    }

    // Sub-systems
    this.eye.update(this.vrm, safeDelta);
    this.lip.update(this.vrm, safeDelta);
    this.vrm.update(safeDelta);
  }
}
