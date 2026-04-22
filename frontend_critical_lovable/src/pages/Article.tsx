import { useParams, useNavigate } from "react-router-dom";
import { getArticleById } from "@/data/articles";
import Header from "@/components/Header";
import ArticleNewspaperLayout from "@/components/ArticleNewspaperLayout";
import ArticleClassicLayout from "@/components/ArticleClassicLayout";
import { ArrowLeft } from "lucide-react";
import { useState, useEffect } from "react";

const Article = () => {
  useEffect(() => { window.scrollTo(0, 0); }, []);
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [profileOpen, setProfileOpen] = useState(false);

  const article = id ? getArticleById(id) : undefined;

  if (!article) {
    return (
      <div className="min-h-screen flex flex-col bg-background">
        <Header
          profileOpen={profileOpen}
          onOpenProfile={() => setProfileOpen(true)}
          onCloseProfile={() => setProfileOpen(false)}
        />
        <div className="flex-1 flex items-center justify-center">
          <p className="font-body text-muted-foreground">Article introuvable.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col bg-background">
      <Header
        profileOpen={profileOpen}
        onOpenProfile={() => setProfileOpen(true)}
        onCloseProfile={() => setProfileOpen(false)}
      />

      <div className="w-full px-6">
        <div className="max-w-5xl mx-auto border-t border-rule" />
      </div>

      {/* Back button – sticky */}
      <div className="sticky top-0 z-30 pointer-events-none">
        <div className="bg-background/80 backdrop-blur-sm pointer-events-auto">
          <div className="max-w-5xl mx-auto w-full px-6 py-3">
            <button
              onClick={() => navigate(-1)}
              className="flex items-center gap-2 font-ui text-sm text-muted-foreground hover:text-foreground transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
              Retour
            </button>
          </div>
        </div>
        <div className="h-8 bg-gradient-to-b from-background/50 to-transparent" />
      </div>

      <main className="flex-1">
        {article.format === "long" ? (
          <ArticleNewspaperLayout article={article} />
        ) : (
          <ArticleClassicLayout article={article} />
        )}
      </main>
    </div>
  );
};

export default Article;
