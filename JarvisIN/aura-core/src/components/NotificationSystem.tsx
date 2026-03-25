import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { AlertCircle, FileText, Bell, X } from "lucide-react";

interface Notification {
  id: string;
  type: "info" | "warning" | "file";
  message: string;
  time: string;
}

const mockNotifications: Notification[] = [
  { id: "1", type: "file", message: "main.py modified", time: "2s ago" },
  { id: "2", type: "info", message: "Build completed successfully", time: "1m ago" },
  { id: "3", type: "warning", message: "High memory usage detected", time: "5m ago" },
];

const NotificationSystem = () => {
  const [notifications, setNotifications] = useState<Notification[]>([]);

  useEffect(() => {
    // Simulate notifications arriving
    const timeouts = mockNotifications.map((notif, idx) =>
      setTimeout(() => {
        setNotifications((prev) => [...prev, notif]);
      }, (idx + 1) * 3000)
    );
    return () => timeouts.forEach(clearTimeout);
  }, []);

  const dismiss = (id: string) => {
    setNotifications((prev) => prev.filter((n) => n.id !== id));
  };

  const iconMap = {
    info: Bell,
    warning: AlertCircle,
    file: FileText,
  };

  const colorMap = {
    info: "text-primary",
    warning: "text-secondary",
    file: "text-primary",
  };

  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col-reverse gap-2 w-72">
      <AnimatePresence>
        {notifications.map((notif) => {
          const Icon = iconMap[notif.type];
          return (
            <motion.div
              key={notif.id}
              className="glass-card p-3 flex items-center gap-3"
              initial={{ opacity: 0, y: 20, scale: 0.9 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: 20, scale: 0.9 }}
              layout
            >
              <Icon className={`w-4 h-4 ${colorMap[notif.type]} shrink-0`} />
              <div className="flex-1 min-w-0">
                <p className="text-xs text-foreground">{notif.message}</p>
                <p className="font-mono text-[10px] text-muted-foreground">{notif.time}</p>
              </div>
              <button onClick={() => dismiss(notif.id)} className="text-muted-foreground hover:text-foreground transition-colors">
                <X className="w-3 h-3" />
              </button>
            </motion.div>
          );
        })}
      </AnimatePresence>
    </div>
  );
};

export default NotificationSystem;
