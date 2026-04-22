import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { ArrowRight, CreditCard, Check, X, CalendarClock, Crown, Zap, Sparkles } from "lucide-react";
import type { PlanName } from "@/contexts/PlanContext";

interface PlanCheckoutDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  currentPlan: PlanName;
  targetPlan: PlanName;
  onConfirm: () => void;
}

const planDetails: Record<PlanName, { price: string; credits: number; features: string[] }> = {
  Free: { price: "0 €", credits: 5, features: [] },
  Pro: { price: "9 €", credits: 15, features: ["Export PDF", "Analyses de discours"] },
  Premium: { price: "19 €", credits: 50, features: ["Export PDF", "Analyses de discours"] },
};

const PlanCheckoutDialog = ({ open, onOpenChange, currentPlan, targetPlan, onConfirm }: PlanCheckoutDialogProps) => {
  const isUpgrade = ["Free", "Pro", "Premium"].indexOf(targetPlan) > ["Free", "Pro", "Premium"].indexOf(currentPlan);
  const current = planDetails[currentPlan];
  const target = planDetails[targetPlan];

  // Only non-credit features for gained/lost
  const gained = target.features.filter((f) => !current.features.includes(f));
  const lost = current.features.filter((f) => !target.features.includes(f));

  const creditDiff = target.credits - current.credits;

  // Renewal / effective date
  const now = new Date();
  const renewalDay = now.getDate();
  const nextRenewal = new Date(now.getFullYear(), now.getMonth() + 1, renewalDay);
  const formatDate = (d: Date) =>
    d.toLocaleDateString("fr-FR", { day: "numeric", month: "long", year: "numeric" });

  const isDowngradeToFree = !isUpgrade && targetPlan === "Free";

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md bg-[hsl(var(--paper))]">
        <DialogHeader>
         <DialogTitle className="font-display text-xl flex items-center gap-2">
            {isUpgrade ? "Passer à" : "Rétrograder vers"}{" "}
            {targetPlan === "Premium" ? <Crown className="w-5 h-5 inline" /> : targetPlan === "Pro" ? <Zap className="w-5 h-5 inline" /> : <Sparkles className="w-5 h-5 inline" />}
            {targetPlan}
          </DialogTitle>
          <DialogDescription className="font-body text-sm">
            Récapitulatif des changements sur votre abonnement.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-2">
          {/* Price change */}
          <div className="flex items-center justify-between rounded-sm border border-border bg-secondary/50 px-4 py-3">
            <div className="font-ui text-sm text-muted-foreground">Tarif mensuel</div>
            <div className="flex items-center gap-2">
              <span className="font-ui text-sm text-muted-foreground line-through">{current.price}/mois</span>
              <ArrowRight className="w-3.5 h-3.5 text-muted-foreground" />
              <span className="font-display text-base font-bold text-foreground">{target.price}/mois</span>
            </div>
          </div>

          {/* Credits change */}
          <div className="flex items-center justify-between rounded-sm border border-border bg-secondary/50 px-4 py-3">
            <div className="font-ui text-sm text-muted-foreground">Crédits quotidiens</div>
            <div className="flex items-center gap-2">
              <span className="font-ui text-sm text-muted-foreground">{current.credits}</span>
              <ArrowRight className="w-3.5 h-3.5 text-muted-foreground" />
              <span className={`font-display text-base font-bold ${creditDiff > 0 ? "text-accent" : "text-destructive"}`}>
                {target.credits}
              </span>
            </div>
          </div>

          {/* Gained features */}
          {gained.length > 0 && (
            <div className="space-y-1.5">
              <div className="font-ui text-xs uppercase tracking-wider text-muted-foreground">Vous gagnez</div>
              {gained.map((f) => (
                <div key={f} className="flex items-center gap-2 text-sm font-ui text-accent">
                  <Check className="w-3.5 h-3.5" strokeWidth={2.5} />
                  {f}
                </div>
              ))}
            </div>
          )}

          {/* Lost features */}
          {lost.length > 0 && (
            <div className="space-y-1.5">
              <div className="font-ui text-xs uppercase tracking-wider text-muted-foreground">Vous perdez</div>
              {lost.map((f) => (
                <div key={f} className="flex items-center gap-2 text-sm font-ui text-destructive">
                  <X className="w-3.5 h-3.5" strokeWidth={2.5} />
                  {f}
                </div>
              ))}
            </div>
          )}

          {/* Renewal / effective date notice */}
          <div className="flex items-start gap-2.5 rounded-sm border border-border bg-secondary/30 px-4 py-3">
            <CalendarClock className="w-4 h-4 mt-0.5 text-muted-foreground flex-shrink-0" />
            <p className="font-ui text-xs text-muted-foreground leading-relaxed">
              {isDowngradeToFree
                ? `Votre abonnement actuel reste effectif jusqu'au ${formatDate(nextRenewal)}. Vous ne serez pas débité après cette date.`
                : isUpgrade
                  ? `Votre abonnement sera renouvelé automatiquement le ${renewalDay} de chaque mois.`
                  : `Le changement prendra effet à votre prochaine date de renouvellement, le ${formatDate(nextRenewal)}.`}
            </p>
          </div>
        </div>

        <DialogFooter className="flex-col gap-2 sm:flex-col sm:space-x-0">
          <Button
            onClick={onConfirm}
            className="w-full gap-2 font-ui"
            variant={isUpgrade ? "default" : "outline"}
          >
            <CreditCard className="w-4 h-4" />
            {isUpgrade ? `Payer ${target.price}/mois` : "Confirmer le changement"}
          </Button>
          <Button
            variant="ghost"
            onClick={() => onOpenChange(false)}
            className="w-full font-ui text-sm"
          >
            Annuler
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default PlanCheckoutDialog;
