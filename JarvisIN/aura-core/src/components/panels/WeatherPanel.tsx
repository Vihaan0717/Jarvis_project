import { motion } from "framer-motion";
import { Cloud, Droplets, Wind, Thermometer, Sun } from "lucide-react";

interface WeatherProps {
  data?: {
    location: string;
    temperature: number;
    description: string;
    humidity: number;
    wind_speed: number;
    feels_like: number;
  };
}

const WeatherPanel = ({ data }: WeatherProps) => {
  return (
    <motion.div
      className="glass-card p-5 w-72"
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
    >
      <div className="flex items-center gap-2 mb-4">
        <Sun className="w-4 h-4 text-primary" />
        <h3 className="font-mono text-xs text-primary tracking-widest uppercase">Weather</h3>
      </div>

      <div className="text-center mb-4">
        <div className="text-5xl font-light text-foreground">{Math.round(data?.temperature || 0)}°</div>
        <div className="text-sm text-muted-foreground mt-1">{data?.location || "Unknown City"}</div>
        <div className="text-xs text-muted-foreground">{data?.description || "Standby"}</div>
      </div>

      <div className="grid grid-cols-3 gap-3 pt-3 border-t border-border">
        <div className="text-center">
          <Wind className="w-4 h-4 text-primary mx-auto mb-1" />
          <div className="font-mono text-xs text-foreground">{data?.wind_speed || 0} km/h</div>
          <div className="font-mono text-[10px] text-muted-foreground">Wind</div>
        </div>
        <div className="text-center">
          <Droplets className="w-4 h-4 text-secondary mx-auto mb-1" />
          <div className="font-mono text-xs text-foreground">{data?.humidity || 0}%</div>
          <div className="font-mono text-[10px] text-muted-foreground">Humidity</div>
        </div>
        <div className="text-center">
          <Thermometer className="w-4 h-4 text-primary mx-auto mb-1" />
          <div className="font-mono text-xs text-foreground">{Math.round(data?.feels_like || 0)}°</div>
          <div className="font-mono text-[10px] text-muted-foreground">Feels</div>
        </div>
      </div>
    </motion.div>
  );
};

export default WeatherPanel;
