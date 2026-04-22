import { useState, useRef, useEffect } from "react";
import { FolderOpen, ChevronUp, Flame, Radio, Sun } from "lucide-react";
import { useNavigate } from "react-router-dom";
import ArchiveCard from "./ArchiveCard";
import { articles } from "@/data/articles";
import { TextShimmer } from "@/components/ui/text-shimmer";
import { usePinnedArticles } from "@/contexts/PinnedArticlesContext";

const FR_MONTHS: Record<string, number> = {
  "jan.": 0, "jan": 0, "janvier": 0,
  "fév.": 1, "fév": 1, "février": 1,
  "mars": 2,
  "avr.": 3, "avr": 3, "avril": 3,
  "mai": 4,
  "juin": 5,
  "juil.": 6, "juil": 6, "juillet": 6,
  "août": 7,
  "sept.": 8, "sept": 8, "septembre": 8,
  "oct.": 9, "oct": 9, "octobre": 9,
  "nov.": 10, "nov": 10, "novembre": 10,
  "déc.": 11, "déc": 11, "décembre": 11,
};

const parseFrDate = (d: string): number => {
  const parts = d.toLowerCase().trim().split(/\s+/);
  if (parts.length < 3) return 0;
  const day = parseInt(parts[0], 10);
  const month = FR_MONTHS[parts[1]] ?? 0;
  const year = parseInt(parts[2], 10);
  return new Date(year, month, day).getTime();
};

const archiveItems = articles.map((a) => ({
  id: a.id,
  title: a.title,
  author: a.author,
  date: a.date,
  verdict: a.verdict,
  summary: a.summary,
  format: a.format,
}));

const featuredItems = articles
  .filter((a) => a.featured)
  .map((a) => ({
    id: a.id,
    title: a.title,
    author: a.author,
    date: a.date,
    verdict: a.verdict,
    summary: a.summary,
    format: a.format,
  }));

export type DrawerTab = "archives" | "featured" | "live";

interface ArchivesDrawerProps {
  isOpen: boolean;
  activeTab: DrawerTab;
  onOpen: (tab: DrawerTab) => void;
  onClose: () => void;
}

const CardGrid = ({ items, animate, showPins }: { items: typeof archiveItems; animate: boolean; showPins?: boolean }) => {
  const { isPinned } = usePinnedArticles();

  // Sort: chronological (newest first), pinned on top
  const sortedItems = [...items].sort((a, b) => {
    if (showPins) {
      const ap = isPinned(a.id) ? 0 : 1;
      const bp = isPinned(b.id) ? 0 : 1;
      if (ap !== bp) return ap - bp;
    }
    return parseFrDate(b.date) - parseFrDate(a.date);
  });

  if (sortedItems.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 gap-2 min-h-[200px]">
        <Sun className="w-7 h-7 text-muted-foreground/40" />
        <p className="font-body text-sm text-muted-foreground italic text-center">
          L'actualité est calme en ce moment...
        </p>
      </div>
    );
  }

  return (
    <div className="max-h-[340px] overflow-y-auto pr-1 relative z-10 py-3">
      {/* Mobile: single column */}
      <div className="flex flex-col gap-3 md:hidden">
        {sortedItems.map((item, idx) => (
          <div
            key={item.id}
            className={animate ? "animate-fade-up" : ""}
            style={{
              ...(animate ? { animationDelay: `${idx * 80}ms`, animationFillMode: "both", opacity: 0 } : {}),
              transform: `rotate(${idx % 2 === 0 ? "-0.3" : "0.3"}deg)`,
            }}
          >
            <ArchiveCard {...item} clipType={showPins && isPinned(item.id) ? "pin" : "none"} />
          </div>
        ))}
      </div>
      {/* Desktop: two columns */}
      <div className="hidden md:grid grid-cols-2 gap-x-3 items-start">
        {(() => {
          const left = sortedItems.filter((_, i) => i % 2 === 0);
          const right = sortedItems.filter((_, i) => i % 2 === 1);
          return (
            <>
              <div className="flex flex-col gap-3">
                {left.map((item, idx) => (
                  <div
                    key={item.id}
                    className={animate ? "animate-fade-up" : ""}
                    style={{
                      ...(animate ? { animationDelay: `${idx * 2 * 80}ms`, animationFillMode: "both", opacity: 0 } : {}),
                      transform: `rotate(-0.3deg)`,
                    }}
                  >
                    <ArchiveCard {...item} clipType={showPins && isPinned(item.id) ? "pin" : "none"} />
                  </div>
                ))}
              </div>
              <div className="flex flex-col gap-3">
                {right.map((item, idx) => (
                  <div
                    key={item.id}
                    className={animate ? "animate-fade-up" : ""}
                    style={{
                      ...(animate ? { animationDelay: `${(idx * 2 + 1) * 80}ms`, animationFillMode: "both", opacity: 0 } : {}),
                      transform: `rotate(0.3deg)`,
                    }}
                  >
                    <ArchiveCard {...item} clipType={showPins && isPinned(item.id) ? "pin" : "none"} />
                  </div>
                ))}
              </div>
            </>
          );
        })()}
      </div>
    </div>
  );
};

