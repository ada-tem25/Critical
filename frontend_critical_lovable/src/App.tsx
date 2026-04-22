import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Index from "./pages/Index";
import Article from "./pages/Article";
import Plans from "./pages/Plans";
import LiveFactCheck from "./pages/LiveFactCheck";
import Login from "./pages/Login";
import Settings from "./pages/Settings";
import Approach from "./pages/Approach";
import Demo from "./pages/Demo";
import DemoArticle from "./pages/DemoArticle";
import NotFound from "./pages/NotFound";
import { PlanProvider } from "./contexts/PlanContext";
import { RhetoricProvider } from "./contexts/RhetoricContext";
import { LanguageProvider } from "./contexts/LanguageContext";
import { LocationProvider } from "./contexts/LocationContext";
import { ConsumptionProvider } from "./contexts/ConsumptionContext";
import { PinnedArticlesProvider } from "./contexts/PinnedArticlesContext";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <PlanProvider>
    <LanguageProvider>
    <LocationProvider>
    <ConsumptionProvider>
    <PinnedArticlesProvider>
    <RhetoricProvider>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Index />} />
          <Route path="/article/:id" element={<Article />} />
          <Route path="/plans" element={<Plans />} />
          <Route path="/live" element={<LiveFactCheck />} />
          <Route path="/login" element={<Login />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/approach" element={<Approach />} />
          <Route path="/demo" element={<Demo />} />
          <Route path="/demo/article/:id" element={<DemoArticle />} />
          {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
    </RhetoricProvider>
    </PinnedArticlesProvider>
    </ConsumptionProvider>
    </LocationProvider>
    </LanguageProvider>
    </PlanProvider>
  </QueryClientProvider>
);

export default App;
