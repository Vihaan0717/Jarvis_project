import { PoseDefinition, PoseType } from './types';

// Each pose returns Euler angles (x, y, z) for each bone as a function of phase
// ALL rotations are in LOCAL SPACE relative to the parent bone's rest orientation.
// VRM models have a T-pose as bind pose, so we must explicitly offset arms downward.

const staticPose = (x = 0, y = 0, z = 0) => (_phase: number) => ({ x, y, z });

// ─── Natural arm rest offsets ───────────────────────────────────────────
// VRM bind pose is T-pose. To hang arms at sides:
// - Upper arms rotate ~75° on Z toward body
// - Lower arms bend slightly forward
const ARM_REST = {
  leftUpperArm: staticPose(0.2, 0, 1.4),        // ~80° inward from T-pose
  rightUpperArm: staticPose(0.2, 0, -1.4),
  leftLowerArm: staticPose(-0.25, 0, 0),         // natural elbow bend
  rightLowerArm: staticPose(-0.25, 0, 0),
  leftShoulder: staticPose(0, 0, 0),
  rightShoulder: staticPose(0, 0, 0),
};

// ─── IDLE ────────────────────────────────────────────────────────────────
// VRM axes: for upper arms, Z = forward/back, X = up/down (adduction)
// +Z = forward (left arm: -Z = forward), +X = down toward body
const idlePose: PoseDefinition = {
  spine: (p) => ({ x: Math.sin(p * 1.5) * 0.015 + Math.sin(p * 0.8) * 0.02, y: 0, z: 0 }),
  chest: (p) => ({ x: Math.sin(p * 1.5) * 0.015 * 1.5, y: 0, z: Math.sin(p * 1.5) * 0.03 * 0.3 }),
  upperChest: (p) => ({ x: Math.sin(p * 1.5) * 0.015 * 1.2, y: 0, z: 0 }),
  head: (p) => ({ x: Math.sin(p * 0.5) * 0.015, y: Math.sin(p * 0.3) * 0.01, z: 0 }),
  leftShoulder: staticPose(0, 0, 0),
  rightShoulder: staticPose(0, 0, 0),
  // Arms at sides: ~77° via Z rotation (mirrored for L/R)
  leftUpperArm: (p) => ({ x: 0, y: 0, z: 1.35 + Math.sin(p * 1.5) * 0.015 }),
  rightUpperArm: (p) => ({ x: 0, y: 0, z: -1.35 - Math.sin(p * 1.5) * 0.015 }),
  leftLowerArm: staticPose(-0.15, 0, 0),
  rightLowerArm: staticPose(-0.15, 0, 0),
  leftHand: staticPose(-0.1, 0, 0),
  rightHand: staticPose(-0.1, 0, 0),
};

// ─── WALK ────────────────────────────────────────────────────────────────
const walkPose: PoseDefinition = {
  leftUpperLeg: (p) => ({ x: Math.sin(p * 4) * 0.4, y: 0, z: 0 }),
  rightUpperLeg: (p) => ({ x: -Math.sin(p * 4) * 0.4, y: 0, z: 0 }),
  leftLowerLeg: (p) => ({ x: -Math.max(0, -Math.sin(p * 4)) * 0.5, y: 0, z: 0 }),
  rightLowerLeg: (p) => ({ x: -Math.max(0, Math.sin(p * 4)) * 0.5, y: 0, z: 0 }),
  leftShoulder: staticPose(0, 0, 0),
  rightShoulder: staticPose(0, 0, 0),
  // Arms swing naturally from a lowered position
  leftUpperArm: (p) => ({ x: -Math.sin(p * 4) * 0.15 + 0.1, y: 0, z: 1.0 }),
  rightUpperArm: (p) => ({ x: Math.sin(p * 4) * 0.15 + 0.1, y: 0, z: -1.0 }),
  leftLowerArm: staticPose(-0.2, 0, 0),
  rightLowerArm: staticPose(-0.2, 0, 0),
  spine: staticPose(-0.05, 0, 0),
  chest: staticPose(-0.03, 0, 0),
  head: (p) => ({ x: Math.sin(p * 8) * 0.03, y: Math.sin(p * 4) * 0.05, z: 0 }),
};