/* ── Live streams panel ── */
const hasActiveStream = true;

const LiveStreamsPanel = ({ animate }: { animate: boolean }) => {
  const navigate = useNavigate();

  if (!hasActiveStream) {
    return (
      <div className="flex flex-col items-center justify-center py-12 gap-2 min-h-[200px]">
        <Radio className="w-7 h-7 text-muted-foreground/40" />
        <p className="font-body text-sm text-muted-foreground italic text-center">
          Aucun discours en direct dans votre pays.
        </p>
      </div>
    );
  }

  return (
    <div className="max-h-[340px] min-h-[340px] overflow-y-auto pr-1 relative z-10 py-3">
      {/* Mobile: single column */}
      <div className="flex flex-col gap-3 md:hidden">
        <div
          className={animate ? "animate-fade-up" : ""}
          style={animate ? { animationFillMode: "both", opacity: 0 } : {}}
        >
          <div
            className="cursor-pointer"
            onClick={() => navigate("/live?view=1")}
          >
            <article
              className="
                bg-[hsl(var(--paper))] rounded-sm border border-border p-4
                hover:shadow-xl hover:-translate-y-1 transition-all duration-200
                group relative
              "
              style={{
                boxShadow: "1px 2px 4px hsl(25 20% 30% / 0.08)",
                transform: "rotate(0.3deg)",
              }}
            >
              {/* Live badge */}
              <div className="absolute top-3 right-3 flex items-center gap-1.5 bg-destructive/10 border border-destructive/20 rounded-full px-2.5 py-0.5">
                <span className="w-2 h-2 rounded-full bg-destructive animate-pulse" />
                <span className="font-ui text-[10px] font-bold text-destructive uppercase tracking-wider">
                  En direct
                </span>
              </div>

              <div className="mb-3 pr-28">
                <h4 className="font-display text-base font-semibold text-foreground leading-snug group-hover:text-accent transition-colors">
                  Fact-checking du discours du premier ministre de l'économie
                </h4>
                <div className="flex items-center gap-2 mt-1.5">
                  <span className="font-ui text-xs text-muted-foreground">Discours officiel</span>
                  <span className="text-rule">·</span>
                  <span className="font-ui text-xs text-muted-foreground">
                    {new Date().toLocaleDateString("fr-FR", { day: "numeric", month: "short", year: "numeric" })}
                  </span>
                </div>
              </div>

              <p className="font-body text-sm text-muted-foreground mb-3 line-clamp-2">
                Analyse en temps réel des affirmations économiques du premier ministre. 3 affirmations vérifiées, 2 en cours d'analyse.
              </p>

              <div className="flex items-center gap-3">
                <TextShimmer className="font-ui text-xs" duration={1.5}>
                  Analyse en cours…
                </TextShimmer>
                <span className="font-ui text-xs text-muted-foreground/60">·</span>
                <span className="font-ui text-xs text-muted-foreground/60">
                  5 points détectés
                </span>
              </div>
            </article>
          </div>
        </div>
      </div>
      {/* Desktop: two columns */}
      <div className="hidden md:grid grid-cols-2 gap-x-3 items-start">
        <div className="flex flex-col gap-3">
          <div
            className={animate ? "animate-fade-up" : ""}
            style={animate ? { animationFillMode: "both", opacity: 0 } : {}}
          >
            <div
              className="cursor-pointer"
              onClick={() => navigate("/live?view=1")}
            >
              <article
                className="
                  bg-[hsl(var(--paper))] rounded-sm border border-border p-4
                  hover:shadow-xl hover:-translate-y-1 transition-all duration-200
                  group relative
                "
                style={{
                  boxShadow: "1px 2px 4px hsl(25 20% 30% / 0.08)",
                  transform: "rotate(-0.3deg)",
                }}
              >
                {/* Live badge */}
                <div className="absolute top-3 right-3 flex items-center gap-1.5 bg-destructive/10 border border-destructive/20 rounded-full px-2.5 py-0.5">
                  <span className="w-2 h-2 rounded-full bg-destructive animate-pulse" />
                  <span className="font-ui text-[10px] font-bold text-destructive uppercase tracking-wider">
                    En direct
                  </span>
                </div>

                <div className="mb-3 pr-28">
                  <h4 className="font-display text-base font-semibold text-foreground leading-snug group-hover:text-accent transition-colors">
                    Fact-checking du discours du premier ministre de l'économie
                  </h4>
                  <div className="flex items-center gap-2 mt-1.5">
                    <span className="font-ui text-xs text-muted-foreground">Discours officiel</span>
                    <span className="text-rule">·</span>
                    <span className="font-ui text-xs text-muted-foreground">
                      {new Date().toLocaleDateString("fr-FR", { day: "numeric", month: "short", year: "numeric" })}
                    </span>
                  </div>
                </div>

                <p className="font-body text-sm text-muted-foreground mb-3 line-clamp-2">
                  Analyse en temps réel des affirmations économiques du premier ministre. 3 affirmations vérifiées, 2 en cours d'analyse.
                </p>

                <div className="flex items-center gap-3">
                  <TextShimmer className="font-ui text-xs" duration={1.5}>
                    Analyse en cours…
                  </TextShimmer>
                  <span className="font-ui text-xs text-muted-foreground/60">·</span>
                  <span className="font-ui text-xs text-muted-foreground/60">
                    5 points détectés
                  </span>
                </div>
              </article>
            </div>
          </div>
        </div>
        <div className="flex flex-col gap-3">
          {/* Colonne droite vide */}
        </div>
      </div>
    </div>
  );
};

