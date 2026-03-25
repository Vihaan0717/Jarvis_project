import { useRef, useEffect, useCallback, useState, memo } from "react";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { OrbitControls, Environment, ContactShadows } from "@react-three/drei";
import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { VRM, VRMLoaderPlugin } from "@pixiv/three-vrm";
import { VRMAnimationManager } from "@/animation/VRMAnimationManager";

interface ModelProps {
  url: string;
  state: string;
  tracking?: { headPitch: number; headYaw: number; eyePitch: number; eyeYaw: number; blinkLeft?: number; blinkRight?: number };
  audioAmplitude?: number;
  onLoaded: (manager: VRMAnimationManager) => void;
}

const VRMModel = memo(({ url, state, tracking, audioAmplitude, onLoaded }: ModelProps) => {
  const [vrm, setVrm] = useState<VRM | null>(null);
  const managerRef = useRef(new VRMAnimationManager());
  const prevStateRef = useRef(state);

  const handleLookAt = useCallback((headY: number, headP: number, eyeY: number, eyeP: number) => {
    if (managerRef.current.isAttached) {
      managerRef.current.setLookAt(headY, headP, eyeY, eyeP);
    }
  }, []);

  // Integrate face tracking directly from props (backend data)
  useEffect(() => {
    if (tracking) {
      if (tracking.headYaw !== undefined && tracking.headPitch !== undefined) {
        handleLookAt(tracking.headYaw, tracking.headPitch, tracking.eyeYaw ?? 0, tracking.eyePitch ?? 0);
      }
      
      if (managerRef.current.isAttached) {
        managerRef.current.setBlinkExact(tracking.blinkLeft, tracking.blinkRight);
      }
    } else if (managerRef.current.isAttached) {
      // Clear exact blinks to fallback to random idle blinks
      managerRef.current.setBlinkExact(undefined, undefined);
    }
  }, [tracking, handleLookAt]);

  useEffect(() => {
    const loader = new GLTFLoader();
    loader.register((parser) => new VRMLoaderPlugin(parser));

    loader.loadAsync(url).then((gltf) => {
      const loadedVrm = gltf.userData.vrm;
      if (!loadedVrm) return;

      loadedVrm.scene.rotation.y = Math.PI;
      setVrm(loadedVrm);
      
      managerRef.current.attach(loadedVrm);
      
      // Map state to initial emotion/pose
      const { emotion, pose } = mapStateToAnimation(state);
      managerRef.current.setEmotion(emotion as any);
      managerRef.current.playAction(pose as any);

      onLoaded(managerRef.current);
    });
  }, [url]);

  // Handle state changes
  useEffect(() => {
    if (prevStateRef.current !== state && managerRef.current.isAttached) {
      const { emotion, pose } = mapStateToAnimation(state);
      managerRef.current.setEmotion(emotion as any);
      managerRef.current.playAction(pose as any);
      prevStateRef.current = state;
    }
  }, [state]);

  useFrame((state_clock, delta) => {
    if (managerRef.current.isAttached) {
      // Only apply lookAt if active tracking is provided (remove mouse fallback)
      if (tracking && tracking.headYaw !== undefined) {
        managerRef.current.setLookAt(tracking.headYaw, tracking.headPitch, tracking.eyeYaw ?? 0, tracking.eyePitch ?? 0);
      }
      if (audioAmplitude !== undefined) {
        managerRef.current.setMouthOpen(audioAmplitude);
      }
      managerRef.current.update(delta);
    }
  });

  return vrm ? <primitive object={vrm.scene} /> : null;
});

const mapStateToAnimation = (state: string) => {
  switch (state) {
    case "listening": return { emotion: "relaxed", pose: "think" };
    case "thinking": return { emotion: "serious", pose: "think" };
    case "scanning": return { emotion: "surprised", pose: "scan" };
    default: return { emotion: "neutral", pose: "idle" };
  }
};

const JarvisVRM = memo(({ state, tracking, audioAmplitude }: { state: string, tracking?: {headYaw: number, headPitch: number, eyeYaw: number, eyePitch: number, blinkLeft?: number, blinkRight?: number}, audioAmplitude?: number }) => {
  const managerRef = useRef<VRMAnimationManager | null>(null);

  const handleLoaded = useCallback((manager: VRMAnimationManager) => {
    managerRef.current = manager;
  }, []);

  return (
    <div className="absolute inset-0 w-full h-full pointer-events-auto">
      <Canvas 
        camera={{ position: [0.8, 1.0, 3.0], fov: 35 }} 
        className="w-full h-full"
        dpr={[1, 1.5]}
        gl={{ powerPreference: "high-performance", antialias: true, toneMapping: THREE.ACESFilmicToneMapping }}
      >
        <ambientLight intensity={0.8} />
        <directionalLight position={[2, 3, 5]} intensity={1.2} castShadow />
        <directionalLight position={[-2, 2, -3]} intensity={0.3} color="#ff88cc" />
        <pointLight position={[0, 2, 2]} intensity={0.4} color="#8844ff" />
        
        <group position={[0, 0, 0]}>
          <VRMModel url="/avatar.vrm" state={state} tracking={tracking} audioAmplitude={audioAmplitude} onLoaded={handleLoaded} />
        </group>
        
        <ContactShadows position={[0, 0, 0]} opacity={0.4} blur={2} />
        <Environment files="/studio_small_03_1k.hdr" />
        
        <OrbitControls
          target={[0.8, 0.9, 0]}
          minDistance={1}
          maxDistance={6}
          minPolarAngle={Math.PI * 0.1}
          maxPolarAngle={Math.PI * 0.85}
        />
      </Canvas>
    </div>
  );
});

export default JarvisVRM;