// ─── RUN ─────────────────────────────────────────────────────────────────
const runPose: PoseDefinition = {
  leftUpperLeg: (p) => ({ x: Math.sin(p * 6) * 0.65, y: 0, z: 0 }),
  rightUpperLeg: (p) => ({ x: -Math.sin(p * 6) * 0.65, y: 0, z: 0 }),
  leftLowerLeg: (p) => ({ x: -Math.max(0, -Math.sin(p * 6)) * 1.0 - 0.3, y: 0, z: 0 }),
  rightLowerLeg: (p) => ({ x: -Math.max(0, Math.sin(p * 6)) * 1.0 - 0.3, y: 0, z: 0 }),
  leftShoulder: staticPose(0, 0, 0),
  rightShoulder: staticPose(0, 0, 0),
  leftUpperArm: (p) => ({ x: -Math.sin(p * 6) * 0.5, y: 0, z: 0.8 }),
  rightUpperArm: (p) => ({ x: Math.sin(p * 6) * 0.5, y: 0, z: -0.8 }),
  leftLowerArm: (p) => ({ x: -Math.abs(Math.sin(p * 6)) * 0.6 - 0.4, y: 0, z: 0 }),
  rightLowerArm: (p) => ({ x: -Math.abs(Math.sin(p * 6 + Math.PI)) * 0.6 - 0.4, y: 0, z: 0 }),
  spine: (p) => ({ x: -0.1 + Math.sin(p * 12) * 0.02, y: 0, z: 0 }),
  chest: staticPose(-0.06, 0, 0),
  head: (p) => ({ x: Math.sin(p * 12) * 0.04, y: Math.sin(p * 6) * 0.03, z: 0 }),
  hips: (p) => ({ x: 0, y: Math.sin(p * 6) * 0.05, z: 0 }),
};

// ─── JUMP ────────────────────────────────────────────────────────────────
const jumpPose: PoseDefinition = {
  hips: (p) => {
    const cycle = (p * 0.8) % 1;
    if (cycle < 0.3) return { x: -0.15, y: 0, z: 0 };
    if (cycle < 0.7) return { x: 0.05, y: 0, z: 0 };
    return { x: -0.1, y: 0, z: 0 };
  },
  leftUpperLeg: (p) => {
    const cycle = (p * 0.8) % 1;
    if (cycle < 0.3) return { x: 0.5, y: 0, z: 0 };
    if (cycle < 0.7) return { x: -0.3, y: 0, z: 0 };
    return { x: 0.2, y: 0, z: 0 };
  },
  rightUpperLeg: (p) => {
    const cycle = (p * 0.8) % 1;
    if (cycle < 0.3) return { x: 0.5, y: 0, z: 0 };
    if (cycle < 0.7) return { x: -0.3, y: 0, z: 0 };
    return { x: 0.2, y: 0, z: 0 };
  },
  leftLowerLeg: (p) => {
    const cycle = (p * 0.8) % 1;
    if (cycle < 0.3) return { x: -0.8, y: 0, z: 0 };
    if (cycle < 0.7) return { x: -0.1, y: 0, z: 0 };
    return { x: -0.4, y: 0, z: 0 };
  },
  rightLowerLeg: (p) => {
    const cycle = (p * 0.8) % 1;
    if (cycle < 0.3) return { x: -0.8, y: 0, z: 0 };
    if (cycle < 0.7) return { x: -0.1, y: 0, z: 0 };
    return { x: -0.4, y: 0, z: 0 };
  },
  // Arms raise during jump
  leftUpperArm: (p) => {
    const cycle = (p * 0.8) % 1;
    return cycle < 0.7 ? { x: -0.5, y: 0, z: 0.6 } : { x: 0.1, y: 0, z: 1.0 };
  },
  rightUpperArm: (p) => {
    const cycle = (p * 0.8) % 1;
    return cycle < 0.7 ? { x: -0.5, y: 0, z: -0.6 } : { x: 0.1, y: 0, z: -1.0 };
  },
  leftLowerArm: staticPose(-0.3, 0, 0),
  rightLowerArm: staticPose(-0.3, 0, 0),
  spine: staticPose(-0.05, 0, 0),
  chest: staticPose(-0.03, 0, 0),
};

