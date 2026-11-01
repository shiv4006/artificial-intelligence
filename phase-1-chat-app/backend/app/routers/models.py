from fastapi import APIRouter

from app.llm import provider_for
from app.pricing import model_prices

router = APIRouter(tags=["models"])

@router.get("/models")
async def list_models():
    return [
        {
            "id": model,
            "provider": provider_for(model),
            "input_price_per_million": input_price,
            "output_price_per_million": output_price,
        }
        for model, (input_price, output_price) in model_prices().items()
    ]