// ── Types matching backend PipelineResult ──────────────────────

export interface ArticleSource {
  id: number;
  url: string;
  title: string;
  date: string;
  bias: string;
}

export interface Rhetoric {
  type: string;
  passage: string;
  explanation: string;
}

export interface ArticleData {
  id: string;
  // Original input
  text: string;
  source_type: string;
  source_url: string;
  author: string;
  date: string;
  rhetorics: Rhetoric[];
  // Writer output
  title: string;
  subtitle?: string;
  verdict: string;
  summary: string;
  article: string;
  format: string; // "short" | "long"
  language?: string; // "French" | "English" — set by the pipeline
  sources: ArticleSource[];
  quote?: { text: string; author: string; date?: string };
  // Frontend-only display hints (optional, not from backend)
  featured?: boolean;
  chartData?: { label: string; value: number }[];
}

// ── Verdict helpers ────────────────────────────────────────────

export function getVerdictColor(verdict: string): string {
  const v = verdict.toUpperCase();
  if (v === "VRAI") return "text-emerald-800";
  if (v === "FAUX") return "text-red-800";
  return "text-orange-700";
}

export function getVerdictBgColor(verdict: string): string {
  const v = verdict.toUpperCase();
  if (v === "VRAI") return "text-emerald-800 bg-emerald-100";
  if (v === "FAUX") return "text-red-800 bg-red-100";
  return "text-orange-700 bg-orange-100";
}

// ── Article content helpers ────────────────────────────────────

/** Split backend article string into paragraphs for rendering */
export function splitParagraphs(article: string): string[] {
  return article.split(/\n\n+/).filter(Boolean);
}

// ── Mock data ──────────────────────────────────────────────────

