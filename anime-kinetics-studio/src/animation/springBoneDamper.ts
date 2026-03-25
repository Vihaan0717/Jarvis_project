import * as THREE from 'three';
import { VRM } from '@pixiv/three-vrm';

/**
 * Spring Bone Physics Manager for VRM hair, clothing, and accessories.
 * 
 * Handles:
 * - Physics parameter tuning (stiffness, gravity, drag)
 * - Sphere collider setup on head/shoulders to prevent clipping
 * - Procedural idle sway (low-frequency sine wind effect)
 * - Transition dampening to prevent jitter during pose changes
 */

// ─── Target physics values ──────────────────────────────────────────────
const PHYSICS_DEFAULTS = {
  stiffness: 1.0,       // mid-range: hair returns to shape but isn't rigid
  gravityPower: 0.05,   // slight downward pull for realistic weight
  dragForce: 0.5,       // prevents jittery shaking after movement
};

const TRANSITION_PHYSICS = {
  stiffness: 3.0,       // stiffer during transitions to prevent wild swings
  dragForce: 0.85,      // high drag to dampen overshoot
};

// ─── Idle sway parameters ───────────────────────────────────────────────
const SWAY = {
  frequency: 0.4,       // very slow oscillation (Hz)
  amplitude: 0.0008,    // subtle — just enough to feel alive
  secondaryFreq: 0.7,   // secondary harmonic for organic feel
  secondaryAmp: 0.0004,
};

let initialized = false;
let swayPhase = 0;

/**
 * One-time setup: configure spring bone physics parameters and add colliders.
 * Called once after VRM load.
 */
export function initializeSpringBones(vrm: VRM) {
  const manager = (vrm as any).springBoneManager;
  if (!manager) {
    console.log('[SpringBone] No spring bone manager found on VRM');
    return;
  }

  // ─── Tune all joints ────────────────────────────────────────────────
  const joints = manager.joints ?? manager.springBones ?? [];
  console.log(`[SpringBone] Found ${joints.length} spring bone joints`);

  for (const joint of joints) {
    if (!joint) continue;

    if (joint.settings) {
      // VRM 1.x API
      joint.settings.stiffness = PHYSICS_DEFAULTS.stiffness;
      joint.settings.gravityPower = PHYSICS_DEFAULTS.gravityPower;
      joint.settings.gravityDir = new THREE.Vector3(0, -1, 0);
      joint.settings.dragForce = PHYSICS_DEFAULTS.dragForce;
    } else {
      // VRM 0.x direct properties
      if ('stiffnessForce' in joint) joint.stiffnessForce = PHYSICS_DEFAULTS.stiffness;
      if ('gravityPower' in joint) joint.gravityPower = PHYSICS_DEFAULTS.gravityPower;
      if ('gravityDir' in joint) joint.gravityDir = new THREE.Vector3(0, -1, 0);
      if ('dragForce' in joint) joint.dragForce = PHYSICS_DEFAULTS.dragForce;
    }
  }

  // ─── Add sphere colliders to head & shoulders ───────────────────────
  setupColliders(vrm, manager);

  initialized = true;
  console.log('[SpringBone] Initialization complete');
}

/**
 * Add sphere colliders on head and shoulder bones to prevent hair 
 * clipping through the face/chest during Wave, Seiza, etc.
 */
function setupColliders(vrm: VRM, manager: any) {
  const humanoid = vrm.humanoid;
  if (!humanoid) return;

  const colliderGroups = manager.colliderGroups ?? [];

  // Helper: find bone node
  const getBone = (name: string): THREE.Object3D | null =>
    humanoid.getNormalizedBoneNode(name as any) ??
    humanoid.getRawBoneNode(name as any) ??
    null;

  const headBone = getBone('head');
  const leftShoulderBone = getBone('leftShoulder') ?? getBone('leftUpperArm');
  const rightShoulderBone = getBone('rightShoulder') ?? getBone('rightUpperArm');
  const chestBone = getBone('chest') ?? getBone('upperChest');

  // Create collider shapes if the VRM API supports adding them
  const collidersToAdd: Array<{ bone: THREE.Object3D; radius: number; offset: THREE.Vector3 }> = [];

  if (headBone) {
    collidersToAdd.push(
      { bone: headBone, radius: 0.1, offset: new THREE.Vector3(0, 0.05, 0.02) },   // face front
      { bone: headBone, radius: 0.08, offset: new THREE.Vector3(0, 0.08, -0.03) },  // back of head
    );
  }
  if (leftShoulderBone) {
    collidersToAdd.push({ bone: leftShoulderBone, radius: 0.06, offset: new THREE.Vector3(0, 0, 0) });
  }
  if (rightShoulderBone) {
    collidersToAdd.push({ bone: rightShoulderBone, radius: 0.06, offset: new THREE.Vector3(0, 0, 0) });
  }
  if (chestBone) {
    collidersToAdd.push({ bone: chestBone, radius: 0.12, offset: new THREE.Vector3(0, 0.05, 0.05) });
  }

  // Try to register colliders with the spring bone manager
  // VRM 1.x uses colliderGroups with shape arrays
  if (manager.colliders && Array.isArray(manager.colliders)) {
    for (const { bone, radius, offset } of collidersToAdd) {
      try {
        const collider = {
          shape: { radius, offset },
          bone,
        };
        manager.colliders.push(collider);
      } catch (e) {
        // Collider API may vary by VRM version; silently skip
      }
    }
    console.log(`[SpringBone] Added ${collidersToAdd.length} colliders`);
  } else {
    console.log('[SpringBone] Collider API not available, skipping collider setup');
  }
}

