import React from "react";
import { useLanguage } from "@/contexts/LanguageContext";

const LOADING_LABELS: Record<string, string> = {
  fr: "Chargement",
  en: "Loading",
  es: "Cargando",
  de: "Laden",
};

const LoadingLines: React.FC = () => {
  const { language } = useLanguage();
  const letters = (LOADING_LABELS[language] || "Loading").split("");

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-background/80 backdrop-blur-sm">
      <div className="relative flex flex-col items-center gap-4">
        {/* Animated letters */}
        <div className="flex gap-[2px]">
          {letters.map((letter, idx) => (
            <span
              key={idx}
              className="font-display text-2xl font-bold opacity-0"
              style={{
                color: "hsl(var(--foreground))",
                animation: `letterAnim 2s ease-in-out ${idx * 0.2}s infinite`,
              }}
            >
              {letter}
            </span>
          ))}
        </div>

        {/* Loader bar */}
        <div
          className="relative w-40 h-[3px] rounded-full overflow-hidden"
          style={{ backgroundColor: "hsl(var(--rule))" }}
        >
          <div
            className="absolute inset-0 rounded-full"
            style={{
              background: `linear-gradient(90deg, transparent, hsl(var(--primary)), transparent)`,
              animation: "transformAnim 2s ease-in-out infinite",
            }}
          />
        </div>
      </div>

      <style>{`
        @keyframes transformAnim {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(100%); }
        }
        @keyframes letterAnim {
          0% { opacity: 0; }
          5% { opacity: 1; text-shadow: 0 0 4px hsl(var(--primary) / 0.4); transform: scale(1.1) translateY(-2px); }
          20% { opacity: 0.2; }
          100% { opacity: 0; }
        }
      `}</style>
    </div>
  );
};

export default LoadingLines;
