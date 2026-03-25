import { useState, useEffect, useCallback } from 'react';

export interface JarvisMessage {
  type: 'AI_RESPONSE' | 'ANIMATION' | 'TRACKING';
  text?: string;
  emotion?: string;
  action?: string;
  [key: string]: any;
}

export function useJarvisCommunication() {
  const [lastResponse, setLastResponse] = useState<string>("");
  const [currentEmotion, setCurrentEmotion] = useState<string>("neutral");
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    const socket = new WebSocket("ws://127.0.0.1:8765");

    socket.onopen = () => {
      console.log("Connected to JARVIS Backend!");
      setIsConnected(true);
    };

    socket.onmessage = (event) => {
      try {
        const data: JarvisMessage = JSON.parse(event.data);
        
        if (data.type === 'AI_RESPONSE') {
          const { text, emotion } = data;
          if (text) setLastResponse(text);
          if (emotion) setCurrentEmotion(emotion);

          // Dispatch the global event as requested
          window.dispatchEvent(new CustomEvent('jarvis-action', {
            detail: { action: emotion || 'neutral', text }
          }));
        } else if (data.type === 'ANIMATION') {
          window.dispatchEvent(new CustomEvent('jarvis-action', {
            detail: { action: data.action }
          }));
        }
      } catch (e) {
        console.error("Error parsing JARVIS message:", e);
      }
    };

    socket.onclose = () => {
      console.log("Disconnected from JARVIS Backend.");
      setIsConnected(false);
    };

    return () => socket.close();
  }, []);

  return { lastResponse, currentEmotion, isConnected };
}
