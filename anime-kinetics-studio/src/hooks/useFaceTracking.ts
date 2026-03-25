import { useRef, useState, useCallback, useEffect } from 'react';

interface FaceTrackingCallbacks {
  onLookAt?: (x: number, y: number) => void;
  onBlink?: (value: number) => void;
  onMouthOpen?: (value: number) => void;
}

export function useFaceTracking(callbacks: FaceTrackingCallbacks) {
  const [isTracking, setIsTracking] = useState(false);
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const rafRef = useRef<number>(0);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  const startTracking = useCallback(async () => {
    try {
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

      // Simple brightness-based face tracking simulation
      // For production, use MediaPipe FaceMesh
      const track = () => {
        if (!videoRef.current || !canvasRef.current) return;
        const ctx = canvasRef.current.getContext('2d');
        if (!ctx) return;

        ctx.drawImage(videoRef.current, 0, 0, 320, 240);
        const imageData = ctx.getImageData(0, 0, 320, 240);
        const data = imageData.data;

        // Find brightest region (approximate face position)
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
          const faceX = (totalX / totalBright / 320 - 0.5) * 2;
          const faceY = -(totalY / totalBright / 240 - 0.5) * 2;
          callbacks.onLookAt?.(faceX, faceY);
        }

        rafRef.current = requestAnimationFrame(track);
      };

      track();
    } catch (err) {
      console.error('Failed to start face tracking:', err);
    }
  }, [callbacks]);

  const stopTracking = useCallback(() => {
    setIsTracking(false);
    cancelAnimationFrame(rafRef.current);
    streamRef.current?.getTracks().forEach(t => t.stop());
    streamRef.current = null;
  }, []);

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
