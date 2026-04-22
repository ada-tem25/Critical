import { createContext, useContext, useState, useCallback, type ReactNode } from "react";

interface PinnedArticlesContextType {
  pinnedIds: Set<string>;
  togglePin: (id: string) => void;
  isPinned: (id: string) => boolean;
}

const PinnedArticlesContext = createContext<PinnedArticlesContextType | null>(null);

export const PinnedArticlesProvider = ({ children }: { children: ReactNode }) => {
  const [pinnedIds, setPinnedIds] = useState<Set<string>>(() => {
    try {
      const stored = localStorage.getItem("pinned-articles");
      return stored ? new Set(JSON.parse(stored)) : new Set<string>();
    } catch {
      return new Set<string>();
    }
  });

  const togglePin = useCallback((id: string) => {
    setPinnedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      localStorage.setItem("pinned-articles", JSON.stringify([...next]));
      return next;
    });
  }, []);

  const isPinned = useCallback((id: string) => pinnedIds.has(id), [pinnedIds]);

  return (
    <PinnedArticlesContext.Provider value={{ pinnedIds, togglePin, isPinned }}>
      {children}
    </PinnedArticlesContext.Provider>
  );
};

export const usePinnedArticles = () => {
  const ctx = useContext(PinnedArticlesContext);
  if (!ctx) throw new Error("usePinnedArticles must be used within PinnedArticlesProvider");
  return ctx;
};