// ─── SIT (Chair) ─────────────────────────────────────────────────────────
const sitPose: PoseDefinition = {
  hips: staticPose(-0.08, 0, 0),
  leftUpperLeg: staticPose(1.5, 0, 0.06),    // ~86° forward
  rightUpperLeg: staticPose(1.5, 0, -0.06),
  leftLowerLeg: staticPose(-1.5, 0, 0),      // fold back ~86°
  rightLowerLeg: staticPose(-1.5, 0, 0),
  leftFoot: staticPose(0.1, 0, 0.04),
  rightFoot: staticPose(0.1, 0, -0.04),
  spine: staticPose(0.08, 0, 0),
  chest: staticPose(0.04, 0, 0),
  leftShoulder: staticPose(0, 0, 0),
  rightShoulder: staticPose(0, 0, 0),
  // Hands resting on thighs
  leftUpperArm: staticPose(0.3, 0.2, 0.8),
  rightUpperArm: staticPose(0.3, -0.2, -0.8),
  leftLowerArm: staticPose(-0.8, 0.15, 0),
  rightLowerArm: staticPose(-0.8, -0.15, 0),
};

// ─── SEIZA (正座) - Japanese formal kneeling ─────────────────────────────
// Knees forward, shins flat, hips 0.25 units above floor
const seizaPose: PoseDefinition = {
  hips: staticPose(-0.25, 0, 0),               // lowered toward floor
  leftUpperLeg: staticPose(1.8, 0, 0.04),      // thighs forward ~103°
  rightUpperLeg: staticPose(1.8, 0, -0.04),
  leftLowerLeg: staticPose(-2.6, 0, 0),        // fold back ~149° (shins flat)
  rightLowerLeg: staticPose(-2.6, 0, 0),
  leftFoot: staticPose(-0.5, 0, 0.06),         // toes pointing back, flat
  rightFoot: staticPose(-0.5, 0, -0.06),
  spine: staticPose(0.08, 0, 0),               // upright
  chest: staticPose(0.04, 0, 0),
  upperChest: staticPose(0.02, 0, 0),
  head: staticPose(-0.05, 0, 0),
  leftShoulder: staticPose(0, 0, 0),
  rightShoulder: staticPose(0, 0, 0),
  // Hands resting on thighs (corrected axes)
  leftUpperArm: staticPose(0.15, 0, 0.9),
  rightUpperArm: staticPose(0.15, 0, -0.9),
  leftLowerArm: staticPose(-0.6, 0.1, 0),
  rightLowerArm: staticPose(-0.6, -0.1, 0),
  leftHand: staticPose(-0.2, 0, 0),
  rightHand: staticPose(-0.2, 0, 0),
};

// ─── AGURA (胡座) - Cross-legged sitting ─────────────────────────────────
const aguraPose: PoseDefinition = {
  hips: staticPose(-0.12, 0, 0),
  leftUpperLeg: staticPose(1.4, -0.5, 0.6),    // thigh forward + rotated out
  rightUpperLeg: staticPose(1.4, 0.5, -0.6),
  leftLowerLeg: staticPose(-2.2, 0.3, 0),      // folded back tightly
  rightLowerLeg: staticPose(-2.2, -0.3, 0),
  leftFoot: staticPose(-0.2, 0, 0.15),
  rightFoot: staticPose(-0.2, 0, -0.15),
  spine: staticPose(0.05, 0, 0),
  chest: staticPose(0.03, 0, 0),
  leftShoulder: staticPose(0, 0, 0),
  rightShoulder: staticPose(0, 0, 0),
  leftUpperArm: staticPose(0.2, 0.1, 0.9),
  rightUpperArm: staticPose(0.2, -0.1, -0.9),
  leftLowerArm: staticPose(-0.7, 0.2, 0),
  rightLowerArm: staticPose(-0.7, -0.2, 0),
};

