import { useState, useEffect, useCallback } from "react";

type AvatarState = "idle" | "listening" | "thinking" | "scanning";

interface JarvisData {
  weather?: any;
  news?: any[];
  movies?: any[];
  os_context?: {
    active_window: string;
    cpu_percent: number;
    memory_percent: number;
    battery_percent?: number;
    is_plugged_in?: boolean;
    biological_state?: string;
    timestamp: string;
  };
  system_config?: {
    environment: string;
    model: string;
  };
  file_change?: {
    path: string;
    event: string;
  };
  biometric?: {
    status: string;
    user?: string;
  };
  tracking?: {
    headPitch: number;
    headYaw: number;
    eyePitch: number;
    eyeYaw: number;
    blinkLeft?: number;
    blinkRight?: number;
  };
  code_result?: string;
  audioAmplitude?: number;
}

export const useJarvisSocket = (url: string = "ws://127.0.0.1:8765") => {
  const [data, setData] = useState<JarvisData>({});
  const [avatarState, setAvatarState] = useState<AvatarState>("idle");
  const [socket, setSocket] = useState<WebSocket | null>(null);

  useEffect(() => {
    const ws = new WebSocket(url);
    
    ws.onopen = () => {
      console.log("Connected to JARVIS Backend");
      setSocket(ws);
    };

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        console.log("JARVIS Message:", msg.type, msg);

        switch (msg.type) {
          case "INIT_DATA":
            setData(prev => ({ 
              ...prev, 
              ...msg,
              system_config: msg.system_config || prev.system_config 
            }));
            break;
          case "OS_CONTEXT":
            setData(prev => ({ 
              ...prev, 
              os_context: {
                ...msg.context,
                timestamp: msg.timestamp
              } 
            }));
            break;
          case "FILE_CHANGE":
            setData(prev => ({ ...prev, file_change: msg }));
            break;
          case "BIOMETRIC_EVENT":
            if (msg.status === "SCANNING") setAvatarState("scanning");
            else if (msg.status === "VERIFIED") setAvatarState("idle");
            break;
          case "CODE_RESULT":
            setData(prev => ({ ...prev, code_result: msg.code }));
            setAvatarState("idle");
            break;
          case "VISION_TRACKING":
          case "TRACKING":
            if (msg.detected) {
              const bl = msg.blink_left;
              const br = msg.blink_right;
              
              if (msg.yaw !== undefined) {
                // Decouple head movement from eye movement
                const headP = msg.pitch ?? 0;
                const headY = msg.yaw ?? 0;
                // Use explicit eye tracking if available, else infer slightly from head
                const eyeP = msg.eye_pitch ?? (headP * 0.3);
                const eyeY = msg.eye_yaw ?? (headY * 0.3);

                setData(prev => ({ 
                  ...prev, 
                  tracking: { 
                    headPitch: headP, 
                    headYaw: -headY, // Invert yaw
                    eyePitch: eyeP,
                    eyeYaw: -eyeY,
                    blinkLeft: bl, 
                    blinkRight: br 
                  } 
                }));
              }
            } else {
              // Not detected, clear tracking so it falls back to mouse tracking
              setData(prev => ({ ...prev, tracking: undefined }));
            }
            break;
          case "PLAY_AUDIO":
            if (msg.url) {
              const audio = new Audio(msg.url);
              
              // Setup Audio Analysis for Lip Sync
              const AudioContextClass = (window.AudioContext || (window as any).webkitAudioContext);
              const audioCtx = new AudioContextClass();
              const source = audioCtx.createMediaElementSource(audio);
              const analyser = audioCtx.createAnalyser();
              analyser.fftSize = 256;
              source.connect(analyser);
              analyser.connect(audioCtx.destination);
              
              const bufferLength = analyser.frequencyBinCount;
              const dataArray = new Uint8Array(bufferLength);
              
              const updateAmplitude = () => {
                if (audio.paused || audio.ended) {
                  setData(prev => ({ ...prev, audioAmplitude: 0 }));
                  audioCtx.close();
                  return;
                }
                
                analyser.getByteFrequencyData(dataArray);
                let sum = 0;
                for (let i = 0; i < bufferLength; i++) {
                  sum += dataArray[i];
                }
                const average = sum / bufferLength;
                const normalized = Math.min(1.0, average / 40.0); // Adjust sensitivity
                
                setData(prev => ({ ...prev, audioAmplitude: normalized }));
                requestAnimationFrame(updateAmplitude);
              };
              
              audio.play().then(() => {
                if (audioCtx.state === 'suspended') {
                  audioCtx.resume();
                }
                updateAmplitude();
              }).catch(e => console.error("Audio playback failed:", e));
            }
            break;
          default:
            // Generic process_frame fallback
            if (msg.detected !== undefined && msg.yaw !== undefined) {
                setData(prev => ({ 
                  ...prev, 
                  tracking: msg.detected ? { 
                    headPitch: msg.pitch ?? 0, 
                    headYaw: -(msg.yaw ?? 0),
                    eyePitch: msg.eye_pitch ?? 0,
                    eyeYaw: -(msg.eye_yaw ?? 0)
                  } : undefined 
                }));
            }
            break;
        }
      } catch (err) {
        console.error("Failed to parse JARVIS message", err);
      }
    };

    ws.onclose = () => {
      console.log("Disconnected from JARVIS Backend");
      setSocket(null);
      setAvatarState("idle");
    };

    return () => ws.close();
  }, [url]);

  const sendCommand = useCallback((type: string, payload: any) => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(json.stringify({ type, ...payload }));
      if (type === "GET_CODE_GEN") setAvatarState("thinking");
    }
  }, [socket]);

  return { data, avatarState, setAvatarState, sendCommand };
};

const json = JSON; // Safety for minifiers if needed
