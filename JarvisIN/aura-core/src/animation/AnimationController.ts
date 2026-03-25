import * as THREE from 'three';
import { VRM, VRMHumanBoneName, VRMExpressionPresetName } from '@pixiv/three-vrm';
import { EmotionType, PoseType, Vowel, AnimationAPI } from './types';
import { POSE_LIBRARY, ALL_BONE_NAMES } from './poses';
import { getEmotionModifiers } from './emotionModifiers';
import { computeBreathing } from './breathing';
import { EyeController } from './eyeController';
import { LipSyncController } from './lipSync';
import { initializeSpringBones, updateSpringBones } from './springBoneDamper';

// 0.5s crossfade = speed of 2 (1/0.5)
const TRANSITION_SPEED = 2;

// ─── Default "arms down" rotations ──────────────────────────────────────
// VRM bind = T-pose (all zeros). These ensure arms NEVER stay horizontal.
// VRM right arm local axes (normalized):
//   +Z rotation = arm moves FORWARD (toward face)
//   -Z rotation = arm moves BACKWARD
//   +X rotation = arm moves DOWN (toward body / adduction)
//   -X rotation = arm moves UP (abduction above head)
//
// For the LEFT arm, Z is mirrored (+Z = backward, -Z = forward)
// and X is also mirrored.
const ARM_DOWN_DEFAULTS: Record<string, { x: number; y: number; z: number }> = {
  leftUpperArm:  { x: 0, y: 0, z: 1.35 },     // ~77° down from T-pose
  rightUpperArm: { x: 0, y: 0, z: -1.35 },
  leftLowerArm:  { x: -0.15, y: 0, z: 0 },
  rightLowerArm: { x: -0.15, y: 0, z: 0 },
  leftHand:      { x: -0.1, y: 0, z: 0 },
  rightHand:     { x: -0.1, y: 0, z: 0 },
  leftShoulder:  { x: 0, y: 0, z: 0 },
  rightShoulder: { x: 0, y: 0, z: 0 },
};

const ARM_BONE_NAMES = new Set(Object.keys(ARM_DOWN_DEFAULTS));

// ─── Wave override ──────────────────────────────────────────────────────
// VRM RIGHT arm local axes (confirmed by observation):
//   X-axis: +X = adduction (toward body/down), -X = abduction (up/away)
//   Y-axis: +Y = twist outward (supination)  
//   Z-axis: +Z = forward (toward face), -Z = backward
//
// Goal: arm 25° FORWARD + 110° UP from resting (resting = X≈+1.35)
//   Forward: Z = +0.44 (25°)
//   Up: from X=+1.35 (rest), 110° up = X = 1.35 - 1.92 = -0.57
const WAVE_BONES = new Set(['rightShoulder', 'rightUpperArm', 'rightLowerArm', 'rightHand']);

function getWaveOverrideEuler(boneName: string, phase: number): { x: number; y: number; z: number } | null {
  const wave = Math.sin(phase * 5);

  switch (boneName) {
    case 'rightShoulder':
      // Lift shoulder slightly + push forward 15° to clear sleeve
      return { x: -0.1, y: 0, z: 0.26 };

    case 'rightUpperArm':
      // 110° up from rest + 25° forward to clear chest/sleeves
      return { x: -0.57, y: 0, z: 0.44 };

    case 'rightLowerArm':
      // Elbow bent ~90° + wave oscillation ±30°
      return {
        x: -1.57,
        y: wave * 0.52,    // ±30° side-to-side wave on Y (twist axis)
        z: 0,
      };

    case 'rightHand':
      // Open palm, subtle follow-through
      return {
        x: 0.1,
        y: wave * 0.18,
        z: 0.05,
      };

    default:
      return null;
  }
}

function getVRMBone(vrm: VRM, name: string): THREE.Object3D | null {
  return vrm.humanoid?.getNormalizedBoneNode(name as VRMHumanBoneName)
    ?? vrm.humanoid?.getRawBoneNode(name as VRMHumanBoneName)
    ?? null;
}

export class AnimationController {
  private vrm: VRM | null = null;
  
  // State
  private currentPose: PoseType = 'idle';
  private currentEmotion: EmotionType = 'neutral';
  private exertion = 0; // 0-1
  
  // Timing
  private phase = 0;
  private transitionProgress = 1;
  
  // Sub-controllers
  public eyeController = new EyeController();
  public lipSync = new LipSyncController();

  setVRM(vrm: VRM) {
    this.vrm = vrm;
    initializeSpringBones(vrm);
  }

  getAPI(): AnimationAPI {
    return {
      play: (pose: PoseType) => this.setPose(pose),
      setEmotion: (emotion: EmotionType) => this.setEmotion(emotion),
      setExertion: (level: number) => { this.exertion = Math.max(0, Math.min(1, level)); },
      speakVowel: (vowel: Vowel) => this.lipSync.setVowel(vowel),
      setLookAt: (x: number, y: number) => this.eyeController.setLookAt(x, y),
      setBlink: (v: number) => this.eyeController.setBlinkOverride(v),
      setMouthOpen: (v: number) => {
        if (this.vrm?.expressionManager) {
          this.vrm.expressionManager.setValue('aa', v);
        }
      },
    };
  }