// ─── DANCE ───────────────────────────────────────────────────────────────
const dancePose: PoseDefinition = {
  hips: (p) => ({ x: 0, y: Math.sin(p * 3) * 0.2, z: 0 }),
  spine: (p) => ({ x: Math.sin(p * 6) * 0.05, y: -Math.sin(p * 3) * 0.1, z: 0 }),
  chest: (p) => ({ x: 0, y: Math.sin(p * 3) * 0.15, z: 0 }),
  head: (p) => ({ x: Math.sin(p * 6) * 0.08, y: Math.sin(p * 3) * 0.12, z: 0 }),
  leftShoulder: staticPose(0, 0, 0),
  rightShoulder: staticPose(0, 0, 0),
  leftUpperArm: (p) => ({ x: Math.sin(p * 3) * 0.6, y: 0, z: 0.6 }),
  rightUpperArm: (p) => ({ x: Math.sin(p * 3 + Math.PI) * 0.6, y: 0, z: -0.6 }),
  leftLowerArm: (p) => ({ x: -Math.abs(Math.sin(p * 3)) * 0.8 - 0.3, y: 0, z: 0 }),
  rightLowerArm: (p) => ({ x: -Math.abs(Math.sin(p * 3 + Math.PI)) * 0.8 - 0.3, y: 0, z: 0 }),
  leftUpperLeg: (p) => ({ x: Math.sin(p * 6) * 0.25, y: 0, z: 0 }),
  rightUpperLeg: (p) => ({ x: -Math.sin(p * 6) * 0.25, y: 0, z: 0 }),
  leftLowerLeg: (p) => ({ x: -Math.max(0, Math.sin(p * 6)) * 0.4, y: 0, z: 0 }),
  rightLowerLeg: (p) => ({ x: -Math.max(0, -Math.sin(p * 6)) * 0.4, y: 0, z: 0 }),
};

// ─── WAVE ────────────────────────────────────────────────────────────────
// Right arm: upper arm lifts ~90° from rest (Z goes from -1.4 rest to ~-0.2 raised)
// Plus forward tilt to clear the head. Forearm oscillates in local Y.
const wavePose: PoseDefinition = {
  // Left arm at natural rest (matches idle)
  leftUpperArm: staticPose(0.2, 0, 1.4),
  leftLowerArm: staticPose(-0.25, 0, 0),
  leftHand: staticPose(-0.1, 0, 0),
  leftShoulder: staticPose(0, 0, 0),
  rightShoulder: staticPose(0, 0, 0),
  // Upper arm: Z=-0.3 lifts well above horizontal, X=-0.4 tilts forward to avoid head
  rightUpperArm: staticPose(-0.4, 0.2, -0.3),
  // Forearm bent up with side-to-side wave
  rightLowerArm: (p) => ({
    x: -1.2,                             // bent ~70° at elbow
    y: Math.sin(p * 5) * 0.4,            // side-to-side wave
    z: 0,
  }),
  // Hand open, fingers relaxed
  rightHand: (p) => ({
    x: 0.1,                              // slight dorsiflexion (open palm)
    y: Math.sin(p * 5) * 0.15,           // subtle follow-through
    z: 0.05,
  }),
};

// ─── BOW ─────────────────────────────────────────────────────────────────
const bowPose: PoseDefinition = {
  spine: staticPose(-0.5, 0, 0),
  chest: staticPose(-0.3, 0, 0),
  head: staticPose(-0.2, 0, 0),
  leftShoulder: staticPose(0, 0, 0),
  rightShoulder: staticPose(0, 0, 0),
  leftUpperArm: staticPose(0.1, 0, 1.1),
  rightUpperArm: staticPose(0.1, 0, -1.1),
  leftLowerArm: staticPose(-0.1, 0, 0),
  rightLowerArm: staticPose(-0.1, 0, 0),
};

