

fact_checking_queries_instructions="""

### B — Verifiable Claims
Claims that can be checked true or false against data and sources.
- factual: a precise factual assertion.
- statistical: a claim citing numbers, percentages, or data. For those, be vigilant about context, sample size, year, and methodology.
- quote: a statement attributed to someone. Search for speech archives, interviews, official records.
- event: a claim that something happened or is happening. Events are often mischaracterized — pay close attention to the difference between "voted", "proposed", "discussed", "considered".

### C — Partly Verifiable Claims
Claims where data and studies exist but may not be sufficient to settle the matter. They contain implicit assumptions or require reframing.
- causal: asserts a cause-and-effect relationship. Causality is rarely proven at 100%. You must assess whether there is a consensus or merely a correlation.
- comparative: a comparison that often hides implicit criteria. Example: "Coffee is more dangerous than alcohol" — dangerous in what sense? You must decide how to interpret the claim, and generate the appropriate query.
- predictive: an assertion about the future. Not verifiable by nature, but its credibility can be assessed based on underlying assumptions, who makes it, and what evidence supports it. Choose the underlying assumptions you think are correct, and generate the appropriate queries.

"""

opinion_analysis_queries_instructions="""

### Non-Verifiable Claims (D) | Opinion
No fact-checking is possible. These are value judgments or political opinions grounded in beliefs, sentiments, or personal values rather than objective facts.
- opinion: This needs contextualization, opposing viewpoints, and supporting data where relevant.

"""

interpretive_analysis_queries_instructions="""

### Non-Verifiable Claims (D) | interpretive


"""
