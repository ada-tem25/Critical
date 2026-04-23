import { ArticleData } from "@/data/articles";
import { splitParagraphs, getVerdictColor } from "@/data/articles";
import SourceInlineRef from "@/components/SourceInlineRef";
import { getBiasLabel } from "@/lib/bias";
import ArticleFeedback from "@/components/ArticleFeedback";
import ArticlePinButton from "@/components/ArticlePinButton";
import { ExternalLink } from "lucide-react";

const QUOTE_MARKER = /^~\d+$/;

const ArticleClassicLayout = ({ article }: { article: ArticleData }) => {
  const paragraphs = splitParagraphs(article.article);

  // If no ~N marker exists but a quote is present, fall back to ~40% position
  const hasQuoteMarker = paragraphs.some((p) => QUOTE_MARKER.test(p.trim()));
  const fallbackQuoteAfter = !hasQuoteMarker && article.quote
    ? Math.floor(paragraphs.length * 0.4)
    : -1;

  const renderQuote = () => article.quote ? (
    <blockquote className="my-8 py-6 border-t border-b border-rule text-center">
      <p className="font-display text-xl md:text-2xl italic text-foreground leading-snug mb-3 px-4">
        « {article.quote.text} »
      </p>
      <cite className="font-ui text-sm text-muted-foreground not-italic">
        — {article.quote.author}
      </cite>
    </blockquote>
  ) : null;

  return (
    <article className="max-w-2xl mx-auto px-6 py-10 animate-fade-up">
      {/* Big centered title */}
      <div className="text-center mb-8">
        <h1 className="font-display text-3xl md:text-4xl lg:text-5xl font-bold text-foreground leading-tight mb-4">
          {article.title}
        </h1>
        {article.subtitle && (
          <p className="font-body text-lg text-muted-foreground mb-4">
            {article.subtitle}
          </p>
        )}
        <div className="flex items-center gap-3 font-body text-sm text-muted-foreground">
          <div className="flex items-center justify-center gap-3 flex-1">
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
            <span className="text-rule">·</span>
            <span className={`font-ui text-xs font-bold tracking-widest uppercase ${getVerdictColor(article.verdict)}`}>
              {article.verdict}
            </span>
          </div>
          <ArticlePinButton articleId={article.id} />
        </div>
      </div>

      <div className="w-16 mx-auto border-t border-rule mb-8" />

      {/* Content paragraphs */}
      <div className="space-y-5">
        {paragraphs.map((p, i) => {
          // ~N marker → render quote here
          if (QUOTE_MARKER.test(p.trim())) {
            return <div key={i}>{renderQuote()}</div>;
          }

          return (
            <div key={i}>
              <p className="font-body text-[16px] leading-[1.8] text-foreground">
                <SourceInlineRef text={p} sources={article.sources} />
              </p>

              {/* Fallback quote position for legacy articles without ~N */}
              {i === fallbackQuoteAfter && renderQuote()}
            </div>
          );
        })}
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

export default ArticleClassicLayout;