const ArchivesDrawer = ({ isOpen, activeTab, onOpen, onClose }: ArchivesDrawerProps) => {
  const seenTabsRef = useRef<Set<DrawerTab>>(new Set());
  const [animatingTab, setAnimatingTab] = useState<DrawerTab | null>(null);
  const prevIsOpen = useRef(isOpen);

  // Reset seen tabs when drawer closes
  useEffect(() => {
    if (!isOpen && prevIsOpen.current) {
      seenTabsRef.current = new Set();
      setAnimatingTab(null);
    }
    prevIsOpen.current = isOpen;
  }, [isOpen]);

  // Trigger animation only for first-time tab visits
  useEffect(() => {
    if (isOpen && !seenTabsRef.current.has(activeTab)) {
      setAnimatingTab(activeTab);
      seenTabsRef.current.add(activeTab);
      const timer = setTimeout(() => {
        setAnimatingTab(null);
      }, 2000);
      return () => clearTimeout(timer);
    } else {
      setAnimatingTab(null);
    }
  }, [isOpen, activeTab]);

  const shouldAnimate = animatingTab === activeTab;

  const handleTabClick = (tab: DrawerTab) => {
    if (!isOpen) {
      onOpen(tab);
    } else if (activeTab === tab) {
      onClose();
    } else {
      onOpen(tab);
    }
  };

  const tabBtn = (
    tab: DrawerTab,
    icon: React.ReactNode,
    label: string,
    count?: number,
    isFirst?: boolean,
  ) => {
    const isDark = document.documentElement.classList.contains("dark");

    const getTabColor = () => {
      if (isDark) {
        if (tab === "featured") return "#3d3630";
        if (tab === "live") return "#3d2f2f";
        return "#383330";
      }
      if (tab === "featured") return "#d4c9bd";
      if (tab === "live") return "#ecd3d3";
      return "#e4ded5";
    };

    const getDarkenedColor = () => {
      if (isDark) {
        if (tab === "featured") return "#332d28";
        if (tab === "live") return "#332828";
        return "#2e2a27";
      }
      if (tab === "featured") return "#c4b9ad";
      if (tab === "live") return "#dfc0c0";
      return "#d8d2c9";
    };

    const isActiveTab = activeTab === tab;
    const isOtherActive = isOpen && !isActiveTab;
    const buttonBg = isOtherActive ? getDarkenedColor() : getTabColor();

    // L'onglet actif est toujours AU-DESSUS du panel (z-30), ouvert ou fermé
    const buttonZIndex = isActiveTab ? 30 : (isOpen ? 5 : 20);

    return (
      <button
        onClick={() => handleTabClick(tab)}
        className={`relative -mb-px px-5 py-2.5 rounded-t-md flex items-center gap-2 transition-colors group ${
          !isFirst ? "-ml-1" : ""
        }`}
        style={{
          zIndex: buttonZIndex,
          clipPath: "polygon(8px 0%, calc(100% - 8px) 0%, 100% 100%, 0% 100%)",
          backgroundColor: buttonBg,
          ...(isActiveTab ? {
            backgroundImage: 'url("data:image/svg+xml,%3Csvg width=\'100\' height=\'100\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cfilter id=\'n\'%3E%3CfeTurbulance type=\'fractalNoise\' baseFrequency=\'0.65\' numOctaves=\'4\' stitchTiles=\'stitch\'/%3E%3C/filter%3E%3Crect width=\'100\' height=\'100\' filter=\'url(%23n)\' opacity=\'0.04\'/%3E%3C/svg%3E")',
          } : {})
        }}
      >
        {icon}
        <span
          className="font-ui text-sm font-semibold text-foreground tracking-wide uppercase"
          style={{ letterSpacing: "0.08em" }}
        >
          {label}
        </span>
        {count !== undefined && (
          <span className="font-ui text-xs text-muted-foreground ml-0.5">({count})</span>
        )}
        <ChevronUp
          className={`w-3.5 h-3.5 text-muted-foreground transition-transform duration-300 ${
            isOpen && activeTab === tab ? "rotate-180" : ""
          }`}
        />
      </button>
    );
  };

  return (
    <>
      {isOpen && (
        <div className="fixed inset-0 bg-black/30 z-30 animate-fade-in" onClick={onClose} />
      )}
      <div
        className="fixed bottom-0 left-1/2 -translate-x-1/2 w-full max-w-5xl px-6 z-40 transition-transform duration-500 pointer-events-none"
        style={{
          transform: `translateX(-50%) translateY(${isOpen ? "0" : "calc(100% - 44px)"})`,
          transitionTimingFunction: "cubic-bezier(0.16, 1, 0.3, 1)",
        }}
      >
        {/* Tab buttons — wrapped for drop-shadow (clipPath clips box-shadow) */}
        <div
          className="pointer-events-auto flex items-end ml-2 gap-0 relative"
        >
          {archiveItems.length > 0 && tabBtn(
            "archives",
            <FolderOpen className="w-4 h-4 text-muted-foreground group-hover:text-foreground transition-colors" />,
            "Mes archives",
            archiveItems.length,
            true,
          )}
          {tabBtn(
            "featured",
            <Flame className="w-4 h-4 text-muted-foreground group-hover:text-foreground transition-colors" />,
            "A la une",
            featuredItems.length,
            archiveItems.length === 0,
          )}
          {tabBtn(
            "live",
            hasActiveStream ? (
              <span className="relative flex items-center justify-center w-4 h-4">
                <Radio className="w-4 h-4 text-destructive" />
                <span className="absolute inset-0 rounded-full animate-ping bg-destructive/30" />
              </span>
            ) : (
              <Radio className="w-4 h-4 text-muted-foreground group-hover:text-foreground transition-colors" />
            ),
            "En direct",
          )}
        </div>

        {/* Panel content */}
        <div
          className="pointer-events-auto rounded-tr-md px-5 py-[5px] transition-colors duration-300 relative"
          style={{
            zIndex: 25,
            backgroundColor: (() => {
              const isDark = document.documentElement.classList.contains("dark");
              if (isDark) {
                return activeTab === "featured" ? "#3d3630" : activeTab === "live" ? "#3d2f2f" : "#383330";
              }
              return activeTab === "featured" ? "#d4c9bd" : activeTab === "live" ? "#ecd3d3" : "#e4ded5";
            })(),
            backgroundImage:
              'url("data:image/svg+xml,%3Csvg width=\'100\' height=\'100\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cfilter id=\'n\'%3E%3CfeTurbulance type=\'fractalNoise\' baseFrequency=\'0.65\' numOctaves=\'4\' stitchTiles=\'stitch\'/%3E%3C/filter%3E%3Crect width=\'100\' height=\'100\' filter=\'url(%23n)\' opacity=\'0.04\'/%3E%3C/svg%3E")',
            boxShadow: '0 -8px 16px rgba(0, 0, 0, 0.12), 0 4px 8px rgba(0, 0, 0, 0.08)',
          }}
        >
          {activeTab === "live" ? (
            <LiveStreamsPanel animate={shouldAnimate} />
          ) : (
            <CardGrid items={activeTab === "featured" ? featuredItems : archiveItems} animate={shouldAnimate} showPins={activeTab === "archives"} />
          )}
        </div>
      </div>
    </>
  );
};

export default ArchivesDrawer;