// ─── THINK ──────────────────────────────────────────────────────────────
// Weight on one leg, right hand to chin, head tilted ~15° to side + looking up
const thinkPose: PoseDefinition = {
  hips: staticPose(0, 0.06, 0),                   // weight shift
  leftUpperLeg: staticPose(0.05, 0, 0),
  rightUpperLeg: staticPose(-0.05, 0, 0.08),      // relaxed leg
  spine: staticPose(0.03, 0, 0),
  chest: staticPose(0.02, 0, 0),
  head: (p) => ({
    x: -0.08 + Math.sin(p * 0.3) * 0.02,          // slight look up
    y: 0,
    z: 0.26,                                        // ~15° side tilt
  }),
  // Left arm at rest
  leftUpperArm: staticPose(0.2, 0, 1.35),
  leftLowerArm: staticPose(-0.25, 0, 0),
  // Right arm: hand to chin (IK-like positioning via bone chain)
  rightShoulder: staticPose(0, 0, 0),
  rightUpperArm: staticPose(-0.8, 0.3, -0.6),     // arm forward and up
  rightLowerArm: staticPose(-2.0, 0, 0),           // elbow bent sharply
  rightHand: (p) => ({
    x: -0.3 + Math.sin(p * 0.5) * 0.03,            // subtle tap
    y: 0,
    z: 0.1,
  }),
};

// ─── CRY (Severe sadness) ───────────────────────────────────────────────
// Covers eyes with both hands, sobbing chest shudder
const cryPose: PoseDefinition = {
  spine: (p) => ({
    x: 0.15 + Math.sin(p * 8) * 0.03,              // sobbing shudder
    y: 0,
    z: 0,
  }),
  chest: (p) => ({
    x: 0.1 + Math.sin(p * 8 + 0.5) * 0.025,        // chest heave
    y: 0,
    z: 0,
  }),
  head: staticPose(-0.4, 0, 0),                     // looking down
  // Both hands covering face
  leftShoulder: staticPose(0, 0, 0),
  rightShoulder: staticPose(0, 0, 0),
  leftUpperArm: staticPose(-1.2, 0.4, 0.5),
  rightUpperArm: staticPose(-1.2, -0.4, -0.5),
  leftLowerArm: staticPose(-1.8, 0.2, 0),
  rightLowerArm: staticPose(-1.8, -0.2, 0),
  leftHand: staticPose(-0.4, 0, 0.1),
  rightHand: staticPose(-0.4, 0, -0.1),
};

// ─── SHIVER (Fever) ─────────────────────────────────────────────────────
// Procedural high-frequency jitter across skeleton
const shiverPose: PoseDefinition = {
  spine: (p) => ({
    x: Math.sin(p * 18) * 0.015,
    y: Math.sin(p * 22) * 0.01,
    z: Math.sin(p * 15) * 0.012,
  }),
  chest: (p) => ({
    x: Math.sin(p * 20) * 0.012,
    y: 0,
    z: Math.sin(p * 17) * 0.008,
  }),
  head: (p) => ({
    x: -0.08 + Math.sin(p * 25) * 0.015,
    y: Math.sin(p * 19) * 0.01,
    z: Math.sin(p * 23) * 0.008,
  }),
  leftUpperArm: (p) => ({
    x: 0.15 + Math.sin(p * 20) * 0.02,
    y: 0,
    z: 1.2 + Math.sin(p * 22) * 0.015,
  }),
  rightUpperArm: (p) => ({
    x: 0.15 + Math.sin(p * 21) * 0.02,
    y: 0,
    z: -1.2 + Math.sin(p * 23) * 0.015,
  }),
  leftLowerArm: (p) => ({
    x: -0.3 + Math.sin(p * 24) * 0.015,
    y: 0,
    z: 0,
  }),
  rightLowerArm: (p) => ({
    x: -0.3 + Math.sin(p * 26) * 0.015,
    y: 0,
    z: 0,
  }),
  hips: (p) => ({
    x: Math.sin(p * 16) * 0.008,
    y: Math.sin(p * 14) * 0.006,
    z: 0,
  }),
};

