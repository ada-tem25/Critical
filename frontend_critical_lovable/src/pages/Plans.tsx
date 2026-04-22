import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { usePlan, type PlanName } from "@/contexts/PlanContext";
import { ArrowLeft, Check, Sparkles, Zap, Crown, ArrowDown } from "lucide-react";
import Header from "@/components/Header";
import PlanCheckoutDialog from "@/components/PlanCheckoutDialog";
import { motion } from "framer-motion";
import { useIsMobile } from "@/hooks/use-mobile";

const PAPER_NOISE =
  "url(\"data:image/svg+xml,%3Csvg width='100' height='100' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100' height='100' filter='url(%23n)' opacity='0.05'/%3E%3C/svg%3E\")";

interface PlanFeature {
  text: string;
  included: boolean;
}

interface PlanData {
  name: string;
  price: string;
  period: string;
  description: string;
  icon: React.ReactNode;
  features: PlanFeature[];
  popular?: boolean;
}

const plans: PlanData[] = [
  {
    name: "Free",
    price: "0 €",
    period: "/ mois",
    description: "Pour découvrir l'analyse critique",
    icon: <Sparkles className="w-5 h-5" />,
    features: [
      { text: "5 crédits par jour", included: true },
      { text: "Export PDF", included: false },
      { text: "Analyses de discours", included: false },
    ],
  },
  {
    name: "Pro",
    price: "9 €",
    period: "/ mois",
    description: "Pour les esprits curieux",
    icon: <Zap className="w-5 h-5" />,
    popular: true,
    features: [
      { text: "15 crédits par jour", included: true },
      { text: "Export PDF", included: true },
      { text: "Analyses de discours", included: true },
    ],
  },
  {
    name: "Premium",
    price: "19 €",
    period: "/ mois",
    description: "Pour les professionnels de l'info",
    icon: <Crown className="w-5 h-5" />,
    features: [
      { text: "50 crédits par jour", included: true },
      { text: "Export PDF", included: true },
      { text: "Analyses de discours", included: true },
    ],
  },
];