export const articles: ArticleData[] = [
  {
    id: "ue-smartphones",
    title: "L'UE prévoit d'interdire les smartphones avant 16 ans",
    subtitle: "Un projet de directive controversé qui divise les parlementaires européens",
    author: "Le Monde",
    source_url: "https://www.lemonde.fr",
    source_type: "article",
    text: "",
    date: "3 fév. 2026",
    verdict: "INCERTAIN",
    format: "long",
    rhetorics: [],
    summary:
      "Un projet de directive européenne visant à interdire les smartphones aux moins de 16 ans circule au Parlement, mais aucune décision officielle n'a été prise. Le texte divise les États membres et suscite de vives réactions des lobbies technologiques.",
    article: [
      "Depuis plusieurs mois, un projet de directive européenne visant à interdire l'accès aux smartphones pour les mineurs de moins de 16 ans fait l'objet de vifs débats au sein des institutions de l'Union européenne. Le texte, initialement porté par un groupe de parlementaires issus de plusieurs familles politiques, a été présenté comme une mesure de protection de la santé mentale des jeunes¹.",
      "Selon les documents consultés par notre rédaction, la proposition prévoit une interdiction progressive : dès 2027, les fabricants de smartphones seraient tenus d'intégrer des mécanismes de vérification d'âge renforcés. Les opérateurs téléphoniques devraient quant à eux refuser l'activation de lignes mobiles pour les mineurs de moins de 16 ans sans autorisation parentale explicite².",
      "Cependant, plusieurs sources proches des négociations indiquent que le texte est loin de faire l'unanimité. Les pays nordiques, traditionnellement favorables aux libertés numériques, ont exprimé de fortes réserves. La Suède et le Danemark ont notamment fait valoir que l'éducation au numérique serait plus efficace qu'une interdiction pure et simple³. Le rapporteur du texte a d'ailleurs présenté le débat comme un [[Faux dilemme]] : « soit on interdit, soit on sacrifie nos enfants ».",
      "Les lobbies technologiques ont également réagi avec force. Dans une lettre ouverte publiée la semaine dernière, un consortium regroupant les principaux fabricants de smartphones a qualifié la mesure de « disproportionnée et techniquement irréaliste ». Ils soulignent que les systèmes de vérification d'âge existants sont facilement contournables⁴.",
      "Du côté des associations de parents d'élèves, les avis sont partagés. Si certaines fédérations saluent une « initiative courageuse » en recourant à un [[Appel à l'émotion]] centré sur la protection des enfants, d'autres craignent qu'une interdiction totale ne pousse les adolescents vers des pratiques encore plus risquées, comme l'utilisation d'appareils non sécurisés ou le recours à des réseaux alternatifs⁵.",
      "Le Parlement européen devrait se prononcer sur une version amendée du texte d'ici la fin du premier semestre 2026. En attendant, plusieurs États membres ont annoncé vouloir légiférer à l'échelle nationale, créant un patchwork réglementaire que les observateurs jugent problématique pour le marché unique numérique⁶.",
    ].join("\n\n"),
    quote: {
      text: "Cette directive, si elle est adoptée, constituerait un précédent mondial en matière de régulation de l'accès des mineurs aux technologies mobiles.",
      author: "Maria Johansson, eurodéputée suédoise",
    },
    chartData: [
      { label: "Pour", value: 42 },
      { label: "Contre", value: 35 },
      { label: "Indécis", value: 23 },
    ],
    sources: [
      { id: 1, title: "Commission européenne, rapport préliminaire sur la santé numérique des mineurs, janvier 2026", url: "https://ec.europa.eu/health/digital-minors-2026", date: "", bias: "" },
      { id: 2, title: "Proposition de directive COM(2026) 47, article 3, paragraphe 2", url: "https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=COM:2026:47", date: "", bias: "" },
      { id: 3, title: "Déclaration conjointe des ministres du numérique nordiques, 15 janvier 2026", url: "https://www.government.se/statements/nordic-digital-ministers-2026", date: "", bias: "progressiste" },
      { id: 4, title: "Lettre ouverte du Digital Industry Consortium, 28 janvier 2026", url: "https://digitalindustry.eu/open-letter-smartphone-ban", date: "", bias: "conservateur" },
      { id: 5, title: "Fédération européenne des associations de parents d'élèves, communiqué du 30 janvier 2026", url: "https://www.epa-parents.eu/communique-smartphones-2026", date: "", bias: "progressiste" },
      { id: 6, title: "Euractiv, « Smartphones et mineurs : l'Europe divisée », 1er février 2026", url: "https://www.euractiv.fr/section/numerique/smartphones-mineurs-europe", date: "", bias: "" },
    ],
  },
  {
    id: "nasa-eau-mars",
    title: "La NASA confirme la découverte d'eau sur Mars",
    subtitle: "Une avancée majeure pour l'exploration spatiale et la recherche de vie extraterrestre",
    author: "France Info",
    source_url: "https://www.francetvinfo.fr",
    source_type: "article",
    text: "",
    date: "1 fév. 2026",
    verdict: "VRAI",
    format: "long",
    rhetorics: [],
    summary:
      "La NASA a bien publié un communiqué officiel confirmant la présence de traces d'eau liquide sous la surface martienne.",
    article: [
      "La NASA a officiellement confirmé, lors d'une conférence de presse tenue au Jet Propulsion Laboratory de Pasadena, la découverte de traces d'eau liquide sous la surface de Mars. Cette annonce, attendue depuis plusieurs semaines par la communauté scientifique, repose sur les données collectées par le rover Perseverance et l'orbiteur Mars Reconnaissance Orbiter¹.",
      "Les analyses spectrométriques révèlent la présence de poches d'eau saumâtre situées entre 2 et 5 kilomètres sous la surface du cratère Jezero, zone d'exploration principale de Perseverance depuis son atterrissage en février 2021. La concentration en sels dissous suggère des conditions qui pourraient, en théorie, être compatibles avec certaines formes de vie microbienne².",
      "« C'est un moment historique pour l'exploration spatiale », a déclaré le Dr. Sarah Chen, directrice adjointe du programme Mars de la NASA. « Nous ne parlons plus de glace ou de traces d'écoulement passé. Nous avons des preuves solides de la présence d'eau à l'état liquide, maintenue sous pression par les couches géologiques supérieures³. »",
      "Cette découverte relance le débat sur la possibilité d'une vie passée ou présente sur Mars. Les exobiologistes rappellent toutefois que la présence d'eau, bien que nécessaire, n'est pas suffisante pour conclure à l'existence de vie. Les conditions de température, de radiation et de chimie du sol restent des facteurs déterminants⁴.",
      "L'Agence spatiale européenne (ESA) a salué la découverte et annoncé un renforcement de sa collaboration avec la NASA dans le cadre du programme Mars Sample Return, dont l'objectif est de ramener des échantillons martiens sur Terre d'ici 2032. Ces échantillons pourraient contenir des indices biologiques décisifs⁵.",
      "Du côté du secteur privé, SpaceX a réagi en affirmant que cette découverte « conforte la vision d'une présence humaine durable sur Mars ». Elon Musk a évoqué sur X la possibilité d'utiliser ces réserves d'eau souterraines pour alimenter de futures colonies martiennes, bien que les experts jugent cette perspective encore très lointaine⁶.",
    ].join("\n\n"),
    quote: {
      text: "Nous avons des preuves solides de la présence d'eau à l'état liquide, maintenue sous pression par les couches géologiques supérieures.",
      author: "Dr. Sarah Chen, NASA",
    },
    sources: [
      { id: 1, title: "NASA, communiqué officiel « Water on Mars: Confirmed », 30 janvier 2026", url: "https://www.nasa.gov/press-release/water-on-mars-confirmed-2026", date: "", bias: "" },
      { id: 2, title: "Journal of Geophysical Research: Planets, vol. 131, « Subsurface brines in Jezero Crater »", url: "https://agupubs.onlinelibrary.wiley.com/journal/jgre", date: "", bias: "" },
      { id: 3, title: "Conférence de presse NASA-JPL, retranscription officielle, 30 janvier 2026", url: "https://www.jpl.nasa.gov/news/press-conference-mars-water-2026", date: "", bias: "" },
      { id: 4, title: "Nature Astrobiology, « Habitability constraints on Martian subsurface environments », février 2026", url: "https://www.nature.com/articles/astrobiology-mars-2026", date: "", bias: "" },
      { id: 5, title: "ESA, déclaration du directeur général Josef Aschbacher, 31 janvier 2026", url: "https://www.esa.int/Science_Exploration/Human_and_Robotic_Exploration/mars-water-statement", date: "", bias: "" },
      { id: 6, title: "Publication X (ex-Twitter) d'Elon Musk, 30 janvier 2026", url: "https://x.com/elonmusk/status/1234567890", date: "", bias: "conservateur" },
    ],
  },
  {
    id: "cafe-alcool",
    title: "Le café serait plus dangereux que l'alcool selon une étude",
    author: "Twitter/X",
    source_url: "https://x.com",
    source_type: "tweet",
    text: "",
    date: "28 jan. 2026",
    verdict: "FAUX",
    format: "short",
    rhetorics: [],
    summary:
      "L'étude citée ne compare pas directement le café et l'alcool. Les conclusions ont été déformées et sorties de leur contexte.",
    article: [
      "Une publication virale sur X (anciennement Twitter) affirme qu'une étude scientifique récente aurait démontré que le café est « plus dangereux que l'alcool pour la sant�� ». Cette affirmation repose sur un [[Homme de paille]] : l'étude originale ne comparait pas les deux substances. Ce contenu a été partagé plus de 50 000 fois en 48 heures.",
      "Après vérification, l'étude citée existe bien mais ses conclusions ont été considérablement déformées. Les chercheurs n'ont jamais comparé directement le café et l'alcool¹.",
      "L'étude originale, publiée dans le European Journal of Nutrition, portait sur les effets de doses élevées de caféine sur le rythme cardiaque, pas sur une comparaison avec l'alcool¹.",
      "Les auteurs de l'étude ont publié un démenti formel sur le site de leur université².",
    ].join("\n\n"),
    sources: [
      { id: 1, title: "European Journal of Nutrition, « High-dose caffeine and cardiac rhythm », janvier 2026", url: "https://link.springer.com/journal/394", date: "", bias: "" },
      { id: 2, title: "Université de Heidelberg, communiqué de démenti, 29 janvier 2026", url: "https://www.uni-heidelberg.de/en/newsroom/caffeine-study-clarification", date: "", bias: "" },
    ],
  },
  {
    id: "ia-tremblements-terre",
    title: "Un algorithme IA capable de prédire les tremblements de terre",
    author: "TechCrunch",
    source_url: "https://techcrunch.com",
    source_type: "article",
    text: "",
    date: "25 jan. 2026",
    verdict: "INCERTAIN",
    format: "long",
    rhetorics: [],
    summary:
      "Des avancées réelles existent en matière de détection sismique par intelligence artificielle, mais les affirmations de prédiction fiable à 90 % restent largement exagérées par rapport aux résultats effectivement publiés dans la littérature scientifique.",
    article: [
      "Un article de TechCrunch affirme qu'un algorithme d'intelligence artificielle développé par une startup californienne serait capable de prédire les tremblements de terre avec « une précision de 90 % ».",
      "L'algorithme en question existe et a fait l'objet d'une publication dans Science¹, mais les résultats sont nettement plus nuancés que ce que laisse entendre l'article.",
      "Les sismologues consultés rappellent que la prédiction des tremblements de terre reste un défi majeur et qu'aucun système n'atteint une fiabilité opérationnelle².",
    ].join("\n\n"),
    sources: [
      { id: 1, title: "Science, « Machine learning approaches to seismic forecasting », janvier 2026", url: "https://www.science.org/doi/10.1126/science.seismic-ml-2026", date: "", bias: "" },
      { id: 2, title: "USGS, déclaration sur les limites actuelles de la prédiction sismique, 26 janvier 2026", url: "https://www.usgs.gov/faqs/can-you-predict-earthquakes", date: "", bias: "" },
    ],
  },
  {
    id: "discours-premier-ministre",
    title: "Fact-checking du discours du Premier Ministre sur l'économie",
    subtitle: "Déclaration télévisée du 20 février 2026 — Analyse point par point",
    author: "France 2",
    source_url: "https://www.france.tv/france-2",
    source_type: "recording",
    text: "",
    date: "21 fév. 2026",
    verdict: "INCERTAIN",
    format: "long",
    rhetorics: [],
    summary:
      "Analyse détaillée des principales affirmations du Premier Ministre lors de son allocution sur la politique économique. Plusieurs déclarations sont vérifiées, d'autres sont trompeuses ou invérifiables.",
    article: [
      "Le Premier Ministre a affirmé que « le chômage est au plus bas depuis 15 ans ». Selon les données de l'INSEE publiées en janvier 2026, le taux de chômage s'établit à 6,9 %, son niveau le plus bas depuis le premier trimestre 2011. Cette affirmation est donc exacte¹.",
      "Il a ensuite déclaré que « la France est le pays européen qui investit le plus dans la transition écologique ». En valeur absolue, la France figure parmi les premiers investisseurs. Mais rapporté au PIB, elle se classe derrière le Danemark, l'Allemagne et la Suède². L'affirmation dépend donc du critère retenu.",
      "Concernant les impôts, le Premier Ministre a soutenu que « les impôts ont baissé pour 80 % des Français ». La suppression de la taxe d'habitation a effectivement bénéficié à une large majorité de ménages. Cependant, d'autres prélèvements ont augmenté sur la même période, rendant le bilan global plus nuancé³.",
      "L'affirmation selon laquelle « aucun hôpital n'a fermé sous ce gouvernement » est fausse. Au moins trois établissements hospitaliers ont été fermés ou fusionnés depuis la prise de fonction du gouvernement, selon les données du ministère de la Santé⁴.",
      "Enfin, « le pouvoir d'achat a augmenté de 3 % en moyenne ». Les données de l'INSEE confirment une hausse moyenne du pouvoir d'achat de 2,8 % sur les 12 derniers mois⁵, un chiffre cohérent avec l'affirmation arrondie du Premier Ministre.",
    ].join("\n\n"),
    sources: [
      { id: 1, title: "INSEE, Enquête emploi T4 2025, publiée le 15 janvier 2026", url: "https://www.insee.fr/fr/statistiques/enquete-emploi-t4-2025", date: "", bias: "" },
      { id: 2, title: "Eurostat, Green Deal Investment Tracker, données 2025", url: "https://ec.europa.eu/eurostat/green-deal-tracker", date: "", bias: "" },
      { id: 3, title: "Direction générale des Finances publiques, rapport annuel 2025", url: "https://www.economie.gouv.fr/dgfip/rapport-annuel-2025", date: "", bias: "" },
      { id: 4, title: "Ministère de la Santé, carte hospitalière mise à jour février 2026", url: "https://www.sante.gouv.fr/carte-hospitaliere-2026", date: "", bias: "" },
      { id: 5, title: "INSEE, Note de conjoncture « Pouvoir d'achat des ménages », janvier 2026", url: "https://www.insee.fr/fr/statistiques/pouvoir-achat-2026", date: "", bias: "" },
    ],
  },
  // ── "A la une" articles ──────────────────────────────
  {
    id: "desinformation-vaccins-grippe",
    title: "Vague de désinformation sur le vaccin contre la grippe aviaire",
    subtitle: "Des vidéos virales accusent le vaccin de contenir des puces — analyse complète",
    author: "AFP Factuel",
    source_url: "https://factuel.afp.com",
    source_type: "article",
    text: "",
    date: "5 mars 2026",
    verdict: "FAUX",
    format: "long",
    featured: true,
    rhetorics: [],
    summary:
      "Une série de vidéos virales sur TikTok et X affirment que le nouveau vaccin contre la grippe aviaire H5N1 contiendrait des « nano-puces de traçage ». Ces allégations sont entièrement fausses et reposent sur des images manipulées.",
    article: [
      "Depuis fin février, plusieurs vidéos cumulant des millions de vues sur TikTok et X prétendent que le vaccin contre la grippe aviaire H5N1, autorisé par l'EMA le 15 février 2026, contiendrait des « nano-puces de traçage GPS ». Les créateurs de ces contenus utilisent un [[Appel à l'émotion]] en montrant des images d'enfants hospitalisés qui n'ont aucun lien avec la vaccination¹.",
      "L'analyse des vidéos révèle plusieurs manipulations. Les images microscopiques présentées comme des « puces » sont en réalité des cristaux de sel adjuvant, parfaitement normaux dans la composition d'un vaccin. Un expert en imagerie de l'Institut Pasteur a confirmé cette identification².",
      "Les auteurs de ces vidéos recourent systématiquement au [[Cherry Picking]], sélectionnant uniquement les effets secondaires rares listés dans la notice du vaccin tout en ignorant les données globales de pharmacovigilance qui montrent un profil de sécurité comparable aux vaccins grippaux classiques³.",
      "L'OMS a publié un démenti détaillé accompagné d'une vidéo explicative. Le porte-parole de l'agence a souligné que ces campagnes de désinformation mettent en danger la santé publique dans un contexte où le virus H5N1 a déjà causé 47 décès humains en 2026⁴.",
      "Plusieurs plateformes ont commencé à restreindre la diffusion de ces contenus, mais les créateurs contournent les filtres en utilisant des orthographes alternatives et des visuels modifiés���.",
    ].join("\n\n"),
    quote: {
      text: "Chaque vague de désinformation vaccinale a un coût en vies humaines. Ce n'est pas un débat d'opinions, c'est une question de santé publique.",
      author: "Dr. Tedros Adhanom, directeur général de l'OMS",
    },
    sources: [
      { id: 1, title: "AFP Factuel, « Non, le vaccin H5N1 ne contient pas de puces », 3 mars 2026", url: "https://factuel.afp.com/vaccin-h5n1-puces-faux", date: "", bias: "" },
      { id: 2, title: "Institut Pasteur, analyse d'imagerie vaccinale, février 2026", url: "https://www.pasteur.fr/fr/imagerie-vaccin-h5n1", date: "", bias: "" },
      { id: 3, title: "EMA, rapport de pharmacovigilance vaccin H5N1, 28 février 2026", url: "https://www.ema.europa.eu/h5n1-vaccine-safety-2026", date: "", bias: "" },
      { id: 4, title: "OMS, communiqué « Countering H5N1 vaccine misinformation », 2 mars 2026", url: "https://www.who.int/news/h5n1-misinformation-2026", date: "", bias: "" },
      { id: 5, title: "Reuters, « Social platforms struggle with H5N1 vaccine hoaxes », 4 mars 2026", url: "https://www.reuters.com/technology/h5n1-vaccine-hoaxes-2026", date: "", bias: "" },
    ],
  },
  {
    id: "france-nucleaire-fusion",
    title: "La France annonce un prototype de réacteur à fusion pour 2035",
    subtitle: "Le CEA dévoile le projet « Étoile » lors d'une allocution présidentielle",
    author: "Les Échos",
    source_url: "https://www.lesechos.fr",
    source_type: "article",
    text: "",
    date: "6 mars 2026",
    verdict: "INCERTAIN",
    format: "long",
    featured: true,
    rhetorics: [],
    summary:
      "Le président a annoncé un programme national de fusion nucléaire doté de 4 milliards d'euros. Si le financement est réel, les experts jugent le calendrier annoncé très optimiste au vu de l'état actuel de la recherche.",
    article: [
      "Lors d'un discours prononcé au centre CEA de Cadarache, le président de la République a annoncé le lancement du programme « Étoile », un projet national visant à construire un prototype de réacteur à fusion nucléaire d'ici 2035. L'enveloppe budgétaire annoncée s'élève à 4 milliards d'euros sur dix ans¹.",
      "Le CEA a présenté les grandes lignes techniques du projet, qui s'appuierait sur les avancées du programme international ITER, dont le site est précisément situé à quelques kilomètres de Cadarache. Cependant, plusieurs physiciens ont souligné que le discours présidentiel relevait en partie de l'[[Appel à l'autorité]], en citant des résultats d'ITER qui n'ont pas encore été obtenus².",
      "Les experts du secteur sont divisés. Le professeur Jean-Marc Lévy, directeur de recherche au CNRS, estime que « le calendrier 2035 est un objectif politique, pas un objectif scientifique ». Il rappelle qu'ITER lui-même accuse plusieurs années de retard et que la démonstration du gain net d'énergie par fusion n'a été réalisée qu'à très petite échelle au NIF américain³.",
      "Du côté des industriels, le groupe EDF a accueilli l'annonce « avec intérêt mais prudence », soulignant que la fusion reste à ce jour une technologie de laboratoire. Le PDG a toutefois confirmé la participation d'EDF aux études préliminaires⁴.",
      "Les associations écologistes ont réagi de manière contrastée. Certaines saluent l'investissement dans une énergie potentiellement propre et quasi illimitée, tandis que d'autres dénoncent un [[Faux dilemme]] entre « tout nucléaire ou tout renouvelable », estimant que les fonds seraient mieux employés dans le solaire et l'éolien⁵.",
    ].join("\n\n"),
    quote: {
      text: "La fusion est l'énergie du XXIe siècle. La France doit en être le fer de lance, comme elle l'a été pour la fission.",
      author: "Discours présidentiel, Cadarache, 5 mars 2026",
    },
    sources: [
      { id: 1, title: "Élysée, communiqué « Programme Étoile : la France pionnière de la fusion », 5 mars 2026", url: "https://www.elysee.fr/programme-etoile-fusion-2026", date: "", bias: "" },
      { id: 2, title: "ITER Organization, rapport d'avancement 2025", url: "https://www.iter.org/rapport-2025", date: "", bias: "institutionnel" },
      { id: 3, title: "CNRS, interview Pr. Lévy, « Fusion 2035 : ambition ou illusion ? », 6 mars 2026", url: "https://lejournal.cnrs.fr/fusion-2035-ambition-illusion", date: "", bias: "" },
      { id: 4, title: "EDF, communiqué de presse, 5 mars 2026", url: "https://www.edf.fr/communiques/programme-etoile-fusion", date: "", bias: "industriel" },
      { id: 5, title: "Greenpeace France, réaction au programme Étoile, 6 mars 2026", url: "https://www.greenpeace.fr/programme-etoile-reaction", date: "", bias: "écologiste" },
    ],
  },
  {
    id: "tiktok-sante-mentale",
    title: "TikTok accusé d'amplifier les troubles alimentaires chez les adolescents",
    author: "The Guardian",
    source_url: "https://www.theguardian.com",
    source_type: "article",
    text: "",
    date: "4 mars 2026",
    verdict: "VRAI",
    format: "long",
    featured: true,
    rhetorics: [],
    summary:
      "Une étude de l'université d'Oxford confirme que l'algorithme de TikTok expose massivement les adolescents vulnérables à du contenu pro-anorexie en moins de 30 minutes d'utilisation.",
    article: [
      "Une étude publiée dans The Lancet Digital Health par des chercheurs de l'université d'Oxford démontre que l'algorithme de recommandation de TikTok oriente activement les adolescents vers du contenu lié aux troubles alimentaires, et ce dès les premières minutes d'utilisation¹.",
      "Les chercheurs ont créé 200 profils simulant des adolescents de 13 à 17 ans. En moins de 30 minutes d'interaction passive, 68 % des profils ont été exposés à du contenu classifié comme « pro-anorexie » ou « glorifiant la maigreur extrême ». L'étude note que l'algorithme intensifie ces recommandations lorsqu'il détecte un engagement (même un simple arrêt de scroll) sur ce type de contenu².",
      "TikTok a répondu en qualifiant la méthodologie de « non représentative des conditions réelles d'utilisation » et en rappelant ses investissements dans la modération. Cependant, les chercheurs dénoncent cet argument comme un [[Homme de paille]], soulignant que leur protocole reproduisait précisément le comportement typique d'un adolescent découvrant la plateforme³.",
      "Le Défenseur des droits en France a annoncé l'ouverture d'une enquête préliminaire. Plusieurs associations de protection de l'enfance demandent une régulation européenne contraignante des algorithmes de recommandation⁴.",
    ].join("\n\n"),
    sources: [
      { id: 1, title: "The Lancet Digital Health, « Algorithmic amplification of eating disorder content on TikTok », mars 2026", url: "https://www.thelancet.com/journals/landig/article/tiktok-ed-2026", date: "", bias: "" },
      { id: 2, title: "Université d'Oxford, rapport complet de l'étude, 3 mars 2026", url: "https://www.ox.ac.uk/research/tiktok-eating-disorders-2026", date: "", bias: "" },
      { id: 3, title: "TikTok, déclaration officielle « Our commitment to user safety », 4 mars 2026", url: "https://newsroom.tiktok.com/user-safety-statement-2026", date: "", bias: "corporate" },
      { id: 4, title: "Défenseur des droits, communiqué du 4 mars 2026", url: "https://www.defenseurdesdroits.fr/tiktok-enquete-2026", date: "", bias: "" },
    ],
  },
  {
    id: "debat-retraites-senat",
    title: "Analyse du débat sénatorial sur la réforme des retraites",
    subtitle: "Séance publique du 2 mars 2026 — Les arguments au crible",
    author: "Public Sénat",
    source_url: "https://www.publicsenat.fr",
    source_type: "recording",
    text: "",
    date: "3 mars 2026",
    verdict: "INCERTAIN",
    format: "long",
    featured: true,
    rhetorics: [],
    summary:
      "Décryptage des principales affirmations avancées lors du débat au Sénat sur l'ajustement de la réforme des retraites. Entre chiffres vérifiés et raccourcis trompeurs.",
    article: [
      "Le sénateur a affirmé que « le système sera en déficit de 15 milliards d'ici 2030 ». Le COR prévoit un déficit entre 5 et 15 milliards selon les scénarios économiques. Le sénateur a retenu l'hypothèse la plus pessimiste sans le préciser¹.",
      "La déclaration selon laquelle « l'espérance de vie en bonne santé stagne depuis 10 ans » est vérifiée. Les données d'Eurostat confirment une stagnation de l'espérance de vie en bonne santé autour de 64 ans pour les hommes et 65 ans pour les femmes depuis 2016².",
      "L'affirmation que « les fonctionnaires cotisent moins que les salariés du privé » est fausse. Les taux de cotisation apparents diffèrent, mais le coût total (part salariale + employeur) est comparable. Cette affirmation repose sur une comparaison incomplète³.",
      "Concernant « la France a le système de retraite le plus généreux d'Europe », la réalité est plus nuancée. En termes de taux de remplacement moyen, la France se situe au-dessus de la moyenne européenne mais derrière l'Italie, l'Autriche et le Luxembourg⁴.",
    ].join("\n\n"),
    sources: [
      { id: 1, title: "Conseil d'orientation des retraites, rapport annuel 2025", url: "https://www.cor-retraites.fr/rapport-2025", date: "", bias: "" },
      { id: 2, title: "Eurostat, « Healthy life years at birth by sex », données 2016-2025", url: "https://ec.europa.eu/eurostat/healthy-life-years", date: "", bias: "" },
      { id: 3, title: "Cour des comptes, rapport « Cotisations retraites : public et privé », octobre 2025", url: "https://www.ccomptes.fr/cotisations-retraites-2025", date: "", bias: "" },
      { id: 4, title: "OCDE, Panorama des pensions 2025", url: "https://www.oecd.org/pensions/pensions-at-a-glance-2025", date: "", bias: "" },
    ],
  },
];

export const getArticleById = (id: string): ArticleData | undefined =>
  articles.find((a) => a.id === id);