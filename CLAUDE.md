# Critical — Backend Architecture

## Overview

Critical is a fact-checking and critical analysis platform. The backend processes diverse input formats (articles, tweets, social media posts, video/audio transcripts, live speech) and produces journalistic-style fact-check articles.

The backend has two architectural layers:

1. **The Main Pipeline** — a high-level orchestration of components that manages the overall data flow. Some components are LLM agents, some are deterministic scripts. This is NOT a LangGraph graph — it's standard async orchestration (e.g. Python asyncio, task queues, or simple sequential calls).

2. **The Analysis Workflow** — a LangGraph graph with nodes, edges, and conditional edges. This is the core analysis engine, called once per claim by the Orchestrator.

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
│               │  2. Passes through E, A, and framing claims directly to Writer.
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

All three analysis levels (L2, L3, L4) share the same research loop structure:

```
Generate Queries → Brave Search → Rank & Select → Fetch & Extract → Reflection → Synthesizer
                   ▲                                                      │
                   └──────────── follow-up queries (if insufficient) ─────┘
```

### Entry routing (conditional edge based on verifiability)

```
Input: { claim, child_results }
│
├─ Verifiability A ──► passthrough (handled directly by Writer)
├─ Verifiability B or C ──► L2 (fact-checking)
├─ Verifiability D, type opinion ──► L3 directly (political/critical analysis)
├─ Verifiability D, type interpretive ──► L4 directly (intellectual contextualization)
└─ Verifiability null, role framing ──► skip (no analysis, passed directly to Writer)
```

### Escalation paths

- **L2 → L3:** When the L2 Synthesizer sets `needs_next_level = true` (only for verifiability C claims; B claims cannot escalate).
- **L3 → L4:** When the L3 Synthesizer sets `needs_next_level = true`.
- **D/opinion → L3 directly** (skips L2).
- **D/interpretive → L4 directly** (skips L2 and L3).

### Level 2 — Fact-Checking

```
Generate Queries L2
│   Generates 1-3 search queries to verify the author's claims.
│   Uses claim type to adapt query strategy. For example, for statistics, we'll also recontextualize it,
│   find if there is a better one to settle this matter etc.
│   If the claim type is inconsistent with the set rules, do a basic search.
│   Receives child_results in its prompt context.
│
▼
Brave Search + Domain Tagger (deterministic, no LLM)
│   Executes queries via Brave Search API.
│   Deduplicates by URL, tags each result by checking domain against
│   a curated registry (~400+ sources) with reliability, category,
│   region, and bias fields.
│
▼
Rank & Select (deterministic, no LLM)
│   Scores sources: reliability_weight × 0.6 + snippet_relevance × 0.4.
│   Prioritizes tiered (non-unknown) sources, fills remaining slots
│   with best unknowns.
│
▼
Fetch & Extract (deterministic, no LLM)
│   Fetches each page with a 4-level cascade:
│   1. httpx + Trafilatura (direct fetch + content extraction)
│   2. Jina Reader (r.jina.ai fallback)
│   3. Google Cache (webcache.googleusercontent.com fallback)
│   4. Fail → URL blacklisted, Brave snippet discarded
│
▼
Reflection (LLM agent — Haiku)
│   Evaluates if enough material was gathered.
│   If insufficient, generates 1-2 follow-up queries for another loop.
│   Max loops: 1 (eco) / 2 (perf).
│
▼
Synthesizer L2
│   Evaluates the solidity of the AUTHOR'S argument (not the topic itself).
│   Receives child_results + all tagged sources in its prompt context.
│   Weighs sources reliability.
│   Outputs: summary + needs_next_level boolean + sources.
│
├─ needs_next_level = false ──► END
└─ needs_next_level = true (C only) ──► L3
```

### Level 3 — Political / Critical Analysis

Same research loop structure as L2 (Generate Queries → Brave → Rank → Fetch → Reflection → Synthesizer).

Entered either directly (D/opinion) or via L2 escalation (C with needs_next_level).

