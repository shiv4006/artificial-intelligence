"""Checks that your Groq key works by listing the models it can use."""

import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

key = os.getenv("GROQ_API_KEY")
if not key:
    raise SystemExit("GROQ_API_KEY is missing. Copy .env.example to .env and paste your key.")

client = OpenAI(api_key=key, base_url="https://api.groq.com/openai/v1")

if __name__ == "__main__":
    models = client.models.list()
    
    for model in sorted(models, key=lambda m: m.id):
        print(model.id)