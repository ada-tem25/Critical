import { ArrowLeft } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useState } from "react";
import Header from "@/components/Header";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";

const faqItems = [
  { q: "Comment fonctionne Critical ?", a: "Réponse à venir." },
  { q: "Quelle technologie d'IA utilisez-vous ?", a: "Réponse à venir." },
  { q: "En quoi Critical est-il différent de ChatGPT ou d'un chatbot classique ?", a: "Réponse à venir." },
  { q: "Comment Critical choisit-il ses sources ?", a: "Réponse à venir." },
  { q: "Comment limitez-vous les hallucinations de l'IA ?", a: "Réponse à venir." },
  { q: "Critical a-t-il des engagements politiques ?", a: "Réponse à venir." },
  { q: "Qu'est-ce que la détection rhétorique ?", a: "Réponse à venir." },
  { q: "Critical est-il gratuit ?", a: "Réponse à venir." },
  { q: "Puis-je analyser n'importe quel type de contenu ?", a: "Réponse à venir." },
  { q: "Critical peut-il se tromper ?", a: "Réponse à venir." },
];

const Approach = () => {
  const navigate = useNavigate();
  const [profileOpen, setProfileOpen] = useState(false);

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Header
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

      <main className="max-w-2xl mx-auto w-full px-6 py-8">
        {/* Notre approche section */}
        <section className="mb-14">
          <h2 className="font-display text-3xl font-bold text-foreground mb-2">
            Notre approche
          </h2>
          <p className="font-ui text-sm text-muted-foreground mb-6 uppercase tracking-wider">
            Objectivité · Transparence · Esprit critique
          </p>
          <div className="space-y-4 font-body text-base text-foreground/85 leading-relaxed">
            <p>
              Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
            </p>
            <p>
              Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
            </p>
          </div>
        </section>

        {/* Divider */}
        <div className="w-16 h-px bg-[hsl(var(--rule))] mx-auto mb-14" />

        {/* FAQ */}
        <section>
          <h2 className="font-display text-2xl font-bold text-foreground mb-6">
            Questions fréquentes
          </h2>
          <Accordion type="single" collapsible className="w-full">
            {faqItems.map((item, i) => (
              <AccordionItem key={i} value={`faq-${i}`} className="border-[hsl(var(--rule))]">
                <AccordionTrigger className="font-body text-sm text-foreground hover:no-underline py-4">
                  {item.q}
                </AccordionTrigger>
                <AccordionContent className="font-body text-sm text-muted-foreground leading-relaxed">
                  {item.a}
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </section>
      </main>
    </div>
  );
};

export default Approach;
