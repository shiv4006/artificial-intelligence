from app.config import settings

# Groq prices, USD per 1M tokens: (input, output). Copy the real numbers from groq.com/pricing.
PRICES: dict[str, tuple[float, float]] = {
    "openai/gpt-oss-20b": (0.075, 0.3),
    "openai/gpt-oss-120b": (0.15, 0.60),
}

def model_prices() -> dict[str, tuple[float, float]]:
    """Every model the app offers: the Groq models above, plus local Ollama models at $0."""
    return PRICES | {model: (0.0, 0.0) for model in settings.ollama_models}

def cost_usd(model: str, prompt_tokens: int, completion_tokens: int) -> float | None:
    prices = model_prices().get(model)
    if prices is None:
        return None
    input_price, output_price = prices
    return (prompt_tokens * input_price + completion_tokens * output_price) / 1_000_000