```
Generate Queries L3
│   Generates queries oriented toward critical analysis:
│   political positions, counterarguments, alternative studies/data.
│   Receives level 2 summary (if exists) + child_results.
│
▼
[Research loop: Brave Search → Rank & Select → Fetch & Extract → Reflection]
│   Max loops: 1 (eco) / 2 (perf) for D/opinion entering directly.
│   No loops (just initial pass) for C claims escalated from L2.
│
▼
Synthesizer L3
│   Produces the L3 analysis: political context, main counterarguments,
│   complementary data illuminating the debate beyond the author's article.
│   Merges L2 + L3 cited sources.
│   Output field: `analysis` (stored in AnalyzedClaim.analysis).
│
├─ needs_next_level = false ──► END
└─ needs_next_level = true ──► L4
```

### Level 4 — Intellectual Contextualization

Same research loop structure as L2/L3.

Entered either directly (D/interpretive) or via L3 escalation.

```
Generate Queries L4
│   Generates queries oriented toward:
│   - Academic works, books, essays that address the same phenomenon
│   - Cultural studies, political science, sociology analyses
│   - Does NOT search for "counter-arguments" or "political positions"
│
▼
[Research loop: Brave Search → Rank & Select → Fetch & Extract → Reflection]
│   Max loops: 1 (eco) / 2 (perf) for D/interpretive entering directly.
│   No loops (just initial pass) for D/opinion escalated from L3.
│
▼
Synthesizer L4
│   Evaluates whether substantive academic/intellectual work was found.
│   Output field: `perspective` (stored in AnalyzedClaim.perspective).
│   Also outputs `recommended_reading` (list of academic references with id, url, title, author, year).
│   Sets `analyzed = true` if substantive sources found, `false` otherwise (The Writer will handle this claim as "author's interpretation,presented as such.").
│
▼
END
```

---

## Main Pipeline Formats

### Normalized Input (output of Normalizer, input to Decomposer)

```json
{
  "text": "",
  "source_type": "recording | instagram | text ...",
  "source_url": "",
  "author": "",
  "date": ""
}
```

### Claim (output of Decomposer, input to Orchestrator)

