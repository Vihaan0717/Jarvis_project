import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { FolderOpen, File, Plus, Trash2, ExternalLink, Folder } from "lucide-react";

interface ProjectItem {
  id: string;
  name: string;
  type: "folder" | "file";
  modified: string;
}

interface FileExplorerProps {
  onAction?: (action: string, params: any) => void;
}

const FileExplorer = ({ onAction }: FileExplorerProps) => {
  const [items, setItems] = useState<ProjectItem[]>([
    { id: "1", name: "jarvis-core", type: "folder", modified: "2h ago" },
    { id: "2", name: "neural-engine", type: "folder", modified: "1d ago" },
    { id: "3", name: "config.yaml", type: "file", modified: "3h ago" },
    { id: "4", name: "main.py", type: "file", modified: "30m ago" },
    { id: "5", name: "api-gateway", type: "folder", modified: "5h ago" },
  ]);

  const addProject = () => {
    const name = `new-project-${items.length + 1}`;
    const newItem: ProjectItem = {
      id: Date.now().toString(),
      name: name,
      type: "folder",
      modified: "Just now",
    };
    setItems((prev) => [newItem, ...prev]);
    onAction?.("create_project", { name });
  };

  const deleteItem = (id: string, name: string) => {
    setItems((prev) => prev.filter((item) => item.id !== id));
    onAction?.("delete_project", { name });
  };

  const openIDE = (name: string) => {
    onAction?.("open_ide", { path: name });
  };

  return (
    <motion.div
      className="glass-card p-5 w-80"
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
    >
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <FolderOpen className="w-4 h-4 text-primary" />
          <h3 className="font-mono text-xs text-primary tracking-widest uppercase">Projects</h3>
        </div>
        <motion.button
          onClick={addProject}
          className="p-1.5 rounded-md bg-primary/10 text-primary hover:bg-primary/20 transition-colors"
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
        >
          <Plus className="w-3.5 h-3.5" />
        </motion.button>
      </div>

      <div className="space-y-1 max-h-72 overflow-y-auto pr-1">
        <AnimatePresence>
          {items.map((item, idx) => (
            <motion.div
              key={item.id}
              className="group flex items-center gap-3 p-2.5 rounded-lg hover:bg-muted/30 transition-colors"
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, x: -20, height: 0 }}
              transition={{ delay: idx * 0.05 }}
            >
              {item.type === "folder" ? (
                <Folder className="w-4 h-4 text-primary shrink-0" />
              ) : (
                <File className="w-4 h-4 text-muted-foreground shrink-0" />
              )}
              <div className="flex-1 min-w-0">
                <p className="text-sm text-foreground truncate">{item.name}</p>
                <p className="font-mono text-[10px] text-muted-foreground">{item.modified}</p>
              </div>
              <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <button 
                  onClick={() => openIDE(item.name)}
                  className="p-1 rounded text-muted-foreground hover:text-primary transition-colors"
                >
                  <ExternalLink className="w-3 h-3" />
                </button>
                <button
                  onClick={() => deleteItem(item.id, item.name)}
                  className="p-1 rounded text-muted-foreground hover:text-destructive transition-colors"
                >
                  <Trash2 className="w-3 h-3" />
                </button>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </motion.div>
  );
};

export default FileExplorer;
