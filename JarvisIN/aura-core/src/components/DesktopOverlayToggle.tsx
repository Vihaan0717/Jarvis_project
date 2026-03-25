import { motion } from "framer-motion";
import { Monitor } from "lucide-react";

interface DesktopOverlayToggleProps {
  enabled: boolean;
  onToggle: () => void;
}

const DesktopOverlayToggle = ({ enabled, onToggle }: DesktopOverlayToggleProps) => {
  return (
    <motion.button
      onClick={onToggle}
      className={`fixed top-4 left-4 z-50 glass-card p-2.5 flex items-center gap-2 cursor-pointer transition-colors ${
        enabled ? "border-primary/40" : ""
      }`}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <Monitor className={`w-4 h-4 ${enabled ? "text-primary" : "text-muted-foreground"}`} />
      <span className="font-mono text-xs text-muted-foreground">
        {enabled ? "OVERLAY" : "DESKTOP"}
      </span>
      <div className={`w-6 h-3 rounded-full flex items-center px-0.5 transition-colors ${
        enabled ? "bg-primary/30" : "bg-muted"
      }`}>
        <motion.div
          className={`w-2 h-2 rounded-full ${enabled ? "bg-primary" : "bg-muted-foreground"}`}
          animate={{ x: enabled ? 12 : 0 }}
          transition={{ type: "spring", stiffness: 500, damping: 30 }}
        />
      </div>
    </motion.button>
  );
};

export default DesktopOverlayToggle;
