import React, { useState, useEffect, useCallback } from "react";
import { ArrowLeft, Mail } from "lucide-react";
import { toast } from "@/hooks/use-toast";

interface VerificationScreenProps {
  email: string;
  onBack: () => void;
}

const COOLDOWN_SECONDS = 60;

const VerificationScreen = ({ email, onBack }: VerificationScreenProps) => {
  const [cooldown, setCooldown] = useState(0);

  useEffect(() => {
    if (cooldown <= 0) return;
    const timer = setInterval(() => setCooldown((c) => c - 1), 1000);
    return () => clearInterval(timer);
  }, [cooldown]);

  const handleResend = useCallback(() => {
    if (cooldown > 0) return;
    setCooldown(COOLDOWN_SECONDS);
    toast({ title: "E-mail renvoyé", description: `Un nouveau lien a été envoyé à ${email}.` });
  }, [cooldown, email]);

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <header className="px-6 py-4">
        <button onClick={onBack} className="flex items-center gap-2 font-ui text-sm text-muted-foreground hover:text-foreground transition-colors">
          <ArrowLeft className="w-4 h-4" />
          Retour
        </button>
      </header>
      <main className="flex-1 flex items-center justify-center px-6">
        <div className="max-w-md w-full text-center space-y-6">
          <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mx-auto">
            <Mail className="w-7 h-7 text-primary" />
          </div>
          <h1 className="font-display text-3xl font-bold text-foreground">Vérifiez votre boîte mail</h1>
          <p className="font-body text-muted-foreground leading-relaxed">
            Un e-mail de vérification a été envoyé à <span className="font-semibold text-foreground">{email}</span>.
            Cliquez sur le lien dans l'e-mail pour activer votre compte.
          </p>
          <div className="border-t border-rule pt-6">
            <p className="font-ui text-sm text-muted-foreground">
              Vous n'avez pas reçu l'e-mail ?{" "}
              {cooldown > 0 ? (
                <span className="text-muted-foreground/60 font-medium">
                  Renvoyer dans {cooldown}s
                </span>
              ) : (
                <button className="text-primary hover:underline font-medium" onClick={handleResend}>
                  Renvoyer
                </button>
              )}
            </p>
          </div>
        </div>
      </main>
    </div>
  );
};

export default VerificationScreen;
