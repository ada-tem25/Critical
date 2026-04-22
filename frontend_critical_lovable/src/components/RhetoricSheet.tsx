import type { RhetoricFallacy } from "@/data/rhetoric";
import type { RhetoricSide } from "@/contexts/RhetoricContext";
import { AlertTriangle, X } from "lucide-react";
import { useRef, useMemo, useEffect, useState } from "react";

interface Props {
  fallacy: RhetoricFallacy | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  side: RhetoricSide;
}

const RhetoricSheet = ({ fallacy, open, onOpenChange, side }: Props) => {
  const prevSideRef = useRef(side);
  const [skipTransition, setSkipTransition] = useState(false);

  // When side changes while closed, disable transition so it can reposition instantly
  useEffect(() => {
    if (side !== prevSideRef.current) {
      if (!open) {
        setSkipTransition(true);
        // Re-enable transition after a frame so the open animation works
        requestAnimationFrame(() => {
          requestAnimationFrame(() => {
            setSkipTransition(false);
          });
        });
      }
      prevSideRef.current = side;
    }
  }, [side, open]);

  const motion = useMemo(() => {
    const rot = side === "left" ? (0.5 + Math.random() * 2) : (-0.5 - Math.random() * 2);
    const exitRot = side === "left" ? -(6 + Math.random() * 8) : (6 + Math.random() * 8);
    const dur = 400 + Math.random() * 200;
    return { rot, exitRot, dur };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open, side]);

  useEffect(() => {
    if (open) {
      document.body.style.overflow = "hidden";
      return () => { document.body.style.overflow = ""; };
    }
  }, [open]);

  if (!fallacy) return null;

  const positionStyle = side === "left"
    ? { top: "80px", left: "24px" }
    : { top: "80px", right: "24px" };

  const exitX = side === "left" ? "-400px" : "400px";

  return (
    <>
      {/* Overlay */}
      {open && (
        <div
          className="fixed inset-0 bg-black/50 z-40 animate-fade-in overflow-hidden"
          style={{ touchAction: "none" }}
          onClick={() => onOpenChange(false)}
        />
      )}

      {/* Paper card */}
      <div
        className={`fixed z-50 ${
          open ? "opacity-100 scale-100" : "opacity-0 scale-95 pointer-events-none"
        }`}
        style={{
          ...positionStyle,
          transition: skipTransition ? "none" : `all ${motion.dur}ms cubic-bezier(0.16, 1, 0.3, 1)`,
          transform: open
            ? `translateX(0) rotate(${motion.rot}deg)`
            : `translateX(${exitX}) rotate(${motion.exitRot}deg)`,
        }}
      >
        {/* Shadow */}
        <div
          className="absolute inset-0 rounded-sm"
          style={{
            background: "hsl(25 20% 20% / 0.12)",
            filter: "blur(16px)",
            transform: "translate(6px, 8px) rotate(-0.5deg)",
          }}
        />

        {/* Main card */}
        <div
          className="relative w-80 bg-[hsl(var(--paper))] border border-border rounded-sm overflow-hidden"
          style={{
            backgroundImage:
              "url(\"data:image/svg+xml,%3Csvg width='100' height='100' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100' height='100' filter='url(%23n)' opacity='0.05'/%3E%3C/svg%3E\")",
          }}
        >
          {/* Eyelets + close */}
          <div className="flex items-center justify-center gap-6 py-3.5 border-b border-dashed border-rule relative">
            {[0, 1, 2].map((i) => (
              <div key={i} className="relative">
                <div
                  className="w-4 h-4 rounded-full border border-[hsl(var(--rule))]"
                  style={{
                    background:
                      "linear-gradient(135deg, hsl(25 15% 78% / 0.5) 0%, hsl(30 12% 70% / 0.4) 100%)",
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
                onOpenChange(false);
              }}
              className="absolute right-3 top-1/2 -translate-y-1/2 w-7 h-7 flex items-center justify-center rounded-full bg-transparent z-50 cursor-pointer group/close active:scale-90 transition-transform"
            >
              <X className="w-3.5 h-3.5 text-muted-foreground group-hover/close:text-foreground active:text-[hsl(var(--ink))] transition-colors" />
            </button>
          </div>

          {/* Content */}
          <div className="px-5 py-4">
            {/* Header */}
            <div className="flex items-center gap-2 mb-1">
              <AlertTriangle className="w-3.5 h-3.5 text-orange-600 flex-shrink-0" />
              <span className="font-ui text-[10px] font-bold tracking-widest uppercase text-orange-600">
                Rhétorique détectée
              </span>
            </div>
            <h3 className="font-display text-lg font-bold text-foreground mb-1">
              {fallacy.label}
            </h3>
            <div className="w-10 h-0.5 bg-[hsl(var(--rule))] mb-4" />

            {/* Definition */}
            <div className="mb-4">
              <span className="font-ui text-[10px] uppercase tracking-wider text-muted-foreground font-semibold">
                Définition
              </span>
              <p className="font-body text-sm leading-relaxed text-foreground mt-1.5">
                {fallacy.definition}
              </p>
            </div>

            {/* Divider */}
            <div
              className="w-full h-px bg-[hsl(var(--rule))] mb-3"
              style={{
                maskImage:
                  "url(\"data:image/svg+xml,%3Csvg width='200' height='2' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M0,1 Q10,0 20,1 T40,1 T60,1 T80,1 T100,1 T120,1 T140,1 T160,1 T180,1 T200,1' stroke='black' fill='none' stroke-width='2'/%3E%3C/svg%3E\")",
                WebkitMaskImage:
                  "url(\"data:image/svg+xml,%3Csvg width='200' height='2' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M0,1 Q10,0 20,1 T40,1 T60,1 T80,1 T100,1 T120,1 T140,1 T160,1 T180,1 T200,1' stroke='black' fill='none' stroke-width='2'/%3E%3C/svg%3E\")",
              }}
            />

            {/* Examples */}
            <div>
              <span className="font-ui text-[10px] uppercase tracking-wider text-muted-foreground font-semibold">
                {fallacy.examples.length > 1 ? "Exemples" : "Exemple"}
              </span>
              <div className="space-y-2.5 mt-1.5">
                {fallacy.examples.map((ex, i) => (
                  <blockquote
                    key={i}
                    className="border-l-2 border-orange-400/50 pl-3 py-0.5"
                  >
                    <p className="font-body text-sm leading-relaxed text-muted-foreground italic">
                      {ex}
                    </p>
                  </blockquote>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default RhetoricSheet;
