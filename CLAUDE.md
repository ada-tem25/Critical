# Critical — Backend Architecture

## Overview

Critical is a fact-checking and critical analysis platform. The backend processes diverse input formats (articles, tweets, social media posts, video/audio transcripts, live speech) and produces journalistic-style fact-check articles.

The backend has two architectural layers:

1. **The Main Pipeline** — a high-level orchestration of components that manages the overall data flow. Some components are LLM agents, some are deterministic scripts. This is NOT a LangGraph graph — it's standard async orchestration (e.g. Python asyncio, task queues, or simple sequential calls).

2. **The Analysis Workflow** — a LangGraph graph with nodes, edges, and conditional edges. This is the core fact-checking/analysis engine, called once per claim by the Orchestrator. Every node inside this workflow is an LLM agent.

---

## Layer 1: Main Pipeline

```
User Input (link, text, media, audio...)
│
▼
┌──────────────┐
│  NORMALIZER  │  (deterministic — not an LLM agent)
│              │  Scrapes/transcribes/extracts content.
│              │  Produces a standardized text object.
└──────┬───────┘
       │
       │  Sends its output in parallel to 3 recipients:
       │
       ├──────────────────────────────────────────────────────► WRITER (waits for all other inputs)
       │
       ├───────────────────────► RHETORIC DETECTOR (LLM agent)
       │                         Runs on the full text in parallel
       │                         with the Decomposer + analysis chain.
       │                         Detects manipulative rhetorical devices
       │                         from a bank of ~20 known biases.
       │                         Output: list of detected rhetorics
       │                                 with passage + explanation.
       │                         ───────────────────────────────► WRITER
       │
       ▼
┌──────────────┐
│  DECOMPOSER  │  (LLM agent)
│              │  Reads the full text, and decomposes it into multiple claims (see prompts.py for its full instructions). 
│              │  Extracts a DAG of claims (see Claim Format below).
└──────┬───────┘
       │
       ▼
┌───────────────┐
│ ORCHESTRATOR  │  (deterministic — not an LLM agent)
│               │  1. Computes execution levels via topological sort.
│               │  2. Batches all verifiability-A claims into one LLM call.
│               │  3. Launches analysis per level, injecting child_results
│               │     into downstream claims.
│               │  4. Collects all results into the fully analyzed DAG.
└──────┬────────┘
       │
       ▼
┌──────────────┐
│    WRITER    │  (LLM agent)
│              │  Receives 3 inputs:
│              │  - Original text (from Normalizer)
│              │  - Fully analyzed DAG (from Orchestrator)
│              │  - Detected rhetorics (from Rhetoric Detector)
│              │  Produces the final journalistic article.
│              │  Decides the displayed verdict (VRAI/FAUX/INCERTAIN/TROMPEUR...).
└──────────────┘
```

---

## Layer 2: Analysis Workflow (LangGraph)

This is a LangGraph graph called by the Orchestrator **once per claim**. The Orchestrator passes in the claim object and its child_results (results from previously analyzed child claims).

### Entry routing (conditional edge based on verifiability)

```
Input: { claim, child_results }
│
├─ Verifiability A ──► Common Knowledge Teacher ──► END
├─ Verifiability B or C ──► Generate Queries L2 ──► (level 2 branch)
├─ Verifiability D, type opinion ──► Generate Queries L3 ──► (level 3 branch)
├─ Verifiability D, type interpretive ──► Generate Queries L3 ──► (level 3 interpretive branch)
└─ Verifiability null, role framing ──► skip (no analysis, passed directly to Writer)
```

### Level 2 branch (fact-checking)

```
Generate Queries L2
│   Generates 1-3 search queries to verify the author's claims.
│   Uses claim type to adapt query strategy.
│   Receives child_results in its prompt context.
│
▼
Web Research (unbiased)
│   Executes queries. Only retains high-reliability sources
│   (news agencies, recognized media, institutions, scientific publications).
│
▼
Sources Evaluator
│   Evaluates if sources are sufficient (quantity, convergence, circularity).
│
├─ Insufficient ──► Web Research (biased)
│                   │   Widens to lower-reliability or biased sources.
│                   │   Explicitly tags the bias of each source.
│                   │
│                   ▼
│                   Sources Evaluator (second pass) ──► Synthesizer
│
└─ Sufficient ──► Synthesizer
                  │   Evaluates the solidity of the AUTHOR'S argument (not the topic itself).
                  │   Receives child_results in its prompt context.
                  │   Outputs: summary + needs_level3 boolean + sources.
                  │
                  ├─ needs_level3 = false ──► END
                  └─ needs_level3 = true  ──► (level 3 branch)
```

### Level 3 branch — D/opinion (critical analysis)

