"""
Cost calculation for LLM API calls.
Pricing per token for each model, computed dynamically from agent metrics.
"""

# Prices per token (not per million tokens)
PRICING = {
    "claude-sonnet-4-5": {
        "input": 3.00 / 1_000_000,
        "output": 15.00 / 1_000_000,
        "cache_write": 3.75 / 1_000_000,
        "cache_read": 0.30 / 1_000_000,
    },
    "claude-sonnet-4-6": {
        "input": 3.00 / 1_000_000,
        "output": 15.00 / 1_000_000,
        "cache_write": 3.75 / 1_000_000,
        "cache_read": 0.30 / 1_000_000,
    },
    "claude-haiku-4-5": {
        "input": 1.00 / 1_000_000,
        "output": 5.00 / 1_000_000,
        "cache_write": 1.25 / 1_000_000,
        "cache_read": 0.10 / 1_000_000,
    },
}


def _pass_cost(p: dict) -> float:
    """Computes the cost of a single LLM pass from its metrics."""
    model = p.get("model", "")
    prices = PRICING.get(model)
    if prices is None:
        print(f"[COST] WARNING: unknown model '{model}', cannot compute cost")
        return 0.0

    input_tokens = p.get("input_tokens", 0)
    output_tokens = p.get("output_tokens", 0)
    cache_creation = p.get("cache_creation_input_tokens", 0)
    cache_read = p.get("cache_read_input_tokens", 0)

    # Non-cached input tokens = total input - cache_creation - cache_read
    regular_input = max(0, input_tokens - cache_creation - cache_read)

    cost = (
        regular_input * prices["input"]
        + output_tokens * prices["output"]
        + cache_creation * prices["cache_write"]
        + cache_read * prices["cache_read"]
    )
    return cost


def compute_cost(all_metrics: dict) -> float:
    """Computes and prints the cost breakdown for a pipeline run.
    all_metrics: dict keyed by agent name, each value has a 'passes' list.
    Returns total cost in $."""

    total_cost = 0.0

    print(f"[COST] Breakdown:")
    for agent_name, metrics in all_metrics.items():
        passes = metrics.get("passes", [])
        if not passes:
            continue

        agent_cost = 0.0
        for p in passes:
            cost = _pass_cost(p)
            agent_cost += cost
            cache_info = ""
            cache_creation = p.get("cache_creation_input_tokens", 0)
            cache_read = p.get("cache_read_input_tokens", 0)
            if cache_creation or cache_read:
                cache_info = f" (cache write: {cache_creation}, cache read: {cache_read})"
            label = p.get("agent", agent_name)
            tokens_info = f" ({p.get('input_tokens', 0)}/{p.get('output_tokens', 0)})"
            print(f"  {label} [{p.get('model', '?')}]: ${cost:.4f}{tokens_info}{cache_info}")
        total_cost += agent_cost

    print(f"[COST] Total: ${total_cost:.4f}")
    return total_cost