/**
 * Per-frame spring bone update.
 * - Applies transition dampening when poses are blending
 * - Adds subtle procedural sway during idle/neutral states
 * 
 * Called every frame from AnimationController.update()
 */
export function updateSpringBones(
  vrm: VRM,
  delta: number,
  transitionActive: boolean,
  isIdleOrStatic: boolean,
) {
  const manager = (vrm as any).springBoneManager;
  if (!manager) return;

  // Auto-init if not yet done
  if (!initialized) {
    initializeSpringBones(vrm);
  }

  const joints = manager.joints ?? manager.springBones ?? [];

  // ─── Transition dampening ──────────────────────────────────────────
  for (const joint of joints) {
    if (!joint) continue;

    if (transitionActive) {
      // Temporarily stiffen to prevent wild swings
      if (joint.settings) {
        joint.settings.stiffness = lerp(joint.settings.stiffness ?? 1, TRANSITION_PHYSICS.stiffness, delta * 3);
        joint.settings.dragForce = lerp(joint.settings.dragForce ?? 0.5, TRANSITION_PHYSICS.dragForce, delta * 3);
      } else {
        if ('stiffnessForce' in joint) {
          joint.stiffnessForce = lerp(joint.stiffnessForce ?? 1, TRANSITION_PHYSICS.stiffness, delta * 3);
        }
        if ('dragForce' in joint) {
          joint.dragForce = lerp(joint.dragForce ?? 0.5, TRANSITION_PHYSICS.dragForce, delta * 3);
        }
      }
    } else {
      // Smoothly restore to defaults
      if (joint.settings) {
        joint.settings.stiffness = lerp(joint.settings.stiffness ?? 1, PHYSICS_DEFAULTS.stiffness, delta * 2);
        joint.settings.dragForce = lerp(joint.settings.dragForce ?? 0.5, PHYSICS_DEFAULTS.dragForce, delta * 2);
      } else {
        if ('stiffnessForce' in joint) {
          joint.stiffnessForce = lerp(joint.stiffnessForce ?? 1, PHYSICS_DEFAULTS.stiffness, delta * 2);
        }
        if ('dragForce' in joint) {
          joint.dragForce = lerp(joint.dragForce ?? 0.5, PHYSICS_DEFAULTS.dragForce, delta * 2);
        }
      }
    }
  }

  // ─── Idle sway: subtle wind-like force on hair ─────────────────────
  if (isIdleOrStatic && !transitionActive) {
    swayPhase += delta;
    applyIdleSway(vrm, manager, swayPhase);
  }
}

/**
 * Apply a subtle procedural sway to spring bones during idle.
 * Uses overlapping sine waves for organic movement.
 */
function applyIdleSway(vrm: VRM, manager: any, phase: number) {
  // Compute a world-space "wind" direction that slowly shifts
  const windX = Math.sin(phase * SWAY.frequency * Math.PI * 2) * SWAY.amplitude
    + Math.sin(phase * SWAY.secondaryFreq * Math.PI * 2 + 1.3) * SWAY.secondaryAmp;
  const windZ = Math.cos(phase * SWAY.frequency * Math.PI * 2 * 0.7 + 0.5) * SWAY.amplitude * 0.6;

  // Apply as a slight gravity direction offset to all joints
  const joints = manager.joints ?? manager.springBones ?? [];
  for (const joint of joints) {
    if (!joint) continue;

    if (joint.settings && joint.settings.gravityDir) {
      // Nudge gravity direction slightly to simulate breeze
      joint.settings.gravityDir.set(windX, -PHYSICS_DEFAULTS.gravityPower, windZ).normalize();
    } else if ('gravityDir' in joint && joint.gravityDir) {
      joint.gravityDir.set(windX, -PHYSICS_DEFAULTS.gravityPower, windZ).normalize();
    }
  }
}

function lerp(a: number, b: number, t: number): number {
  return a + (b - a) * Math.min(t, 1);
}

// ─── Legacy export for backward compatibility ───────────────────────────
export function applySpringBoneDampening(vrm: VRM, transitionActive: boolean) {
  updateSpringBones(vrm, 1 / 60, transitionActive, false);
}
