import * as THREE from 'three';
import { VRM } from '@pixiv/three-vrm';

/**
 * Eye tracking with 0.5s lag for realism.
 * Also handles natural random-interval blinking.
 */
export class EyeController {
  private targetX = 0;
  private targetY = 0;
  public currentX = 0;
  public currentY = 0;
  private lagSpeed = 12.0; // Faster for responsive eyes
  
  private blinkTimer = 0;
  private nextBlinkAt = 3;
  private blinkValue = 0;
  private blinkDecay = 10; // how fast blink closes/opens
  
  private blinkOverrideLeft?: number;
  private blinkOverrideRight?: number;

  // (No longer using vrm.lookAt Target)
  // private lookAtTarget = new THREE.Object3D();

  setLookAt(yaw: number, pitch: number) {
    this.targetX = yaw;
    this.targetY = pitch;
  }

  forceBlink() {
    this.blinkValue = 1;
  }

  update(vrm: VRM, delta: number) {
    if (!vrm) return;

    // --- Eye tracking with smoother, faster response ---
    const t = Math.min(1, delta * this.lagSpeed);
    this.currentX += (this.targetX - this.currentX) * t;
    this.currentY += (this.targetY - this.currentY) * t;

    if (vrm.lookAt) {
      // Disable the built-in auto-lookAt system because it fights with manual bone rotations
      vrm.lookAt.autoUpdate = false;
    }

    // --- Natural blinking ---
    this.blinkTimer += delta;
    if (this.blinkTimer >= this.nextBlinkAt) {
      this.blinkValue = 1;
      this.blinkTimer = 0;
      // Random interval: 2-5 seconds, occasionally double-blink
      this.nextBlinkAt = 2 + Math.random() * 3;
    }

    // Decay blink
    if (this.blinkValue > 0) {
      this.blinkValue = Math.max(0, this.blinkValue - delta * this.blinkDecay);
    }

    if (vrm.expressionManager) {
      if (this.blinkOverrideLeft !== undefined && this.blinkOverrideRight !== undefined) {
         vrm.expressionManager.setValue('blinkLeft', this.blinkOverrideLeft);
         vrm.expressionManager.setValue('blinkRight', this.blinkOverrideRight);
      } else {
         vrm.expressionManager.setValue('blinkLeft', this.blinkValue);
         vrm.expressionManager.setValue('blinkRight', this.blinkValue);
      }
    }
  }

  setBlinkOverride(value: number) {
    this.blinkValue = value;
  }

  setBlinkExact(left?: number, right?: number) {
    this.blinkOverrideLeft = left;
    this.blinkOverrideRight = right;
  }
}
