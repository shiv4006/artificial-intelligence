# USD per 1M tokens: (input, output). Copy the real numbers from groq.com/pricing.
PRICES: dict[str, tuple[float, float]] = {
    "openai/gpt-oss-20b": (0.075, 0.3),
    "openai/gpt-oss-120b": (0.15, 0.60),
}

def cost_usd(model: str, prompt_tokens: int, completion_tokens: int) -> float | None:
    prices = PRICES.get(model)
    if prices is None:
        return None
    input_price, output_price = prices
    return (prompt_tokens * input_price + completion_tokens * output_price) / 1_000_000