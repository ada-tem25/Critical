import { createContext, useContext, useState, type ReactNode } from "react";

export const LOCATIONS = [
  { code: "fr", label: "France", flag: "🇫🇷" },
  { code: "gb", label: "Royaume-Uni", flag: "🇬🇧" },
  { code: "us", label: "États-Unis", flag: "🇺🇸" },
  { code: "de", label: "Allemagne", flag: "🇩🇪" },
  { code: "es", label: "Espagne", flag: "🇪🇸" },
  { code: "be", label: "Belgique", flag: "🇧🇪" },
  { code: "other", label: "Autre", flag: "🌍" },
];

interface LocationContextType {
  location: string;
  setLocation: (loc: string) => void;
}

const LocationContext = createContext<LocationContextType | undefined>(undefined);

export const LocationProvider = ({ children }: { children: ReactNode }) => {
  const [location, setLocation] = useState("fr");
  return (
    <LocationContext.Provider value={{ location, setLocation }}>
      {children}
    </LocationContext.Provider>
  );
};

export const useLocation_ = () => {
  const ctx = useContext(LocationContext);
  if (!ctx) throw new Error("useLocation_ must be used within LocationProvider");
  return ctx;
};
