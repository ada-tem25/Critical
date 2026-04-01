"""
Orchestrator — deterministic topological sort and claim analysis dispatch.
Not an LLM agent. Receives claims from the Decomposer, computes execution order,
and launches the Analysis Workflow (Layer 2) for each claim.
"""
import asyncio
from collections import defaultdict
from models import Claim, AnalyzedClaim


def _categorize_claims(claims: list[Claim]) -> tuple[list[Claim], list[Claim], list[Claim], list[Claim]]:
    """Splits claims into 4 categories: E, framing, A, and analyzable (B/C/D)."""
    e_claims = []
    framing_claims = []
    a_claims = []
    analyzable_claims = []

    for c in claims:
        if c.verifiability == "E":
            e_claims.append(c)
        elif c.role == "framing":
            framing_claims.append(c)
        elif c.verifiability == "A":
            a_claims.append(c)
        else:
            analyzable_claims.append(c)

    return e_claims, framing_claims, a_claims, analyzable_claims


def _compute_levels(claims: list[Claim]) -> list[list[Claim]]:
    """Computes topological execution levels from the DAG.
    Level 0 = leaf claims (not supported by any other claim).
    Level N = claims whose all children are in levels < N.
    Returns a list of levels, each level being a list of claims."""

    claim_by_id = {c.id: c for c in claims}
    all_ids = set(claim_by_id.keys())

    # Build children map: for each claim, which claims support it (its children)
    children_of = defaultdict(set)  # parent_id → {child_ids}
    for c in claims:
        for parent_id in c.supports:
            if parent_id in all_ids:
                children_of[parent_id].add(c.id)

    # Compute levels using iterative approach
    assigned = {}  # claim_id → level
    levels_dict = defaultdict(list)

    # Claims with no children in this set are level 0 (leaves)
    remaining = set(all_ids)

    level = 0
    while remaining:
        # Find claims whose all children (within remaining) are already assigned
        current_level = []
        for cid in remaining:
            children_in_set = children_of[cid] & all_ids
            if all(child_id in assigned for child_id in children_in_set):
                current_level.append(cid)

        if not current_level:
            # Cycle detected or orphan — assign remaining to current level to avoid infinite loop
            print(f"[ORCHESTRATOR] WARNING: cycle or orphan detected, forcing remaining claims to level {level}")
            current_level = list(remaining)

        for cid in current_level:
            assigned[cid] = level
            remaining.discard(cid)
            levels_dict[level].append(claim_by_id[cid])

        level += 1

    # Convert to ordered list of levels
    return [levels_dict[i] for i in range(len(levels_dict))]


def _merge_a_claims(a_claims: list[Claim]) -> Claim:
    """Merges all A claims into a single 'Common Knowledge Questions' claim."""
    questions = "\n".join(f"- [#{c.id}] {c.idea}" for c in a_claims)
    return Claim(
        id=-1,  # synthetic ID
        idea=f"Common Knowledge Questions:\n{questions}",
        verifiability="A",
        type="common_knowledge",
        role="supporting",
        supports=[],
    )


def _build_child_results(claim: Claim, results: dict[int, AnalyzedClaim], all_claims: list[Claim]) -> list[dict]:
    """Builds child_results for a claim: the analysis results of claims that support it."""
    # Find claims that support this one (children)
    child_ids = [c.id for c in all_claims if claim.id in c.supports]
    child_results = []
    for child_id in child_ids:
        if child_id in results:
            r = results[child_id]
            child_results.append({
                "claim_id": r.claim_id,
                "idea": r.idea,
                "summary": r.summary,
                "sources": [s.model_dump() for s in r.sources],
            })
    return child_results


async def _analyze_claim(claim: Claim, child_results: list[dict]) -> AnalyzedClaim:
    """Placeholder — calls the Analysis Workflow (Layer 2) for a single claim.
    TODO: replace with actual LangGraph workflow invocation."""
    print(f"    → Analyzing #{claim.id} [{claim.verifiability}/{claim.type}] with {len(child_results)} child results")
    return AnalyzedClaim(
        claim_id=claim.id,
        idea=claim.idea,
        role=claim.role,
        summary="[placeholder — analysis workflow not yet implemented]",
        analyzed=False,
        supports=claim.supports,
        sources=[],
    )


