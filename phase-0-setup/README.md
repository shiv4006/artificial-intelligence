# Phase 0: `chat.py`, a terminal chatbot

A streaming terminal chatbot that talks to a hosted model (Groq) or a local model (Ollama) through the same OpenAI SDK code. After each reply it prints the token counts and the cost of that turn.

## Files

| File | What it does |
|---|---|
| `chat.py` | The chatbot: chat loop, streaming, CLI flags, token and cost reporting, Groq or Ollama |
| `check_groq.py` | Loads `GROQ_API_KEY` from `.env`, creates the Groq client, and lists the models your key can use when run directly |
| `.env.example` | Template for `.env` (which is gitignored) |

## Setup

```
cd phase-0-setup
cp .env.example .env        # then paste your key from console.groq.com/keys
uv sync                     # creates .venv with Python 3.12 and the packages in pyproject.toml
uv run check_groq.py        # prints the model IDs your key can use
```

For the local model, install Ollama, keep the Ollama app running, and pull the model once:

```
ollama pull llama3.1:8b
curl http://localhost:11434/    # should print "Ollama is running"
```

## Run

```
uv run chat.py                                                    # Groq, openai/gpt-oss-20b
uv run chat.py --model openai/gpt-oss-120b --reasoning_effort high
uv run chat.py --system "You are a pirate. Answer in pirate speak."
uv run chat.py --provider ollama                                  # local llama3.1:8b
uv run chat.py --help
```

| Flag | Default | Notes |
|---|---|---|
| `--provider` | `groq` | `groq` or `ollama`. Only the client's `base_url` changes. |
| `--model` | depends on provider | `openai/gpt-oss-20b` for Groq, `llama3.1:8b` for Ollama |
| `--system` | `You are a helpful assistant. Answer in plain text.` | The system message |
| `--reasoning_effort` | `low` | `low`, `medium` or `high`. Sent only to `openai/gpt-oss-*` models. |

Type `-1`, or press Ctrl+C or Ctrl+D, to exit. After each reply the script prints a line like:

```
Prompt: 131 | Completion: 50 (reasoning 5) | Cost: $0.000000
```

## How it works

- **The model is stateless.** `messages` starts with the system message. Each turn appends the user message, sends the whole list, then appends the assistant reply. The model "remembers" earlier turns only because they are sent again every time.
- **Streaming.** With `stream=True` the API sends server-sent events, and the SDK yields one chunk per event. The new text is in `chunk.choices[0].delta.content`, which is empty on the first chunk and `None` on reasoning chunks. gpt-oss sends its thinking separately in `delta.reasoning` (channel `analysis`), which `chat.py` doesn't print.
- **Usage.** `stream_options={"include_usage": True}` asks for token counts at the end of the stream. Some providers send them in a final chunk with an empty `choices` list, so the loop reads `chunk.usage` before it skips chunks without choices.
- **Cost** = (prompt_tokens × input price + completion_tokens × output price) ÷ 1,000,000, using the prices in `PRICES`. Local models print `local, $0`.
- **One code path for both providers.** Groq and Ollama both serve the OpenAI-compatible `/v1/chat/completions` API, so switching only changes `base_url` (and the API key, which Ollama ignores).

## Results

### Groq vs local Ollama (2026-10-26)

Same three messages ("hello", "hello", "how are you man") with the default system prompt. Groq ran `openai/gpt-oss-20b` at `reasoning_effort=low`. Ollama ran `llama3.1:8b` on an Apple M5 with 16 GB of memory, 100% on the GPU.

"Stream open" is the time until `create()` returned. Tokens/sec is completion tokens divided by the time from stream open to the end of the reply.

| Turn | Groq stream open | Groq tokens/sec | Ollama stream open | Ollama tokens/sec |
|---|---|---|---|---|
| 1 | 0.60 s | ~514 | 2.57 s (model loading) | ~26 |
| 2 | 0.49 s | ~961 | 0.12 s | ~27 |
| 3 | 0.81 s | ~497 | 0.12 s | ~25 |

- Once the model is loaded, Ollama opens the stream about 4–7× sooner than Groq: there's no network round trip and no queue.
- Groq generates text about 20–35× faster. The Groq replies were only 22–50 tokens long, so their tokens/sec numbers are noisy. A longer run, measured by Groq's own `usage` field, did 2,048 tokens in 2.19 s of completion time (about 935 tokens/sec), after 0.96 s in Groq's queue.
- About 25 tokens/sec locally is still about 4× faster than people read, so local chat feels instant.
- Ollama unloads the model after about 5 idle minutes. The next first reply waits for it to load again (2.57 s here).

### Prompt tokens grow every turn

| Turn | gpt-oss-20b prompt tokens | llama3.1:8b prompt tokens |
|---|---|---|
| 1 | 86 | 27 |
| 2 | 106 | 62 |
| 3 | 131 | 86 |

- Every turn costs more than the one before, because the whole history is sent again.
- The same system prompt plus "hello" is 86 tokens on gpt-oss but 27 on Llama. Each model wraps messages in its own chat template, and the gpt-oss template adds more hidden text. You pay for it on every call.
- Only the visible reply is appended to `messages`, so earlier reasoning tokens aren't sent again.

### Reasoning can use up the whole output budget

"Explain how HTTP works in 200 words." on gpt-oss-20b at the default reasoning effort streamed 2,048 completion tokens and printed nothing. 2,046 of them were reasoning, and the last chunk had `finish_reason: "length"`. The model kept drafting and re-counting words to hit exactly 200, because it sees tokens, not words. It hit the output limit before writing an answer, and those tokens were still billed.

Fix: `reasoning_effort="low"` and "about 200 words". Lesson: check `finish_reason`. `"stop"` means the model finished; `"length"` means the answer was cut off or never started.

### Other notes

- Only the models your key can access are available. `llama-3.1-8b-instant` and `llama-3.3-70b-versatile` aren't on this key, so the Groq default is `openai/gpt-oss-20b`.
- Ollama gives `llama3.1:8b` a 4,096-token context by default, though the model supports 128k. Longer chats lose their oldest messages without any error.

## Not recorded yet

- [ ] Real prices in `PRICES`. They are still `0.0` placeholders, so Groq cost prints `$0.000000`.
- [ ] Temperature 0 vs 1: 5 runs each, and the differences
- [ ] Clearing `messages` mid-chat, and the one-line explanation
- [ ] gpt-oss-20b vs gpt-oss-120b on the same 5 questions: quality and tokens/sec
- [ ] tiktoken counts for English, code, JSON, emoji and non-English text
- [ ] Groq free-tier limits, and the 429 rate-limit experiment
- [ ] Measure true time to first token. `chat.py` takes the "First Token" timestamp when `create()` returns (stream open), not when the first text chunk arrives.