```
Generate Queries L3
│   Generates queries oriented toward critical analysis:
│   political positions, counterarguments, alternative studies/data.
│   Receives level 2 verdict (if exists) + child_results.
│
▼
Web Research L3
│   Searches for political context, opposing viewpoints, complementary data.
│
▼
Critical Analyst
│   Produces the level 3 analysis: political context, main counterarguments,
│   key data illuminating the debate beyond the author's article.
│
▼
END
```

### Level 3 branch — D/interpretive (intellectual contextualization)

```
Generate Queries L3 (interpretive mode)
│   Generates queries oriented toward:
│   - Academic works, books, essays that address the same phenomenon
│   - Cultural studies, political science, sociology analyses
│   - Does NOT search for "counter-arguments" or "political positions"
│     (unlike D/opinion mode)
│
▼
Web Research L3
│   Searches for books, academic papers, longform essays.
│   For each result, extracts: title, author, year, and a short summary
│   of how it relates to the author's claim.
│
▼
Sources Evaluator (interpretive)
│   Evaluates whether substantive academic/intellectual work was found.
│   Threshold: at least 1 serious source (book, peer-reviewed paper,
│   recognized essayist) that directly addresses the phenomenon described
│   in the claim.
│
├─ Found substantive sources ──► END (analyzed: true)
│   Output includes summary + sources + recommended_reading
│
└─ No substantive sources ──► END (analyzed: false)
    Output includes recommended_reading (if any books were found
    even tangentially) but summary is empty and analyzed is false.
    The Writer will handle this claim as "author's interpretation,
    presented as such."
```

Note: unlike the D/opinion branch, there is NO Critical Analyst step. The Sources Evaluator terminates directly. The Writer integrates the results (found books, or absence of results) into the final article.

---

## Main Pipeline Formats

### Normalized Input (output of Normalizer, input to Decomposer)

```json
{
  "text": "",
  "source_type": "recording | instagram | text ...",
  "source_url": "",
  "author": "",
  "date": "",
}
```

### Claim (output of Decomposer, input to Orchestrator)

```json
{
  "id": 1,
  "idea": "Single sentence summarizing the claim",
  "verifiability": "A | B | C | D | E | None",
  "type": "factual_common_knowledge | factual | statistical | quote | event | causal | comparative | predictive | opinion | None",
  "role": "thesis | supporting | counterargument | framing",
  "supports": [2, 3]
}
```

### Claim input to Analysis Workflow (passed by Orchestrator)

```json
{
  "id": 2,
  "idea": "...",
  "verifiability": "C",
  "type": "causal",
  "role": "supporting",
  "supports": [1],
  "child_results": [
    {
      "claim_id": 3,
      "idea": "...",
      "summary": "...",
      "sources": [
        {"url": "...", "title": "...", "date": "...", "anchor": "...", "bias": "neutral"}
      ]
    }
  ]
}
```

### Claim output from Analysis Workflow (returned to Orchestrator)

Standard (L2 only):

```json
{
  "claim_id": 2,
  "idea": "...",
  "role": "",
  "summary": "Short analysis of the author's argument solidity for this claim.",
  "analyzed": true,
  "supports": [],
  "sources": [
    {"url": "...", "title": "...", "date": "...", "anchor": "...", "bias": "neutral"}
  ]
}
```

When level 3 was triggered (D/opinion):

```json
{
  "claim_id": 2,
  "idea": "...",
  "role": "",
  "summary": "Level 2 summary...",
  "analyzed": true,
  "supports": [],
  "analysis": "Level 3 analysis...",
  "sources": [
    {"url": "...", "title": "...", "date": "...", "anchor": "...", "bias": "neutral"}
  ]
}
```

D/interpretive (with or without substantive sources):

```json
{
  "claim_id": 2,
  "idea": "...",
  "role": "",
  "summary": "",
  "analyzed": false,
  "supports": [],
  "recommended_reading": [
    {"title": "La Société du Spectacle", "author": "Guy Debord", "year": 1967},
    {"title": "No Logo", "author": "Naomi Klein", "year": 1999}
  ],
  "sources": []
}
```

### Input to Writer (origin text + rhetorics + fully analyzed DAG)

```json
{
  "text": "",
  "source_type": "recording | instagram | text ...",
  "source_url": "",
  "author": "",
  "date": "",
  "rhetorics": [{
    "type": "false correlation | straw man | false dillema | framing ...",
    "passage": "The passage in the origin text where this rhetoric took place.",
    "explanation": "How exactly was this rhetoric used in the passage.",
  }],
  "analyzed_claims": [{
    "id": 1,
    "idea": "...",
    "role": "",
    "summary": "Level 2 summary...",
    "analyzed": true,
    "supports": [],
    "analysis": "Level 3 analysis...",
    "recommended_reading": [],
    "sources": [
      {"url": "...", "title": "...", "date": "...", "anchor": "...", "bias": "neutral"}
    ]
  }]
}
```