  setPose(pose: PoseType) {
    if (pose === this.currentPose) return;
    this.transitionProgress = 0;
    this.currentPose = pose;
    
    // Auto-set exertion based on pose
    if (pose === 'run') this.exertion = 0.7;
    else if (pose === 'walk') this.exertion = 0.3;
    else if (pose === 'dance') this.exertion = 0.5;
    else if (pose === 'jump') this.exertion = 0.8;
    else if (pose === 'shiver') this.exertion = 0.4;
    else if (pose === 'cry') this.exertion = 0.3;
    else this.exertion = 0;

    // Auto-set matching emotions for certain poses
    if (pose === 'think') this.setEmotion('thinking');
    else if (pose === 'cry') this.setEmotion('sad_severe');
    else if (pose === 'shiver') this.setEmotion('fever');
    else if (pose === 'hug_self') this.setEmotion('cold');
    else if (pose === 'gasp') this.setEmotion('surprised');
    else if (pose === 'peace_sign') this.setEmotion('happy');
  }

  setEmotion(emotion: EmotionType) {
    this.currentEmotion = emotion;
    if (!this.vrm?.expressionManager) return;
    
    const presets: VRMExpressionPresetName[] = ['happy', 'angry', 'sad', 'surprised', 'relaxed', 'neutral'];
    presets.forEach(p => this.vrm!.expressionManager!.setValue(p, 0));
    
    // Map extended emotions to VRM presets
    const emotionMap: Record<string, VRMExpressionPresetName | null> = {
      neutral: null,
      happy: 'happy',
      angry: 'angry',
      sad: 'sad',
      sad_mild: 'sad',
      sad_moderate: 'sad',
      sad_severe: 'sad',
      surprised: 'surprised',
      relaxed: 'relaxed',
      thinking: 'neutral',
      serious: 'neutral',
      fever: 'neutral',
      cold: 'neutral',
    };
    
    const preset = emotionMap[emotion];
    if (preset && preset !== 'neutral') {
      this.vrm.expressionManager.setValue(preset, 1);
    }

    // Fever/cold: half-closed eyes via blink blendshape
    const mod = getEmotionModifiers(emotion);
    if (mod.eyeSquint && mod.eyeSquint > 0) {
      this.vrm.expressionManager.setValue('blink', mod.eyeSquint);
    }
  }

  update(delta: number) {
    if (!this.vrm) return;

    this.phase += delta;

    // Update transition
    const isTransitioning = this.transitionProgress < 1;
    if (isTransitioning) {
      this.transitionProgress = Math.min(1, this.transitionProgress + delta * TRANSITION_SPEED);
    }

    // Spring bone physics: dampening during transitions + idle sway
    const isIdleOrStatic = ['idle', 'sit', 'seiza', 'agura', 'think', 'hug_self'].includes(this.currentPose);
    updateSpringBones(this.vrm, delta, isTransitioning, isIdleOrStatic);

    // Get emotion modifiers
    const emotionMod = getEmotionModifiers(this.currentEmotion);

    // Compute breathing additive layer
    const breathing = computeBreathing({
      phase: this.phase,
      exertion: this.exertion,
      emotionScale: emotionMod.breatheScale,
    });

    // Get current pose definition
    const poseDef = POSE_LIBRARY[this.currentPose];

    // Apply per-bone
    ALL_BONE_NAMES.forEach(boneName => {
      const node = getVRMBone(this.vrm!, boneName);
      if (!node) return;

      // Base pose rotation — use pose definition if available,
      // otherwise use arm-down defaults for arm bones to NEVER fall back to T-pose
      const poseFn = poseDef[boneName];
      let euler: { x: number; y: number; z: number };
      
      if (poseFn) {
        euler = poseFn(this.phase);
      } else if (ARM_BONE_NAMES.has(boneName)) {
        // No pose definition for this arm bone → use natural hanging position
        euler = { ...ARM_DOWN_DEFAULTS[boneName] };
      } else {
        euler = { x: 0, y: 0, z: 0 };
      }

      // Wave override: completely replaces euler for wave bones (full weight)
      const isWaveBone = this.currentPose === 'wave' && WAVE_BONES.has(boneName);
      if (isWaveBone) {
        const waveEuler = getWaveOverrideEuler(boneName, this.phase);
        if (waveEuler) euler = waveEuler;
      }

      // Add emotion modifiers (only to relevant non-wave bones)
      let ex = euler.x, ey = euler.y, ez = euler.z;
      if (!isWaveBone && boneName === 'spine') {
        ex += emotionMod.spineForwardLean;
      }
      if (!isWaveBone && boneName === 'head') {
        ex += emotionMod.headTilt;
      }
      if (!isWaveBone && (boneName === 'leftShoulder' || boneName === 'rightShoulder')) {
        ex += emotionMod.shoulderHeightOffset;
      }

      // Add breathing (additive layer) only for non-wave bones
      const breathKey = boneName as keyof typeof breathing;
      if (!isWaveBone && breathKey in breathing) {
        const b = breathing[breathKey] as { x: number; y?: number; z: number };
        ex += b.x;
        if ('y' in b && b.y !== undefined) ey += b.y;
        ez += b.z;
      }

      const targetQ = new THREE.Quaternion().setFromEuler(new THREE.Euler(ex, ey, ez));

      // Slerp: 0.5s crossfade for all transitions.
      // Wave bones blend faster for responsiveness.
      const slerpFactor = isWaveBone
        ? 0.3
        : isTransitioning
          ? Math.min(1, delta * TRANSITION_SPEED * 2)
          : 0.12;  // gentle idle micro-movements
      node.quaternion.slerp(targetQ, slerpFactor);
    });

    // Eye tracking + blinking
    this.eyeController.update(this.vrm, delta);

    // Lip sync
    this.lipSync.update(this.vrm, delta);

    // VRM internal update
    this.vrm.update(delta);
  }

  getCurrentPose(): PoseType { return this.currentPose; }
  getCurrentEmotion(): EmotionType { return this.currentEmotion; }
}
