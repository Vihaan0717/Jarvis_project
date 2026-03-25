import { useRef, useEffect, useCallback } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { OrbitControls, Environment, ContactShadows } from '@react-three/drei';
import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { VRMLoaderPlugin, VRMHumanBoneName } from '@pixiv/three-vrm';
import { VRMAnimationManager } from '@/animation/VRMAnimationManager';
import type { EmotionType, PoseType } from '@/animation/types';

// Re-export for convenience
export type { AnimationAPI } from '@/animation/types';

interface VRMModelProps {
  url: string;
  onLoaded: (manager: VRMAnimationManager) => void;
  emotion: EmotionType;
  pose: PoseType;
  animate: boolean;
}

function VRMModel({ url, onLoaded, emotion, pose }: VRMModelProps) {
  const { scene } = useThree();
  const managerRef = useRef(new VRMAnimationManager());
  const prevPoseRef = useRef(pose);
  const prevEmotionRef = useRef(emotion);

  useEffect(() => {
    const loader = new GLTFLoader();
    loader.register((parser) => new VRMLoaderPlugin(parser));

    loader.loadAsync(url).then((gltf) => {
      const vrm = gltf.userData.vrm;
      if (!vrm) return;

      vrm.scene.rotation.y = Math.PI;
      scene.add(vrm.scene);

      if (vrm.humanoid) {
        const allBones = Object.values(VRMHumanBoneName);
        const available = allBones.filter(b =>
          vrm.humanoid?.getRawBoneNode(b) || vrm.humanoid?.getNormalizedBoneNode(b)
        );
        console.log('Available VRM bones:', available);
        console.log('Expressions:', vrm.expressionManager?.expressions?.map((e: any) => e.expressionName));
      }

      managerRef.current.attach(vrm);
      managerRef.current.setEmotion(emotion);
      managerRef.current.playAction(pose);
      onLoaded(managerRef.current);
    });

    return () => {
      scene.children.forEach(child => {
        if ((child as any).isVRM || child.userData?.vrm) {
          scene.remove(child);
        }
      });
    };
  }, [url, scene]);

  useEffect(() => {
    if (prevPoseRef.current !== pose) {
      managerRef.current.playAction(pose);
      prevPoseRef.current = pose;
    }
  }, [pose]);

  useEffect(() => {
    if (prevEmotionRef.current !== emotion) {
      managerRef.current.setEmotion(emotion);
      prevEmotionRef.current = emotion;
    }
  }, [emotion]);

  useFrame((_, delta) => {
    managerRef.current.update(delta);
  });

  return null;
}

interface VRMSceneProps {
  modelUrl: string;
  emotion: EmotionType;
  pose: PoseType;
  animate: boolean;
  onModelLoaded: (manager: VRMAnimationManager) => void;
}

export default function VRMScene({ modelUrl, emotion, pose, animate, onModelLoaded }: VRMSceneProps) {
  const handleLoaded = useCallback((manager: VRMAnimationManager) => {
    onModelLoaded(manager);
  }, [onModelLoaded]);

  return (
    <Canvas
      camera={{ position: [0, 1.0, 3], fov: 30 }}
      className="w-full h-full"
      gl={{ antialias: true, toneMapping: THREE.ACESFilmicToneMapping }}
    >
      <ambientLight intensity={0.8} />
      <directionalLight position={[2, 3, 5]} intensity={1.2} castShadow />
      <directionalLight position={[-2, 2, -3]} intensity={0.3} color="#ff88cc" />
      <pointLight position={[0, 2, 2]} intensity={0.4} color="#8844ff" />

      <VRMModel
        url={modelUrl}
        onLoaded={handleLoaded}
        emotion={emotion}
        pose={pose}
        animate={animate}
      />

      <ContactShadows position={[0, 0, 0]} opacity={0.4} blur={2} />
      <Environment files="/studio_small_03_1k.hdr" />
      <OrbitControls
        target={[0, 0.9, 0]}
        minDistance={1}
        maxDistance={6}
        minPolarAngle={Math.PI * 0.1}
        maxPolarAngle={Math.PI * 0.85}
      />
    </Canvas>
  );
}
