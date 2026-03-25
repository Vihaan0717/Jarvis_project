import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Cloud, Newspaper, Film, BarChart3, FolderOpen, Settings, ChevronRight } from "lucide-react";

type ToolPanel = "weather" | "news" | "movies" | "stats" | "files" | "settings" | null;

interface ToolboxSidebarProps {
  activePanel: ToolPanel;
  onPanelChange: (panel: ToolPanel) => void;
}

const tools = [
  { id: "weather" as ToolPanel, icon: Cloud, label: "Weather" },
  { id: "news" as ToolPanel, icon: Newspaper, label: "News" },
  { id: "movies" as ToolPanel, icon: Film, label: "Movies" },
  { id: "stats" as ToolPanel, icon: BarChart3, label: "Stats" },
  { id: "files" as ToolPanel, icon: FolderOpen, label: "Files" },
  { id: "settings" as ToolPanel, icon: Settings, label: "Settings" },
];

const ToolboxSidebar = ({ activePanel, onPanelChange }: ToolboxSidebarProps) => {
  const [hovered, setHovered] = useState<ToolPanel>(null);

  return (
    <motion.div
      className="fixed left-0 top-1/2 -translate-y-1/2 z-40 flex items-center"
      initial={{ x: -60 }}
      animate={{ x: 0 }}
      transition={{ delay: 0.2, type: "spring", stiffness: 100 }}
    >
      <div className="glass-card p-2 rounded-r-xl rounded-l-none flex flex-col gap-1">
        {tools.map((tool) => (
          <motion.button
            key={tool.id}
            onMouseEnter={() => setHovered(tool.id)}
            onMouseLeave={() => setHovered(null)}
            onClick={() => onPanelChange(activePanel === tool.id ? null : tool.id)}
            className={`relative p-3 rounded-lg transition-colors ${
              activePanel === tool.id
                ? "bg-primary/20 text-primary"
                : "text-muted-foreground hover:text-foreground hover:bg-muted/50"
            }`}
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
          >
            <tool.icon className="w-5 h-5" />

            {/* Tooltip */}
            <AnimatePresence>
              {hovered === tool.id && (
                <motion.div
                  className="absolute left-full ml-2 top-1/2 -translate-y-1/2 glass-card px-3 py-1.5 whitespace-nowrap"
                  initial={{ opacity: 0, x: -5 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -5 }}
                >
                  <span className="font-mono text-xs text-foreground">{tool.label}</span>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.button>
        ))}
      </div>

      {/* Active indicator */}
      {activePanel && (
        <motion.div
          className="ml-1 text-primary"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <ChevronRight className="w-3 h-3" />
        </motion.div>
      )}
    </motion.div>
  );
};

export default ToolboxSidebar;
export type { ToolPanel };
