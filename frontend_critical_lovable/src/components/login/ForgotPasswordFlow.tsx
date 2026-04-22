import React, { useState, useEffect, useRef } from "react";
import { ArrowLeft, Eye, EyeOff, CheckCircle } from "lucide-react";
import { InputOTP, InputOTPGroup, InputOTPSlot } from "@/components/ui/input-otp";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { toast } from "@/hooks/use-toast";

const CORRECT_CODE = "111111";
const COOLDOWN_SECONDS = 60;

const PASSWORD_RULES = [
  { test: (p: string) => p.length >= 8, label: "Au moins 8 caractères" },
  { test: (p: string) => /[A-Z]/.test(p), label: "Une lettre majuscule" },
  { test: (p: string) => /[a-z]/.test(p), label: "Une lettre minuscule" },
  { test: (p: string) => /[0-9]/.test(p), label: "Un chiffre" },
  { test: (p: string) => /[^A-Za-z0-9]/.test(p), label: "Un caractère spécial" },
];

interface ForgotPasswordFlowProps {
  email: string;
  onBack: () => void;
}

type Step = "code" | "reset" | "done";

const ForgotPasswordFlow = ({ email, onBack }: ForgotPasswordFlowProps) => {
  const [step, setStep] = useState<Step>("code");
  const [code, setCode] = useState("");
  const [codeError, setCodeError] = useState(false);
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [cooldown, setCooldown] = useState(COOLDOWN_SECONDS);

  useEffect(() => {
    if (cooldown <= 0) return;
    const timer = setInterval(() => setCooldown((c) => c - 1), 1000);
    return () => clearInterval(timer);
  }, [cooldown]);

  useEffect(() => {
    if (code.length === 6 && step === "code") {
      if (code === CORRECT_CODE) {
        setCodeError(false);
        setStep("reset");
      } else {
        setCodeError(true);
        toast({ title: "Code incorrect", description: "Veuillez réessayer.", variant: "destructive" });
      }
    }
  }, [code, step]);

  const handleResendCode = () => {
    if (cooldown > 0) return;
    setCooldown(COOLDOWN_SECONDS);
    toast({ title: "Code renvoyé", description: `Un nouveau code a été envoyé à ${email}.` });
  };

  const handleVerifyCode = () => {
    if (code === CORRECT_CODE) {
      setCodeError(false);
      setStep("reset");
    } else {
      setCodeError(true);
      toast({ title: "Code incorrect", description: "Veuillez réessayer.", variant: "destructive" });
    }
  };

  const passwordErrors = PASSWORD_RULES.filter((r) => !r.test(newPassword));
  const isPasswordValid = newPassword.length > 0 && passwordErrors.length === 0;

  const handleResetPassword = (e: React.FormEvent) => {
    e.preventDefault();
    if (!isPasswordValid) {
      toast({ title: "Mot de passe invalide", description: "Respectez tous les critères.", variant: "destructive" });
      return;
    }
    if (newPassword !== confirmPassword) {
      toast({ title: "Les mots de passe ne correspondent pas", variant: "destructive" });
      return;
    }
    setStep("done");
    toast({ title: "Mot de passe réinitialisé", description: "Vous pouvez maintenant vous connecter." });
  };

  if (step === "done") {
    return (
      <div className="min-h-screen bg-background flex flex-col">
        <header className="px-6 py-4" />
        <main className="flex-1 flex items-center justify-center px-6">
          <div className="max-w-sm w-full text-center space-y-6">
            <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mx-auto">
              <CheckCircle className="w-7 h-7 text-primary" />
            </div>
            <h1 className="font-display text-3xl font-bold text-foreground">Mot de passe modifié</h1>
            <p className="font-body text-muted-foreground leading-relaxed">
              Votre mot de passe a été réinitialisé avec succès.
            </p>
            <Button className="w-full font-ui" onClick={onBack}>
              Se connecter
            </Button>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <header className="px-6 py-4">
        <button
          onClick={step === "code" ? onBack : () => setStep("code")}
          className="flex items-center gap-2 font-ui text-sm text-muted-foreground hover:text-foreground transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Retour
        </button>
      </header>

      <main className="flex-1 flex items-center justify-center px-6 pb-12">
        <div className="max-w-sm w-full space-y-8">
          {/* Logo */}
          <div className="text-center space-y-3">
            <div className="w-12 h-12 rounded-sm bg-primary flex items-center justify-center mx-auto">
              <span className="text-primary-foreground font-display font-bold text-xl">C</span>
            </div>
            <h1 className="font-display text-3xl font-bold text-foreground">
              {step === "code" ? "Entrez le code" : "Nouveau mot de passe"}
            </h1>
            <p className="font-body text-sm text-muted-foreground">
              {step === "code"
                ? <>Un code à 6 chiffres a été envoyé à <span className="font-semibold text-foreground">{email}</span>.</>
                : "Choisissez un nouveau mot de passe pour votre compte."}
            </p>
          </div>

          {step === "code" ? (
            <div className="space-y-6">
              <div className="flex justify-center">
                <InputOTP maxLength={6} value={code} onChange={setCode}>
                  <InputOTPGroup>
                    <InputOTPSlot index={0} />
                    <InputOTPSlot index={1} />
                    <InputOTPSlot index={2} />
                    <InputOTPSlot index={3} />
                    <InputOTPSlot index={4} />
                    <InputOTPSlot index={5} />
                  </InputOTPGroup>
                </InputOTP>
              </div>

              {codeError && (
                <p className="text-center font-ui text-sm text-destructive">Code incorrect. Réessayez.</p>
              )}

              <Button className="w-full font-ui" onClick={handleVerifyCode} disabled={code.length < 6}>
                Vérifier
              </Button>

              <div className="text-center">
                <p className="font-ui text-sm text-muted-foreground">
                  Vous n'avez pas reçu le code ?{" "}
                  {cooldown > 0 ? (
                    <span className="text-muted-foreground/60 font-medium">Renvoyer dans {cooldown}s</span>
                  ) : (
                    <button className="text-primary hover:underline font-medium" onClick={handleResendCode}>
                      Renvoyer
                    </button>
                  )}
                </p>
              </div>
            </div>
          ) : (
            <form onSubmit={handleResetPassword} className="space-y-4">
              <div className="space-y-2">
                <label className="font-ui text-sm font-medium text-foreground">Nouveau mot de passe</label>
                <div className="relative">
                  <Input
                    type={showPassword ? "text" : "password"}
                    required
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    placeholder="••••••••"
                    className="font-ui pr-10"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>
              {newPassword.length > 0 && passwordErrors.length > 0 && (
                <ul className="space-y-1 text-sm font-ui">
                  {PASSWORD_RULES.map((rule) => (
                    <li key={rule.label} className={rule.test(newPassword) ? "text-green-600" : "text-destructive"}>
                      {rule.test(newPassword) ? "✓" : "✗"} {rule.label}
                    </li>
                  ))}
                </ul>
              )}
              <div className="space-y-2">
                <label className="font-ui text-sm font-medium text-foreground">Confirmer le mot de passe</label>
                <Input
                  type={showPassword ? "text" : "password"}
                  required
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="••••••••"
                  className="font-ui"
                />
              </div>
              <Button type="submit" className="w-full font-ui" disabled={!isPasswordValid}>
                Réinitialiser le mot de passe
              </Button>
            </form>
          )}
        </div>
      </main>
    </div>
  );
};

export default ForgotPasswordFlow;