async def _analyze_common_knowledge(merged_claim: Claim, original_a_claims: list[Claim]) -> list[AnalyzedClaim]:
    """Placeholder — calls the Common Knowledge Teacher for all A claims in a single batch.
    TODO: replace with actual LLM call."""
    print(f"    → Common Knowledge Teacher: answering {len(original_a_claims)} questions")
    return [
        AnalyzedClaim(
            claim_id=c.id,
            idea=c.idea,
            role=c.role,
            summary="[placeholder — common knowledge teacher not yet implemented]",
            analyzed=False,
            supports=c.supports,
            sources=[],
        )
        for c in original_a_claims
    ]


async def orchestrate(claims: list[Claim]) -> list[AnalyzedClaim]:
    """Deterministic orchestrator. Categorizes claims, computes topological order,
    and dispatches analysis level by level."""

    print(f"\n{'='*50}")
    print(f"[ORCHESTRATOR] Received {len(claims)} claims")

    # 1. Categorize
    e_claims, framing_claims, a_claims, analyzable_claims = _categorize_claims(claims)

    print(f"[ORCHESTRATOR] Categories:")
    print(f"  E (skipped):  {len(e_claims)} — {[c.id for c in e_claims]}")
    print(f"  Framing:      {len(framing_claims)} — {[c.id for c in framing_claims]}")
    print(f"  A (common):   {len(a_claims)} — {[c.id for c in a_claims]}")
    print(f"  Analyzable:   {len(analyzable_claims)} — {[c.id for c in analyzable_claims]}")

    # 2. Passthrough claims (E + framing) → directly to output
    results: dict[int, AnalyzedClaim] = {}

    for c in e_claims + framing_claims:
        results[c.id] = AnalyzedClaim(
            claim_id=c.id,
            idea=c.idea,
            role=c.role,
            summary="",
            analyzed=False,
            supports=c.supports,
            sources=[],
        )

    # 3. Compute topological levels for analyzable claims
    levels = _compute_levels(analyzable_claims)

    print(f"[ORCHESTRATOR] Topological levels ({len(levels)}):")
    for i, level_claims in enumerate(levels):
        ids_str = ", ".join(f"#{c.id}[{c.verifiability}]" for c in level_claims)
        print(f"  Level {i}: {ids_str}")

    # 4. Add merged A claim to level 0 (if any A claims exist)
    merged_a = None
    if a_claims:
        merged_a = _merge_a_claims(a_claims)
        print(f"[ORCHESTRATOR] Merged {len(a_claims)} A claims into single batch for level 0")

    # 5. Execute level by level
    all_claims_for_lookup = claims  # original full list for child_results lookup

    for i, level_claims in enumerate(levels):
        print(f"\n[ORCHESTRATOR] === Executing level {i} ({len(level_claims)} claims) ===")

        tasks = []

        # At level 0, also launch the A batch
        if i == 0 and merged_a is not None:
            tasks.append(_analyze_common_knowledge(merged_a, a_claims))

        # Launch each analyzable claim at this level
        for c in level_claims:
            child_results = _build_child_results(c, results, all_claims_for_lookup)
            tasks.append(_analyze_claim(c, child_results))

        # Run all tasks for this level in parallel
        level_results = await asyncio.gather(*tasks)

        # Collect results
        for result in level_results:
            if isinstance(result, list):
                # Common Knowledge Teacher returns a list
                for r in result:
                    results[r.claim_id] = r
                    print(f"    ✓ #{r.claim_id} (common knowledge)")
            else:
                results[result.claim_id] = result
                print(f"    ✓ #{result.claim_id}")

    # 6. Assemble final output (preserve original claim order)
    output = [results[c.id] for c in claims if c.id in results]

    print(f"\n[ORCHESTRATOR] Done — {len(output)} analyzed claims returned")
    print(f"{'='*50}\n")

    return output
