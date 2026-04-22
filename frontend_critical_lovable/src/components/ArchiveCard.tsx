import { ExternalLink } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { getVerdictColor } from "@/data/articles";

interface ArchiveCardProps {
  id: string;
  title: string;
  author: string;
  date: string;
  verdict: string;
  summary: string;
  format: string;
  clipType?: "pin" | "bookmark" | "none";
}

const ArchiveCard = ({ id, title, author, date, verdict, summary, format, clipType = "none" }: ArchiveCardProps) => {
  const navigate = useNavigate();
  const isLong = format === "long";

  return (
    <div className="relative" style={{ isolation: "isolate" }}>
      <article
        onClick={() => navigate(`/article/${id}`)}
        className="
          bg-[hsl(var(--paper))] rounded-sm border border-border p-4
          hover:shadow-xl hover:-translate-y-1 transition-all duration-200
          group cursor-pointer
          relative
        "
        style={{
          boxShadow: "1px 2px 4px hsl(25 20% 30% / 0.08)",
          zIndex: 1,
        }}
      >

        {clipType === "pin" && (
          <svg
            className="absolute -top-2.5 right-2.5 w-6 h-8 scale-80"
            viewBox="0 0 24 32"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            style={{ transform: "rotate(30deg)" }}
          >
            <ellipse cx="13" cy="10" rx="6" ry="3" fill="hsl(25 20% 30% / 0.18)" />
            <line x1="11" y1="14" x2="13" y2="26" stroke="hsl(0 0% 72%)" strokeWidth="1.6" strokeLinecap="round" />
            <line x1="11.4" y1="14" x2="13.2" y2="24" stroke="hsl(0 0% 85%)" strokeWidth="0.5" strokeLinecap="round" />
            <ellipse cx="10" cy="8" rx="7" ry="6.5" fill="hsl(28, 13%, 50%)" />
            <ellipse cx="10" cy="8" rx="7" ry="6.5" fill="url(#pinShine)" />
            <ellipse cx="7.5" cy="5.5" rx="2.5" ry="2" fill="white" opacity="0.3" />
            <defs>
              <radialGradient id="pinShine" cx="0.35" cy="0.28" r="0.55">
                <stop offset="0%" stopColor="white" stopOpacity="0.5" />
                <stop offset="60%" stopColor="white" stopOpacity="0" />
              </radialGradient>
            </defs>
          </svg>
        )}

        {clipType === "bookmark" && (
          <div
            className="absolute -top-1 right-4 pointer-events-none"
            style={{ zIndex: 10 }}
          >
            <svg width="14" height="28" viewBox="0 0 22 40" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M3 0 L3 34 L11 28 L19 34 L19 0 Z" fill="hsl(25 20% 30% / 0.10)" transform="translate(1.5, 1.5)" />
              <path d="M2 0 L2 33 L11 27 L20 33 L20 0 Z" fill="hsl(28, 18%, 42%)" />
              <path d="M2 0 L2 33 L11 27 L20 33 L20 0 Z" fill="url(#bookmarkShine)" />
              <defs>
                <linearGradient id="bookmarkShine" x1="0" y1="0" x2="22" y2="0">
                  <stop offset="0%" stopColor="white" stopOpacity="0.12" />
                  <stop offset="40%" stopColor="white" stopOpacity="0" />
                  <stop offset="100%" stopColor="black" stopOpacity="0.08" />
                </linearGradient>
              </defs>
            </svg>
          </div>
        )}

        {/* Header */}
        <div className="mb-3">
          <h4 className="font-display text-base font-semibold text-foreground leading-snug line-clamp-2 group-hover:text-accent transition-colors pr-6">
            {title}
          </h4>
          <div className="flex items-center gap-2 mt-1">
            <span className="font-ui text-xs text-muted-foreground">{author}</span>
            <span className="text-rule">·</span>
            <span className="font-ui text-xs text-muted-foreground">{date}</span>
            <span className="text-rule">·</span>
            <span className={`font-ui text-xs font-bold tracking-widest uppercase ${getVerdictColor(verdict)}`}>
              {verdict}
            </span>
          </div>
        </div>

        {/* Summary */}
        <p className={`font-body text-sm text-muted-foreground mb-3 ${isLong ? "line-clamp-4" : "line-clamp-2"}`}>
          {summary}
        </p>

        {/* Footer */}
        <div className="flex items-center text-xs font-ui text-accent opacity-0 group-hover:opacity-100 transition-opacity">
          Voir le détail
          <ExternalLink className="w-3 h-3 ml-1" />
        </div>
      </article>
    </div>
  );
};

export default ArchiveCard;
