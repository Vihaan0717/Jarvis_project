import * as THREE from 'three';
import { VRM } from '@pixiv/three-vrm';

/**
 * Eye tracking with 0.5s lag for realism.
 * Also handles natural random-interval blinking.
 */
export class EyeController {
  private targetX = 0;
  private targetY = 0;
  private currentX = 0;
  private currentY = 0;
  private lagSpeed = 2.0; // ~0.5s to reach target (1/0.5)
  
  private blinkTimer = 0;
  private nextBlinkAt = 3;
  private blinkValue = 0;
  private blinkDecay = 10; // how fast blink closes/opens

  private lookAtTarget = new THREE.Object3D();

  setLookAt(x: number, y: number) {
    this.targetX = x;
    this.targetY = y;
  }

  forceBlink() {
    this.blinkValue = 1;
  }

  update(vrm: VRM, delta: number) {
    if (!vrm) return;

    // --- Eye tracking with lag ---
    this.currentX += (this.targetX - this.currentX) * Math.min(1, delta * this.lagSpeed);
    this.currentY += (this.targetY - this.currentY) * Math.min(1, delta * this.lagSpeed);

    if (vrm.lookAt) {
      this.lookAtTarget.position.set(this.currentX * 0.5, this.currentY * 0.5 + 1.5, -1);
      vrm.lookAt.target = this.lookAtTarget;
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
      vrm.expressionManager.setValue('blinkLeft', this.blinkValue);
      vrm.expressionManager.setValue('blinkRight', this.blinkValue);
    }
  }

  setBlinkOverride(value: number) {
    this.blinkValue = value;
  }
}