---

## Analysis Workflow Agent Roles Summaries

**Common Knowledge Teacher** — Responds directly and briefly to verifiability-A claims without any web search. Can handle multiple A claims in a single batched call.

**Generate Queries (L2)** — Generates 1-3 search queries aimed at verifying the evidence the author advances for this specific claim. Adapts queries based on claim type (statistical → find the source of the number, quote → search speech archives, etc.) and child_results if they exist.

**Generate Queries (L3 — opinion mode)** — Generates queries oriented toward critical analysis: political party positions, existing counterarguments, studies or data illuminating the debate from other angles. Takes into account the level 2 verdict and child_results to target what deserves deeper exploration.

**Generate Queries (L3 — interpretive mode)** — Generates queries oriented toward academic and intellectual contextualization: books, essays, cultural studies, political science or sociology analyses that address the same phenomenon. Does NOT search for counter-arguments or political positions.

**Web Research (unbiased)** — Executes queries and only retains high-reliability sources: news agencies, recognized media, institutions, scientific publications. Returns for each source the URL, reliability tier, and a summary of relevant content.

**Web Research (biased)** — Executes the same queries but widens the spectrum to less reliable or politically oriented sources. Explicitly tags the bias of each source. Only activated if the Sources Evaluator judges that the first search did not provide enough information.

**Sources Evaluator** — Evaluates whether the sources found by Web Research are sufficient to conclude on the claim, checking quantity, convergence, and source circularity. Redirects to Web Research (biased) if information is insufficient, or to the Synthesizer if it is.

**Synthesizer** — Produces an analysis of the solidity of the author's argument for this claim, based on the sources found and the child_results. Determines via the `needs_level3` field whether the claim requires deeper critical analysis (diverging sources, gray zone topic).

**Critical Analyst** — Produces the level 3 analysis: political context, main counterarguments, complementary data illuminating the debate. Its role is no longer to evaluate the article but to broaden the perspective so the reader understands the stakes beyond what the author wrote. Only used in the D/opinion branch.

**Sources Evaluator (interpretive)** — Evaluates whether substantive academic/intellectual work was found for a D/interpretive claim. Threshold: at least 1 serious source (book, peer-reviewed paper, recognized essayist) that directly addresses the phenomenon. Outputs `analyzed: true/false` and `recommended_reading`.

---

## Key Architectural Decisions

- **Level 2 evaluates the article.** The Synthesizer judges whether the author's evidence supports their argument. It does not independently validate the claim's subject matter.
- **Level 3 evaluates the subject.** The Critical Analyst broadens the perspective beyond what the author wrote.
- **No internal verdict field.** The analysis workflow outputs `needs_level3` (boolean) and `summary` (rich text). The Writer decides the displayed verdict.
- **No confidence field.** It served no routing decision and would give a false sense of precision.
- **No source_text field in claims.** The Writer receives the full original text directly from the Normalizer and can locate relevant passages itself.
- **The Orchestrator is deterministic.** It computes topological execution order and injects child_results into downstream prompts. It is not an LLM agent. It skips framing claims (passes them directly to the Writer without analysis) and routes D claims based on their type (opinion → L3 opinion branch, interpretive → L3 interpretive branch).
- **The Rhetoric Detector runs in parallel** with the entire Decomposer → Orchestrator → Analysis chain. It does not add latency to the pipeline.
- **Framing is a Decomposer role**, not a rhetorical device. The Decomposer identifies framing claims (null verifiability, null type) which the Orchestrator passes through to the Writer without analysis. The Rhetoric Detector handles manipulative rhetorical devices (straw man, false dilemma, etc.) separately.
- **The `analyzed` flag** indicates whether the analysis workflow found substantive material to analyze a claim. For D/interpretive claims, `analyzed: false` means the Writer should present the claim as the author's interpretation without endorsing or refuting it. `recommended_reading` provides academic/intellectual references when available.

### Writer behavior for special claim types

- **`analyzed: false` (D/interpretive, no substantive sources):** Present the interpretation as the author's own. Example: "L'auteur soutient que [claim]. Cette lecture n'a pas pu être vérifiée par notre analyse." If `recommended_reading` has entries, mention them: "Pour approfondir, on pourra consulter [titles]."
- **`analyzed: true` (D/interpretive, substantive sources found):** Present the author's interpretation, then mention convergent or divergent academic works found. No verdict on these claims — present as context.
- **Framing claims (role: framing):** Mention as the author's ideological framing without any attempt at verification. Example: "L'auteur s'inscrit dans une lecture où [framing claim]."
- **`recommended_reading`:** When present, mention as suggested reading for readers who want to explore further.