import { useState, useEffect, useRef, useCallback, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import Header from "@/components/Header";
import { Mic, Square } from "lucide-react";
import SourceInlineRef from "@/components/SourceInlineRef";
import { getBiasLabel } from "@/lib/bias";
import { Button } from "@/components/ui/button";
import { Search } from "lucide-react";
import { TextShimmer } from "@/components/ui/text-shimmer";
import type { DiscoursePoint, ArticleSource } from "@/data/articles";

/* ── Simulated live data ── */
const LIVE_POINTS: DiscoursePoint[] = [
  {
    id: 1,
    label: "« Le déficit commercial s'est réduit de 30 % cette année »",
    status: "uncertain",
    summary:
      "Les dernières données douanières montrent une réduction de 18 %, pas 30 %. Le chiffre cité semble inclure des corrections saisonnières non publiées¹.",
  },
  {
    id: 2,
    label: "« Nous avons créé 400 000 emplois en six mois »",
    status: "verified",
    summary:
      "L'INSEE confirme 387 000 créations nettes d'emploi sur la période janvier-juin 2026, un chiffre cohérent avec l'affirmation arrondie².",
  },
  {
    id: 3,
    label: "« La dette publique est stabilisée »",
    status: "false",
    summary:
      "Selon la Banque de France, la dette publique a augmenté de 2,1 points de PIB au dernier trimestre, passant de 110,3 % à 112,4 %. L'affirmation est inexacte³.",
  },
  {
    id: 4,
    label: "« La France est le premier exportateur agricole européen »",
    status: "grey_area",
    summary:
      "La France est premier exportateur en valeur pour certaines filières (vins, céréales), mais les Pays-Bas dominent en volume total d'exports agroalimentaires⁴.",
  },
  {
    id: 5,
    label: "« Les investissements étrangers ont doublé en deux ans »",
    status: "verified",
    summary:
      "Business France rapporte une hausse de 94 % des projets d'investissement étranger entre 2024 et 2026, un chiffre très proche du doublement annoncé⁵.",
  },
];

const LIVE_SOURCES: ArticleSource[] = [
  { id: 1, label: "Direction générale des douanes, données préliminaires S1 2026", url: "https://www.douane.gouv.fr" },
  { id: 2, label: "INSEE, Estimations d'emploi T2 2026", url: "https://www.insee.fr" },
  { id: 3, label: "Banque de France, Bulletin trimestriel, juillet 2026", url: "https://www.banque-france.fr" },
  { id: 4, label: "Eurostat, Agricultural trade statistics 2025-2026", url: "https://ec.europa.eu/eurostat" },
  { id: 5, label: "Business France, Bilan annuel 2026 de l'attractivité", url: "https://www.businessfrance.fr" },
];

const POINT_INTERVAL = 6000; // ms between each new point

const SUPERSCRIPT_TO_ID: Record<string, number> = {
  "¹": 1, "²": 2, "³": 3, "⁴": 4, "⁵": 5,
  "⁶": 6, "⁷": 7, "⁸": 8, "⁹": 9,
};

/** Extract source IDs referenced via superscripts in a text */
const extractSourceIds = (text: string): number[] => {
  const ids: number[] = [];
  for (const char of text) {
    if (SUPERSCRIPT_TO_ID[char]) ids.push(SUPERSCRIPT_TO_ID[char]);
  }
  return ids;
};

const statusConfig: Record<DiscoursePoint["status"], { label: string; colorClass: string }> = {
  verified: { label: "Vérifié", colorClass: "text-emerald-800" },
  false: { label: "Faux", colorClass: "text-red-800" },
  uncertain: { label: "Incertain", colorClass: "text-orange-700" },
  grey_area: { label: "Zone grise", colorClass: "text-muted-foreground" },
};

/* ── Typewriter hook for progressive text reveal ── */
const useTypewriter = (text: string, isNew: boolean, speed = 18) => {
  const [displayed, setDisplayed] = useState(isNew ? "" : text);
  const [done, setDone] = useState(!isNew);

  useEffect(() => {
    if (!isNew) {
      setDisplayed(text);
      setDone(true);
      return;
    }
    setDisplayed("");
    setDone(false);
    let i = 0;
    const timer = setInterval(() => {
      i++;
      setDisplayed(text.slice(0, i));
      if (i >= text.length) {
        clearInterval(timer);
        setDone(true);
      }
    }, speed);
    return () => clearInterval(timer);
  }, [text, isNew, speed]);

  return { displayed, done };
};

/* ── Point component (reused from ArticleDiscourseLayout) ── */
const LivePointItem = ({
  point,
  isLast,
  sources,
  isNew,
}: {
  point: DiscoursePoint;
  isLast: boolean;
  sources: ArticleSource[];
  isNew: boolean;
}) => {
  const config = statusConfig[point.status];
  const { displayed: displayedLabel, done: labelDone } = useTypewriter(point.label, isNew, 12);
  const { displayed: displayedSummary, done: summaryDone } = useTypewriter(
    point.summary,
    isNew && labelDone,
    6
  );

  return (
    <div className="relative flex gap-5 animate-fade-up" style={{ animationDelay: "0ms" }}>
      <div className="relative flex-shrink-0 w-4">
        {!isLast && (
          <div className="absolute left-1/2 top-0 bottom-0 w-px -translate-x-1/2 bg-muted-foreground/20" />
        )}
        <div className="absolute left-1/2 -translate-x-1/2 top-[9px] w-3 h-3 rounded-full bg-muted-foreground border-[3px] border-background z-10" />
      </div>

      <div className={`flex-1 ${isLast ? "" : "pb-8"}`}>
        <div className="flex flex-wrap items-baseline gap-2.5 mb-2">
          <h3 className="font-display text-base md:text-lg font-semibold text-foreground leading-snug">
            {displayedLabel}
            {!labelDone && <span className="animate-pulse text-muted-foreground font-normal">|</span>}
          </h3>
          {labelDone && point.status !== "grey_area" && (
            <span className={`font-ui text-xs font-bold tracking-widest uppercase ${config.colorClass}`}>
              {config.label}
            </span>
          )}
        </div>

        {labelDone && (
          <p className="font-body text-sm leading-relaxed text-foreground">
            {summaryDone ? (
              <SourceInlineRef text={point.summary} sources={sources} />
            ) : (
              <>
                {displayedSummary}
                <span className="animate-pulse text-muted-foreground font-normal">|</span>
              </>
            )}
          </p>
        )}

        {summaryDone && point.status === "grey_area" && (
          <Button
            variant="outline"
            size="sm"
            className="font-ui text-xs h-6 px-2.5 gap-1.5 text-muted-foreground hover:text-foreground mt-3"
          >
            <Search className="w-3 h-3" />
            Analyser
          </Button>
        )}
      </div>
    </div>
  );
};

/* ── Pulsing "analyzing" placeholder ── */
const AnalyzingPlaceholder = () => (
  <div className="relative flex gap-5 animate-fade-up">
    <div className="relative flex-shrink-0 w-4">
      <div className="absolute left-1/2 -translate-x-1/2 top-[9px] w-3 h-3 rounded-full bg-muted-foreground/30 border-[3px] border-background z-10 animate-pulse" />
    </div>
    <div className="flex-1 pb-8">
      <div className="flex items-baseline gap-2.5 mb-2">
        <div className="h-4 w-48 bg-muted rounded animate-pulse" />
      </div>
      <div className="space-y-1.5">
        <div className="h-3 w-full bg-muted/60 rounded animate-pulse" />
        <div className="h-3 w-3/4 bg-muted/60 rounded animate-pulse" />
      </div>
    </div>
  </div>
);

/* ── Main page ── */
const LiveFactCheck = () => {
  useEffect(() => { window.scrollTo(0, 0); }, []);
  const navigate = useNavigate();
  const [profileOpen, setProfileOpen] = useState(false);
  const [isRecording, setIsRecording] = useState(true);

  // Check if viewer mode (connected to someone else's stream)
  const searchParams = new URLSearchParams(window.location.search);
  const viewOnly = searchParams.get("view") === "1";
  const [visibleCount, setVisibleCount] = useState(0);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const bottomRef = useRef<HTMLDivElement | null>(null);
  const prevCountRef = useRef(0);

  // Track which point index was the latest "new" one
  const [newestIndex, setNewestIndex] = useState<number | null>(null);




  const startListening = useCallback(() => {
    const delay = setTimeout(() => {
      setVisibleCount((prev) => {
        if (prev === 0) {
          setNewestIndex(0);
          return 1;
        }
        return prev;
      });

      timerRef.current = setInterval(() => {
        setVisibleCount((prev) => {
          const next = prev + 1;
          setNewestIndex(next - 1);
          if (next >= LIVE_POINTS.length) {
            if (timerRef.current) clearInterval(timerRef.current);
            setIsRecording(false);
          }
          return Math.min(next, LIVE_POINTS.length);
        });
      }, POINT_INTERVAL);
    }, 3000);

    return delay;
  }, []);

  // Start revealing points on mount
  const initialDelayRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  useEffect(() => {
    initialDelayRef.current = startListening();
    return () => {
      if (initialDelayRef.current) clearTimeout(initialDelayRef.current);
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Auto-scroll to bottom when new points appear
  useEffect(() => {
    if (visibleCount > prevCountRef.current && bottomRef.current) {
      // Delay to let sources render before scrolling
      setTimeout(() => {
        bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
      }, 100);
    }
    prevCountRef.current = visibleCount;
  }, [visibleCount]);

  const handleStopRecording = useCallback(() => {
    setIsRecording(false);
    if (initialDelayRef.current) {
      clearTimeout(initialDelayRef.current);
      initialDelayRef.current = null;
    }
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
  }, []);

  const handleResumeRecording = useCallback(() => {
    if (visibleCount >= LIVE_POINTS.length) return;
    setIsRecording(true);
    initialDelayRef.current = startListening();
  }, [visibleCount, startListening]);

  const visiblePoints = LIVE_POINTS.slice(0, visibleCount);
  const referencedIds = new Set(visiblePoints.flatMap((p) => extractSourceIds(p.summary)));
  const visibleSources = LIVE_SOURCES.filter((s) => referencedIds.has(s.id));
  const stillListening = isRecording && visibleCount < LIVE_POINTS.length;

  return (
    <div className="min-h-screen flex flex-col bg-background">
      <Header
        profileOpen={profileOpen}
        onOpenProfile={() => setProfileOpen(true)}
        onCloseProfile={() => setProfileOpen(false)}
      />

      <div className="w-full px-6">
        <div className="border-t border-rule" />
      </div>

      {/* Back button */}
      <div className="max-w-5xl mx-auto w-full px-6 pt-4">
        <button
          onClick={() => navigate("/")}
          className="flex items-center gap-2 font-ui text-sm text-muted-foreground hover:text-foreground transition-colors"
        >
          <span className="text-sm">←</span>
          Retour
        </button>
      </div>

      <main className="flex-1">
        <article className="max-w-2xl mx-auto px-6 py-10 animate-fade-up">
          {/* Recording control — hidden in view-only mode */}
          {viewOnly ? (
            <div className="flex flex-col items-center mb-10">
              <div className="flex items-center gap-2 bg-destructive/10 border border-destructive/20 rounded-full px-4 py-2">
                <span className="w-2.5 h-2.5 rounded-full bg-destructive animate-pulse" />
                <span className="font-ui text-sm font-semibold text-destructive uppercase tracking-wider">
                  En direct
                </span>
              </div>
              <div className="mt-3">
                <TextShimmer className="font-body text-sm opacity-70" duration={1.2}>
                  {visibleCount === 0 ? "En attente du flux…" : "Flux en cours…"}
                </TextShimmer>
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center mb-10">
              {isRecording ? (
                <button
                  onClick={handleStopRecording}
                  className="w-16 h-16 rounded-full bg-destructive text-destructive-foreground flex items-center justify-center shadow-lg transition-transform hover:scale-105 active:scale-95"
                  style={{ animation: "pulse 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite" }}
                  title="Arrêter l'enregistrement"
                >
                  <Square className="w-6 h-6 fill-current" />
                </button>
              ) : (
                <button
                  onClick={handleResumeRecording}
                  disabled={visibleCount >= LIVE_POINTS.length}
                  className="w-16 h-16 rounded-full bg-muted flex items-center justify-center transition-transform hover:scale-105 active:scale-95 disabled:opacity-50 disabled:pointer-events-none"
                  title="Reprendre l'enregistrement"
                >
                  <Mic className="w-6 h-6 text-muted-foreground" />
                </button>
              )}
              <div className="mt-3">
                {isRecording ? (
                  <TextShimmer className="font-body text-sm opacity-70" duration={1.2}>
                    {visibleCount === 0 ? "Début de l'écoute…" : "Analyse en cours…"}
                  </TextShimmer>
                ) : (
                  <p className="font-body text-sm text-muted-foreground opacity-70">
                    {visibleCount >= LIVE_POINTS.length ? "Analyse terminée" : "Enregistrement en pause"}
                  </p>
                )}
              </div>
            </div>
          )}

          {/* Header */}
          <div className="mb-8">
            <h1 className="font-display text-2xl md:text-3xl lg:text-4xl font-bold text-foreground leading-tight mb-3">
              {viewOnly ? "Fact-checking du discours du premier ministre de l'économie" : "Fact-checking en direct"}
            </h1>
            <p className="font-body text-base text-muted-foreground mb-3">
              {viewOnly ? "Vous suivez ce flux en direct" : "Analyse en temps réel des affirmations détectées"}
            </p>
            <div className="flex items-center gap-3 font-body text-sm text-muted-foreground">
              <span>{viewOnly ? "Discours officiel" : "Enregistrement live"}</span>
              <span className="text-rule">·</span>
              <span>{new Date().toLocaleDateString("fr-FR", { day: "numeric", month: "short", year: "numeric" })}</span>
            </div>
          </div>

          <div className="border-t-2 border-foreground mb-8" />

          {/* Points timeline */}
          {visibleCount === 0 ? (
            <div className="flex flex-col items-center py-12">
              <TextShimmer className="font-body text-sm" duration={1.5}>
                En attente des premières affirmations…
              </TextShimmer>
            </div>
          ) : (
            <div className="space-y-0">
              {visiblePoints.map((point, i) => (
                <LivePointItem
                  key={point.id}
                  point={point}
                  isLast={!stillListening && i === visiblePoints.length - 1}
                  sources={LIVE_SOURCES}
                  isNew={i === newestIndex}
                />
              ))}
              {/* Show analyzing placeholder while still listening */}
              {stillListening && <AnalyzingPlaceholder />}
              
            </div>
          )}

          {/* Sources */}
          {visibleSources.length > 0 && (
            <div className="mt-12 pt-6 border-t border-rule">
              <h3 className="font-ui text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">
                Sources
              </h3>
              <ol className="space-y-1.5">
                {visibleSources.map((s) => {
                  const biasLabel = getBiasLabel(s.bias);
                  return (
                    <li key={s.id} className="font-body text-xs text-muted-foreground leading-relaxed">
                      <span className="font-ui font-semibold text-foreground mr-1">{s.id}.</span>
                      {s.url ? (
                        <a href={s.url} target="_blank" rel="noopener noreferrer" className="hover:underline">
                          {s.label}
                        </a>
                      ) : (
                        s.label
                      )}
                      {biasLabel && <span className="font-bold ml-1">({biasLabel})</span>}
                    </li>
                  );
                })}
              </ol>
            </div>
          )}
          <div ref={bottomRef} />
        </article>
      </main>
    </div>
  );
};

export default LiveFactCheck;
