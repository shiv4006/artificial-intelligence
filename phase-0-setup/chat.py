import time
import argparse
from openai import OpenAI
from check_groq import client as groq_client

# USD per 1M tokens: (input, output). Replace the zeros with the prices from groq.com/pricing
PRICES = {
    "openai/gpt-oss-20b": (0.0, 0.0),
    "openai/gpt-oss-120b": (0.0, 0.0),
}

DEFAULT_MODELS = {
    "groq": "openai/gpt-oss-20b",
    "ollama": "llama3.1:8b"
}

parser = argparse.ArgumentParser(description="Terminal Chatbot")
parser.add_argument("--provider", choices=["groq", "ollama"], default="groq")
parser.add_argument("--model", help="defaults to a model that fits the provider")
parser.add_argument("--system", default="You are a helpful assistant. Answer in plain text.")
parser.add_argument("--reasoning_effort", choices=["low", "medium", "high"], default="low")
args = parser.parse_args()

model = args.model or DEFAULT_MODELS[args.provider]

if args.provider == "ollama":
    client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
else:
    client = groq_client

extra = {}
if model.startswith("openai/gpt-oss"):
    extra["reasoning_effort"] = args.reasoning_effort

messages = [
    { "role": "system", "content": args.system }
]

def print_usage(usage):
    if usage is None:
        print("(no usage data returned)")
        return
    
    line = f"Prompt: {usage.prompt_tokens} | Completion: {usage.completion_tokens}"

    details = usage.completion_tokens_details
    if details and details.reasoning_tokens:
        line += f" (reasoning {details.reasoning_tokens})"
    
    prices = PRICES.get(model)
    if prices:
        input_price, output_price = prices
        cost = (usage.prompt_tokens * input_price + usage.completion_tokens * output_price) / 1_000_000
        line += f" | Cost: ${cost:.6f}"
    else:
        line += " | Cost: local, $0"
    
    print(line)
    
    
def chatbot():
    print("Start: ", time.perf_counter())
    stream = client.chat.completions.create(
        model=model,
        messages=messages,
        stream=True,
        stream_options={"include_usage": True},
        **extra
    )
    print("First Token: ", time.perf_counter())

    reply = ""
    usage = None
    for chunk in stream:
        if chunk.usage:
            usage = chunk.usage
        
        if not chunk.choices:
            continue
        
        # print("Chunk: ", chunk)
        text = chunk.choices[0].delta.content
        if text:
            print(text, end="", flush=True)
            reply += text
            
    print()
    assistant_message = {
        "role": "assistant",
        "content": reply
    }
    
    messages.append(assistant_message)
    print_usage(usage)
    print("End: ", time.perf_counter())
    
# Entry Point
while True:
    try:
        user_input = input("\nYou: ")
    except (KeyboardInterrupt, EOFError):
        break
    
    if (user_input == "-1"):
        break
    if not user_input.strip():
        continue
    
    user_message = {
        "role": "user",
        "content": user_input
    }

    messages.append(user_message)
    chatbot()
    