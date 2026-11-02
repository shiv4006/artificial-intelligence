"""Context window test: a 40-turn chat that asks, at the end, about a fact from turn 2.

Run it once per CONTEXT_STRATEGY in .env (none, window, summary), restarting the backend in between:
    uv run python scripts/long_chat.py
"""
import argparse
import json
import time

import httpx

FACT = "Two facts about me: my dog is called Biscuit and my favourite colour is teal. Just reply OK."
QUESTION = "What is my dog's name, and what is my favourite colour? Answer in one line."
TOPICS = [
    "how rainbows form", "how vaccines train the immune system", "why the sea has tides",
    "how a compiler works", "how GPS finds your position", "how noise-cancelling headphones work",
    "how bread rises", "why the sky is blue", "how a bicycle stays upright", "how card payments are processed",
    "how a fridge keeps food cold", "how photosynthesis works", "how earthquakes happen", "how a jet engine works",
    "how DNS works", "how batteries store energy", "how volcanoes form", "how the heart pumps blood",
    "how coffee is decaffeinated", "how a camera sensor captures light", "how Wi-Fi sends data",
    "how bees make honey", "how glass is made", "how aeroplanes fly", "how solar panels make electricity",
    "how a stock exchange works", "how a microwave oven heats food", "how clouds form", "how antibiotics work",
    "how a touchscreen detects a finger", "why the moon has phases", "how paper is recycled", "how lifts work",
    "how hurricanes form", "how a pin tumbler lock works", "how sound travels", "how 3D printers work",
]

def chat(client: httpx.Client, conversation_id: str, content: str) -> tuple[str, dict]:
    """Send one message and return the full reply and the done event."""
    reply, done = "", {}
    with client.stream("POST", f"/conversations/{conversation_id}/chat", json={"content": content}) as response:
        response.raise_for_status()
        for line in response.iter_lines():
            if not line.startswith("data: "):
                continue
            event = json.loads(line.removeprefix("data: "))
            if event["type"] == "token":
                reply += event["text"]
            elif event["type"] == "error":
                raise RuntimeError(event["message"])
            elif event["type"] == "done":
                done = event
    return reply, done

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="llama3.1:8b")
    parser.add_argument("--turns", type=int, default=40)
    parser.add_argument("--api", default="http://localhost:8000")
    args = parser.parse_args()

    client = httpx.Client(base_url=args.api, timeout=300)
    conversation_id = client.post("/conversations", json={"title": "Context test", "model": args.model}).json()["id"]

    messages = ["Hi! I'm going to ask you a lot of questions today.", FACT]
    messages += [f"In about 80 words, explain {topic}." for topic in TOPICS[: args.turns - 3]]
    messages.append(QUESTION)

    print("turn   sent  estimate  actual  seconds")
    for turn, content in enumerate(messages, start=1):
        start = time.perf_counter()
        reply, done = chat(client, conversation_id, content)
        context = done["context"]
        sent = f"{context['messages_sent']}/{context['messages_total']}"
        print(f"{turn:>4} {sent:>6} {context['estimated_tokens']:>9} {done['usage']['prompt_tokens']:>7} {time.perf_counter() - start:>8.1f}")

    detail = client.get(f"/conversations/{conversation_id}").json()
    remembered = "biscuit" in reply.lower() and "teal" in reply.lower()
    print(f"\nStrategy: {context['strategy']}")
    print(f"Answer:   {reply.strip()}")
    print("PASS: remembered turn 2" if remembered else "FAIL: forgot turn 2")
    if detail["summary"]:
        print(f"\nSummary:\n{detail['summary']}")
    print(f"\nKept as \"{detail['title']}\" ({conversation_id}), so you can open it in the UI.")

if __name__ == "__main__":
    main()