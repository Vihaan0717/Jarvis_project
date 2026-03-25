import { motion } from "framer-motion";
import { Radio, Brain, ScanFace, AlertTriangle, Circle } from "lucide-react";

type AvatarState = "idle" | "listening" | "thinking" | "scanning";

interface AvatarStateControlsProps {
  currentState: AvatarState;
  onStateChange: (state: AvatarState) => void;
}

const states: { id: AvatarState; icon: typeof Circle; label: string }[] = [
  { id: "idle", icon: Circle, label: "Idle" },
  { id: "listening", icon: Radio, label: "Listen" },
  { id: "thinking", icon: Brain, label: "Think" },
  { id: "scanning", icon: ScanFace, label: "Scan" },
];

const AvatarStateControls = ({ currentState, onStateChange }: AvatarStateControlsProps) => {
  return (
    <motion.div
      className="fixed bottom-24 left-1/2 -translate-x-1/2 z-30 glass-card p-2 flex gap-1"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.8 }}
    >
      {states.map((s) => (
        <motion.button
          key={s.id}
          onClick={() => onStateChange(s.id)}
          className={`px-3 py-1.5 rounded-md font-mono text-xs flex items-center gap-1.5 transition-colors ${
            currentState === s.id
              ? "bg-primary/20 text-primary"
              : "text-muted-foreground hover:text-foreground hover:bg-muted/30"
          }`}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <s.icon className="w-3 h-3" />
          {s.label}
        </motion.button>
      ))}
    </motion.div>
  );
};

export default AvatarStateControls;
