DOMAIN_REGISTRY: dict[str, dict] = {

    # ── Tier 1: Institutional / Primary sources ──────────────────────

    # French government & public data
    "insee.fr":                     {"tier": "tier_1", "bias": "neutral"},
    "legifrance.gouv.fr":           {"tier": "tier_1", "bias": "neutral"},
    "data.gouv.fr":                 {"tier": "tier_1", "bias": "neutral"},
    "vie-publique.fr":              {"tier": "tier_1", "bias": "neutral"},
    "assemblee-nationale.fr":       {"tier": "tier_1", "bias": "neutral"},
    "senat.fr":                     {"tier": "tier_1", "bias": "neutral"},
    "service-public.fr":            {"tier": "tier_1", "bias": "neutral"},
    "education.gouv.fr":            {"tier": "tier_1", "bias": "neutral"},
    "economie.gouv.fr":             {"tier": "tier_1", "bias": "neutral"},
    "interieur.gouv.fr":            {"tier": "tier_1", "bias": "neutral"},
    "securite-sociale.fr":          {"tier": "tier_1", "bias": "neutral"},
    "ccomptes.fr":                  {"tier": "tier_1", "bias": "neutral"},
    "conseil-constitutionnel.fr":   {"tier": "tier_1", "bias": "neutral"},
    "has-sante.fr":                 {"tier": "tier_1", "bias": "neutral"},

    # European & international institutions
    "eurostat.ec.europa.eu":        {"tier": "tier_1", "bias": "neutral"},
    "europa.eu":                    {"tier": "tier_1", "bias": "neutral"},
    "who.int":                      {"tier": "tier_1", "bias": "neutral"},
    "worldbank.org":                {"tier": "tier_1", "bias": "neutral"},
    "imf.org":                      {"tier": "tier_1", "bias": "neutral"},
    "oecd.org":                     {"tier": "tier_1", "bias": "neutral"},
    "un.org":                       {"tier": "tier_1", "bias": "neutral"},
    "unicef.org":                   {"tier": "tier_1", "bias": "neutral"},
    "unhcr.org":                    {"tier": "tier_1", "bias": "neutral"},
    "ecb.europa.eu":                {"tier": "tier_1", "bias": "neutral"},

    # Academic & scientific
    "scholar.google.com":           {"tier": "tier_1", "bias": "neutral"},
    "pubmed.ncbi.nlm.nih.gov":     {"tier": "tier_1", "bias": "neutral"},
    "nature.com":                   {"tier": "tier_1", "bias": "neutral"},
    "sciencedirect.com":            {"tier": "tier_1", "bias": "neutral"},
    "thelancet.com":                {"tier": "tier_1", "bias": "neutral"},
    "cairn.info":                   {"tier": "tier_1", "bias": "neutral"},
    "persee.fr":                    {"tier": "tier_1", "bias": "neutral"},
    "hal.science":                  {"tier": "tier_1", "bias": "neutral"},
    "jstor.org":                    {"tier": "tier_1", "bias": "neutral"},

    # Fact-checking
    "factuel.afp.com":              {"tier": "tier_1", "bias": "neutral"},
    "lemonde.fr/les-decodeurs":     {"tier": "tier_1", "bias": "neutral"},
    "liberation.fr/checknews":      {"tier": "tier_1", "bias": "neutral"},

    # News agencies
    "afp.com":                      {"tier": "tier_1", "bias": "neutral"},
    "reuters.com":                  {"tier": "tier_1", "bias": "neutral"},
    "apnews.com":                   {"tier": "tier_1", "bias": "neutral"},

    # Encyclopedias
    "wikipedia.org":                {"tier": "tier_1", "bias": "neutral"},
    "britannica.com":               {"tier": "tier_1", "bias": "neutral"},

    # ── Tier 2: Quality media ────────────────────────────────────────

    # French quality press
    "lemonde.fr":                   {"tier": "tier_2", "bias": "center-left"},
    "lefigaro.fr":                  {"tier": "tier_2", "bias": "center-right"},
    "liberation.fr":                {"tier": "tier_2", "bias": "left"},
    "la-croix.com":                 {"tier": "tier_2", "bias": "center"},
    "lesechos.fr":                  {"tier": "tier_2", "bias": "center-right"},
    "latribune.fr":                 {"tier": "tier_2", "bias": "center-right"},
    "lopinion.fr":                  {"tier": "tier_2", "bias": "center-right"},
    "mediapart.fr":                 {"tier": "tier_2", "bias": "left"},
    "ouest-france.fr":              {"tier": "tier_2", "bias": "center"},
    "sudouest.fr":                  {"tier": "tier_2", "bias": "center"},
    "20minutes.fr":                 {"tier": "tier_2", "bias": "center"},
    "leparisien.fr":                {"tier": "tier_2", "bias": "center"},
    "francetvinfo.fr":              {"tier": "tier_2", "bias": "center"},
    "radiofrance.fr":               {"tier": "tier_2", "bias": "center"},
    "france24.com":                 {"tier": "tier_2", "bias": "center"},
    "rfi.fr":                       {"tier": "tier_2", "bias": "center"},
    "arte.tv":                      {"tier": "tier_2", "bias": "center"},
    "courrier-international.com":   {"tier": "tier_2", "bias": "center"},
    "alternatives-economiques.fr":  {"tier": "tier_2", "bias": "center-left"},
    "lobs.com":                     {"tier": "tier_2", "bias": "center-left"},
    "lexpress.fr":                  {"tier": "tier_2", "bias": "center"},
    "lepoint.fr":                   {"tier": "tier_2", "bias": "center-right"},
    "huffingtonpost.fr":            {"tier": "tier_2", "bias": "center-left"},

    # International quality press
    "theguardian.com":              {"tier": "tier_2", "bias": "center-left"},
    "nytimes.com":                  {"tier": "tier_2", "bias": "center-left"},
    "washingtonpost.com":           {"tier": "tier_2", "bias": "center-left"},
    "bbc.com":                      {"tier": "tier_2", "bias": "center"},
    "bbc.co.uk":                    {"tier": "tier_2", "bias": "center"},
    "economist.com":                {"tier": "tier_2", "bias": "center-right"},
    "ft.com":                       {"tier": "tier_2", "bias": "center-right"},
    "elpais.com":                   {"tier": "tier_2", "bias": "center-left"},
    "dw.com":                       {"tier": "tier_2", "bias": "center"},
    "aljazeera.com":                {"tier": "tier_2", "bias": "center"},

    # ── Biased: Usable but tagged ────────────────────────────────────

    # French — right / far-right
    "valeursactuelles.com":         {"tier": "biased", "bias": "right"},
    "cnews.fr":                     {"tier": "biased", "bias": "right"},
    "bvoltaire.fr":                 {"tier": "biased", "bias": "far-right"},
    "fdesouche.com":                {"tier": "biased", "bias": "far-right"},
    "lejdd.fr":                     {"tier": "biased", "bias": "right"},

    # French — left / far-left
    "regards.fr":                   {"tier": "biased", "bias": "left"},
    "humanite.fr":                  {"tier": "biased", "bias": "far-left"},
    "politis.fr":                   {"tier": "biased", "bias": "left"},
    "reporterre.net":               {"tier": "biased", "bias": "left"},
    "bastamag.net":                 {"tier": "biased", "bias": "left"},

    # Think tanks & advocacy (French)
    "ifrap.org":                    {"tier": "biased", "bias": "right"},
    "fondapol.org":                 {"tier": "biased", "bias": "center-right"},
    "jean-jaures.org":              {"tier": "biased", "bias": "center-left"},
    "terra-nova.fr":                {"tier": "biased", "bias": "center-left"},
    "institut-montaigne.org":       {"tier": "biased", "bias": "center-right"},

    # International — biased but notable
    "foxnews.com":                  {"tier": "biased", "bias": "right"},
    "breitbart.com":                {"tier": "biased", "bias": "far-right"},
    "jacobin.com":                  {"tier": "biased", "bias": "left"},
    "rt.com":                       {"tier": "biased", "bias": "state-controlled"}, #Détailler davantage en quoi consiste ce state-control? 
    "sputniknews.com":              {"tier": "biased", "bias": "state-controlled"},
}