import { useState, useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import {
  ArrowLeft,
  ChevronRight,
  Globe,
  Lock,
  LogOut,
  Trash2,
  Eye,
  EyeOff,
  Check,
  X,
  Sparkles,
  Zap,
  Crown,
  MapPin,
  Gauge,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import Header from "@/components/Header";
import { usePlan } from "@/contexts/PlanContext";
import { useLanguage, LANGUAGES } from "@/contexts/LanguageContext";
import { useLocation_, LOCATIONS } from "@/contexts/LocationContext";
import { useConsumption, type ConsumptionMode } from "@/contexts/ConsumptionContext";
import { toast } from "@/hooks/use-toast";
import LoadingLines from "@/components/ui/loading-lines";

const PAPER_NOISE =
  "url(\"data:image/svg+xml,%3Csvg width='100' height='100' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100' height='100' filter='url(%23n)' opacity='0.05'/%3E%3C/svg%3E\")";

const PASSWORD_RULES = [
  { test: (p: string) => p.length >= 8, label: "Au moins 8 caractères" },
  { test: (p: string) => /[A-Z]/.test(p), label: "Une lettre majuscule" },
  { test: (p: string) => /[a-z]/.test(p), label: "Une lettre minuscule" },
  { test: (p: string) => /[0-9]/.test(p), label: "Un chiffre" },
  { test: (p: string) => /[^A-Za-z0-9]/.test(p), label: "Un caractère spécial" },
];

const expandVariants = {
  hidden: { height: 0, opacity: 0, overflow: "hidden" as const },
  visible: { height: "auto", opacity: 1, overflow: "hidden" as const },
};

type ExpandedSection = null | "language" | "location" | "consumption" | "password" | "delete" | "linked";

const Settings = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { currentPlan, renewalDate } = usePlan();
  const [profileOpen, setProfileOpen] = useState(false);
  const [expanded, setExpanded] = useState<ExpandedSection>(null);

  const { language, setLanguage } = useLanguage();
  const { location, setLocation } = useLocation_();
  const { mode: consumptionMode, setMode: setConsumptionMode } = useConsumption();

  // Auto-expand section from query param
  useEffect(() => {
    const section = searchParams.get("section");
    if (section === "language" || section === "location") {
      setExpanded(section);
    }
  }, [searchParams]);

  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showCurrent, setShowCurrent] = useState(false);
  const [showNew, setShowNew] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);

  const [linkedGoogle, setLinkedGoogle] = useState(false);
  const [linkedApple, setLinkedApple] = useState(false);

  const [deleteConfirm, setDeleteConfirm] = useState("");
  const [deletePassword, setDeletePassword] = useState("");
  const [showDeletePassword, setShowDeletePassword] = useState(false);

  const passwordValid = newPassword.length > 0 && PASSWORD_RULES.every((r) => r.test(newPassword));
  const passwordsMatch = newPassword === confirmPassword && confirmPassword.length > 0;

  const toggle = (section: ExpandedSection) => {
    setExpanded(expanded === section ? null : section);
  };

  const [globalLoading, setGlobalLoading] = useState(false);

  const handlePasswordChange = () => {
    if (!currentPassword) {
      toast({ title: "Mot de passe actuel requis", variant: "destructive" });
      return;
    }
    if (!passwordValid) {
      toast({ title: "Le nouveau mot de passe ne respecte pas les critères", variant: "destructive" });
      return;
    }
    if (!passwordsMatch) {
      toast({ title: "Les mots de passe ne correspondent pas", variant: "destructive" });
      return;
    }
    setGlobalLoading(true);
    setTimeout(() => {
      setGlobalLoading(false);
      toast({ title: "Mot de passe modifié avec succès" });
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
      setExpanded(null);
    }, 2000);
  };

  const handleDeleteAccount = () => {
    if (deleteConfirm !== "SUPPRIMER") {
      toast({ title: "Tapez SUPPRIMER pour confirmer", variant: "destructive" });
      return;
    }
    setGlobalLoading(true);
    setTimeout(() => {
      setGlobalLoading(false);
      toast({ title: "Compte supprimé", description: "Votre compte a été supprimé." });
      navigate("/login");
    }, 2000);
  };

  const handleLogout = () => {
    setGlobalLoading(true);
    setTimeout(() => {
      setGlobalLoading(false);
      toast({ title: "Déconnexion réussie" });
      navigate("/login");
    }, 1500);
  };

  return (
    <div className="min-h-screen flex flex-col bg-background">
      {globalLoading && <LoadingLines />}
      <Header
        title="Paramètres"
        profileOpen={profileOpen}
        onOpenProfile={() => setProfileOpen(true)}
        onCloseProfile={() => setProfileOpen(false)}
      />

      <div className="w-full px-6">
        <div className="border-t border-rule" />
      </div>

      <div className="px-6 pt-4">
        <button
          onClick={() => {
            if (window.history.length > 1) {
              navigate(-1);
            } else {
              navigate("/");
            }
          }}
          className="flex items-center gap-2 font-ui text-sm text-muted-foreground hover:text-foreground transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Retour
        </button>
      </div>

      <div className="max-w-2xl mx-auto w-full px-6 py-8 flex flex-col gap-4">
        {/* ─── CONSOMMATION ─── */}
        <SettingsCard>
          <button
            onClick={() => toggle("consumption")}
            className="w-full flex items-center justify-between px-5 py-4 group"
          >
            <div className="flex items-center gap-3">
              <Gauge className="w-4 h-4 text-muted-foreground group-hover:text-accent transition-colors" />
              <div className="flex flex-col text-left">
                <span className="font-ui text-sm font-medium text-foreground group-hover:text-accent transition-colors">
                  Consommation
                </span>
                <span className="font-ui text-xs text-muted-foreground">
                  {consumptionMode === "economy" ? "Économie" : "Précision"}
                </span>
              </div>
            </div>
            <ChevronRight
              className={`w-4 h-4 text-muted-foreground transition-transform ${expanded === "consumption" ? "rotate-90" : ""}`}
            />
          </button>
          <AnimatePresence>
            {expanded === "consumption" && (
              <motion.div
                key="consumption-panel"
                initial="hidden"
                animate="visible"
                exit="hidden"
                variants={expandVariants}
                transition={{ duration: 0.25, ease: [0.25, 0.46, 0.45, 0.94] }}
              >
                <div className="px-5 pb-4 border-t border-dashed border-rule pt-3 flex flex-col gap-2">
                  {[
                    {
                      value: "economy" as ConsumptionMode,
                      label: "Économie",
                      desc: "N'approfondit l'analyse que lorsque vous le demandez explicitement. Réutilise les meilleurs articles existants sur un sujet quand ils sont disponibles.",
                    },
                    {
                      value: "precision" as ConsumptionMode,
                      label: "Précision",
                      desc: "Pousse systématiquement chaque analyse au maximum, en croisant davantage de sources pour un résultat plus complet.",
                    },
                  ].map((opt) => (
                    <button
                      key={opt.value}
                      onClick={() => {
                        setConsumptionMode(opt.value);
                        setExpanded(null);
                        
                      }}
                      className={`flex flex-col text-left px-3 py-3 rounded-sm transition-colors ${
                        consumptionMode === opt.value
                          ? "bg-[hsl(var(--highlight))]"
                          : "hover:bg-[hsl(var(--highlight)/0.5)]"
                      }`}
                    >
                      <div className="flex items-center gap-2">
                        <span className="font-ui text-sm text-foreground font-medium">{opt.label}</span>
                        {consumptionMode === opt.value && <Check className="w-3.5 h-3.5 text-accent ml-auto" />}
                      </div>
                      <span className="font-body text-xs text-muted-foreground mt-1 leading-relaxed">{opt.desc}</span>
                    </button>
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </SettingsCard>

        {/* ─── LOCALISATION ─── */}
        <SettingsCard>
          <button
            onClick={() => toggle("location")}
            className="w-full flex items-center justify-between px-5 py-4 group"
          >
            <div className="flex items-center gap-3">
              <MapPin className="w-4 h-4 text-muted-foreground group-hover:text-accent transition-colors" />
              <div className="flex flex-col text-left">
                <span className="font-ui text-sm font-medium text-foreground group-hover:text-accent transition-colors">
                  Localisation
                </span>
                <span className="font-ui text-xs text-muted-foreground">
                  {LOCATIONS.find((l) => l.code === location)?.flag} {LOCATIONS.find((l) => l.code === location)?.label}
                </span>
              </div>
            </div>
            <ChevronRight
              className={`w-4 h-4 text-muted-foreground transition-transform ${expanded === "location" ? "rotate-90" : ""}`}
            />
          </button>
          <AnimatePresence>
            {expanded === "location" && (
              <motion.div
                key="location-panel"
                initial="hidden"
                animate="visible"
                exit="hidden"
                variants={expandVariants}
                transition={{ duration: 0.25, ease: [0.25, 0.46, 0.45, 0.94] }}
              >
                <div className="px-5 pb-4 border-t border-dashed border-rule pt-3 flex flex-col gap-1">
                  <p className="font-body text-xs text-muted-foreground mb-2 italic">
                    Influence les flux En Direct proposés selon l'actualité de votre région.
                  </p>
                  {LOCATIONS.map((loc) => (
                    <button
                      key={loc.code}
                      onClick={() => {
                        setLocation(loc.code);
                        setExpanded(null);
                        
                      }}
                      className={`flex items-center gap-3 px-3 py-2.5 rounded-sm transition-colors ${
                        location === loc.code ? "bg-[hsl(var(--highlight))]" : "hover:bg-[hsl(var(--highlight)/0.5)]"
                      }`}
                    >
                      <span className="text-base">{loc.flag}</span>
                      <div className="flex items-center gap-1.5">
                        <span className="font-ui text-sm text-foreground">{loc.label}</span>
                        {loc.code === "other" && (
                          <span className="font-ui text-[10px] text-muted-foreground italic">— davantage à venir</span>
                        )}
                      </div>
                      {location === loc.code && <Check className="w-3.5 h-3.5 text-accent ml-auto" />}
                    </button>
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </SettingsCard>

        {/* ─── LANGUE ─── */}
        <SettingsCard>
          <button
            onClick={() => toggle("language")}
            className="w-full flex items-center justify-between px-5 py-4 group"
          >
            <div className="flex items-center gap-3">
              <Globe className="w-4 h-4 text-muted-foreground group-hover:text-accent transition-colors" />
              <div className="flex flex-col text-left">
                <span className="font-ui text-sm font-medium text-foreground group-hover:text-accent transition-colors">
                  Langue
                </span>
                <span className="font-ui text-xs text-muted-foreground">
                  {LANGUAGES.find((l) => l.code === language)?.label}
                </span>
              </div>
            </div>
            <ChevronRight
              className={`w-4 h-4 text-muted-foreground transition-transform ${expanded === "language" ? "rotate-90" : ""}`}
            />
          </button>
          <AnimatePresence>
            {expanded === "language" && (
              <motion.div
                key="language-panel"
                initial="hidden"
                animate="visible"
                exit="hidden"
                variants={expandVariants}
                transition={{ duration: 0.25, ease: [0.25, 0.46, 0.45, 0.94] }}
              >
                <div className="px-5 pb-4 border-t border-dashed border-rule pt-3 flex flex-col gap-1">
                  {LANGUAGES.map((lang) => (
                    <button
                      key={lang.code}
                      onClick={() => {
                        setLanguage(lang.code);
                        setExpanded(null);
                      }}
                      className={`flex items-center gap-3 px-3 py-2.5 rounded-sm transition-colors ${
                        language === lang.code ? "bg-[hsl(var(--highlight))]" : "hover:bg-[hsl(var(--highlight)/0.5)]"
                      }`}
                    >
                      <span className="font-ui text-sm text-foreground">{lang.label}</span>
                      {language === lang.code && <Check className="w-3.5 h-3.5 text-accent ml-auto" />}
                    </button>
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </SettingsCard>

        <div className="w-full h-px bg-[hsl(var(--rule))] my-2" />

        {/* ─── PLAN ─── */}
        <SettingsCard>
          <button
            onClick={() => navigate("/plans")}
            className="w-full flex items-center justify-between px-5 py-4 group"
          >
            <div className="flex items-center gap-3">
              {currentPlan === "Premium" ? (
                <Crown className="w-4 h-4 text-muted-foreground group-hover:text-accent transition-colors" />
              ) : currentPlan === "Pro" ? (
                <Zap className="w-4 h-4 text-muted-foreground group-hover:text-accent transition-colors" />
              ) : (
                <Sparkles className="w-4 h-4 text-muted-foreground group-hover:text-accent transition-colors" />
              )}
              <div className="flex flex-col text-left">
                <span className="font-ui text-sm font-medium text-foreground group-hover:text-accent transition-colors">
                  Abonnement
                </span>
                <span className="font-ui text-xs text-muted-foreground">
                  {currentPlan} Plan
                  {renewalDate && currentPlan !== "Free" && (
                    <> · Renouvellement le {renewalDate.toLocaleDateString("fr-FR", { day: "numeric", month: "long" })}</>
                  )}
                </span>
              </div>
            </div>
            <ChevronRight className="w-4 h-4 text-muted-foreground" />
          </button>
        </SettingsCard>

        {/* ─── COMPTES LIÉS ─── */}
        <SettingsCard>
          <button onClick={() => toggle("linked")} className="w-full flex items-center justify-between px-5 py-4 group">
            <div className="flex items-center gap-3">
              <svg
                className="w-4 h-4 text-muted-foreground group-hover:text-accent transition-colors"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" />
                <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" />
              </svg>
              <div className="flex flex-col text-left">
                <span className="font-ui text-sm font-medium text-foreground group-hover:text-accent transition-colors">
                  Comptes liés
                </span>
                <span className="font-ui text-xs text-muted-foreground">Google, Apple</span>
              </div>
            </div>
            <ChevronRight
              className={`w-4 h-4 text-muted-foreground transition-transform ${expanded === "linked" ? "rotate-90" : ""}`}
            />
          </button>
          <AnimatePresence>
            {expanded === "linked" && (
              <motion.div
                key="linked-panel"
                initial="hidden"
                animate="visible"
                exit="hidden"
                variants={expandVariants}
                transition={{ duration: 0.25, ease: [0.25, 0.46, 0.45, 0.94] }}
              >
                <div className="px-5 pb-4 border-t border-dashed border-rule pt-3 flex flex-col gap-2">
                  <div className="flex items-center justify-between px-3 py-3 rounded-sm bg-[hsl(var(--highlight)/0.3)]">
                    <div className="flex items-center gap-3">
                      <svg className="w-5 h-5" viewBox="0 0 24 24">
                        <path
                          d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 01-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z"
                          fill="#4285F4"
                        />
                        <path
                          d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                          fill="#34A853"
                        />
                        <path
                          d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                          fill="#FBBC05"
                        />
                        <path
                          d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                          fill="#EA4335"
                        />
                      </svg>
                      <span className="font-ui text-sm text-foreground">Google</span>
                    </div>
                    <button
                      onClick={() => {
                        setLinkedGoogle(!linkedGoogle);
                        toast({ title: linkedGoogle ? "Google dissocié" : "Google associé" });
                      }}
                      className={`font-ui text-xs px-3 py-1.5 rounded-sm transition-colors ${
                        linkedGoogle
                          ? "bg-destructive/10 text-destructive hover:bg-destructive/20"
                          : "bg-primary text-primary-foreground hover:bg-primary/90"
                      }`}
                    >
                      {linkedGoogle ? "Dissocier" : "Associer"}
                    </button>
                  </div>
                  <div className="flex items-center justify-between px-3 py-3 rounded-sm bg-[hsl(var(--highlight)/0.3)]">
                    <div className="flex items-center gap-3">
                      <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M17.05 20.28c-.98.95-2.05.88-3.08.4-1.09-.5-2.08-.48-3.24 0-1.44.62-2.2.44-3.06-.4C2.79 15.25 3.51 7.59 9.05 7.31c1.35.07 2.29.74 3.08.8 1.18-.24 2.31-.93 3.57-.84 1.51.12 2.65.72 3.4 1.8-3.12 1.87-2.38 5.98.48 7.13-.57 1.5-1.31 2.99-2.54 4.09zM12.03 7.25c-.15-2.23 1.66-4.07 3.74-4.25.29 2.58-2.34 4.5-3.74 4.25z" />
                      </svg>
                      <span className="font-ui text-sm text-foreground">Apple</span>
                    </div>
                    <button
                      onClick={() => {
                        setLinkedApple(!linkedApple);
                        toast({ title: linkedApple ? "Apple dissocié" : "Apple associé" });
                      }}
                      className={`font-ui text-xs px-3 py-1.5 rounded-sm transition-colors ${
                        linkedApple
                          ? "bg-destructive/10 text-destructive hover:bg-destructive/20"
                          : "bg-primary text-primary-foreground hover:bg-primary/90"
                      }`}
                    >
                      {linkedApple ? "Dissocier" : "Associer"}
                    </button>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </SettingsCard>

        {/* ─── MOT DE PASSE ─── */}
        <SettingsCard>
          <button
            onClick={() => toggle("password")}
            className="w-full flex items-center justify-between px-5 py-4 group"
          >
            <div className="flex items-center gap-3">
              <Lock className="w-4 h-4 text-muted-foreground group-hover:text-accent transition-colors" />
              <div className="flex flex-col text-left">
                <span className="font-ui text-sm font-medium text-foreground group-hover:text-accent transition-colors">
                  Mot de passe
                </span>
                <span className="font-ui text-xs text-muted-foreground">Modifier votre mot de passe</span>
              </div>
            </div>
            <ChevronRight
              className={`w-4 h-4 text-muted-foreground transition-transform ${expanded === "password" ? "rotate-90" : ""}`}
            />
          </button>
          <AnimatePresence>
            {expanded === "password" && (
              <motion.div
                key="password-panel"
                initial="hidden"
                animate="visible"
                exit="hidden"
                variants={expandVariants}
                transition={{ duration: 0.25, ease: [0.25, 0.46, 0.45, 0.94] }}
              >
                <div className="px-5 pb-5 border-t border-dashed border-rule pt-4 flex flex-col gap-3">
                  <div>
                    <label className="font-ui text-xs text-muted-foreground mb-1 block">Mot de passe actuel</label>
                    <div className="relative">
                      <input
                        type={showCurrent ? "text" : "password"}
                        value={currentPassword}
                        onChange={(e) => setCurrentPassword(e.target.value)}
                        className="w-full h-10 px-3 pr-10 rounded-sm border border-input bg-background font-ui text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
                      />
                      <button
                        type="button"
                        onClick={() => setShowCurrent(!showCurrent)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                      >
                        {showCurrent ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                    </div>
                  </div>
                  <div>
                    <label className="font-ui text-xs text-muted-foreground mb-1 block">Nouveau mot de passe</label>
                    <div className="relative">
                      <input
                        type={showNew ? "text" : "password"}
                        value={newPassword}
                        onChange={(e) => setNewPassword(e.target.value)}
                        className="w-full h-10 px-3 pr-10 rounded-sm border border-input bg-background font-ui text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
                      />
                      <button
                        type="button"
                        onClick={() => setShowNew(!showNew)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                      >
                        {showNew ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                    </div>
                    {newPassword.length > 0 && (
                      <ul className="mt-2 space-y-1">
                        {PASSWORD_RULES.map((rule) => {
                          const pass = rule.test(newPassword);
                          return (
                            <li key={rule.label} className="flex items-center gap-2">
                              {pass ? (
                                <Check className="w-3 h-3 text-accent" />
                              ) : (
                                <X className="w-3 h-3 text-destructive" />
                              )}
                              <span className={`font-ui text-xs ${pass ? "text-accent" : "text-destructive"}`}>
                                {rule.label}
                              </span>
                            </li>
                          );
                        })}
                      </ul>
                    )}
                  </div>
                  <div>
                    <label className="font-ui text-xs text-muted-foreground mb-1 block">
                      Confirmer le mot de passe
                    </label>
                    <div className="relative">
                      <input
                        type={showConfirm ? "text" : "password"}
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        className="w-full h-10 px-3 pr-10 rounded-sm border border-input bg-background font-ui text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
                      />
                      <button
                        type="button"
                        onClick={() => setShowConfirm(!showConfirm)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                      >
                        {showConfirm ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                    </div>
                    {confirmPassword.length > 0 && !passwordsMatch && (
                      <p className="font-ui text-xs text-destructive mt-1">Les mots de passe ne correspondent pas</p>
                    )}
                  </div>
                  <button
                    onClick={handlePasswordChange}
                    disabled={!passwordValid || !passwordsMatch || !currentPassword}
                    className="mt-1 w-full py-2.5 rounded-sm bg-primary text-primary-foreground font-ui text-sm font-medium hover:bg-primary/90 transition-colors disabled:opacity-40 disabled:pointer-events-none active:scale-[0.98]"
                  >
                    Modifier le mot de passe
                  </button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </SettingsCard>

        <div className="w-full h-px bg-[hsl(var(--rule))] my-2" />

        {/* ─── DÉCONNEXION ─── */}
        <SettingsCard>
          <button onClick={handleLogout} className="w-full flex items-center gap-3 px-5 py-4 group">
            <LogOut className="w-4 h-4 text-muted-foreground group-hover:text-foreground transition-colors" />
            <span className="font-ui text-sm font-medium text-foreground">Se déconnecter</span>
          </button>
        </SettingsCard>

        {/* ─── SUPPRIMER ─── */}
        <SettingsCard variant="danger">
          <button onClick={() => toggle("delete")} className="w-full flex items-center justify-between px-5 py-4 group">
            <div className="flex items-center gap-3">
              <Trash2 className="w-4 h-4 text-destructive" />
              <div className="flex flex-col text-left">
                <span className="font-ui text-sm font-medium text-destructive">Supprimer mon compte</span>
                <span className="font-ui text-xs text-muted-foreground">Cette action est irréversible</span>
              </div>
            </div>
            <ChevronRight
              className={`w-4 h-4 text-destructive/60 transition-transform ${expanded === "delete" ? "rotate-90" : ""}`}
            />
          </button>
          <AnimatePresence>
            {expanded === "delete" && (
              <motion.div
                key="delete-panel"
                initial="hidden"
                animate="visible"
                exit="hidden"
                variants={expandVariants}
                transition={{ duration: 0.25, ease: [0.25, 0.46, 0.45, 0.94] }}
              >
                <div className="px-5 pb-5 border-t border-dashed border-destructive/20 pt-4 flex flex-col gap-3">
                  <p className="font-body text-sm text-muted-foreground">
                    Toutes vos données, archives et préférences seront définitivement supprimées. Tapez{" "}
                    <strong className="text-destructive">SUPPRIMER</strong> et saisissez votre mot de passe pour
                    confirmer.
                  </p>
                  <div>
                    <label className="font-ui text-xs text-muted-foreground mb-1 block">Mot de passe</label>
                    <div className="relative">
                      <input
                        type={showDeletePassword ? "text" : "password"}
                        value={deletePassword}
                        onChange={(e) => setDeletePassword(e.target.value)}
                        placeholder="Votre mot de passe"
                        className="w-full h-10 px-3 pr-10 rounded-sm border border-destructive/30 bg-background font-ui text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-destructive/50"
                      />
                      <button
                        type="button"
                        onClick={() => setShowDeletePassword(!showDeletePassword)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                      >
                        {showDeletePassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                    </div>
                  </div>
                  <input
                    type="text"
                    value={deleteConfirm}
                    onChange={(e) => setDeleteConfirm(e.target.value)}
                    placeholder="SUPPRIMER"
                    className="w-full h-10 px-3 rounded-sm border border-destructive/30 bg-background font-ui text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-destructive/50"
                  />
                  <button
                    onClick={handleDeleteAccount}
                    disabled={deleteConfirm !== "SUPPRIMER" || !deletePassword}
                    className="w-full py-2.5 rounded-sm bg-destructive text-destructive-foreground font-ui text-sm font-medium hover:bg-destructive/90 transition-colors disabled:opacity-40 disabled:pointer-events-none active:scale-[0.98]"
                  >
                    Supprimer définitivement
                  </button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </SettingsCard>

        {/* ─── DEMO (temporaire) ─── */}
        <div className="mt-4">
          <SettingsCard>
            <button
              onClick={() => navigate("/demo")}
              className="w-full flex items-center gap-3 px-5 py-4 group"
            >
              <svg className="w-4 h-4 text-muted-foreground group-hover:text-accent transition-colors" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <polygon points="5 3 19 12 5 21 5 3" />
              </svg>
              <span className="font-ui text-sm font-medium text-foreground group-hover:text-accent transition-colors">Demo</span>
            </button>
          </SettingsCard>
        </div>
      </div>

      <footer className="w-full px-6 py-4 border-t border-border mt-auto">
        <div className="max-w-3xl mx-auto flex items-center justify-between px-4">
          {["Mentions légales", "Politique de confidentialité", "Contact", "À propos"].map((item) => (
            <button
              key={item}
              type="button"
              className="font-ui text-xs text-muted-foreground transition-colors duration-150 hover:text-muted-foreground/50 active:text-foreground cursor-pointer select-none bg-transparent border-none p-0"
            >
              {item}
            </button>
          ))}
        </div>
      </footer>
    </div>
  );
};

const SettingsCard = ({ children, variant }: { children: React.ReactNode; variant?: "danger" }) => (
  <div className="relative">
    <div
      className="absolute inset-0 rounded-sm"
      style={{
        background: "hsl(25 20% 20% / 0.06)",
        filter: "blur(10px)",
        transform: "translate(3px, 4px)",
      }}
    />
    <div
      className={`relative bg-[hsl(var(--paper))] border rounded-sm overflow-hidden ${
        variant === "danger" ? "border-destructive/20" : "border-border"
      }`}
      style={{
        backgroundImage: PAPER_NOISE,
      }}
    >
      {children}
    </div>
  </div>
);

export default Settings;