// ─── HUG SELF (Cold) ────────────────────────────────────────────────────
// Arms crossed over chest, body hunched
const hugSelfPose: PoseDefinition = {
  spine: staticPose(0.12, 0, 0),
  chest: staticPose(0.08, 0, 0),
  head: staticPose(-0.1, 0, 0),
  leftShoulder: staticPose(0.05, 0, 0.1),
  rightShoulder: staticPose(0.05, 0, -0.1),
  // Arms crossed: each hand grips opposite upper arm
  leftUpperArm: staticPose(-0.6, 0.5, 0.9),
  rightUpperArm: staticPose(-0.6, -0.5, -0.9),
  leftLowerArm: staticPose(-1.6, 0.3, 0),
  rightLowerArm: staticPose(-1.6, -0.3, 0),
  leftHand: staticPose(-0.2, 0, 0),
  rightHand: staticPose(-0.2, 0, 0),
};

// ─── GASP (Easter egg) ──────────────────────────────────────────────────
// Both hands cover mouth, eyes wide
const gaspPose: PoseDefinition = {
  spine: staticPose(-0.05, 0, 0),
  head: staticPose(0.05, 0, 0),                     // slight look up
  leftShoulder: staticPose(0, 0, 0),
  rightShoulder: staticPose(0, 0, 0),
  leftUpperArm: staticPose(-1.0, 0.3, 0.6),
  rightUpperArm: staticPose(-1.0, -0.3, -0.6),
  leftLowerArm: staticPose(-1.6, 0.15, 0),
  rightLowerArm: staticPose(-1.6, -0.15, 0),
  leftHand: staticPose(-0.3, 0, 0.05),
  rightHand: staticPose(-0.3, 0, -0.05),
};

// ─── PEACE SIGN (Victory, Easter egg) ───────────────────────────────────
// Right hand peace sign near face, slight head tilt + wink handled by emotion
const peaceSignPose: PoseDefinition = {
  head: staticPose(0.05, 0, 0.15),                  // cute head tilt
  leftUpperArm: staticPose(0.2, 0, 1.35),           // left at rest
  leftLowerArm: staticPose(-0.25, 0, 0),
  rightShoulder: staticPose(0, 0, 0),
  // Right arm: peace sign near face
  rightUpperArm: staticPose(-0.9, 0.2, -0.5),
  rightLowerArm: staticPose(-1.8, -0.1, 0),
  rightHand: staticPose(-0.1, 0, 0.15),              // slight angle for ✌️
};

