import { SearchCheck, Settings, X, ChevronRight, Crown, Zap, Sparkles, BookOpen } from "lucide-react";
import { useRef, useMemo } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { usePlan } from "@/contexts/PlanContext";
import { useLanguage, LANGUAGES } from "@/contexts/LanguageContext";

interface ProfilePanelProps {
  isOpen: boolean;
  onClose: () => void;
}

const ProfilePanel = ({ isOpen, onClose }: ProfilePanelProps) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { currentPlan } = usePlan();
  const { language } = useLanguage();
  const currentLang = LANGUAGES.find(l => l.code === language) || LANGUAGES[0];
  const dailyCreditsUsed = 2;
  const dailyCreditsTotal = currentPlan === "Free" ? 5 : currentPlan === "Pro" ? 15 : 50;

  // Randomize rotation & speed on each open
  const openCountRef = useRef(0);
  if (isOpen) openCountRef.current;
  const motion = useMemo(() => {
    void openCountRef.current;
    const rot = -2 - Math.random() * 6;
    const exitRot = 10 + Math.random() * 15;
    const dur = 400 + Math.random() * 200;
    return { rot, exitRot, dur };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOpen]);

  return (
    <>
      {isOpen && <div className="fixed inset-0 bg-black/50 z-50 animate-fade-in overflow-hidden" style={{ touchAction: "none" }} onClick={onClose} />}

      <div
        className={`fixed z-[60] transition-all ${
          isOpen ? "opacity-100 scale-100" : "opacity-0 scale-95 pointer-events-none"
        }`}
        style={{
          top: "60px",
          right: "24px",
          transitionDuration: `${motion.dur}ms`,
          transitionTimingFunction: "cubic-bezier(0.16, 1, 0.3, 1)",
          transform: isOpen
            ? `translateX(0) rotate(${motion.rot}deg)`
            : `translateX(400px) rotate(${motion.exitRot}deg)`,
        }}
      >
        <div
          className="absolute inset-0 rounded-sm"
          style={{
            background: "hsl(25 20% 20% / 0.12)",
            filter: "blur(16px)",
            transform: "translate(6px, 8px) rotate(-0.5deg)",
          }}
        />

        <div
          className="relative w-72 bg-[hsl(var(--paper))] border border-border rounded-sm overflow-hidden"
          style={{
            backgroundImage:
              "url(\"data:image/svg+xml,%3Csvg width='100' height='100' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100' height='100' filter='url(%23n)' opacity='0.05'/%3E%3C/svg%3E\")",
          }}
        >
          <div className="flex items-center justify-center gap-6 py-3.5 border-b border-dashed border-rule relative">
            {[0, 1, 2].map((i) => (
              <div key={i} className="relative">
                <div
                  className="w-4 h-4 rounded-full border border-[hsl(var(--rule))]"
                  style={{
                    background: "linear-gradient(135deg, hsl(25 15% 78% / 0.5) 0%, hsl(30 12% 70% / 0.4) 100%)",
                  }}
                />
                <div
                  className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-1.5 h-1.5 rounded-full bg-transparent"
                  style={{ boxShadow: "inset 0 1px 2px hsl(25 20% 20% / 0.3)" }}
                />
              </div>
            ))}
            <button
              onClick={(e) => {
                e.stopPropagation();
                onClose();
              }}
              className="absolute right-3 top-1/2 -translate-y-1/2 w-7 h-7 flex items-center justify-center rounded-full bg-transparent z-50 cursor-pointer group/close active:scale-90 transition-transform"
            >
              <X className="w-3.5 h-3.5 text-muted-foreground group-hover/close:text-foreground active:text-[hsl(var(--ink))] transition-colors" />
            </button>
          </div>

          <div className="px-5 py-4 flex flex-col">
            <div className="mb-5">
              <h2 className="font-display text-xl font-bold text-foreground">Téo</h2>
              <div className="mt-1 w-10 h-0.5 bg-[hsl(var(--rule))]" />
            </div>

            {currentPlan === "Premium" || currentPlan === "Pro" ? (
              <div className="mb-4">
                <span className="font-ui text-[10px] uppercase tracking-wider text-muted-foreground font-semibold">
                  CRÉDITS JOURNALIERS
                </span>
                <div className="flex items-center gap-2.5 mt-2">
                  <div className="flex-1 h-2 rounded-full bg-[hsl(var(--rule)/0.3)] overflow-hidden">
                    <div
                      className="h-full rounded-full bg-[hsl(var(--accent))] transition-all"
                      style={{ width: `${((dailyCreditsTotal - dailyCreditsUsed) / dailyCreditsTotal) * 100}%` }}
                    />
                  </div>
                  <span className="font-ui text-xs text-muted-foreground whitespace-nowrap">
                    {dailyCreditsTotal - dailyCreditsUsed}/{dailyCreditsTotal}
                  </span>
                </div>
              </div>
            ) : (
              <div className="mb-4">
                <span className="font-ui text-[10px] uppercase tracking-wider text-muted-foreground font-semibold">
                  CRÉDITS JOURNALIERS
                </span>
                <div className="flex items-center gap-1.5 mt-1.5">
                  {Array.from({ length: dailyCreditsTotal }).map((_, i) => (
                    <SearchCheck
                      key={i}
                      className={`w-4 h-4 transition-colors ${
                        i < dailyCreditsUsed
                          ? "text-[hsl(var(--accent))] fill-[hsl(var(--accent))]"
                          : "text-[hsl(var(--rule))]"
                      }`}
                      strokeWidth={i < dailyCreditsUsed ? 2 : 1.5}
                    />
                  ))}
                  <span className="ml-1.5 font-ui text-xs text-muted-foreground">
                    {dailyCreditsUsed}/{dailyCreditsTotal}
                  </span>
                </div>
              </div>
            )}

            <div
              className="w-full h-px bg-[hsl(var(--rule))] mb-3"
              style={{
                maskImage:
                  "url(\"data:image/svg+xml,%3Csvg width='200' height='2' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M0,1 Q10,0 20,1 T40,1 T60,1 T80,1 T100,1 T120,1 T140,1 T160,1 T180,1 T200,1' stroke='black' fill='none' stroke-width='2'/%3E%3C/svg%3E\")",
                WebkitMaskImage:
                  "url(\"data:image/svg+xml,%3Csvg width='200' height='2' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M0,1 Q10,0 20,1 T40,1 T60,1 T80,1 T100,1 T120,1 T140,1 T160,1 T180,1 T200,1' stroke='black' fill='none' stroke-width='2'/%3E%3C/svg%3E\")",
              }}
            />

            {/* Plan */}
            <button
              onClick={() => { onClose(); if (location.pathname !== "/plans") navigate("/plans"); }}
              className="w-full flex items-center justify-between px-2 py-2.5 rounded-sm hover:bg-[hsl(var(--highlight))] transition-colors group mb-1"
            >
              <div className="flex items-center gap-2.5">
                {currentPlan === "Premium" ? <Crown className="w-3.5 h-3.5 text-muted-foreground group-hover:text-foreground transition-colors" /> : currentPlan === "Pro" ? <Zap className="w-3.5 h-3.5 text-muted-foreground group-hover:text-foreground transition-colors" /> : <Sparkles className="w-3.5 h-3.5 text-muted-foreground group-hover:text-foreground transition-colors" />}
                <span className="font-ui text-sm text-foreground">{currentPlan} Plan</span>
              </div>
              <ChevronRight className="w-3.5 h-3.5 text-muted-foreground group-hover:text-foreground transition-colors" />
            </button>

            {/* Notre approche */}
            <button
              onClick={() => { onClose(); navigate("/approach"); }}
              className="w-full flex items-center justify-between px-2 py-2.5 rounded-sm hover:bg-[hsl(var(--highlight))] transition-colors group mb-1"
            >
              <div className="flex items-center gap-2.5">
                <BookOpen className="w-3.5 h-3.5 text-muted-foreground group-hover:text-foreground transition-colors" />
                <span className="font-ui text-sm text-foreground">Notre approche</span>
              </div>
              <ChevronRight className="w-3.5 h-3.5 text-muted-foreground group-hover:text-foreground transition-colors" />
            </button>

            <div className="w-full h-px bg-[hsl(var(--rule))] my-1.5" />

            {/* Settings */}
            <button
              onClick={() => { onClose(); if (location.pathname !== "/settings") navigate("/settings"); }}
              className="w-full flex items-center gap-2.5 px-2 py-2.5 rounded-sm hover:bg-[hsl(var(--highlight))] transition-colors group"
            >
              <Settings className="w-3.5 h-3.5 text-muted-foreground group-hover:text-foreground transition-colors" />
              <span className="font-ui text-sm text-foreground">Paramètres</span>
            </button>
          </div>
        </div>
      </div>
    </>
  );
};

export default ProfilePanel;
