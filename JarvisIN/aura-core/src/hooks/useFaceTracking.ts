import { useRef, useState, useCallback, useEffect } from 'react';

interface FaceTrackingCallbacks {
  onLookAt?: (x: number, y: number) => void;
  onBlink?: (value: number) => void;
  onMouthOpen?: (value: number) => void;
}

export function useFaceTracking(callbacks: FaceTrackingCallbacks, autoStart = true) {
  const [isTracking, setIsTracking] = useState(false);
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const rafRef = useRef<number>(0);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  
  // Smoothing history
  const smoothedX = useRef(0);
  const smoothedY = useRef(0);
  const EMA_ALPHA = 0.05; // Aggressive smoothing for stability
  const DEADZONE = 0.01;  // Ignore micro-jitter

  const callbacksRef = useRef(callbacks);
  useEffect(() => {
    callbacksRef.current = callbacks;
  }, [callbacks]);

  const startTracking = useCallback(async () => {
    try {
      if (streamRef.current) return;
      
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 320, height: 240, facingMode: 'user' },
      });
      streamRef.current = stream;

      if (!videoRef.current) {
        videoRef.current = document.createElement('video');
        videoRef.current.setAttribute('playsinline', '');
        videoRef.current.style.display = 'none';
        document.body.appendChild(videoRef.current);
      }
      videoRef.current.srcObject = stream;
      await videoRef.current.play();

      if (!canvasRef.current) {
        canvasRef.current = document.createElement('canvas');
        canvasRef.current.width = 320;
        canvasRef.current.height = 240;
      }

      setIsTracking(true);

      const track = () => {
        if (!videoRef.current || !canvasRef.current) return;
        const ctx = canvasRef.current.getContext('2d');
        if (!ctx) return;

        ctx.drawImage(videoRef.current, 0, 0, 320, 240);
        const imageData = ctx.getImageData(0, 0, 320, 240);
        const data = imageData.data;

        let totalX = 0, totalY = 0, totalBright = 0;
        for (let y = 0; y < 240; y += 4) {
          for (let x = 0; x < 320; x += 4) {
            const i = (y * 320 + x) * 4;
            const brightness = (data[i] + data[i + 1] + data[i + 2]) / 3;
            if (brightness > 100) {
              totalX += x * brightness;
              totalY += y * brightness;
              totalBright += brightness;
            }
          }
        }

        if (totalBright > 0) {
          const rawX = (totalX / totalBright / 320 - 0.5) * 2;
          const rawY = -(totalY / totalBright / 240 - 0.5) * 2;

          const dx = rawX - smoothedX.current;
          const dy = rawY - smoothedY.current;
          const dist = Math.sqrt(dx * dx + dy * dy);

          // Only update if movement exceeds deadzone
          if (dist > DEADZONE) {
            smoothedX.current = EMA_ALPHA * rawX + (1 - EMA_ALPHA) * smoothedX.current;
            smoothedY.current = EMA_ALPHA * rawY + (1 - EMA_ALPHA) * smoothedY.current;
            callbacksRef.current.onLookAt?.(smoothedX.current, smoothedY.current);
          }
        }

        rafRef.current = requestAnimationFrame(track);
      };

      track();
    } catch (err) {
      console.error('Failed to start face tracking:', err);
    }
  }, []);

  const stopTracking = useCallback(() => {
    setIsTracking(false);
    if (rafRef.current) cancelAnimationFrame(rafRef.current);
    streamRef.current?.getTracks().forEach(t => t.stop());
    streamRef.current = null;
  }, []);

  const startedRef = useRef(false);

  useEffect(() => {
    if (autoStart && !startedRef.current) {
      startedRef.current = true;
      const timer = setTimeout(() => {
        startTracking();
      }, 2000);
      return () => clearTimeout(timer);
    }
  }, [autoStart, startTracking]);

  const toggleTracking = useCallback(() => {
    if (isTracking) {
      stopTracking();
    } else {
      startTracking();
    }
  }, [isTracking, startTracking, stopTracking]);

  useEffect(() => {
    return () => {
      stopTracking();
      if (videoRef.current) {
        videoRef.current.remove();
      }
    };
  }, [stopTracking]);

  return { isTracking, toggleTracking };
}
