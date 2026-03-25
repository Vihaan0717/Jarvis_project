import { motion, useSpring, useTransform } from "framer-motion";
import { useEffect } from "react";
import { Activity, Cpu, HardDrive, Battery, BatteryCharging, Zap, Shield, Database } from "lucide-react";

interface OSHealthProps {
  data?: {
    active_window: string;
    cpu_percent: number;
    memory_percent: number;
    battery_percent?: number;
    is_plugged_in?: boolean;
    biological_state?: string;
  };
  config?: {
    environment: string;
    model: string;
  };
}

const OSHealthWidget = ({ data, config }: OSHealthProps) => {
  // Spring configurations for smooth, non-glitchy transitions
  const springConfig = { damping: 20, stiffness: 100, mass: 0.5 };
  const cpuSpring = useSpring(0, springConfig);
  const memSpring = useSpring(0, springConfig);
  const batSpring = useSpring(100, springConfig);

  useEffect(() => {
    cpuSpring.set(data?.cpu_percent || 0);
    memSpring.set(data?.memory_percent || 0);
    batSpring.set(data?.battery_percent ?? 100);
  }, [data, cpuSpring, memSpring, batSpring]);

  const stats = {
    isPluggedIn: data?.is_plugged_in ?? true,
    state: data?.biological_state || "System Nominal",
    activity: data?.active_window || "Standby",
  };

  const StatBar = ({ label, springValue, icon: Icon, colorClass = "" }: { label: string; springValue: any; icon: any; colorClass?: string }) => {
    const width = useTransform(springValue, (v: number) => `${Math.min(100, Math.max(0, v))}%`);
    const displayValue = useTransform(springValue, (v: number) => Math.round(v));
    
    return (
      <div className="flex items-center gap-2">
        <Icon className={`w-3 h-3 shrink-0 ${colorClass || "text-primary"}`} />
        <span className="font-mono text-[10px] text-muted-foreground w-12 uppercase tracking-tighter">{label}</span>
        <div className="flex-1 h-1.5 rounded-full bg-muted overflow-hidden">
          <motion.div
            className="h-full rounded-full"
            style={{ 
              width,
              background: "hsl(184 100% 50%)", // Default color
            }}
          />
        </div>
        <motion.span className="font-mono text-[10px] text-muted-foreground w-8 text-right">
          {displayValue}
        </motion.span>
      </div>
    );
  };

  return (
    <motion.div
      className="glass-card p-4 w-72"
      initial={{ opacity: 0, x: 30 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: 0.3 }}
    >
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Activity className="w-3.5 h-3.5 text-primary" />
          <h3 className="font-mono text-[10px] text-primary tracking-widest uppercase">System Awareness</h3>
        </div>
        <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-primary/10 border border-primary/20">
          <Shield className="w-2.5 h-2.5 text-primary" />
          <span className="font-mono text-[9px] text-primary uppercase">{config?.environment || "DEV"}</span>
        </div>
      </div>

      <div className="space-y-3">
        <StatBar label="CPU" springValue={cpuSpring} icon={Cpu} />
        <StatBar label="MEM" springValue={memSpring} icon={HardDrive} />
        <StatBar 
          label="PWR" 
          springValue={batSpring}
          icon={stats.isPluggedIn ? BatteryCharging : Battery} 
          colorClass={stats.isPluggedIn ? "text-yellow-400" : ""}
        />
      </div>

      <div className="mt-4 pt-3 border-t border-white/5 space-y-2.5">
        <div className="flex items-start gap-2">
          <Zap className="w-3 h-3 text-primary mt-0.5 shrink-0" />
          <div className="flex flex-col gap-0.5">
            <span className="font-mono text-[9px] text-muted-foreground uppercase leading-none">Biological State</span>
            <span className={`font-mono text-[10px] uppercase tracking-wide ${stats.state.includes("Stressed") ? "text-red-400" : "text-primary"}`}>
              {stats.state}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-2 px-2 py-1.5 rounded bg-black/20 border border-white/5">
          <Database className="w-2.5 h-2.5 text-muted-foreground" />
          <span className="font-mono text-[9px] text-muted-foreground uppercase truncate">
            Model: <span className="text-white/70">{config?.model || "LLAMA 3.2"}</span>
          </span>
        </div>

        <div className="flex items-center gap-2 opacity-80 text-muted-foreground">
          <div className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse-glow" />
          <span className="font-mono text-[9px] truncate" title={stats.activity}>
             Focus: {stats.activity}
          </span>
        </div>
      </div>
    </motion.div>
  );
};

export default OSHealthWidget;