const Plans = () => {
  const navigate = useNavigate();
  const [profileOpen, setProfileOpen] = useState(false);
  const { currentPlan, setCurrentPlan, renewalDate } = usePlan();
  const isMobile = useIsMobile();
  const [checkoutTarget, setCheckoutTarget] = useState<PlanName | null>(null);

  return (
    <div className="min-h-screen flex flex-col bg-background">
      <Header
        title="Abonnements"
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
          onClick={() => navigate(-1)}
          className="flex items-center gap-2 font-ui text-sm text-muted-foreground hover:text-foreground transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Retour
        </button>
      </div>

      {/* Renewal notice moved below cards */}

      {/* Subtitle */}
      <div className="text-center mt-8 mb-12 px-6">
        <h2 className="font-display text-3xl md:text-4xl font-bold text-foreground mb-3">
          Choisissez votre formule
        </h2>
        <p className="font-body text-base text-muted-foreground max-w-md mx-auto">
          Accédez à des analyses plus profondes et des outils exclusifs pour décrypter l'information.
        </p>
      </div>

      {/* Cards */}
      <div className="flex justify-center px-6 pb-20">
        <div className="flex flex-col md:flex-row items-center md:items-stretch gap-6 md:gap-0">
          {plans.map((plan, index) => {
            const isCurrent = plan.name === currentPlan;
            const planOrder = ["Free", "Pro", "Premium"];
            const currentIndex = planOrder.indexOf(currentPlan);
            const planIndex = planOrder.indexOf(plan.name);
            const isUpgrade = planIndex > currentIndex;
            const isPremiumCurrent = currentPlan === "Premium";
            const rotations = [-2.5, 0, 2.5];
            const baseZIndexes = [10, 20, 10];
            const zIndexes = isPremiumCurrent ? [10, 10, 20] : baseZIndexes;
            const offsets = ["md:translate-x-4", "", "md:-translate-x-4"];

            return (
              <motion.div
                key={plan.name}
                initial={{ opacity: 0, y: 40 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: index * 0.12, ease: [0.25, 0.46, 0.45, 0.94] }}
                className={`relative transition-transform duration-300 hover:scale-[1.03] ${offsets[index]} ${
                  isCurrent ? "md:-mt-4 md:mb-4" : ""
                }`}
                style={{
                  zIndex: zIndexes[index],
                  rotate: isMobile ? 0 : rotations[index],
                }}
              >
                {/* Shadow */}
                <div
                  className="absolute inset-0 rounded-sm"
                  style={{
                    background: "hsl(25 20% 20% / 0.1)",
                    filter: isCurrent ? "blur(20px)" : "blur(14px)",
                    transform: "translate(4px, 6px)",
                  }}
                />

                {/* Card */}
                <div
                  className={`relative w-72 bg-[hsl(var(--paper))] border rounded-sm overflow-hidden ${
                    isCurrent
                      ? "border-accent ring-2 ring-accent/20"
                      : "border-border"
                  }`}
                  style={{ backgroundImage: PAPER_NOISE }}
                >
                  {/* Current plan badge */}
                  {isCurrent && (
                    <div className="bg-accent text-accent-foreground font-ui text-[10px] uppercase tracking-wider font-semibold text-center py-1.5">
                      Plan actuel
                    </div>
                  )}

                  {/* Popular badge */}
                  {plan.popular && !isCurrent && !isPremiumCurrent && (
                    <div className="bg-primary text-primary-foreground font-ui text-[10px] uppercase tracking-wider font-semibold text-center py-1.5">
                      Populaire
                    </div>
                  )}

                  {/* Eyelets */}
                  <div className="flex items-center justify-center gap-6 py-3 border-b border-dashed border-rule">
                    {[0, 1, 2].map((i) => (
                      <div key={i} className="relative">
                        <div
                          className="w-3.5 h-3.5 rounded-full border border-rule"
                          style={{
                            background:
                              "linear-gradient(135deg, hsl(25 15% 78% / 0.5) 0%, hsl(30 12% 70% / 0.4) 100%)",
                          }}
                        />
                        <div
                          className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-1.5 h-1.5 rounded-full"
                          style={{ boxShadow: "inset 0 1px 2px hsl(25 20% 20% / 0.3)" }}
                        />
                      </div>
                    ))}
                  </div>

                  {/* Content */}
                  <div className="px-5 py-5">
                    <div className="flex items-center gap-2.5 mb-1">
                      <span className="text-muted-foreground">{plan.icon}</span>
                      <h3 className="font-display text-lg font-bold text-foreground">
                        {plan.name}
                      </h3>
                    </div>

                    <p className="font-body text-sm text-muted-foreground mb-4">
                      {plan.description}
                    </p>

                    <div className="flex items-baseline gap-1 mb-5">
                      <span className="font-display text-3xl font-bold text-foreground">
                        {plan.price}
                      </span>
                      <span className="font-ui text-sm text-muted-foreground">
                        {plan.period}
                      </span>
                    </div>

                    {/* Torn divider */}
                    <div
                      className="w-full h-px bg-rule mb-4"
                      style={{
                        maskImage:
                          "url(\"data:image/svg+xml,%3Csvg width='200' height='2' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M0,1 Q10,0 20,1 T40,1 T60,1 T80,1 T100,1 T120,1 T140,1 T160,1 T180,1 T200,1' stroke='black' fill='none' stroke-width='2'/%3E%3C/svg%3E\")",
                        WebkitMaskImage:
                          "url(\"data:image/svg+xml,%3Csvg width='200' height='2' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M0,1 Q10,0 20,1 T40,1 T60,1 T80,1 T100,1 T120,1 T140,1 T160,1 T180,1 T200,1' stroke='black' fill='none' stroke-width='2'/%3E%3C/svg%3E\")",
                      }}
                    />

                    {/* Features */}
                    <ul className="space-y-2.5 mb-6">
                      {plan.features.map((feat) => (
                        <li key={feat.text} className="flex items-start gap-2.5">
                          <Check
                            className={`w-4 h-4 mt-0.5 flex-shrink-0 ${
                              feat.included ? "text-accent" : "text-muted-foreground/30"
                            }`}
                            strokeWidth={feat.included ? 2.5 : 1.5}
                          />
                          <span
                            className={`font-ui text-sm ${
                              feat.included
                                ? "text-foreground"
                                : "text-muted-foreground/50 line-through"
                            }`}
                          >
                            {feat.text}
                          </span>
                        </li>
                      ))}
                    </ul>

                    {/* Action button */}
                    {isCurrent ? (
                      <div className="w-full py-2.5 rounded-sm border border-border bg-secondary text-center font-ui text-sm text-muted-foreground">
                        Plan actuel
                      </div>
                    ) : isUpgrade ? (
                      <button
                        onClick={() => setCheckoutTarget(plan.name as PlanName)}
                        className="w-full py-2.5 rounded-sm bg-primary text-primary-foreground font-ui text-sm font-medium hover:bg-primary/90 transition-colors active:scale-[0.98]"
                      >
                        Passer à {plan.name}
                      </button>
                    ) : (
                      <button
                        onClick={() => setCheckoutTarget(plan.name as PlanName)}
                        className="w-full py-2 rounded-sm border border-border font-ui text-xs text-muted-foreground hover:text-foreground hover:border-foreground/30 transition-colors flex items-center justify-center gap-1.5"
                      >
                        <ArrowDown className="w-3 h-3" />
                        Rétrograder
                      </button>
                    )}
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>

      {/* Renewal notice */}
      {renewalDate && currentPlan !== "Free" && (
        <div className="text-center px-6 pb-8 -mt-12">
          <p className="font-ui text-xs text-muted-foreground">
            Votre abonnement {currentPlan} sera renouvelé le{" "}
            {renewalDate.toLocaleDateString("fr-FR", { day: "numeric", month: "long", year: "numeric" })}
          </p>
        </div>
      )}

      <PlanCheckoutDialog
        open={!!checkoutTarget}
        onOpenChange={(open) => !open && setCheckoutTarget(null)}
        currentPlan={currentPlan}
        targetPlan={checkoutTarget ?? currentPlan}
        onConfirm={() => {
          if (checkoutTarget) {
            setCurrentPlan(checkoutTarget);
            setCheckoutTarget(null);
          }
        }}
      />
    </div>
  );
};

export default Plans;
