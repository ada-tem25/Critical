import { useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { demoArticles } from "@/data/demoArticles";
import TypewriterTitle from "@/components/TypewriterTitle";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { ArrowRight, Menu, X } from "lucide-react";

type Lang = "fr" | "en";

const PAPER_NOISE =
  "url(\"data:image/svg+xml,%3Csvg width='100' height='100' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100' height='100' filter='url(%23n)' opacity='0.05'/%3E%3C/svg%3E\")";

const t = (lang: Lang, text: { fr: string; en: string }) => text[lang];

import { getVerdictBgColor } from "@/data/articles";

const faqItems = [
  {
    q: { fr: "Comment fonctionne Critical ?", en: "How does Critical work?" },
    a: { fr: "Réponse à venir.", en: "Answer coming soon." },
  },
  {
    q: { fr: "Quelle technologie d'IA utilisez-vous ?", en: "What AI technology do you use?" },
    a: { fr: "Réponse à venir.", en: "Answer coming soon." },
  },
  {
    q: {
      fr: "En quoi Critical est-il différent de ChatGPT ou d'un chatbot classique ?",
      en: "How is Critical different from ChatGPT or a regular chatbot?",
    },
    a: { fr: "Réponse à venir.", en: "Answer coming soon." },
  },
  {
    q: { fr: "Comment Critical choisit-il ses sources ?", en: "How does Critical choose its sources?" },
    a: { fr: "Réponse à venir.", en: "Answer coming soon." },
  },
  {
    q: {
      fr: "Comment limitez-vous les hallucinations de l'IA ?",
      en: "How do you limit AI hallucinations?",
    },
    a: { fr: "Réponse à venir.", en: "Answer coming soon." },
  },
  {
    q: { fr: "Critical a-t-il des engagements politiques ?", en: "Does Critical have political commitments?" },
    a: { fr: "Réponse à venir.", en: "Answer coming soon." },
  },
  {
    q: { fr: "Qu'est-ce que la détection rhétorique ?", en: "What is rhetoric detection?" },
    a: { fr: "Réponse à venir.", en: "Answer coming soon." },
  },
  {
    q: { fr: "Critical est-il gratuit ?", en: "Is Critical free?" },
    a: { fr: "Réponse à venir.", en: "Answer coming soon." },
  },
  {
    q: {
      fr: "Puis-je analyser n'importe quel type de contenu ?",
      en: "Can I analyze any type of content?",
    },
    a: { fr: "Réponse à venir.", en: "Answer coming soon." },
  },
  {
    q: { fr: "Critical peut-il se tromper ?", en: "Can Critical be wrong?" },
    a: { fr: "Réponse à venir.", en: "Answer coming soon." },
  },
];

const Demo = () => {
  const [lang, setLang] = useState<Lang>("fr");
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const navigate = useNavigate();
  const approachRef = useRef<HTMLElement>(null);
  const examplesRef = useRef<HTMLElement>(null);
  const faqRef = useRef<HTMLElement>(null);

  const scrollTo = (ref: React.RefObject<HTMLElement | null>) => {
    const el = ref.current;
    if (!el) return;
    const target = el.getBoundingClientRect().top + window.scrollY - 80;
    const start = window.scrollY;
    const distance = target - start;
    const duration = 1200;
    let startTime: number | null = null;

    const easeInOutCubic = (t: number) =>
      t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;

    const step = (timestamp: number) => {
      if (!startTime) startTime = timestamp;
      const elapsed = timestamp - startTime;
      const progress = Math.min(elapsed / duration, 1);
      window.scrollTo(0, start + distance * easeInOutCubic(progress));
      if (progress < 1) requestAnimationFrame(step);
    };

    requestAnimationFrame(step);
  };

  return (
    <div className="min-h-screen bg-background flex flex-col scroll-smooth">
      {/* Header */}
      <header className="w-full px-6 py-4 flex items-center justify-between border-b border-border relative">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-sm bg-primary flex items-center justify-center">
            <span className="text-primary-foreground font-display font-bold text-sm">C</span>
          </div>
          <span className="font-display text-xl font-semibold tracking-tight text-foreground">
            Critical
          </span>
        </div>

        {/* Desktop nav */}
        <nav className="hidden md:flex items-center gap-6 absolute left-1/2 -translate-x-1/2">
          {[
            { ref: approachRef, label: { fr: "Notre approche", en: "Our approach" } },
            { ref: examplesRef, label: { fr: "Exemples", en: "Examples" } },
            { ref: faqRef, label: { fr: "FAQ", en: "FAQ" } },
          ].map((item, i) => (
            <button
              key={i}
              onClick={() => scrollTo(item.ref)}
              className="relative font-ui text-sm text-foreground cursor-pointer group py-1"
            >
              {t(lang, item.label)}
              <span className="absolute left-0 bottom-0 w-full h-[1.5px] bg-foreground origin-left scale-x-0 transition-transform duration-300 ease-out group-hover:scale-x-100" />
            </button>
          ))}
        </nav>

        {/* Desktop lang toggle */}
        <div className="hidden md:flex justify-end">
          <button
            onClick={() => setLang(lang === "fr" ? "en" : "fr")}
            className="font-ui text-sm text-foreground flex items-center gap-2 cursor-pointer"
          >
            <span className={lang === "fr" ? "border-b-2 border-foreground" : ""}>FR</span>
            <span>/</span>
            <span className={lang === "en" ? "border-b-2 border-foreground" : ""}>ENG</span>
          </button>
        </div>

        {/* Mobile menu button */}
        <button
          className="md:hidden w-9 h-9 flex items-center justify-center"
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          aria-label="Menu"
        >
          {mobileMenuOpen ? <X className="w-5 h-5 text-foreground" /> : <Menu className="w-5 h-5 text-foreground" />}
        </button>

        {/* Mobile dropdown */}
        <AnimatePresence>
          {mobileMenuOpen && (
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.25, ease: [0.25, 0.1, 0.25, 1] }}
              className="absolute top-full left-0 w-full bg-background border-b border-border z-50 px-6 py-4 flex flex-col gap-4 md:hidden"
            >
            <div className="flex items-center justify-between">
              <button
                onClick={() => { scrollTo(approachRef); setMobileMenuOpen(false); }}
                className="font-ui text-sm text-foreground text-left cursor-pointer"
              >
                {t(lang, { fr: "Notre approche", en: "Our approach" })}
              </button>
              <button
                onClick={() => setLang(lang === "fr" ? "en" : "fr")}
                className="font-ui text-sm text-foreground flex items-center gap-2 cursor-pointer"
              >
                <span className={lang === "fr" ? "border-b-2 border-foreground" : ""}>FR</span>
                <span>/</span>
                <span className={lang === "en" ? "border-b-2 border-foreground" : ""}>ENG</span>
              </button>
            </div>
            <button
              onClick={() => { scrollTo(examplesRef); setMobileMenuOpen(false); }}
              className="font-ui text-sm text-foreground text-left cursor-pointer"
            >
              {t(lang, { fr: "Exemples", en: "Examples" })}
            </button>
            <button
              onClick={() => { scrollTo(faqRef); setMobileMenuOpen(false); }}
              className="font-ui text-sm text-foreground text-left cursor-pointer"
            >
              {t(lang, { fr: "FAQ", en: "FAQ" })}
            </button>
            </motion.div>
          )}
        </AnimatePresence>
      </header>

      {/* Hero */}
      <section className="max-w-3xl mx-auto w-full px-6 pt-16 pb-12 text-center">
        <TypewriterTitle interval={8000} />
        <p className="font-body text-lg text-muted-foreground mb-10 max-w-xl mx-auto mt-4">
          Critical combine fact-checking et analyse critique grâce à l'intelligence artificielle.
        </p>

        {/* Flow infographic */}
        <div className="flex items-center justify-center gap-3 md:gap-5 flex-wrap font-ui text-sm">
          <div className="flex flex-col items-center gap-1.5 px-4 py-3 rounded-sm border border-border bg-[hsl(var(--paper))]" style={{ backgroundImage: PAPER_NOISE }}>
            <span className="text-2xl">📰🎙️🐦</span>
            <span className="text-foreground font-medium">
              {t(lang, { fr: "Sources multi-modales", en: "Multi-modal sources" })}
            </span>
          </div>
          <ArrowRight className="w-5 h-5 text-muted-foreground shrink-0" />
          <div className="flex flex-col items-center gap-1.5 px-4 py-3 rounded-sm border border-border bg-[hsl(var(--paper))]" style={{ backgroundImage: PAPER_NOISE }}>
            <span className="text-2xl">🔍</span>
            <span className="text-foreground font-medium">Critical</span>
          </div>
          <ArrowRight className="w-5 h-5 text-muted-foreground shrink-0" />
          <div className="flex flex-col items-center gap-1.5 px-4 py-3 rounded-sm border border-border bg-[hsl(var(--paper))]" style={{ backgroundImage: PAPER_NOISE }}>
            <span className="text-2xl">✅📊</span>
            <span className="text-foreground font-medium">
              {t(lang, { fr: "Fact-checking & Analyse", en: "Fact-checking & Analysis" })}
            </span>
          </div>
        </div>
      </section>

      {/* Divider */}
      <div className="w-16 h-px bg-[hsl(var(--rule))] mx-auto mb-14" />

      {/* Notre approche */}
      <section ref={approachRef} className="max-w-2xl mx-auto w-full px-6 pb-14 scroll-mt-20">
        <h2 className="font-display text-3xl font-bold text-foreground mb-2">
          {t(lang, { fr: "Notre approche", en: "Our approach" })}
        </h2>
        <p className="font-ui text-sm text-muted-foreground mb-6 uppercase tracking-wider">
          {t(lang, {
            fr: "Objectivité · Transparence · Esprit critique",
            en: "Objectivity · Transparency · Critical thinking",
          })}
        </p>
        <div className="space-y-4 font-body text-base text-foreground/85 leading-relaxed">
          <p>
            {t(lang, {
              fr: "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
              en: "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
            })}
          </p>
          <p>
            {t(lang, {
              fr: "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
              en: "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
            })}
          </p>
        </div>
      </section>

      {/* Divider */}
      <div className="w-16 h-px bg-[hsl(var(--rule))] mx-auto mb-14" />

      {/* Examples */}
      <section ref={examplesRef} className="max-w-2xl mx-auto w-full px-6 pb-16 scroll-mt-20">
        <h2 className="font-display text-3xl font-bold text-foreground mb-8">
          {t(lang, { fr: "Exemples", en: "Examples" })}
        </h2>
        <div className="flex flex-col items-center gap-8">
          {demoArticles
            .filter((a) => {
              if (!a.language) return true;
              return a.language === (lang === "fr" ? "French" : "English");
            })
            .map((article, i) => {
            const rotation = i % 2 === 0 ? -1.2 : 1.2;
            return (
              <motion.button
                key={article.id}
                onClick={() => navigate(`/demo/article/${article.id}?lang=${lang}`)}
                className="relative text-left cursor-pointer group w-full"
                style={{ rotate: `${rotation}deg` }}
                whileHover={{ y: -8, rotate: 0 }}
                transition={{ type: "spring", stiffness: 300, damping: 20 }}
              >
                <div
                  className="absolute inset-0 rounded-sm transition-all duration-300 group-hover:opacity-100 opacity-60"
                  style={{
                    background: "hsl(25 20% 20% / 0.1)",
                    filter: "blur(12px)",
                    transform: "translate(4px, 6px)",
                  }}
                />
                <div
                  className="relative bg-[hsl(var(--paper))] border border-border rounded-sm p-8 flex flex-col gap-3 transition-shadow duration-300 group-hover:shadow-xl"
                  style={{ backgroundImage: PAPER_NOISE }}
                >
                  <span className={`font-ui text-[10px] font-bold tracking-widest uppercase px-2 py-0.5 rounded-sm w-fit ${getVerdictBgColor(article.verdict)}`}>
                    {article.verdict}
                  </span>
                  <h4 className="font-display text-xl font-bold text-foreground leading-snug">
                    {article.title}
                  </h4>
                  {article.subtitle && (
                    <p className="font-body text-sm text-muted-foreground">
                      {article.subtitle}
                    </p>
                  )}
                  <p className="font-body text-sm text-foreground/80 leading-relaxed mt-1">
                    {article.summary}
                  </p>
                  <div className="mt-3 flex items-center gap-2 font-ui text-xs text-muted-foreground">
                    <span>{article.author}</span>
                    <span className="text-rule">·</span>
                    <span>{article.date}</span>
                  </div>
                </div>
              </motion.button>
            );
          })}
        </div>
      </section>

      {/* Divider */}
      <div className="w-16 h-px bg-[hsl(var(--rule))] mx-auto mb-14" />

      {/* FAQ */}
      <section ref={faqRef} className="max-w-2xl mx-auto w-full px-6 pb-20 scroll-mt-20">
        <h2 className="font-display text-3xl font-bold text-foreground mb-6">
          {t(lang, { fr: "Questions fréquentes", en: "Frequently asked questions" })}
        </h2>
        <Accordion type="single" collapsible className="w-full">
          {faqItems.map((item, i) => (
            <AccordionItem key={i} value={`faq-${i}`} className="border-[hsl(var(--rule))]">
              <AccordionTrigger className="font-body text-sm text-foreground hover:no-underline py-4">
                {t(lang, item.q)}
              </AccordionTrigger>
              <AccordionContent className="font-body text-sm text-muted-foreground leading-relaxed">
                {t(lang, item.a)}
              </AccordionContent>
            </AccordionItem>
          ))}
        </Accordion>
      </section>
    </div>
  );
};

export default Demo;
