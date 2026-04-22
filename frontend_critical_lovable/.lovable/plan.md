

## Plan: Page Demo standalone avec switch FR/EN

### Vue d'ensemble
Créer une page `/demo` autonome (sans header app, sans bouton retour) servant de showcase statique. Accessible temporairement via un bouton dans Settings. La page inclut un switch langue FR/EN, 3 exemples d'articles cliquables, et les sections "Notre approche" + FAQ en bas.

### Fichiers à créer/modifier

**1. `src/pages/Demo.tsx` (nouveau)** — Page principale :
- **Header minimal** : Logo "Critical" à gauche, switch FR/EN à droite (toggle simple, pas le composant global LanguageContext)
- **État local** `lang: "fr" | "en"` pour piloter tous les textes
- **Section hero** : Titre de l'app + petit texte/infographie expliquant le flux (Sources multi-modales → Critical → Fact-checking & analyse). Textes bilingues via objets `{ fr: "...", en: "..." }`
- **Section 3 exemples** : Cartes plus grandes que les ArchiveCards, avec esthétique paper/ink, surélevées (`shadow-lg`), animation hover (`hover:-translate-y-2 hover:shadow-xl` + légère rotation), chacune cliquable vers `/demo/article/:id`. Données placeholder avec champs structurés identiques à `ArticleData` (titre, subtitle, source, sourceUrl, date, status, layout, content, sources, etc.) pour remplacement facile par JSON
- **Section "Notre approche"** : Reprise du bloc existant, textes bilingues placeholder
- **Section FAQ** : Accordéon avec les 10 questions, textes bilingues placeholder

**2. `src/data/demoArticles.ts` (nouveau)** — Données des 3 articles demo :
- Même interface `ArticleData` que `src/data/articles.ts`
- Champs bilingues wrappés : `{ fr: ArticleData, en: ArticleData }` pour chaque article
- 3 articles placeholder avec tous les champs remplis (titre, subtitle, source, sourceUrl, date, status, summary, layout, content, sources)

**3. `src/pages/DemoArticle.tsx` (nouveau)** — Page article demo :
- Pas de header app global
- Bouton retour en haut à droite → retour vers `/demo`
- Récupère l'article depuis `demoArticles` par id
- Réutilise les layouts existants (`ArticleNewspaperLayout`, `ArticleClassicLayout`, `ArticleDiscourseLayout`) selon le champ `layout`
- Passe la langue via query param ou state

**4. `src/App.tsx`** — Ajout des routes :
- `<Route path="/demo" element={<Demo />} />`
- `<Route path="/demo/article/:id" element={<DemoArticle />} />`

**5. `src/pages/Settings.tsx`** — Ajout bouton "Demo" :
- Sous le bloc "Supprimer mon compte", ajouter un bouton simple avec icône (`Play` ou `Monitor`) qui navigue vers `/demo`

### Détails techniques
- Le switch FR/EN sera un état local dans Demo.tsx, passé via props ou un petit context local, indépendant du `LanguageContext` global de l'app
- Les textes bilingues seront des objets simples `{ fr: string, en: string }` indexés par `lang`
- Les cartes d'exemples utiliseront le même style paper/noise que le reste de l'app
- La structure des données demo sera identique à `ArticleData` pour que le remplacement par du vrai contenu soit trivial