// ── Peek-a-boo pose: duck down, hide face, then pop up surprised ──────
// Phase-driven: 0→2s duck & hide, 2→3s pop up, 3→5s surprise hold, then loop
const peekabooPose: PoseDefinition = {
  hips: (p: number) => {
    const cycle = p % 5;
    // Duck down during hide phase, pop back up for surprise
    if (cycle < 2) {
      const t = cycle / 2; // 0→1
      return { x: 0, y: -0.4 * t, z: 0 }; // sink down
    } else if (cycle < 3) {
      const t = (cycle - 2); // 0→1
      return { x: 0, y: -0.4 + 0.5 * t, z: 0 }; // pop up above start
    } else if (cycle < 4) {
      const t = (cycle - 3);
      return { x: 0, y: 0.1 * (1 - t), z: 0 }; // settle back
    }
    return { x: 0, y: 0, z: 0 };
  },
  spine: (p: number) => {
    const cycle = p % 5;
    if (cycle < 2) {
      const t = cycle / 2;
      return { x: 0.4 * t, y: 0, z: 0 }; // lean forward to hide
    } else if (cycle < 3) {
      return { x: 0.4 - 0.6 * (cycle - 2), y: 0, z: 0 }; // snap back upright
    } else if (cycle < 4) {
      return { x: -0.2 * (1 - (cycle - 3)), y: 0, z: 0 }; // slight lean back (surprise)
    }
    return { x: 0, y: 0, z: 0 };
  },
  head: (p: number) => {
    const cycle = p % 5;
    if (cycle < 2) {
      const t = cycle / 2;
      return { x: -0.3 * t, y: 0, z: 0 }; // tuck chin down
    } else if (cycle < 3) {
      return { x: -0.3 + 0.5 * (cycle - 2), y: 0, z: 0 }; // snap head up
    } else if (cycle < 4) {
      return { x: 0.2 * (1 - (cycle - 3)), y: Math.sin(cycle * 8) * 0.05, z: 0 }; // slight excited wobble
    }
    return { x: 0, y: 0, z: 0 };
  },
  // Hands cover face during hide, then fling out for surprise
  leftUpperArm: (p: number) => {
    const cycle = p % 5;
    if (cycle < 2) {
      const t = Math.min(1, cycle / 1.2);
      return { x: -1.2 * t, y: 0.3 * t, z: 0.8 * t }; // bring to face
    } else if (cycle < 3) {
      const t = cycle - 2;
      return { x: -1.2 + 1.2 * t, y: 0.3 - 0.6 * t, z: 0.8 - 1.2 * t }; // fling out
    } else if (cycle < 4) {
      const t = cycle - 3;
      return { x: 0, y: -0.3 * (1 - t), z: -0.4 * (1 - t) + 1.35 }; // return to sides
    }
    return { x: 0, y: 0, z: 1.35 };
  },
  rightUpperArm: (p: number) => {
    const cycle = p % 5;
    if (cycle < 2) {
      const t = Math.min(1, cycle / 1.2);
      return { x: -1.2 * t, y: -0.3 * t, z: -0.8 * t };
    } else if (cycle < 3) {
      const t = cycle - 2;
      return { x: -1.2 + 1.2 * t, y: -0.3 + 0.6 * t, z: -0.8 + 1.2 * t };
    } else if (cycle < 4) {
      const t = cycle - 3;
      return { x: 0, y: 0.3 * (1 - t), z: 0.4 * (1 - t) - 1.35 };
    }
    return { x: 0, y: 0, z: -1.35 };
  },
  leftLowerArm: (p: number) => {
    const cycle = p % 5;
    if (cycle < 2) {
      const t = Math.min(1, cycle / 1.2);
      return { x: -1.4 * t, y: 0, z: 0 }; // bend to cover face
    } else if (cycle < 3) {
      const t = cycle - 2;
      return { x: -1.4 * (1 - t), y: 0, z: 0 }; // extend out
    }
    return { x: -0.15, y: 0, z: 0 };
  },
  rightLowerArm: (p: number) => {
    const cycle = p % 5;
    if (cycle < 2) {
      const t = Math.min(1, cycle / 1.2);
      return { x: -1.4 * t, y: 0, z: 0 };
    } else if (cycle < 3) {
      const t = cycle - 2;
      return { x: -1.4 * (1 - t), y: 0, z: 0 };
    }
    return { x: -0.15, y: 0, z: 0 };
  },
};

// ── Finger counting poses (1–5) ───────────────────────────────────────
// Right hand raised, fingers extended/curled to show numbers.
// Finger curl: 0 = extended, ~1.5 = fully curled fist

const FINGER_CURLED = 1.5;
const FINGER_OPEN = 0;

// Shared arm position: right arm raised, hand presented forward
const countArmBase: PoseDefinition = {
  rightShoulder: staticPose(-0.1, 0, 0.2),
  rightUpperArm: staticPose(-0.8, 0, -0.6),
  rightLowerArm: staticPose(-1.2, 0, 0),
  rightHand: staticPose(0, 0.3, 0),
};

