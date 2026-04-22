import { useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { User } from "lucide-react";
import ProfilePanel from "./ProfilePanel";

const QUOTES = [
  "« La vérité mérite qu'on s'y attarde »",
  "« Le doute est le commencement de la sagesse » — Aristote",
  "« Un mensonge répété mille fois ne devient pas une vérité »",
  "« L'esprit critique est le gardien de la démocratie »",
  "« Extraordinary claims require extraordinary evidence » - Carl Sagan",
  "« Penser, c'est dire non » — Alain",
  "« La confiance n'exclut pas le contrôle »",
  "« Ce n'est pas le doute, c'est la certitude qui rend fou » — Nietzsche",
  "« Le scepticisme est la première étape vers la vérité » — Diderot",
  "« Les faits sont têtus » — Lénine",
];

interface HeaderProps {
  profileOpen: boolean;
  onOpenProfile: () => void;
  onCloseProfile: () => void;
  title?: string;
}

const Header = ({ profileOpen, onOpenProfile, onCloseProfile, title }: HeaderProps) => {
  const navigate = useNavigate();
  const quote = useMemo(() => {
    const stored = sessionStorage.getItem("critical-quote");
    if (stored) return stored;
    const picked = QUOTES[Math.floor(Math.random() * QUOTES.length)];
    sessionStorage.setItem("critical-quote", picked);
    return picked;
  }, []);

  return (
    <>
      <header className="w-full px-6 py-4 flex items-center justify-between relative z-20">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-sm bg-primary flex items-center justify-center">
            <span className="text-primary-foreground font-display font-bold text-sm">C</span>
          </div>
          <h1
            className="font-display text-xl font-semibold tracking-tight text-foreground cursor-pointer hover:text-primary transition-colors"
            onClick={() => navigate("/login")}
          >
            {title || "Critical"}
          </h1>
        </div>

        <p className="hidden md:block font-body text-sm italic text-muted-foreground absolute left-1/2 -translate-x-1/2 max-w-md text-center">
          {quote}
        </p>

        <div className="relative flex items-center gap-2">
          <span className="font-ui text-sm text-muted-foreground hidden sm:block">Téo</span>
          <button
            onClick={onOpenProfile}
            className="w-9 h-9 rounded-full border border-border bg-card flex items-center justify-center hover:bg-secondary transition-colors"
            aria-label="Profil"
          >
            <User className="w-4 h-4 text-muted-foreground" />
          </button>
        </div>
      </header>

      <ProfilePanel isOpen={profileOpen} onClose={onCloseProfile} />
    </>
  );
};
export default Header;
