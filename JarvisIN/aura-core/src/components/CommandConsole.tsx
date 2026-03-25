import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Send, Copy, Check, Terminal } from "lucide-react";

interface CommandConsoleProps {
  onCommand?: (cmd: string) => void;
  result?: string;
}

const CommandConsole = ({ onCommand, result }: CommandConsoleProps) => {
  const [input, setInput] = useState("");
  const [history, setHistory] = useState<{ type: "input" | "output"; text: string }[]>([
    { type: "output", text: '> JARVIS-X v2.1.0 initialized. Awaiting commands...' },
  ]);
  const [copied, setCopied] = useState<number | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Scroll to bottom when history changes
  const scrollRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [history]);

  // Handle incoming AI results
  useEffect(() => {
    if (result) {
      setHistory((prev) => [
        ...prev,
        { type: "output", text: result },
      ]);
    }
  }, [result]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    setHistory((prev) => [
      ...prev,
      { type: "input", text: input },
    ]);
    onCommand?.(input);
    setInput("");
  };

  const handleCopy = (text: string, idx: number) => {
    navigator.clipboard.writeText(text);
    setCopied(idx);
    setTimeout(() => setCopied(null), 2000);
  };

  return (
    <motion.div
      className="fixed bottom-6 left-1/2 -translate-x-1/2 z-40 w-full max-w-2xl px-4"
      initial={{ y: 50, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ delay: 0.5, duration: 0.6 }}
    >
      <div className="glass-card p-4 glow-cyan" style={{ boxShadow: '0 0 30px hsl(184 100% 50% / 0.15)' }}>
        {/* History */}
        <div ref={scrollRef} className="max-h-40 overflow-y-auto mb-3 space-y-1.5 scrollbar-thin scrollbar-thumb-primary/20">
          <AnimatePresence>
            {history.map((item, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 5 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex items-start gap-2 group"
              >
                <span className={`font-mono text-xs leading-relaxed ${item.type === "input" ? "text-primary" : "text-muted-foreground"}`}>
                  {item.type === "input" ? "❯ " : "  "}
                  {item.text}
                </span>
                {item.type === "output" && (
                  <button
                    onClick={() => handleCopy(item.text, idx)}
                    className="opacity-0 group-hover:opacity-100 transition-opacity ml-auto shrink-0"
                  >
                    {copied === idx ? (
                      <Check className="w-3 h-3 text-primary" />
                    ) : (
                      <Copy className="w-3 h-3 text-muted-foreground" />
                    )}
                  </button>
                )}
              </motion.div>
            ))}
          </AnimatePresence>
        </div>

        {/* Input */}
        <form onSubmit={handleSubmit} className="flex items-center gap-3">
          <Terminal className="w-4 h-4 text-primary shrink-0" />
          <input
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Enter command..."
            className="flex-1 bg-transparent font-mono text-sm text-foreground placeholder:text-muted-foreground outline-none"
          />
          <button type="submit" className="text-primary hover:text-primary/80 transition-colors">
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </motion.div>
  );
};

export default CommandConsole;
