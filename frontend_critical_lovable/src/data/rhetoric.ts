/**
 * Rhetoric catalog — mirrors backend/rhetoric_catalog.py.
 * The Writer uses [[French label]] markers in the article text.
 * This file lets the frontend look up definitions by label.
 */

export interface RhetoricFallacy {
  name: string;       // stable snake_case identifier
  label: string;      // French display name
  definition: string;
  examples: string[];
}

const catalog: Record<string, RhetoricFallacy> = {
  straw_man: {
    name: "straw_man",
    label: "Homme de paille",
    definition: "Consiste à déformer ou simplifier à l'extrême l'argument de l'adversaire pour le rendre plus facile à attaquer, puis réfuter cette version affaiblie plutôt que l'argument réel.",
    examples: [
      "« Les écologistes veulent qu'on retourne vivre dans des grottes. » — Personne ne défend cette position ; l'argument réel porte sur une transition énergétique progressive.",
      "« Vous voulez supprimer la police ? Vous voulez donc le chaos total ! » — La demande initiale portait sur une réforme, pas une suppression.",
    ],
  },
  false_dilemma: {
    name: "false_dilemma",
    label: "Faux dilemme",
    definition: "Présenter une situation comme n'ayant que deux options possibles (souvent une bonne et une mauvaise), alors qu'en réalité d'autres alternatives existent.",
    examples: [
      "« Soit on interdit totalement les smartphones aux enfants, soit on accepte qu'ils soient accros aux écrans. » — Il existe de nombreuses approches intermédiaires.",
      "« Vous êtes avec nous ou contre nous. » — Ignorer les positions nuancées ou neutres.",
    ],
  },
  false_correlation: {
    name: "false_correlation",
    label: "Corrélation fallacieuse",
    definition: "Affirmer qu'un lien de cause à effet existe entre deux phénomènes simplement parce qu'ils se produisent en même temps ou l'un après l'autre, sans démontrer de mécanisme causal réel.",
    examples: [
      "« Depuis l'installation de la 5G, les cas de cancer augmentent dans la région. » — La coïncidence temporelle ne prouve aucun lien causal ; d'autres facteurs peuvent expliquer la hausse.",
      "« Les pays qui consomment le plus de chocolat ont le plus de prix Nobel. » — Une corrélation statistique ne démontre pas que le chocolat rend plus intelligent.",
    ],
  },
  zero_cost_lie: {
    name: "zero_cost_lie",
    label: "Mensonge à coût zéro",
    definition: "Énoncer une affirmation fausse ou invérifiable sur le moment, en comptant sur le fait que personne ne prendra la peine de vérifier ou que le démenti n'aura jamais autant de visibilité que l'affirmation initiale.",
    examples: [
      "« J'ai lu une étude de Harvard qui montre exactement ça. » — Aucune référence précise n'est donnée, et l'interlocuteur ne peut pas vérifier en direct.",
      "« 80 % des Français pensent comme moi. » — Un chiffre inventé, lancé avec assurance pour clore le débat.",
    ],
  },
  out_of_context_comparison: {
    name: "out_of_context_comparison",
    label: "Comparaison hors contexte",
    definition: "Comparer deux situations, chiffres ou entités en ignorant délibérément les différences de contexte qui rendent la comparaison trompeuse (époque, échelle, méthodologie, périmètre).",
    examples: [
      "« La France a moins de lits d'hôpital que dans les années 80. » — Sans préciser que la médecine ambulatoire a transformé la prise en charge et réduit le besoin de lits.",
      "« Le PIB de tel petit pays dépasse celui de tel autre. » — Sans rapporter au nombre d'habitants ni au coût de la vie.",
    ],
  },
  post_truth: {
    name: "post_truth",
    label: "Post-vérité",
    definition: "Faire appel aux émotions et aux croyances personnelles plutôt qu'aux faits objectifs pour façonner l'opinion, rendant la véracité factuelle secondaire par rapport au ressenti.",
    examples: [
      "« Les gens en ont marre, ils le sentent, la criminalité explose. » — Le ressenti est présenté comme preuve, même si les statistiques ne montrent pas cela.",
      "« Peu importe ce que disent les experts, les citoyens savent bien ce qu'ils vivent au quotidien. » — Opposer le vécu émotionnel aux données factuelles pour disqualifier ces dernières.",
    ],
  },
  omission: {
    name: "omission",
    label: "Omission",
    definition: "Passer volontairement sous silence des faits, des données ou des arguments pertinents qui nuiraient à la thèse défendue, donnant ainsi une image incomplète et orientée de la réalité.",
    examples: [
      "« Le chômage a baissé ce trimestre. » — Sans préciser que la baisse est due à un changement de méthode de calcul, pas à une création d'emplois.",
    ],
  },
  blind_trust: {
    name: "blind_trust",
    label: "Confiance aveugle",
    definition: "Demander à l'auditoire de croire une affirmation uniquement sur la base de la confiance envers l'orateur, sans fournir de preuves ni de raisonnement vérifiable.",
    examples: [
      "« Je ne peux pas tout vous révéler, mais croyez-moi, c'est vrai. » — L'impossibilité de vérifier est présentée comme une raison supplémentaire de croire.",
    ],
  },
  appeal_to_authority: {
    name: "appeal_to_authority",
    label: "Appel à l'autorité",
    definition: "Justifier une affirmation en s'appuyant sur l'opinion d'une personne considérée comme experte ou prestigieuse, alors que cette personne s'exprime hors de son domaine de compétence ou que son avis seul ne constitue pas une preuve.",
    examples: [
      "« Un grand patron recommande cette politique économique. » — Diriger une entreprise ne garantit pas une compréhension juste de la macroéconomie nationale.",
    ],
  },
  appeal_to_popularity: {
    name: "appeal_to_popularity",
    label: "Appel à la popularité",
    definition: "Affirmer qu'une chose est vraie, bonne ou souhaitable simplement parce qu'un grand nombre de personnes y croient ou l'adoptent.",
    examples: [
      "« Des millions de personnes utilisent ce produit, il est donc forcément efficace. » — La popularité commerciale ne prouve pas l'efficacité.",
    ],
  },
  appeal_to_exoticism: {
    name: "appeal_to_exoticism",
    label: "Appel à l'exotisme",
    definition: "Présenter une pratique, un produit ou une idée comme supérieure simplement parce qu'elle provient d'une culture lointaine ou perçue comme mystérieuse, sans évaluer son efficacité réelle.",
    examples: [
      "« Ce remède ancestral tibétain guérit naturellement ce que la médecine occidentale n'arrive pas à soigner. » — L'origine géographique ne constitue pas une preuve d'efficacité.",
    ],
  },
  appeal_to_nature: {
    name: "appeal_to_nature",
    label: "Appel à la nature",
    definition: "Affirmer qu'une chose est bonne, saine ou souhaitable parce qu'elle est « naturelle », ou mauvaise parce qu'elle est « artificielle », sans évaluation factuelle.",
    examples: [
      "« Ce produit est 100 % naturel, donc il ne peut pas être nocif. » — De nombreuses substances naturelles sont toxiques (arsenic, amanite phalloïde).",
      "« Les additifs chimiques sont forcément mauvais pour la santé. » — Le sel de table et le bicarbonate sont aussi des « produits chimiques ».",
    ],
  },
  appeal_to_antiquity: {
    name: "appeal_to_antiquity",
    label: "Appel à l'ancienneté",
    definition: "Justifier une pratique ou une croyance par le fait qu'elle existe depuis longtemps, comme si la durée de son existence prouvait sa validité.",
    examples: [
      "« L'homéopathie existe depuis plus de 200 ans, c'est bien la preuve que ça fonctionne. » — La longévité d'une pratique ne démontre pas son efficacité.",
    ],
  },
  appeal_to_tradition: {
    name: "appeal_to_tradition",
    label: "Appel à la tradition",
    definition: "Défendre une idée ou une pratique en invoquant la tradition ou les coutumes, comme si le fait d'être traditionnel la rendait intrinsèquement légitime ou correcte.",
    examples: [
      "« Nos ancêtres faisaient comme ça, pourquoi changer ? » — Les conditions et les connaissances ont évolué depuis.",
    ],
  },
  slippery_slope: {
    name: "slippery_slope",
    label: "Pente glissante",
    definition: "Affirmer qu'une action entraînera inévitablement une chaîne de conséquences de plus en plus graves, sans démontrer la probabilité réelle de chaque étape de l'enchaînement.",
    examples: [
      "« Si on autorise le mariage homosexuel, bientôt on autorisera le mariage avec des animaux. » — Aucun lien logique ou juridique ne relie ces deux situations.",
      "« Si on baisse un peu les impôts, c'est la porte ouverte à la suppression de tous les services publics. » — Une mesure fiscale modérée n'entraîne pas mécaniquement un démantèlement total.",
    ],
  },
  no_true_scotsman: {
    name: "no_true_scotsman",
    label: "Vrai Écossais",
    definition: "Face à un contre-exemple qui réfute une généralisation, redéfinir ad hoc les critères d'appartenance au groupe pour exclure le contre-exemple, rendant l'affirmation infalsifiable.",
    examples: [
      "« — Certains végans mangent du poisson. — Alors ce ne sont pas de vrais végans. » — Plutôt que d'admettre la diversité des pratiques, on déplace la définition.",
      "« Aucun vrai patriote ne critiquerait son gouvernement. » — Redéfinir « patriote » pour exclure toute dissidence rend l'affirmation impossible à contredire.",
    ],
  },
  ad_hominem: {
    name: "ad_hominem",
    label: "Ad hominem",
    definition: "Attaquer la personne qui avance un argument plutôt que l'argument lui-même, afin de discréditer sa position sans en traiter le fond.",
    examples: [
      "« Que voulez-vous qu'il comprenne à l'économie, il n'a jamais travaillé dans le privé. » — L'expérience professionnelle de la personne ne dit rien de la validité de son raisonnement.",
    ],
  },
  whataboutism: {
    name: "whataboutism",
    label: "Whataboutisme",
    definition: "Détourner une critique en pointant le comportement d'un autre acteur, plutôt que de répondre sur le fond de la critique initiale.",
    examples: [
      "« Oui mais l'autre parti a fait bien pire quand il était au pouvoir. » — La faute d'autrui ne répond pas à la critique formulée.",
    ],
  },
  cherry_picking: {
    name: "cherry_picking",
    label: "Cherry Picking",
    definition: "Sélectionner uniquement les données, exemples ou faits qui soutiennent sa thèse en ignorant ceux qui la contredisent. Contrairement à l'omission (cacher un fait précis), le picorage construit un argumentaire entier à partir d'un échantillon biaisé.",
    examples: [
      "« La criminalité a augmenté de 15 % dans cette ville. » — En ne citant que la catégorie de délit qui a augmenté, alors que la criminalité globale a baissé.",
    ],
  },
  false_equivalence: {
    name: "false_equivalence",
    label: "Fausse équivalence",
    definition: "Mettre sur le même plan deux choses fondamentalement différentes pour créer une impression d'équilibre ou de symétrie trompeuse.",
    examples: [
      "« Il y a des arguments des deux côtés sur le changement climatique. » — Donner autant de poids à un consensus scientifique massif qu'à une position marginale crée une fausse impression de débat équilibré.",
    ],
  },
  anecdotal_evidence: {
    name: "anecdotal_evidence",
    label: "Preuve anecdotique",
    definition: "Utiliser un cas personnel ou un exemple isolé comme preuve d'une tendance générale, alors qu'il ne constitue pas un échantillon représentatif.",
    examples: [
      "« Mon grand-père a fumé toute sa vie et il a vécu jusqu'à 95 ans, donc le tabac n'est pas si dangereux. » — Un cas individuel ne réfute pas les données épidémiologiques.",
    ],
  },
  appeal_to_fear: {
    name: "appeal_to_fear",
    label: "Appel à la peur",
    definition: "Utiliser la peur pour pousser vers une conclusion, en exagérant une menace ou en décrivant des conséquences catastrophiques sans les étayer.",
    examples: [
      "« Si on ne ferme pas les frontières immédiatement, notre civilisation disparaîtra. » — La menace existentielle est brandie sans aucune démonstration du lien causal.",
    ],
  },
  appeal_to_ignorance: {
    name: "appeal_to_ignorance",
    label: "Appel à l'ignorance",
    definition: "Affirmer qu'une chose est vraie parce qu'on n'a pas prouvé qu'elle est fausse, ou inversement.",
    examples: [
      "« Prouvez-moi que ce n'est PAS un complot. » — L'absence de preuve contraire n'est pas une preuve.",
    ],
  },
  appeal_to_emotion: {
    name: "appeal_to_emotion",
    label: "Appel à l'émotion",
    definition: "Manipuler les émotions de l'auditoire (peur, pitié, colère) pour obtenir l'adhésion à un argument, en lieu et place de preuves rationnelles.",
    examples: [
      "« Pensez aux enfants ! » — Invoquer la protection des enfants pour couper court à tout débat rationnel.",
      "« Si vous n'agissez pas maintenant, ce sera la catastrophe ! » — Créer un sentiment d'urgence disproportionné.",
    ],
  },
};

/** Build label→entry lookup (case-insensitive) */
const labelIndex = new Map<string, RhetoricFallacy>();
for (const entry of Object.values(catalog)) {
  labelIndex.set(entry.label.toLowerCase(), entry);
}

/** Look up a fallacy by its French label (case-insensitive). Used when parsing [[label]] markers. */
export const getFallacy = (label: string): RhetoricFallacy | undefined => {
  return labelIndex.get(label.toLowerCase().trim());
};

/** Get full catalog (e.g. for listing all known fallacies) */
export const getAllFallacies = (): RhetoricFallacy[] => Object.values(catalog);

export default catalog;
