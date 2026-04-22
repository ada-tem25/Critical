import type { ArticleData } from "@/data/articles";
import { splitParagraphs, getVerdictColor } from "@/data/articles";
import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Cell } from "recharts";
import SourceInlineRef from "@/components/SourceInlineRef";
import { getBiasLabel } from "@/lib/bias";
import ArticleFeedback from "@/components/ArticleFeedback";
import ArticlePinButton from "@/components/ArticlePinButton";
import { ExternalLink } from "lucide-react";

const CHART_COLORS = ["hsl(145, 50%, 36%)", "hsl(0, 55%, 48%)", "hsl(38, 60%, 50%)"];

const ArticleNewspaperLayout = ({ article }: { article: ArticleData }) => {
  const paragraphs = splitParagraphs(article.article);

  // Split content for 2 columns
  const mid = Math.ceil(paragraphs.length / 2);
  const colLeft = paragraphs.slice(0, mid);
  const colRight = paragraphs.slice(mid);

  return (
    <article className="max-w-5xl mx-auto px-6 py-10 animate-fade-up">
      <div className="text-left mb-8">
        <h1 className="font-display text-3xl md:text-4xl lg:text-5xl font-bold text-foreground leading-tight mb-3">
          {article.title}
        </h1>
        {article.subtitle && (
          <p className="font-body text-lg text-muted-foreground italic">
            {article.subtitle}
          </p>
        )}
        <div className="flex items-center gap-3 mt-3 font-body text-sm text-muted-foreground">
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
          <ArticlePinButton articleId={article.id} />
        </div>
      </div>

      <div className="border-t-2 border-b border-foreground mb-8" />

      {/* Two-column layout */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-6">
        {/* Left column */}
        <div className="space-y-4">
          {colLeft.map((p, i) => (
            <p key={i} className="font-body text-[15px] leading-relaxed text-foreground text-justify">
              <SourceInlineRef text={p} sources={article.sources} rhetoricSide="left" />
            </p>
          ))}

          {/* Embedded quote */}
          {article.quote && (
            <blockquote className="my-6 border-l-3 border-accent pl-4 py-2">
              <p className="font-display text-lg italic text-foreground leading-snug mb-2">
                « {article.quote.text} »
              </p>
              <cite className="font-ui text-sm text-muted-foreground not-italic">
                — {article.quote.author}
              </cite>
            </blockquote>
          )}
        </div>

        {/* Right column */}
        <div className="space-y-4">
          {colRight.map((p, i) => (
            <p key={i} className="font-body text-[15px] leading-relaxed text-foreground text-justify">
              <SourceInlineRef text={p} sources={article.sources} />
            </p>
          ))}

          {/* Embedded chart */}
          {article.chartData && (
            <div className="my-6 p-4 bg-card border border-border rounded-sm">
              <h4 className="font-ui text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">
                Répartition des positions au Parlement
              </h4>
              <ResponsiveContainer width="100%" height={160}>
                <BarChart data={article.chartData} layout="vertical" margin={{ left: 10, right: 10 }}>
                  <XAxis type="number" hide />
                  <YAxis
                    dataKey="label"
                    type="category"
                    axisLine={false}
                    tickLine={false}
                    tick={{ fontSize: 12, fontFamily: "Inter", fill: "hsl(25, 12%, 50%)" }}
                    width={55}
                  />
                  <Bar dataKey="value" radius={[0, 3, 3, 0]} barSize={18}>
                    {article.chartData.map((_, idx) => (
                      <Cell key={idx} fill={CHART_COLORS[idx % CHART_COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
              <p className="font-ui text-[11px] text-muted-foreground mt-2 italic">
                En pourcentage des eurodéputés sondés
              </p>
            </div>
          )}
        </div>
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

export default ArticleNewspaperLayout;
