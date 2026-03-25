import { motion } from "framer-motion";
import { Newspaper, ExternalLink } from "lucide-react";

const mockNews = [
  { title: "Quantum Computing Breakthrough: 1000-Qubit Processor Achieved", source: "TechCrunch", time: "2h ago" },
  { title: "SpaceX Mars Colony Plans Enter Phase 3 Development", source: "Reuters", time: "4h ago" },
  { title: "AI Regulation Framework Approved by G20 Nations", source: "BBC", time: "5h ago" },
  { title: "Neural Interface Allows Paralyzed Patients to Walk", source: "Nature", time: "8h ago" },
  { title: "Fusion Energy Plant Construction Begins in France", source: "Bloomberg", time: "12h ago" },
];

interface NewsProps {
  news?: any[];
}

const NewsPanel = ({ news }: NewsProps) => {
  const displayNews = news && news.length > 0 ? news : [
    { title: "Quantum Computing Breakthrough", source: "TechCrunch", time: "2h ago" },
    { title: "SpaceX Mars Colony Plans", source: "Reuters", time: "4h ago" },
  ];

  return (
    <motion.div
      className="glass-card p-5 w-80"
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
    >
      <div className="flex items-center gap-2 mb-4">
        <Newspaper className="w-4 h-4 text-primary" />
        <h3 className="font-mono text-xs text-primary tracking-widest uppercase">Headlines</h3>
      </div>

      <div className="space-y-3 max-h-80 overflow-y-auto pr-1">
        {displayNews.map((item, idx) => (
          <motion.div
            key={idx}
            className="group cursor-pointer p-2 rounded-lg hover:bg-muted/30 transition-colors"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: idx * 0.1 }}
          >
            <div className="flex items-start gap-2">
              <div className="flex-1">
                <p className="text-sm text-foreground leading-snug group-hover:text-primary transition-colors">
                  {item.title}
                </p>
                <div className="flex items-center gap-2 mt-1">
                  <span className="font-mono text-[10px] text-primary">{item.source}</span>
                  <span className="font-mono text-[10px] text-muted-foreground">{item.time}</span>
                </div>
              </div>
              <ExternalLink className="w-3 h-3 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity shrink-0 mt-1" />
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
};

export default NewsPanel;
