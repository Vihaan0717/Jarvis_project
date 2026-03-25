import { Vowel } from './types';
import { VRM } from '@pixiv/three-vrm';

/**
 * VRM BlendShape clip mapping for Japanese vowels.
 * Maps vowel → VRM expression name + intensity.
 */
const VOWEL_BLENDSHAPES: Record<Vowel, { expression: string; intensity: number }[]> = {
  a: [{ expression: 'aa', intensity: 1.0 }],
  i: [{ expression: 'ih', intensity: 0.7 }, { expression: 'ee', intensity: 0.5 }],
  u: [{ expression: 'ou', intensity: 0.8 }],
  e: [{ expression: 'ee', intensity: 0.9 }],
  o: [{ expression: 'oh', intensity: 0.9 }],
  silent: [],
};

// Fallback: use 'aa' for all vowels if specific ones aren't available
const FALLBACK_MAP: Record<Vowel, { expression: string; intensity: number }> = {
  a: { expression: 'aa', intensity: 1.0 },
  i: { expression: 'aa', intensity: 0.3 },
  u: { expression: 'aa', intensity: 0.5 },
  e: { expression: 'aa', intensity: 0.4 },
  o: { expression: 'aa', intensity: 0.7 },
  silent: { expression: 'aa', intensity: 0 },
};

const VOWEL_EXPRESSIONS = ['aa', 'ih', 'ee', 'ou', 'oh'];

export class LipSyncController {
  private currentVowel: Vowel = 'silent';
  private targetValues: Map<string, number> = new Map();
  private currentValues: Map<string, number> = new Map();
  private smoothing = 8; // lerp speed

  setVowel(vowel: Vowel) {
    this.currentVowel = vowel;
    // Reset targets
    this.targetValues.clear();
    VOWEL_EXPRESSIONS.forEach(e => this.targetValues.set(e, 0));

    const shapes = VOWEL_BLENDSHAPES[vowel];
    if (shapes.length > 0) {
      shapes.forEach(s => this.targetValues.set(s.expression, s.intensity));
    }
  }

  update(vrm: VRM, delta: number) {
    if (!vrm.expressionManager) return;

    // Check which expressions are available
    const hasSpecific = VOWEL_EXPRESSIONS.some(
      e => e !== 'aa' && vrm.expressionManager?.getExpression(e)
    );

    if (hasSpecific) {
      // Use specific vowel blendshapes
      for (const [expr, target] of this.targetValues) {
        const current = this.currentValues.get(expr) ?? 0;
        const next = current + (target - current) * Math.min(1, delta * this.smoothing);
        this.currentValues.set(expr, next);
        vrm.expressionManager.setValue(expr, next);
      }
    } else {
      // Fallback: use just 'aa' with varying intensity
      const fb = FALLBACK_MAP[this.currentVowel];
      const current = this.currentValues.get('aa') ?? 0;
      const next = current + (fb.intensity - current) * Math.min(1, delta * this.smoothing);
      this.currentValues.set('aa', next);
      vrm.expressionManager.setValue('aa', next);
    }
  }

  getCurrentVowel(): Vowel {
    return this.currentVowel;
  }
}