```json
{
  "id": 1,
  "idea": "Single sentence summarizing the claim",
  "verifiability": "A | B | C | D | E | None",
  "type": "factual_common_knowledge | factual | statistical | quote | event | causal | comparative | predictive | opinion | interpretive | None",
  "role": "thesis | supporting | counterargument | framing",
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

### AnalyzedClaim (output from Analysis Workflow, returned to Orchestrator)

L2 only (B/C, no escalation):

```json
{
  "claim_id": 2,
  "idea": "...",
  "role": "",
  "summary": "L2 analysis of the author's argument solidity.",
  "analyzed": true,
  "supports": [],
  "sources": [
    {"url": "...", "title": "...", "date": "...", "anchor": "...", "bias": "neutral"}
  ],
  "analysis": null,
  "perspective": "",
  "recommended_reading": []
}
```

L2 + L3 (C escalated, or D/opinion):

```json
{
  "claim_id": 2,
  "idea": "...",
  "role": "",
  "summary": "L2 summary...",
  "analyzed": true,
  "supports": [],
  "sources": [...],
  "analysis": "L3 political/critical analysis...",
  "perspective": "",
  "recommended_reading": []
}
```

L4 (D/interpretive entering directly, or escalated from L3):

```json
{
  "claim_id": 2,
  "idea": "...",
  "role": "",
  "summary": "",
  "analyzed": true,
  "supports": [],
  "sources": [...],
  "analysis": null,
  "perspective": "L4 intellectual contextualization...",
  "recommended_reading": [
    {"id": 1, "url": "...", "title": "La Société du Spectacle", "author": "Guy Debord", "year": 1967}
  ]
}
```

Note: `analyzed` is `false` when L4 found no substantive academic sources. In that case `perspective` is empty and `recommended_reading` may still contain tangentially related references.

### Input to Writer (origin text + rhetorics + fully analyzed DAG)

```json
{
  "source": {
    "text": "full original text...",
    "type": "recording | instagram | text",
    "url": "...",
    "author": "...",
    "date": "YYYY-MM-DD"
  },
  "analyzed_claims": [
    {
      "id": 1,
      "idea": "...",
      "role": "thesis | supporting | counterargument | framing",
      "summary": "L2 analysis...",
      "analyzed": true,
      "supports": [],
      "sources": [
        {"url": "...", "title": "...", "date": "...", "anchor": "...", "bias": "...", "tier": "..."}
      ],
      "analysis": "L3 analysis... (null if no L3)",
      "perspective": "L4 contextualization... (empty if no L4)",
      "recommended_reading": [
        {"id": 1, "url": "...", "title": "...", "author": "...", "year": 1967}
      ]
    }
  ],
  "rhetorics": [
    {
      "type": "false correlation | straw man | false dilemma | framing ...",
      "passage": "The passage in the origin text where this rhetoric took place.",
      "explanation": "How exactly was this rhetoric used in the passage."
    }
  ]
}
```

### Output from Writer (structured, returned to main_pipeline)

```json
{
  "title": "Article title",
  "subtitle": "Optional subtitle (or null)",
  "verdict": "VRAI | FAUX | INCERTAIN | TROMPEUR | ...",
  "summary": "Short summary (2-3 sentences)",
  "article": "Full journalistic fact-check article...",
  "format": "short | long",
  "sources": [
    {"id": 1, "url": "...", "title": "...", "date": "...", "bias": "..."}
  ],
  "quote": {"text": "...", "author": "...", "date": "..."} or null,
  "source_url": "...",
  "date": "YYYY-MM-DD"
}
```

`format` is determined post-LLM: `"short"` if article < 2000 chars, `"long"` otherwise.

---

## Analysis Workflow Agent Roles Summaries

**Generate Queries (L2)** — Generates 1-3 search queries aimed at verifying the evidence the author advances for this specific claim. Adapts queries based on claim type (statistical → find the source of the number, quote → search speech archives, etc.) and child_results if they exist.

**Generate Queries (L3)** — Generates queries oriented toward critical analysis: political party positions, existing counterarguments, studies or data illuminating the debate from other angles. Takes into account the level 2 summary and child_results to target what deserves deeper exploration.

**Generate Queries (L4)** — Generates queries oriented toward academic and intellectual contextualization: books, essays, cultural studies, political science or sociology analyses that address the same phenomenon. Does NOT search for counter-arguments or political positions.

**Brave Search + Domain Tagger** — Deterministic step (no LLM). Executes queries via Brave Search API, deduplicates results by URL, and tags each source via a curated domain registry (~400+ sources) with reliability (reference/established/oriented/unknown), category, region, and bias fields.

**Rank & Select** — Deterministic step (no LLM). Scores sources by reliability_weight × 0.6 + snippet_relevance × 0.4. Prioritizes tiered sources, fills with best unknowns. Selects 4-6 per iteration. Excludes previously failed URLs.

**Fetch & Extract** — Deterministic step (no LLM). 4-level fetch cascade: (1) httpx + Trafilatura, (2) Jina Reader, (3) Google Cache, (4) fail — URL blacklisted, snippet discarded. Boilerplate detection catches JS-only pages and nav noise. Failed sources are NOT forwarded to agents.

**Reflection** — LLM agent (Haiku). Used at all levels (L2, L3, L4). Evaluates if extracted passages are sufficient for synthesis. If not, generates 1-2 follow-up queries for another research loop.

**Synthesizer L2** — Evaluates the solidity of the author's argument for this claim, based on the tagged sources and the child_results. Weighs source reliability based on tier/bias tags. Determines via `needs_next_level` whether the claim requires deeper critical analysis (only C claims can escalate; B claims cannot).

**Synthesizer L3** — Produces the L3 analysis: political context, main counterarguments, complementary data illuminating the debate. Its role is no longer to evaluate the article but to broaden the perspective so the reader understands the stakes beyond what the author wrote. Determines via `needs_next_level` whether intellectual contextualization (L4) is needed.

**Synthesizer L4** — Produces the L4 intellectual contextualization. Evaluates whether substantive academic/intellectual work was found. Outputs `perspective` (the contextualization text), `recommended_reading` (academic references with id, url, title, author, year), and `analyzed: true/false`.

**Writer** — Final LLM agent. Receives original text, fully analyzed DAG, and detected rhetorics. Produces a structured output: title, subtitle, verdict, summary, article, sources (numbered), and optional quote. The `format` field ("short"/"long") is determined post-LLM based on article length.

---

## Modes: Eco vs Performance

The pipeline supports two execution modes, selected by the user via the frontend toggle:

- **Eco (default)** — Each LLM agent runs a single pass. Faster and cheaper.
- **Performance** — Adds a correction/review second pass to multi-pass agents. Slower and more expensive, but higher quality.

Current effects of the mode:

| Agent | Eco | Performance |
|-------|-----|-------------|
| **Decomposer** | Sonnet extracts claims (1 pass) | + Haiku Corrector reviews and corrects the claim DAG (2 passes) |
| **Rhetoric Detector** | Sonnet detects rhetorics (1 pass) | + Sonnet Reviewer adversarially filters false positives (2 passes) |
| **Research Loops (L2/L3/L4)** | Reflection allows 1 additional loop | Up to 2 additional loops |

Loop budgets also depend on entry path:
- **Direct entry** (B/C → L2, D/opinion → L3, D/interpretive → L4): full loop budget (1 eco / 2 perf).
- **Escalated entry** (C → L3 via needs_next_level, D/opinion → L4 via needs_next_level): no loops, just initial search pass.

---

## Key Architectural Decisions

- **Level 2 evaluates the article.** The Synthesizer judges whether the author's evidence supports their argument. It does not independently validate the claim's subject matter.
- **Level 3 evaluates the subject.** The L3 Synthesizer broadens the perspective beyond what the author wrote — political context, counterarguments, complementary data.
- **Level 4 contextualizes intellectually.** The L4 Synthesizer finds academic works, books, and essays that address the same phenomenon. No verdict — presents context.
- **Three distinct output fields per level.** `summary` (L2), `analysis` (L3), `perspective` (L4) — never overwritten across levels, all forwarded to the Writer.
- **No internal verdict field.** The analysis workflow outputs `needs_next_level` (boolean) and level-specific text. The Writer decides the displayed verdict.
- **No confidence field.** It served no routing decision and would give a false sense of precision.
- **No source_text field in claims.** The Writer receives the full original text directly from the Normalizer and can locate relevant passages itself.
- **The Orchestrator is deterministic.** It computes topological execution order and injects child_results into downstream prompts. It is not an LLM agent. It skips framing claims (passes them directly to the Writer without analysis) and routes D claims based on their type (opinion → L3, interpretive → L4).
- **The Rhetoric Detector runs in parallel** with the entire Decomposer → Orchestrator → Analysis chain. It does not add latency to the pipeline.
- **Framing is a Decomposer role**, not a rhetorical device. The Decomposer identifies framing claims (null verifiability, null type) which the Orchestrator passes through to the Writer without analysis. The Rhetoric Detector handles manipulative rhetorical devices (straw man, false dilemma, etc.) separately.
- **The `analyzed` flag** indicates whether the analysis workflow found substantive material to analyze a claim. For D/interpretive claims, `analyzed: false` means the Writer should present the claim as the author's interpretation without endorsing or refuting it. `recommended_reading` provides academic/intellectual references when available.
- **Escalation is one-way and conditional.** B claims never escalate. C claims can escalate L2→L3. D/opinion can escalate L3→L4. D/interpretive enters L4 directly. Escalated entries get no reflection loops (just initial search pass).

### Writer behavior for special claim types

- **`analyzed: false` (D/interpretive, no substantive sources):** Present the interpretation as the author's own. Example: "L'auteur soutient que [claim]. Cette lecture n'a pas pu être vérifiée par notre analyse." If `recommended_reading` has entries, mention them: "Pour approfondir, on pourra consulter [titles]."
- **`analyzed: true` (D/interpretive, substantive sources found):** Present the author's interpretation, then mention convergent or divergent academic works found. No verdict on these claims — present as context.
- **Framing claims (role: framing):** Mention as the author's ideological framing without any attempt at verification. Example: "L'auteur s'inscrit dans une lecture où [framing claim]."
- **`recommended_reading`:** When present, mention as suggested reading for readers who want to explore further.