import { memo } from "react";
import { motion } from "framer-motion";
import JarvisVRM from "./JarvisVRM";

type AvatarState = "idle" | "listening" | "thinking" | "scanning";

interface JarvisAvatarProps {
  state?: AvatarState;
  tracking?: { headPitch: number; headYaw: number; eyePitch: number; eyeYaw: number; blinkLeft?: number; blinkRight?: number };
  audioAmplitude?: number;
}

const JarvisAvatar = memo(({ state = "idle", tracking, audioAmplitude }: JarvisAvatarProps) => {
  const ringColors: Record<AvatarState, string> = {
    idle: "hsl(184, 100%, 50%)",
    listening: "hsl(184, 100%, 50%)",
    thinking: "hsl(278, 99%, 54%)",
    scanning: "hsl(184, 100%, 50%)",
  };

  const color = ringColors[state];

  return (
    <motion.div
      className="fixed inset-0 z-0 pointer-events-none"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 1 }}
    >
      <div className="relative w-full h-full">
        {/* VRM Model - now full screen background integration */}
        <JarvisVRM state={state} tracking={tracking} audioAmplitude={audioAmplitude} />

        {/* State label - repositioned for full screen background overlay */}
        <motion.div
          className="absolute bottom-10 left-1/2 -translate-x-1/2 font-mono text-xs tracking-[0.2em] uppercase whitespace-nowrap"
          style={{ color }}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          {state === "idle" ? "STANDBY" : state.toUpperCase()}
        </motion.div>
      </div>
    </motion.div>
  );
});

export default JarvisAvatar;
