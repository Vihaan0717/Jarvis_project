import { useState, useCallback } from 'react';
import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { VRM, VRMLoaderPlugin, VRMExpressionPresetName, VRMHumanBoneName } from '@pixiv/three-vrm';

export type EmotionType = 'neutral' | 'happy' | 'angry' | 'sad' | 'surprised' | 'relaxed';
export type PoseType = 'idle' | 'walk' | 'sit' | 'dance' | 'wave' | 'bow';

function getBone(vrm: VRM, name: string): THREE.Object3D | null {
  const humanoid = vrm.humanoid;
  if (!humanoid) return null;
  
  // Try normalized first (VRM 1.0), then raw
  let node = humanoid.getNormalizedBoneNode(name as VRMHumanBoneName);
  if (!node) {
    node = humanoid.getRawBoneNode(name as VRMHumanBoneName);
  }
  return node;
}

export function useVRM() {
  const [vrm, setVRM] = useState<VRM | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadVRM = useCallback(async (url: string, scene: THREE.Scene) => {
    setLoading(true);
    setError(null);

    const loader = new GLTFLoader();
    loader.register((parser) => new VRMLoaderPlugin(parser));

    try {
      const gltf = await loader.loadAsync(url);
      const loadedVRM = gltf.userData.vrm as VRM;

      if (!loadedVRM) {
        throw new Error('No VRM data found in the file');
      }

      // VRM models face +Z, rotate to face camera at +Z
      loadedVRM.scene.rotation.y = Math.PI;
      scene.add(loadedVRM.scene);

      // Debug: log available bones
      if (loadedVRM.humanoid) {
        const allBones = Object.values(VRMHumanBoneName);
        const available: string[] = [];
        allBones.forEach(boneName => {
          const raw = loadedVRM.humanoid?.getRawBoneNode(boneName);
          const norm = loadedVRM.humanoid?.getNormalizedBoneNode(boneName);
          if (raw || norm) available.push(boneName);
        });
        console.log('Available VRM bones:', available);
        console.log('Expressions:', loadedVRM.expressionManager?.expressions?.map(e => e.expressionName));
      }

      setVRM(loadedVRM);
      setLoading(false);
      return loadedVRM;
    } catch (e) {
      const msg = e instanceof Error ? e.message : 'Failed to load VRM';
      setError(msg);
      setLoading(false);
      return null;
    }
  }, []);

  const setEmotion = useCallback((emotion: EmotionType) => {
    if (!vrm?.expressionManager) return;
    const presets: VRMExpressionPresetName[] = ['happy', 'angry', 'sad', 'surprised', 'relaxed', 'neutral'];
    presets.forEach(p => vrm.expressionManager?.setValue(p, 0));
    if (emotion !== 'neutral') {
      vrm.expressionManager.setValue(emotion as VRMExpressionPresetName, 1);
    }
  }, [vrm]);

  const setLookAt = useCallback((x: number, y: number) => {
    if (!vrm?.lookAt) return;
    const target = new THREE.Object3D();
    target.position.set(x * 0.5, y * 0.5 + 1.5, -1);
    vrm.lookAt.target = target;
  }, [vrm]);

  const setBlink = useCallback((value: number) => {
    if (!vrm?.expressionManager) return;
    vrm.expressionManager.setValue('blinkLeft', value);
    vrm.expressionManager.setValue('blinkRight', value);
  }, [vrm]);

  const setMouthOpen = useCallback((value: number) => {
    if (!vrm?.expressionManager) return;
    vrm.expressionManager.setValue('aa', value);
  }, [vrm]);

  const applyPose = useCallback((pose: PoseType) => {
    if (!vrm?.humanoid) return;

    const bone = (name: string) => getBone(vrm, name);

    // Reset all bones
    const boneNames = [
      'hips', 'spine', 'chest', 'upperChest', 'neck', 'head',
      'leftUpperArm', 'leftLowerArm', 'leftHand',
      'rightUpperArm', 'rightLowerArm', 'rightHand',
      'leftUpperLeg', 'leftLowerLeg', 'leftFoot',
      'rightUpperLeg', 'rightLowerLeg', 'rightFoot',
    ];

    boneNames.forEach(name => {
      const node = bone(name);
      if (node) node.quaternion.identity();
    });

    switch (pose) {
      case 'wave': {
        const rUpperArm = bone('rightUpperArm');
        const rLowerArm = bone('rightLowerArm');
        if (rUpperArm) rUpperArm.quaternion.setFromEuler(new THREE.Euler(0, 0, -Math.PI * 0.8));
        if (rLowerArm) rLowerArm.quaternion.setFromEuler(new THREE.Euler(0, 0, -Math.PI * 0.3));
        break;
      }
      case 'sit': {
        const lUpperLeg = bone('leftUpperLeg');
        const rUpperLeg = bone('rightUpperLeg');
        const lLowerLeg = bone('leftLowerLeg');
        const rLowerLeg = bone('rightLowerLeg');
        if (lUpperLeg) lUpperLeg.quaternion.setFromEuler(new THREE.Euler(Math.PI * 0.5, 0, 0));
        if (rUpperLeg) rUpperLeg.quaternion.setFromEuler(new THREE.Euler(Math.PI * 0.5, 0, 0));
        if (lLowerLeg) lLowerLeg.quaternion.setFromEuler(new THREE.Euler(-Math.PI * 0.5, 0, 0));
        if (rLowerLeg) rLowerLeg.quaternion.setFromEuler(new THREE.Euler(-Math.PI * 0.5, 0, 0));
        break;
      }
      case 'bow': {
        const sp = bone('spine');
        const ch = bone('chest');
        if (sp) sp.quaternion.setFromEuler(new THREE.Euler(Math.PI * 0.2, 0, 0));
        if (ch) ch.quaternion.setFromEuler(new THREE.Euler(Math.PI * 0.15, 0, 0));
        break;
      }
      default:
        break;
    }
  }, [vrm]);

  return { vrm, loading, error, loadVRM, setEmotion, setLookAt, setBlink, setMouthOpen, applyPose, getBoneForVRM: vrm ? (name: string) => getBone(vrm, name) : null };
}
