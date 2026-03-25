import { useState, useRef, useCallback, useMemo, useEffect } from 'react';
import VRMScene from '@/components/VRMScene';
import ControlPanel from '@/components/ControlPanel';
import { useFaceTracking } from '@/hooks/useFaceTracking';
import { useJarvisCommunication } from '@/hooks/useJarvisCommunication';
import { VRMAnimationManager } from '@/animation/VRMAnimationManager';
import type { EmotionType, PoseType } from '@/animation/types';

const Index = () => {
  const [modelUrl, setModelUrl] = useState<string | null>('/models/JARVIS_PROJECT1.vrm');
  const [emotion, setEmotion] = useState<EmotionType>('neutral');
  const [pose, setPose] = useState<PoseType>('idle');
  const [animate, setAnimate] = useState(true);
  const [exertion, setExertion] = useState(0);
  const managerRef = useRef<VRMAnimationManager | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const trackingCallbacks = useMemo(() => ({
    onLookAt: (x: number, y: number) => managerRef.current?.setLookAt(x, y),
    onBlink: (v: number) => managerRef.current?.setBlink(v),
    onMouthOpen: (v: number) => managerRef.current?.setMouthOpen(v),
  }), []);

  const { isTracking, toggleTracking } = useFaceTracking(trackingCallbacks);
  const { lastResponse, isConnected } = useJarvisCommunication();

  useEffect(() => {
    const handleAction = (event: any) => {
      const { action } = event.detail;
      console.log("Global Action Received:", action);
      if (managerRef.current) {
        // Map common actions to our animation system
        if (action === 'wave') {
          managerRef.current.playAction('wave');
        } else if (action === 'thinking') {
          managerRef.current.playAction('think');
        } else if (['happy', 'sad', 'angry', 'surprised', 'relaxed'].includes(action)) {
          managerRef.current.setEmotion(action);
        } else {
          // Default fallbacks
          managerRef.current.playAction(action);
        }
      }
    };

    window.addEventListener('jarvis-action', handleAction);
    return () => window.removeEventListener('jarvis-action', handleAction);
  }, []);

  const handleUpload = useCallback(() => {
    fileInputRef.current?.click();
  }, []);

  const handleFileChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && file.name.endsWith('.vrm')) {
      const url = URL.createObjectURL(file);
      setModelUrl(url);
      setEmotion('neutral');
      setPose('idle');
    }
  }, []);

  const handleModelLoaded = useCallback((manager: VRMAnimationManager) => {
    managerRef.current = manager;
  }, []);

  const handleExertionChange = useCallback((v: number) => {
    setExertion(v);
    managerRef.current?.setExertion(v);
  }, []);

  return (
    <div className="relative w-full h-screen bg-background overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-b from-muted/50 to-background" />

      <div className="absolute inset-0">
        {modelUrl ? (
          <VRMScene
            modelUrl={modelUrl}
            emotion={emotion}
            pose={pose}
            animate={animate}
            onModelLoaded={handleModelLoaded}
          />
        ) : (
          <div className="flex items-center justify-center h-full">
            <div className="text-center space-y-4">
              <div className="w-24 h-24 mx-auto rounded-full bg-primary/10 flex items-center justify-center border-2 border-dashed border-primary/30">
                <span className="text-4xl">🎭</span>
              </div>
              <h1 className="text-2xl font-bold text-foreground">Anime Avatar Studio</h1>
              <p className="text-muted-foreground max-w-md">
                Upload a VRM model to start. Control expressions, poses, and enable face tracking.
              </p>
              <button
                onClick={handleUpload}
                className="px-6 py-3 bg-primary text-primary-foreground rounded-lg font-medium hover:opacity-90 transition-opacity"
              >
                Upload VRM Model
              </button>
            </div>
          </div>
        )}
      </div>

      <ControlPanel
        emotion={emotion}
        pose={pose}
        tracking={isTracking}
        exertion={exertion}
        onEmotionChange={setEmotion}
        onPoseChange={(p) => { setPose(p); setAnimate(true); }}
        onToggleTracking={toggleTracking}
        onUploadModel={handleUpload}
        onExertionChange={handleExertionChange}
        hasModel={!!modelUrl}
      />

      <input
        ref={fileInputRef}
        type="file"
        accept=".vrm"
        onChange={handleFileChange}
        className="hidden"
      />

      <div className="absolute top-4 left-4 z-10 flex items-center space-x-2">
        <h2 className="text-lg font-bold text-foreground/80">Anime Avatar Studio</h2>
        <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} title={isConnected ? "Connected to JARVIS" : "Disconnected"} />
      </div>

      {lastResponse && (
        <div className="absolute bottom-10 left-1/2 -translate-x-1/2 z-20 w-full max-w-2xl px-4">
          <div className="bg-black/60 backdrop-blur-md border border-white/10 rounded-2xl p-4 text-center animate-in fade-in slide-in-from-bottom-4 duration-500">
            <p className="text-white text-xl font-medium leading-relaxed drop-shadow-lg italic">
              "{lastResponse}"
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default Index;
