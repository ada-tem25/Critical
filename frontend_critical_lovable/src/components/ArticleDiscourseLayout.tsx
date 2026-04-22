import type { ArticleData } from "@/data/articles";
import { splitParagraphs } from "@/data/articles";
import SourceInlineRef from "@/components/SourceInlineRef";
import { getBiasLabel } from "@/lib/bias";
import ArticleFeedback from "@/components/ArticleFeedback";
import ArticlePinButton from "@/components/ArticlePinButton";
import { ExternalLink } from "lucide-react";

/**
 * Discourse layout is not yet implemented in the backend.
 * For now this renders as a simple paragraph layout (same as classic).
 * When discourse is added to the backend, this component will be updated.
 */
const ArticleDiscourseLayout = ({ article }: { article: ArticleData }) => {
  const paragraphs = splitParagraphs(article.article);

  return (
    <article className="max-w-2xl mx-auto px-6 py-10 animate-fade-up">
      {/* Header */}
      <div className="mb-8">
        <h1 className="font-display text-2xl md:text-3xl lg:text-4xl font-bold text-foreground leading-tight mb-3">
          {article.title}
        </h1>
        {article.subtitle && (
          <p className="font-body text-base text-muted-foreground mb-3">
            {article.subtitle}
          </p>
        )}
        <div className="flex items-center gap-3 font-body text-sm text-muted-foreground">
          {article.source_url ? (
            <a href={article.source_url} target="_blank" rel="noopener noreferrer" className="font-semibold hover:underline inline-flex items-center gap-1">
              {article.author}
              <ExternalLink className="w-3 h-3" />
            </a>
          ) : (
            <span className="font-semibold">{article.author}</span>
          )}
          <span className="text-rule">·</span>
          <span>{article.date}</span>
          <ArticlePinButton articleId={article.id} />
        </div>
      </div>

      <div className="border-t-2 border-foreground mb-8" />

      {/* Summary */}
      <p className="font-body text-[15px] leading-relaxed text-foreground mb-10">
        {article.summary}
      </p>

      {/* Content paragraphs */}
      <div className="space-y-5">
        {paragraphs.map((p, i) => (
          <p key={i} className="font-body text-[15px] leading-relaxed text-foreground">
            <SourceInlineRef text={p} sources={article.sources} />
          </p>
        ))}
      </div>

      {/* Sources */}
      <div className="mt-12 pt-6 border-t border-rule">
        <h3 className="font-ui text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">
            Sources
          </h3>
        <ol className="space-y-1.5">
          {article.sources.map((s) => {
            const biasLabel = getBiasLabel(s.bias);
            return (
              <li key={s.id} className="font-body text-xs text-muted-foreground leading-relaxed">
                <span className="font-ui font-semibold text-foreground mr-1">{s.id}.</span>
                {s.url ? (
                  <a href={s.url} target="_blank" rel="noopener noreferrer" className="hover:underline">
                    {s.title}
                  </a>
                ) : s.title}
                {biasLabel && <span className="font-bold ml-1">({biasLabel})</span>}
              </li>
            );
          })}
        </ol>
      </div>

      <ArticleFeedback />
    </article>
  );
};

export default ArticleDiscourseLayout;
