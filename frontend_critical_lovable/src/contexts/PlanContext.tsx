import { createContext, useContext, useState, type ReactNode } from "react";

export type PlanName = "Free" | "Pro" | "Premium";

interface PlanContextType {
  currentPlan: PlanName;
  setCurrentPlan: (plan: PlanName) => void;
  renewalDate: Date | null;
}

const PlanContext = createContext<PlanContextType | undefined>(undefined);

export const PlanProvider = ({ children }: { children: ReactNode }) => {
  const [currentPlan, setCurrentPlanState] = useState<PlanName>("Free");
  const [renewalDate, setRenewalDate] = useState<Date | null>(null);

  const setCurrentPlan = (plan: PlanName) => {
    setCurrentPlanState(plan);
    if (plan === "Free") {
      setRenewalDate(null);
    } else {
      // Set renewal to same day next month
      const now = new Date();
      const renewal = new Date(now.getFullYear(), now.getMonth() + 1, now.getDate());
      setRenewalDate(renewal);
    }
  };

  return (
    <PlanContext.Provider value={{ currentPlan, setCurrentPlan, renewalDate }}>
      {children}
    </PlanContext.Provider>
  );
};

export const usePlan = () => {
  const ctx = useContext(PlanContext);
  if (!ctx) throw new Error("usePlan must be used within PlanProvider");
  return ctx;
};
