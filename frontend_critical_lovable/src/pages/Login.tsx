import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowLeft, Mail, Eye, EyeOff } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { toast } from "@/hooks/use-toast";
import VerificationScreen from "@/components/login/VerificationScreen";
import ForgotPasswordFlow from "@/components/login/ForgotPasswordFlow";
import LoadingLines from "@/components/ui/loading-lines";

type Screen = "choice" | "email" | "verification" | "forgot";

const Login = () => {
  const navigate = useNavigate();
  const [screen, setScreen] = useState<Screen>("choice");
  const [isLogin, setIsLogin] = useState(true);
  const [showPassword, setShowPassword] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const PASSWORD_RULES = [
    { test: (p: string) => p.length >= 8, label: "Au moins 8 caractères" },
    { test: (p: string) => /[A-Z]/.test(p), label: "Une lettre majuscule" },
    { test: (p: string) => /[a-z]/.test(p), label: "Une lettre minuscule" },
    { test: (p: string) => /[0-9]/.test(p), label: "Un chiffre" },
    { test: (p: string) => /[^A-Za-z0-9]/.test(p), label: "Un caractère spécial" },
  ];

  const passwordErrors = PASSWORD_RULES.filter((r) => !r.test(password));
  const isPasswordValid = password.length > 0 && passwordErrors.length === 0;

  const isValidEmail = (e: string) => /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(e);

  const handleEmailSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) return;
    if (!isValidEmail(email)) {
      toast({ title: "E-mail invalide", description: "Vérifiez le format de votre adresse e-mail.", variant: "destructive" });
      return;
    }
    if (!isLogin && !isPasswordValid) {
      toast({ title: "Mot de passe invalide", description: "Respectez tous les critères.", variant: "destructive" });
      return;
    }
    if (!isLogin && password !== confirmPassword) {
      toast({ title: "Les mots de passe ne correspondent pas", variant: "destructive" });
      return;
    }

    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      if (isLogin) {
        toast({ title: "Connexion réussie", description: "Bienvenue sur Critical." });
        navigate("/");
      } else {
        setScreen("verification");
      }
    }, 1500);
  };

  const handleSocialLogin = (provider: string) => {
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      toast({ title: `Connexion via ${provider}`, description: "Bon retour sur Critical !" });
      navigate("/");
    }, 2000);
  };

  const handleForgotPassword = () => {
    if (!email || !isValidEmail(email)) {
      toast({ title: "E-mail invalide", description: "Renseignez une adresse e-mail valide avant de réinitialiser.", variant: "destructive" });
      return;
    }
    toast({ title: "Code envoyé", description: `Un code de vérification a été envoyé à ${email}.` });
    setScreen("forgot");
  };

  if (screen === "verification") {
    return <VerificationScreen email={email} onBack={() => { setScreen("choice"); }} />;
  }

  if (screen === "forgot") {
    return <ForgotPasswordFlow email={email} onBack={() => setScreen("email")} />;
  }

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {loading && <LoadingLines />}
      <header className="px-6 py-4">
        <button
          onClick={() => screen === "email" ? setScreen("choice") : navigate("/")}
          className="flex items-center gap-2 font-ui text-sm text-muted-foreground hover:text-foreground transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Retour
        </button>
      </header>

      <main className="flex-1 flex items-center justify-center px-6 pb-12">
        <div className="max-w-sm w-full space-y-8">
          {/* Logo & heading */}
          <div className="text-center space-y-3">
            <div className="w-12 h-12 rounded-sm bg-primary flex items-center justify-center mx-auto">
              <span className="text-primary-foreground font-display font-bold text-xl">C</span>
            </div>
            <h1 className="font-display text-3xl font-bold text-foreground">
              {screen === "choice" ? "Bienvenue sur Critical" : (isLogin ? "Se connecter" : "Créer un compte")}
            </h1>
            <p className="font-body text-sm text-muted-foreground">
              {screen === "choice"
                ? "L'esprit critique, augmenté."
                : (isLogin ? "Entrez vos identifiants pour continuer." : "Rejoignez la communauté Critical.")}
            </p>
          </div>

          {screen === "choice" ? (
            <div className="space-y-3">
              {/* Google */}
              <button
                onClick={() => handleSocialLogin("Google")}
                className="w-full flex items-center justify-center gap-3 px-4 py-3 rounded-md border border-border bg-card hover:bg-secondary transition-colors font-ui text-sm font-medium text-foreground"
              >
                <svg className="w-5 h-5" viewBox="0 0 533.5 544.3" xmlns="http://www.w3.org/2000/svg">
                  <path d="M533.5 278.4c0-17.4-1.6-34.1-4.6-50.2H272v95h146.9c-6.3 33.9-25 62.5-53.2 81.8v68.1h85.8c50.2-46.3 82-114.6 82-194.7z" fill="#4285F4" />
                  <path d="M272 544.3c71.6 0 131.7-23.7 175.7-64.2l-85.8-68.1c-23.8 16-54.1 25.4-89.9 25.4-69.1 0-127.6-46.6-148.4-109.3h-89.6v68.9C77.7 480.5 168.5 544.3 272 544.3z" fill="#34A853" />
                  <path d="M123.6 328.1c-10.8-32.1-10.8-66.9 0-99l-89.6-68.9c-39.1 77.6-39.1 168.3 0 245.9l89.6-68z" fill="#FBBC05" />
                  <path d="M272 107.7c37.4-.6 73.5 13.2 101.1 38.7l75.4-75.4C403.4 24.5 341.4 0 272 0 168.5 0 77.7 63.8 34 159.2l89.6 68.9C144.4 154.3 202.9 107.7 272 107.7z" fill="#EA4335" />
                </svg>
                Continuer avec Google
              </button>

              {/* Apple */}
              <button
                onClick={() => handleSocialLogin("Apple")}
                className="w-full flex items-center justify-center gap-3 px-4 py-3 rounded-md border border-border bg-card hover:bg-secondary transition-colors font-ui text-sm font-medium text-foreground"
              >
                <svg className="w-5 h-5" viewBox="0 0 814 1000" xmlns="http://www.w3.org/2000/svg">
                  <path d="M788.1 340.9c-5.8 4.5-108.2 62.2-108.2 190.5 0 148.4 130.3 200.9 134.2 202.2-.6 3.2-20.7 71.9-68.7 141.9-42.8 61.6-87.5 123.1-155.5 123.1s-85.5-39.5-164-39.5c-76.5 0-103.7 40.8-165.9 40.8s-105.6-57.8-155.5-127.4c-58.8-82-106.3-209.6-106.3-330.1 0-194.3 126.4-297.3 250.8-297.3 66.1 0 121.2 43.4 162.7 43.4 39.5 0 101.1-46 176.3-46 28.5 0 130.9 2.6 198.3 99.2zm-234-181.5c31.1-36.9 53.1-88.1 53.1-139.3 0-7.1-.6-14.3-1.9-20.1-50.6 1.9-110.8 33.7-147.1 75.8-28.5 32.4-55.1 83.6-55.1 135.5 0 7.8.7 15.6 1.3 18.2 2.6.4 6.5 1.3 10.4 1.3 45.3 0 103.4-30.4 139.3-71.4z" fill="currentColor" />
                </svg>
                Continuer avec Apple
              </button>

              {/* Divider */}
              <div className="relative py-2">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-rule" />
                </div>
                <div className="relative flex justify-center">
                  <span className="bg-background px-3 font-ui text-xs text-muted-foreground uppercase tracking-wider">ou</span>
                </div>
              </div>

              {/* Email */}
              <button
                onClick={() => setScreen("email")}
                className="w-full flex items-center justify-center gap-3 px-4 py-3 rounded-md bg-primary text-primary-foreground hover:bg-primary/90 transition-colors font-ui text-sm font-medium"
              >
                <Mail className="w-4 h-4" />
                Continuer avec un e-mail
              </button>
            </div>
          ) : (
            <>
              <form onSubmit={handleEmailSubmit} className="space-y-4">
                <div className="space-y-2">
                  <label className="font-ui text-sm font-medium text-foreground">E-mail</label>
                  <Input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="vous@exemple.com"
                    className="font-ui"
                  />
                </div>
                <div className="space-y-2">
                  <label className="font-ui text-sm font-medium text-foreground">Mot de passe</label>
                  <div className="relative">
                    <Input
                      type={showPassword ? "text" : "password"}
                      required
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
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
                {!isLogin && password.length > 0 && passwordErrors.length > 0 && (
                  <ul className="space-y-1 text-sm font-ui">
                    {PASSWORD_RULES.map((rule) => (
                      <li key={rule.label} className={rule.test(password) ? "text-green-600" : "text-destructive"}>
                        {rule.test(password) ? "✓" : "✗"} {rule.label}
                      </li>
                    ))}
                  </ul>
                )}
                {!isLogin && (
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
                )}
                <Button type="submit" className="w-full font-ui" disabled={loading || (!isLogin && !isPasswordValid)}>
                  {loading ? "Chargement…" : (isLogin ? "Se connecter" : "Créer mon compte")}
                </Button>
              </form>

              {isLogin && (
                <div className="text-center">
                  <button className="font-ui text-sm text-primary hover:underline" onClick={handleForgotPassword}>
                    Mot de passe oublié ?
                  </button>
                </div>
              )}
            </>
          )}

          {/* Toggle login/signup */}
          <div className="text-center border-t border-rule pt-6">
            <p className="font-ui text-sm text-muted-foreground">
              {isLogin ? "Pas encore de compte ?" : "Déjà un compte ?"}{" "}
              <button
                className="text-primary hover:underline font-medium"
                onClick={() => { setIsLogin(!isLogin); setScreen(isLogin ? "email" : "choice"); }}
              >
                {isLogin ? "S'inscrire" : "Se connecter"}
              </button>
            </p>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Login;
