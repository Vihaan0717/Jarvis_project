import { motion } from "framer-motion";
import { Film, Star } from "lucide-react";

const mockMovies = [
  { title: "Nexus", rating: 8.7, genre: "Sci-Fi", year: 2026 },
  { title: "Echoes of Mars", rating: 8.2, genre: "Drama", year: 2026 },
  { title: "The Algorithm", rating: 7.9, genre: "Thriller", year: 2026 },
  { title: "Phantom Code", rating: 8.5, genre: "Action", year: 2025 },
  { title: "Synthetic Dreams", rating: 7.6, genre: "Sci-Fi", year: 2026 },
  { title: "Dark Signal", rating: 8.1, genre: "Mystery", year: 2025 },
];

interface MoviesProps {
  movies?: any[];
}

const MoviesPanel = ({ movies }: MoviesProps) => {
  const displayMovies = movies && movies.length > 0 ? movies : [
    { title: "Nexus", rating: 8.7, genre: "Sci-Fi", year: 2026 },
    { title: "Echoes of Mars", rating: 8.2, genre: "Drama", year: 2026 },
  ];

  return (
    <motion.div
      className="glass-card p-5 w-80"
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
    >
      <div className="flex items-center gap-2 mb-4">
        <Film className="w-4 h-4 text-primary" />
        <h3 className="font-mono text-xs text-primary tracking-widest uppercase">Trending</h3>
      </div>

      <div className="grid grid-cols-2 gap-3 max-h-80 overflow-y-auto pr-1">
        {displayMovies.map((movie, idx) => (
          <motion.div
            key={idx}
            className="glass-card p-3 cursor-pointer hover:border-primary/30 transition-colors group"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: idx * 0.08 }}
            whileHover={{ scale: 1.03 }}
          >
            <div className="w-full h-20 rounded-md mb-2 flex items-center justify-center"
              style={{
                background: `linear-gradient(135deg, hsl(${184 + idx * 20} 40% 20%), hsl(${234 + idx * 15} 30% 15%))`,
              }}
            >
              <Film className="w-6 h-6 text-primary/40" />
            </div>
            <p className="text-xs text-foreground font-medium truncate">{movie.title}</p>
            <div className="flex items-center justify-between mt-1">
              <span className="font-mono text-[10px] text-muted-foreground">{movie.genre}</span>
              <div className="flex items-center gap-0.5">
                <Star className="w-2.5 h-2.5 text-primary fill-primary" />
                <span className="font-mono text-[10px] text-primary">{movie.rating}</span>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
};

export default MoviesPanel;
