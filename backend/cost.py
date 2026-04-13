"""
Cost calculation for LLM API calls and external APIs.
Pricing per token for each model, computed dynamically from agent metrics.
"""

# ANSI colors
_CYAN = "\033[36m"
_YELLOW = "\033[33m"
_GREEN = "\033[32m"
_DIM = "\033[2m"
_BOLD = "\033[1m"
_RESET = "\033[0m"

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

# External API pricing
BRAVE_COST_PER_QUERY = 0.005  # $0.005 per query


def _pass_cost(p: dict) -> float:
    """Computes the cost of a single pass (LLM or API) from its metrics."""

    # External API pass (e.g. Brave)
    if p.get("type") == "api":
        return p.get("cost", 0.0)

    # LLM pass
    model = p.get("model", "")
    prices = PRICING.get(model)
    if prices is None:
        print(f"{_YELLOW}[COST] WARNING: unknown model '{model}', cannot compute cost{_RESET}")
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

    anthropic_cost = 0.0
    brave_cost = 0.0
    brave_queries = 0

    print(f"{_YELLOW}[COST]{_RESET} Breakdown:")
    for agent_name, metrics in all_metrics.items():
        passes = metrics.get("passes", [])
        if not passes:
            continue

        for p in passes:
            cost = _pass_cost(p)
            label = p.get("agent", agent_name)

            if p.get("type") == "api":
                query_count = p.get("query_count", 0)
                brave_cost += cost
                brave_queries += query_count
                print(f"  {_DIM}{label}: ${cost:.4f} ({query_count} queries){_RESET}")
            else:
                anthropic_cost += cost
                cache_info = ""
                cache_creation = p.get("cache_creation_input_tokens", 0)
                cache_read = p.get("cache_read_input_tokens", 0)
                if cache_creation or cache_read:
                    cache_info = f" {_DIM}(cache write: {cache_creation}, cache read: {cache_read}){_RESET}"
                tokens_info = f" ({p.get('input_tokens', 0)}/{p.get('output_tokens', 0)})"
                print(f"  {label} [{p.get('model', '?')}]: ${cost:.4f}{tokens_info}{cache_info}")

    total_cost = anthropic_cost + brave_cost
    print(f"{_YELLOW}[COST]{_RESET} Subtotal Anthropic: ${anthropic_cost:.4f}")
    print(f"{_YELLOW}[COST]{_RESET} Subtotal Brave: ${brave_cost:.4f} ({brave_queries} queries)")
    print(f"{_YELLOW}[COST]{_RESET} {_BOLD}Total: ${total_cost:.4f}{_RESET}")
    return total_cost
