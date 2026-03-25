import { useState, useMemo } from "react";
import { AnimatePresence, motion } from "framer-motion";
import JarvisAvatar from "@/components/JarvisAvatar";
import CommandConsole from "@/components/CommandConsole";
import OSHealthWidget from "@/components/OSHealthWidget";
import ToolboxSidebar, { type ToolPanel } from "@/components/ToolboxSidebar";
import NotificationSystem from "@/components/NotificationSystem";
import DesktopOverlayToggle from "@/components/DesktopOverlayToggle";
import AvatarStateControls from "@/components/AvatarStateControls";
import WeatherPanel from "@/components/panels/WeatherPanel";
import NewsPanel from "@/components/panels/NewsPanel";
import MoviesPanel from "@/components/panels/MoviesPanel";
import FileExplorer from "@/components/panels/FileExplorer";
import { useJarvisSocket } from "@/hooks/useJarvisSocket";
import { RefreshCw } from "lucide-react";

const Index = () => {
  const { data, avatarState, setAvatarState, sendCommand } = useJarvisSocket();
  const [activePanel, setActivePanel] = useState<ToolPanel>(null);
  const [overlayMode, setOverlayMode] = useState(false);

  const renderPanel = () => {
    switch (activePanel) {
      case "weather": return <WeatherPanel data={data.weather} />;
      case "news": return <NewsPanel news={data.news} />;
      case "movies": return <MoviesPanel movies={data.movies} />;
      case "files": return <FileExplorer onAction={(action, params) => sendCommand("PROJECT_COMMAND", { action, parameters: params })} />;
      default: return null;
    }
  };

  return (
    <div
      className={`relative min-h-screen overflow-hidden transition-colors duration-500 ${
        overlayMode ? "bg-transparent" : ""
      }`}
      style={
        overlayMode
          ? { background: "transparent" }
          : {
              background: "linear-gradient(135deg, hsl(234 33% 5%) 0%, hsl(234 33% 8%) 50%, hsl(234 33% 5%) 100%)",
            }
      }
    >
      {/* Ambient background effects */}
      {!overlayMode && (
        <>
          <div
            className="fixed inset-0 pointer-events-none"
            style={{
              background:
                "radial-gradient(ellipse at 20% 50%, hsl(184 100% 50% / 0.03) 0%, transparent 50%), radial-gradient(ellipse at 80% 20%, hsl(278 99% 54% / 0.03) 0%, transparent 50%)",
            }}
          />
          {/* Grid overlay */}
          <div
            className="fixed inset-0 pointer-events-none opacity-[0.03]"
            style={{
              backgroundImage: `linear-gradient(hsl(184 100% 50% / 0.3) 1px, transparent 1px), linear-gradient(90deg, hsl(184 100% 50% / 0.3) 1px, transparent 1px)`,
              backgroundSize: "60px 60px",
            }}
          />
        </>
      )}

      {/* Header */}
      <motion.div
        className="fixed top-4 left-1/2 -translate-x-1/2 z-50 flex items-center gap-3"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="w-2 h-2 rounded-full bg-primary animate-pulse-glow" />
        <h1 className="font-mono text-sm tracking-[0.3em] text-primary uppercase glow-text-cyan">
          JARVIS-X
        </h1>
        <div className="w-2 h-2 rounded-full bg-primary animate-pulse-glow" />
      </motion.div>

      {/* Desktop Overlay Toggle */}
      <DesktopOverlayToggle enabled={overlayMode} onToggle={() => setOverlayMode(!overlayMode)} />

      {/* OS Health Widget */}
      <div className="fixed top-14 right-4 z-30">
        <OSHealthWidget data={data.os_context} config={data.system_config} />
      </div>

      {/* Avatar Background */}
      <JarvisAvatar state={avatarState} tracking={data.tracking} audioAmplitude={data.audioAmplitude} />

      {/* Header */}
      <ToolboxSidebar activePanel={activePanel} onPanelChange={setActivePanel} />

      {/* Active Panel */}
      <AnimatePresence mode="wait">
        {activePanel && (
          <motion.div
            key={activePanel}
            className="fixed left-16 top-1/2 -translate-y-1/2 z-30"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            {renderPanel()}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Notifications */}
      <NotificationSystem />

      {/* Command Console */}
      <CommandConsole 
        onCommand={(cmd) => sendCommand("GET_CODE_GEN", { prompt: cmd })} 
        result={data.code_result}
      />

      {/* Global Refresh Button */}
      <motion.button
        className="fixed bottom-6 right-6 z-50 p-3 rounded-full bg-black/40 backdrop-blur-md border border-primary/20 text-primary hover:bg-primary/10 hover:border-primary/40 transition-all pointer-events-auto glow-border-cyan"
        whileHover={{ scale: 1.1, rotate: 180 }}
        whileTap={{ scale: 0.9 }}
        onClick={() => window.location.reload()}
        title="Refresh Interface"
      >
        <RefreshCw size={18} />
      </motion.button>
    </div>
  );
};

export default Index;
