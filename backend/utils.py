

def get_categories_for_type(claim_type: str) -> list[str]:
    """Return the relevant domain categories for a given claim type.
    Keeps domain lists focused to avoid dilution in web search."""

    CATEGORIES_BY_TYPE = {
        # Simple facts — fact-checkers, institutions, encyclopedias, news
        "factual": [
            "institutional", "fact_checking", "news_agency",
            "encyclopedia", "press_general", "audiovisual",
        ],
        # Numbers — need original data sources + economic press
        "statistical": [
            "institutional", "academic", "fact_checking",
            "news_agency", "press_economic", "press_general",
        ],
        # Attributed statements — need archives, transcripts, media coverage
        "quote": [
            "fact_checking", "news_agency",
            "press_general", "audiovisual",
        ],
        # Something happened — news coverage is king
        "event": [
            "fact_checking", "news_agency", "encyclopedia",
            "press_general", "press_economic", "press_investigate", "audiovisual",
        ],
        # Cause-effect — needs studies, expert analysis
        "causal": [
            "institutional", "academic", "encyclopedia",
            "press_general", "press_economic", "press_investigative", "think_tank"
        ],
        # X vs Y — needs data + specialized analysis
        "comparative": [
            "institutional", "academic", "encyclopedia",
            "press_economic", "press_general", "think_tank",
        ],
        # Future claims — needs expert track records, models
        "predictive": [
            "institutional", "academic",
            "press_economic", "press_general", "think_tank",
        ],
        # Opinions — needs diverse perspectives, not fact-checkers
        "opinion": [
            "press_general", "press_investigative",
            "press_economic", "audiovisual", "think_tank",
        ],
    }

    return CATEGORIES_BY_TYPE.get(claim_type, [
        "institutional", "fact_checking", "news_agency",
        "press_general", "audiovisual",
    ])
