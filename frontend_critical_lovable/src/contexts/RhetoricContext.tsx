import React, { createContext, useContext, useState, useCallback, useRef } from "react";
import type { RhetoricFallacy } from "@/data/rhetoric";
import { getFallacy } from "@/data/rhetoric";
import RhetoricSheet from "@/components/RhetoricSheet";

export type RhetoricSide = "left" | "right";

interface RhetoricContextType {
  openFallacy: (name: string, side?: RhetoricSide) => void;
}

const RhetoricContext = createContext<RhetoricContextType>({ openFallacy: () => {} });

export const useRhetoric = () => useContext(RhetoricContext);

export const RhetoricProvider = ({ children }: { children: React.ReactNode }) => {
  const [activeFallacy, setActiveFallacy] = useState<RhetoricFallacy | null>(null);
  const [open, setOpen] = useState(false);
  const [side, setSide] = useState<RhetoricSide>("right");
  const openRef = useRef(false);
  const timerRef = useRef<number | null>(null);

  // Keep ref in sync
  openRef.current = open;

  const openFallacy = useCallback((name: string, s: RhetoricSide = "right") => {
    const f = getFallacy(name);
    if (!f) return;

    // Clear any pending timer
    if (timerRef.current) {
      clearTimeout(timerRef.current);
      timerRef.current = null;
    }

    if (openRef.current) {
      // Close first, then reopen with new data after close animation
      setOpen(false);
      timerRef.current = window.setTimeout(() => {
        setActiveFallacy(f);
        setSide(s);
        requestAnimationFrame(() => {
          requestAnimationFrame(() => setOpen(true));
        });
      }, 350);
    } else {
      // Set data first, then open on next frames so DOM paints closed position
      setActiveFallacy(f);
      setSide(s);
      requestAnimationFrame(() => {
        requestAnimationFrame(() => setOpen(true));
      });
    }
  }, []);

  return (
    <RhetoricContext.Provider value={{ openFallacy }}>
      {children}
      <RhetoricSheet fallacy={activeFallacy} open={open} onOpenChange={setOpen} side={side} />
    </RhetoricContext.Provider>
  );
};
