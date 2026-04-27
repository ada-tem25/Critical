import type { ArticleData } from "@/data/articles";

// [DEMO ONLY] Eagerly load all analyzed articles from the analyzed/ directory.
// To add a new demo article: run the pipeline — it writes to analyzed/ automatically.
// In the real app, articles will be fetched from the API instead.
const modules = import.meta.glob<ArticleData>("./analyzed/*.json", {
  eager: true,
  import: "default",
});

export const demoArticles: ArticleData[] = Object.values(modules);
