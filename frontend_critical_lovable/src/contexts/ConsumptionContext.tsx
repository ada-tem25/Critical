import { createContext, useContext, useState, type ReactNode } from "react";

export type ConsumptionMode = "economy" | "precision";

interface ConsumptionContextType {
  mode: ConsumptionMode;
  setMode: (mode: ConsumptionMode) => void;
}

const ConsumptionContext = createContext<ConsumptionContextType | undefined>(undefined);

export const ConsumptionProvider = ({ children }: { children: ReactNode }) => {
  const [mode, setMode] = useState<ConsumptionMode>("economy");
  return (
    <ConsumptionContext.Provider value={{ mode, setMode }}>
      {children}
    </ConsumptionContext.Provider>
  );
};

export const useConsumption = () => {
  const ctx = useContext(ConsumptionContext);
  if (!ctx) throw new Error("useConsumption must be used within ConsumptionProvider");
  return ctx;
};
