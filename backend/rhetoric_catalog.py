"""
Rhetoric catalog — source of truth for all detectable rhetorical devices.
The 'name' field is the stable identifier used by the LLM, the backend, and the frontend.
User-facing content (label, definition, example) is organized by language.
"""

RHETORIC_NAMES = [
    "straw_man",
    "false_dilemma",
    "false_correlation",
    "zero_cost_lie",
    "out_of_context_comparison",
    "post_truth",
    "omission",
    "blind_trust",
    "appeal_to_authority",
    "appeal_to_popularity",
    "appeal_to_exoticism",
    "appeal_to_nature",
    "appeal_to_antiquity",
    "appeal_to_tradition",
    "slippery_slope",
    "no_true_scotsman",
]

VALID_RHETORIC_NAMES = set(RHETORIC_NAMES)

RHETORIC_TRANSLATIONS = { #Other languages must be added!
    "fr": {
        "straw_man": {
            "label": "Homme de paille",
            "definition": "Consiste à déformer ou simplifier à l'extrême l'argument de l'adversaire pour le rendre plus facile à attaquer, puis réfuter cette version affaiblie plutôt que l'argument réel.",
            "examples": [
                "« Les écologistes veulent qu'on retourne vivre dans des grottes. » — Personne ne défend cette position ; l'argument réel porte sur une transition énergétique progressive.",
                "« Vous voulez supprimer la police ? Vous voulez donc le chaos total ! » — La demande initiale portait sur une réforme, pas une suppression.",
            ],
        },
        "false_dilemma": {
            "label": "Faux dilemme",
            "definition": "Présenter une situation comme n'ayant que deux options possibles (souvent une bonne et une mauvaise), alors qu'en réalité d'autres alternatives existent.",
            "examples": [
                "« Soit on interdit totalement les smartphones aux enfants, soit on accepte qu'ils soient accros aux écrans. » — Il existe de nombreuses approches intermédiaires.",
                "« Vous êtes avec nous ou contre nous. » — Ignorer les positions nuancées ou neutres.",
            ],
        },
        "false_correlation": {
            "label": "Corrélation fallacieuse",
            "definition": "Affirmer qu'un lien de cause à effet existe entre deux phénomènes simplement parce qu'ils se produisent en même temps ou l'un après l'autre, sans démontrer de mécanisme causal réel.",
            "examples": [
                "« Depuis l'installation de la 5G, les cas de cancer augmentent dans la région. » — La coïncidence temporelle ne prouve aucun lien causal ; d'autres facteurs peuvent expliquer la hausse.",
                "« Les pays qui consomment le plus de chocolat ont le plus de prix Nobel. » — Une corrélation statistique ne démontre pas que le chocolat rend plus intelligent.",
            ],
        },
        "zero_cost_lie": {
            "label": "Mensonge à coût zéro",
            "definition": "Énoncer une affirmation fausse ou invérifiable sur le moment, en comptant sur le fait que personne ne prendra la peine de vérifier ou que le démenti n'aura jamais autant de visibilité que l'affirmation initiale.",
            "examples": [ #AMELIORER
                "« J'ai lu une étude de Harvard qui montre exactement ça. » — Aucune référence précise n'est donnée, et l'interlocuteur ne peut pas vérifier en direct.",
                "« 80 % des Français pensent comme moi. » — Un chiffre inventé, lancé avec assurance pour clore le débat.",
            ],
        },
        "out_of_context_comparison": {
            "label": "Comparaison hors contexte",
            "definition": "Comparer deux situations, chiffres ou entités en ignorant délibérément les différences de contexte qui rendent la comparaison trompeuse (époque, échelle, méthodologie, périmètre).",
            "examples": [
                "« La France a moins de lits d'hôpital que dans les années 80. » — Sans préciser que la médecine ambulatoire a transformé la prise en charge et réduit le besoin de lits.",
                "« Le PIB de tel petit pays dépasse celui de tel autre. » — Sans rapporter au nombre d'habitants ni au coût de la vie.",
            ],
        },
        "post_truth": {
            "label": "Post-vérité",
            "definition": "Faire appel aux émotions et aux croyances personnelles plutôt qu'aux faits objectifs pour façonner l'opinion, rendant la véracité factuelle secondaire par rapport au ressenti.",
            "examples": [
                "« Les gens en ont marre, ils le sentent, la criminalité explose. » — Le ressenti est présenté comme preuve, même si les statistiques ne montrent pas cela.",
                "« Peu importe ce que disent les experts, les citoyens savent bien ce qu'ils vivent au quotidien. » — Opposer le vécu émotionnel aux données factuelles pour disqualifier ces dernières.",
            ],
        },
        "omission": {
            "label": "Omission",
            "definition": "Passer volontairement sous silence des faits, des données ou des arguments pertinents qui nuiraient à la thèse défendue, donnant ainsi une image incomplète et orientée de la réalité.",
            "examples": [
                "« Le chômage a baissé ce trimestre. » — Sans préciser que la baisse est due à un changement de méthode de calcul, pas à une création d'emplois.",
            ],
        },
        "blind_trust": {
            "label": "Confiance aveugle",
            "definition": "Demander à l'auditoire de croire une affirmation uniquement sur la base de la confiance envers l'orateur, sans fournir de preuves ni de raisonnement vérifiable.",
            "examples": [
                "« Je ne peux pas tout vous révéler, mais croyez-moi, c'est vrai. » — L'impossibilité de vérifier est présentée comme une raison supplémentaire de croire.",
            ],
        },
        "appeal_to_authority": {
            "label": "Appel à l'autorité",
            "definition": "Justifier une affirmation en s'appuyant sur l'opinion d'une personne considérée comme experte ou prestigieuse, alors que cette personne s'exprime hors de son domaine de compétence ou que son avis seul ne constitue pas une preuve.",
            "examples": [
                "« Un grand patron recommande cette politique économique. » — Diriger une entreprise ne garantit pas une compréhension juste de la macroéconomie nationale.",
            ],
        },
        "appeal_to_popularity": {
            "label": "Appel à la popularité",
            "definition": "Affirmer qu'une chose est vraie, bonne ou souhaitable simplement parce qu'un grand nombre de personnes y croient ou l'adoptent.",
            "examples": [
                "« Des millions de personnes utilisent ce produit, il est donc forcément efficace. » — La popularité commerciale ne prouve pas l'efficacité.",
            ],
        },
        "appeal_to_exoticism": {
            "label": "Appel à l'exotisme",
            "definition": "Présenter une pratique, un produit ou une idée comme supérieure simplement parce qu'elle provient d'une culture lointaine ou perçue comme mystérieuse, sans évaluer son efficacité réelle.",
            "examples": [
                "« Ce remède ancestral tibétain guérit naturellement ce que la médecine occidentale n'arrive pas à soigner. » — L'origine géographique ne constitue pas une preuve d'efficacité.",
            ],
        },
        "appeal_to_nature": { #AMELIORER
            "label": "Appel à la nature",
            "definition": "Affirmer qu'une chose est bonne, saine ou souhaitable parce qu'elle est « naturelle », ou mauvaise parce qu'elle est « artificielle », sans évaluation factuelle.",
            "examples": [
                "« Ce produit est 100 % naturel, donc il ne peut pas être nocif. » — De nombreuses substances naturelles sont toxiques (arsenic, amanite phalloïde).",
                "« Les additifs chimiques sont forcément mauvais pour la santé. » — Le sel de table et le bicarbonate sont aussi des « produits chimiques ».",
            ],
        },
        "appeal_to_antiquity": {
            "label": "Appel à l'ancienneté",
            "definition": "Justifier une pratique ou une croyance par le fait qu'elle existe depuis longtemps, comme si la durée de son existence prouvait sa validité.",
            "examples": [
                "« L'homéopathie existe depuis plus de 200 ans, c'est bien la preuve que ça fonctionne. » — La longévité d'une pratique ne démontre pas son efficacité.",
            ],
        },
        "appeal_to_tradition": {
            "label": "Appel à la tradition",
            "definition": "Défendre une idée ou une pratique en invoquant la tradition ou les coutumes, comme si le fait d'être traditionnel la rendait intrinsèquement légitime ou correcte.",
            "examples": [
                "« Nos ancêtres faisaient comme ça, pourquoi changer ? » — Les conditions et les connaissances ont évolué depuis.",
            ],
        },
        "slippery_slope": {
            "label": "Pente glissante",
            "definition": "Affirmer qu'une action entraînera inévitablement une chaîne de conséquences de plus en plus graves, sans démontrer la probabilité réelle de chaque étape de l'enchaînement.",
            "examples": [
                "« Si on autorise le mariage homosexuel, bientôt on autorisera le mariage avec des animaux. » — Aucun lien logique ou juridique ne relie ces deux situations.",
                "« Si on baisse un peu les impôts, c'est la porte ouverte à la suppression de tous les services publics. » — Une mesure fiscale modérée n'entraîne pas mécaniquement un démantèlement total.",
            ],
        },
        "true_scotsman": {
            "label": "Vrai Écossais",
            "definition": "Face à un contre-exemple qui réfute une généralisation, redéfinir ad hoc les critères d'appartenance au groupe pour exclure le contre-exemple, rendant l'affirmation infalsifiable.",
            "examples": [
                "« — Certains végans mangent du poisson. — Alors ce ne sont pas de vrais végans. » — Plutôt que d'admettre la diversité des pratiques, on déplace la définition.",
                "« Aucun vrai patriote ne critiquerait son gouvernement. » — Redéfinir « patriote » pour exclure toute dissidence rend l'affirmation impossible à contredire.",
            ],
        },
    },
    # "en": { ... }
}