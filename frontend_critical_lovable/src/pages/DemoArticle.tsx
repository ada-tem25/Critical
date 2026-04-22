import { useParams, useNavigate, useSearchParams } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import { demoArticles } from "@/data/demoArticles";
import ArticleNewspaperLayout from "@/components/ArticleNewspaperLayout";
import ArticleClassicLayout from "@/components/ArticleClassicLayout";

const DemoArticle = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const lang = (searchParams.get("lang") as "fr" | "en") || "fr";

  const bilingual = demoArticles.find((a) => a.fr.id === id || a.en.id === id);
  const article = bilingual?.[lang];

  if (!article) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <p className="font-body text-muted-foreground">Article not found.</p>
      </div>
    );
  }

  const LayoutComponent = article.format === "long"
    ? ArticleNewspaperLayout
    : ArticleClassicLayout;

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Back button top-right */}
      <div className="w-full px-6 pt-4 flex justify-end">
        <button
          onClick={() => navigate("/demo")}
          className="flex items-center gap-2 font-ui text-sm text-muted-foreground hover:text-foreground transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          {lang === "fr" ? "Retour" : "Back"}
        </button>
      </div>

      <LayoutComponent article={article} />
    </div>
  );
};

export default DemoArticle;
