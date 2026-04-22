import { createContext, useContext, useState, type ReactNode } from "react";

export type LangCode = "fr" | "en" | "es" | "de";

export const LANGUAGES = [
  { code: "fr" as const, label: "Français" },
  { code: "en" as const, label: "English" },
  { code: "es" as const, label: "Español" },
  { code: "de" as const, label: "Deutsch" },
];

interface LanguageContextType {
  language: LangCode;
  setLanguage: (lang: LangCode) => void;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export const LanguageProvider = ({ children }: { children: ReactNode }) => {
  const [language, setLanguage] = useState<LangCode>("fr");
  return (
    <LanguageContext.Provider value={{ language, setLanguage }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => {
  const ctx = useContext(LanguageContext);
  if (!ctx) throw new Error("useLanguage must be used within LanguageProvider");
  return ctx;
};