// Finger states for each count: [thumb, index, middle, ring, little] — true = open
const FINGER_STATES: Record<string, boolean[]> = {
  count_1: [false, true, false, false, false],    // index only
  count_2: [false, true, true, false, false],     // index + middle (peace)
  count_3: [false, true, true, true, false],      // index + middle + ring
  count_4: [false, true, true, true, true],       // all except thumb
  count_5: [true, true, true, true, true],        // all open
};

const FINGER_BONE_PREFIXES = ['rightThumb', 'rightIndex', 'rightMiddle', 'rightRing', 'rightLittle'];
const FINGER_JOINTS = ['Proximal', 'Intermediate', 'Distal'];

function makeCountPose(countKey: string): PoseDefinition {
  const states = FINGER_STATES[countKey];
  const pose: PoseDefinition = { ...countArmBase };

  FINGER_BONE_PREFIXES.forEach((prefix, fi) => {
    const isOpen = states[fi];
    const curl = isOpen ? FINGER_OPEN : FINGER_CURLED;
    FINGER_JOINTS.forEach((joint) => {
      const boneName = prefix + joint;
      // Thumb curls on Z axis, other fingers on X
      if (prefix === 'rightThumb') {
        pose[boneName] = staticPose(0, 0, isOpen ? 0 : 0.8);
      } else {
        pose[boneName] = staticPose(curl * 0.5, 0, 0); // distribute curl across joints
      }
    });
  });

  // Subtle idle sway on extended fingers
  const originalHand = pose.rightHand;
  pose.rightHand = (p: number) => {
    const base = originalHand ? originalHand(p) : { x: 0, y: 0, z: 0 };
    return { x: base.x + Math.sin(p * 1.5) * 0.02, y: base.y, z: base.z };
  };

  return pose;
}

const count1Pose = makeCountPose('count_1');
const count2Pose = makeCountPose('count_2');
const count3Pose = makeCountPose('count_3');
const count4Pose = makeCountPose('count_4');
const count5Pose = makeCountPose('count_5');

export const POSE_LIBRARY: Record<PoseType, PoseDefinition> = {
  idle: idlePose,
  walk: walkPose,
  run: runPose,
  jump: jumpPose,
  sit: sitPose,
  seiza: seizaPose,
  agura: aguraPose,
  dance: dancePose,
  wave: wavePose,
  bow: bowPose,
  think: thinkPose,
  cry: cryPose,
  shiver: shiverPose,
  hug_self: hugSelfPose,
  gasp: gaspPose,
  peace_sign: peaceSignPose,
  peekaboo: peekabooPose,
  count_1: count1Pose,
  count_2: count2Pose,
  count_3: count3Pose,
  count_4: count4Pose,
  count_5: count5Pose,
};

export const ALL_BONE_NAMES = [
  'hips', 'spine', 'chest', 'upperChest', 'neck', 'head',
  'leftUpperArm', 'leftLowerArm', 'leftHand',
  'rightUpperArm', 'rightLowerArm', 'rightHand',
  'leftUpperLeg', 'leftLowerLeg', 'leftFoot',
  'rightUpperLeg', 'rightLowerLeg', 'rightFoot',
  'leftShoulder', 'rightShoulder',
  // Finger bones
  'rightThumbProximal', 'rightThumbIntermediate', 'rightThumbDistal',
  'rightIndexProximal', 'rightIndexIntermediate', 'rightIndexDistal',
  'rightMiddleProximal', 'rightMiddleIntermediate', 'rightMiddleDistal',
  'rightRingProximal', 'rightRingIntermediate', 'rightRingDistal',
  'rightLittleProximal', 'rightLittleIntermediate', 'rightLittleDistal',
  'leftThumbProximal', 'leftThumbIntermediate', 'leftThumbDistal',
  'leftIndexProximal', 'leftIndexIntermediate', 'leftIndexDistal',
  'leftMiddleProximal', 'leftMiddleIntermediate', 'leftMiddleDistal',
  'leftRingProximal', 'leftRingIntermediate', 'leftRingDistal',
  'leftLittleProximal', 'leftLittleIntermediate', 'leftLittleDistal',
];
