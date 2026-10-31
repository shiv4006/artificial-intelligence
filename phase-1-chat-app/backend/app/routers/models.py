from fastapi import APIRouter

from app.pricing import PRICES

router = APIRouter(tags=["models"])

@router.get("/models")
async def list_models():
    return [
        {"id": model, "input_price_per_million": input_price, "output_price_per_million": output_price}
        for model, (input_price, output_price) in PRICES.items()
    ]