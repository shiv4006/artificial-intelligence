# AI Engineer Roadmap (build-first)

Created 2026-10-22 · about 26 weeks at 10–15 hours a week · target role: AI Engineer

You learn each idea by building something that needs it, not by reading about it first. Every phase ends with a deployed project and a set of numbers you can show in an interview.

---

## How to use this file

- Mark each item `[1]` when it's done and `[0]` when it's skipped or not done yet. `[ ]` means you haven't reached it.
- Count your progress: `grep -c '^- \[1\]' ROADMAP.md` (done) and `grep -c '^- \[0\]' ROADMAP.md` (skipped or not done).
- [GUIDE.md](GUIDE.md) explains every tool, library and idea named here, phase by phase, with how-to-call snippets. Each phase below links to its section.
- Give each phase its own folder in `learning-ai/` (`phase-0-setup/`, `phase-1-chat-app/`, …) and commit every week.
- Update the progress tracker and the weekly log (at the bottom) every weekend.
- Work through the items in order inside a phase. If one takes more than 2 sessions, move on and come back.

## Your stack

| Need | Use | Notes |
|---|---|---|
| LLM (hosted) | Groq, free tier | OpenAI-compatible at `https://api.groq.com/openai/v1`, so you use the `openai` SDK and change only `base_url`. Production chat models: `llama-3.1-8b-instant` (fast, cheap), `llama-3.3-70b-versatile`, `openai/gpt-oss-20b`, `openai/gpt-oss-120b` (strongest; supports strict structured outputs, reasoning effort and automatic prompt caching). |
| LLM (local) | Ollama | Same `openai` SDK, `base_url` = `http://localhost:11434/v1`. |
| Embeddings | Local: `sentence-transformers` or Ollama's `nomic-embed-text` | Groq has no embeddings API. |
| Speech to text | Groq `whisper-large-v3-turbo` | Optional, for a voice feature. |
| Guardrails | Groq `meta-llama/llama-prompt-guard-2-86m`, `openai/gpt-oss-safeguard-20b` | Phase 5. These are preview models. |
| Optional later | Anthropic or OpenAI keys | Only to compare providers. Nothing in this roadmap requires them. |

- Model IDs change. Check console.groq.com/docs/models, and build on production models: preview models can be removed at short notice.
- The free tier is capped by requests and tokens per minute and per day. Your limits are at console.groq.com under Settings → Limits. Any script that makes many calls (evals, ingestion) needs retry with backoff on HTTP 429.
- Keep the key in `.env` only. Never commit it or paste it into a chat.

## Progress tracker

| Phase | Weeks | Project you ship | Status | Started | Finished |
|---|---|---|---|---|---|
| 0. Setup | 1 | `chat.py`, a terminal chatbot | Not started | | |
| 1. LLM app basics | 2–3 | Full-stack ChatGPT clone | Not started | | |
| 2. Embeddings and search | 4–5 | Semantic and hybrid search API | Not started | | |
| 3. RAG and evals | 6–9 | Chat with your docs, plus an eval table | Not started | | |
| 4. Agents and MCP | 10–13 | Data analyst agent and an MCP server | Not started | | |
| 5. Production | 14–16 | Production-grade version of project 3 or 4 | Not started | | |
| 6. Build a GPT | 17–20 | Your own mini-GPT and tokenizer | Not started | | |
| 7. Open models and fine-tuning | 21–23 | A fine-tuned model running locally | Not started | | |
| 8. Capstone and job prep | 24–26+ | Capstone product, portfolio, interviews | Not started | | |

---

## Target role and ground rules

**AI Engineer** means building products on top of models: RAG, agents, evals, production. This is the target.
**ML Engineer / Researcher** means training models. Phases 6–7 are the on-ramp. Research roles usually also need serious math and published work, so treat that as a later path.

1. **Build first, read only when stuck.** Look things up only to get unblocked.
2. **Don't use a framework until you've built it by hand.** Frameworks hide exactly what you need to learn.
3. **Measure everything.** Your interview stories are numbers: "recall went from 0.61 to 0.87."
4. **Learn the theory as code.** Cosine similarity is 3 lines of numpy; attention is about 20 lines of PyTorch.
5. **Ship something every week**, even something small.

---

## Cheat sheet: AI terms in full-stack language

| Term | What it is in dev terms |
|---|---|
| Token | A chunk of text, about ¾ of a word. Pricing, speed and limits are all counted in tokens. |
| LLM | A function: text in → probabilities for the next token → run in a loop to generate text. |
| Context window | The most tokens one request can hold (input plus output). The model is stateless: "memory" is you resending the whole conversation every call, like a stateless HTTP request carrying the full session. |
| System prompt | Config text that sets the model's behavior for the whole conversation. |
| Temperature | A randomness setting for how the next token is picked. 0 is near-deterministic; higher is more varied. |
| Embedding | Text → an array of about 1,000 floats, where similar meaning gives nearby vectors. Like a hash that keeps the meaning instead of destroying it. |
| Vector DB | An index for "find the nearest arrays." pgvector is a Postgres extension. |
| RAG | Search your data, paste the best results into the prompt, and tell the model to answer only from them. Search plus string templating. |
| Reranker | A second, slower model that reorders the top search results more accurately. |
| Tool calling | The model returns JSON like `{"tool":"get_order","args":{"id":42}}`; your code runs it and sends back the result. The model writes RPC calls and you execute them. |
| Agent | An LLM with tools, running in a `while` loop until the task is done. |
| MCP | A standard protocol for plugging tools and data into any AI app (like LSP, but for AI tools). |
| Fine-tuning | Further training of a model's weights on your examples. Changes behavior and format; bad at adding facts. |
| LoRA | Cheap fine-tuning: train small add-on matrices instead of the whole model. |
| Quantization | Storing weights with fewer bits (for example 4-bit) so a model runs faster on smaller hardware, at some cost in quality. |
| Evals | Test suites for output that isn't deterministic: a dataset plus scoring (exact match, code checks, or an LLM judge). |
| Hallucination | Confident, plausible, wrong output. You reduce it with retrieval, citations and evals. |
| Prompt injection | Untrusted text (a web page, a doc, an email) that contains instructions the model then follows. The SQL injection of LLM apps. |

---

## Phase 0 — Setup (Week 1)

**Goal:** a working AI dev environment and your first LLM program, using both an API model and a local one.

**Guide:** [GUIDE.md → Phase 0](GUIDE.md#phase-0--setup)

### Setup
- [1] Install Ollama (`brew install ollama` or the app from ollama.com) and pull a small model (3–8B Llama, Qwen or Gemma) from ollama.com/library
- [1] Create a uv project pinned to Python 3.12. Your Mac has Python 3.15, and ML libraries like PyTorch usually lag new Python releases: `uv init phase-0-setup && cd phase-0-setup && uv python pin 3.12`
- [1] Add packages: `uv add openai python-dotenv tiktoken jupyter ipykernel`
- [1] Put your Groq key in `.env` as `GROQ_API_KEY=...` (create keys at console.groq.com/keys)
- [1] Add `.env` to `.gitignore` before your first commit
- [0] Look up your free-tier limits at console.groq.com (Settings → Limits) and note them here: ______
- [1] `git init` the `learning-ai` folder and push it to a public GitHub repo (it becomes your portfolio)

### Python for JS developers (skip what you know)
- [ ] uv and virtual environments vs npm and `node_modules`
- [ ] List and dict comprehensions, f-strings, slicing
- [ ] Type hints, dataclasses and Pydantic models (Python's equivalent of Zod)
- [ ] `async`/`await` and `asyncio` in Python
- [ ] Generators and `yield` (you need these for streaming)
- [ ] Jupyter basics: run cells, restart the kernel, use a notebook as your experiment lab

### Build: `chat.py`
- [1] One API call: use the `openai` SDK with `base_url="https://api.groq.com/openai/v1"` and your Groq key, send "hello", print the reply
- [1] Chat loop: read input, append it to a `messages` list, call the API, print the reply, append it
- [1] Stream the reply token by token
- [1] Take the system prompt from a CLI flag
- [1] Take the model from a CLI flag (`llama-3.1-8b-instant`, `openai/gpt-oss-120b`, …)
- [1] Print input tokens, output tokens and cost for each turn (from the response's `usage` field, priced with Groq's pricing page, even on the free tier)
- [1] Point the same code at local Ollama by changing only `base_url` to `http://localhost:11434/v1`

### Experiments
- [1] Run the same prompt 5 times at temperature 0 and 5 times at 1, and note the differences
- [1] Clear `messages` mid-chat, watch the model "forget", and write one line on why
- [1] Ask `llama-3.1-8b-instant` and `openai/gpt-oss-120b` the same 5 questions; compare quality and tokens per second
- [1] Ask a local Ollama model the same 5 questions; compare it with Groq on quality and speed
- [ ] Make calls in a tight loop until you hit a 429 rate-limit error; read the response headers that say when to retry
- [1] Tokenize an English sentence, code, JSON, emoji and non-English text with tiktoken; compare token counts

### You can explain
- [1] What a token is, and why pricing and limits are counted in tokens
- [1] Why the model is stateless, and how chat "memory" actually works
- [1] What temperature does

### Done when
- [1] `chat.py` works with an API model and a local model, shows the cost of each turn, and is on GitHub

---

## Phase 1 — LLM app basics (Weeks 2–3)

**Goal:** ship a full-stack chat app, and learn context limits, prompting and structured output along the way.

**Guide:** [GUIDE.md → Phase 1](GUIDE.md#phase-1--llm-app-basics)

### Build: ChatGPT clone (backend, FastAPI)
- [ ] `POST /chat` endpoint that streams over server-sent events (`StreamingResponse`)
- [ ] Postgres tables: `conversations` and `messages` (role, content, tokens, cost, created_at)
- [ ] Load the conversation history from the database on each request
- [ ] Model choice per conversation (a fast, cheap model like `llama-3.1-8b-instant` vs a smart one like `openai/gpt-oss-120b`)

### Build: ChatGPT clone (frontend, Next.js)
- [ ] Chat UI that renders tokens as they stream in
- [ ] Markdown and code-block rendering in replies
- [ ] Conversation sidebar, a new-chat button, and a stop button (abort the fetch)
- [ ] Token count and cost shown for each message

### Context window management
- [ ] Count the tokens in the whole history before each call
- [ ] Strategy A, sliding window: keep only the last N messages
- [ ] Strategy B, summarize: fold older messages into a running summary
- [ ] Test both: in a 40-turn chat, ask about something from turn 2
- [ ] Auto-title conversations with a cheap model call

### Structured output
- [ ] `POST /extract`: paste invoice or receipt text, get JSON back (vendor, date, line items, total), checked with Pydantic
- [ ] Build it 3 ways: JSON requested in the prompt, Groq's strict `json_schema` mode (gpt-oss models) or JSON object mode (Llama models), and a tool schema. Compare failure rates over 20 inputs.
- [ ] When validation fails, send the error back to the model and ask it to fix its output

### Prompt engineering lab (notebook)
- [ ] Write 10 test inputs for one task (for example: turn a support ticket into a category and an urgency)
- [ ] Prompt v1 (bare) → v2 (role and clear instructions) → v3 (plus few-shot examples) → v4 (plus XML-tagged sections)
- [ ] Score every version on all 10 inputs by hand in a table and keep the winner
- [ ] On a reasoning task, compare `reasoning_effort` low vs high on `openai/gpt-oss-120b`, and a plain "think step by step" prompt on a Llama model: accuracy vs tokens used
- [ ] Work through Anthropic's interactive prompt engineering tutorial (GitHub: `anthropics/prompt-eng-interactive-tutorial`). It's written for Claude; run its exercises against Groq by swapping the client call. The techniques carry over.

### You can explain
- [ ] Why long chats get slower and more expensive
- [ ] The trade-offs between cutting old messages and summarizing them
- [ ] Why JSON output breaks, and how structured outputs and tool schemas fix it
- [ ] What few-shot prompting is and when it helps
- [ ] Why server-sent events usually beat WebSockets for streaming LLM output

### Done when
- [ ] The chat app is deployed (for example Vercel plus Railway, Fly or Render) with streaming, history and cost display
- [ ] The prompt lab notebook and its scored comparison table are committed

---

## Phase 2 — Embeddings and semantic search (Weeks 4–5)

**Goal:** understand embeddings by computing them, plotting them and searching with them.

**Guide:** [GUIDE.md → Phase 2](GUIDE.md#phase-2--embeddings-and-semantic-search)

### Notebook: embeddings by hand
- [ ] Write or generate 500 sentences across 5 topics
- [ ] Embed them locally (Groq has no embeddings API) with `sentence-transformers` (start with `all-MiniLM-L6-v2` or `BAAI/bge-small-en-v1.5`)
- [ ] Inspect one vector: its length and its value range
- [ ] Write cosine similarity yourself in numpy (dot product divided by the norms), with no library
- [ ] Find the top 5 nearest neighbors for 10 query sentences
- [ ] Squash the vectors to 2D with PCA, then with UMAP, and plot them colored by topic
- [ ] Try "king − man + woman" style vector arithmetic and note where it works and where it fails
- [ ] Compare 2 embedding models on the same neighbor task (for example `all-MiniLM-L6-v2` vs Ollama's `nomic-embed-text`) and decide which ranks better
- [ ] Optional: compare with a hosted embeddings API (Voyage, Cohere or OpenAI)

### Build: semantic search API
- [ ] Pick a real dataset of 5k–50k items (your notes, a product catalog, Hacker News posts, a Kaggle dataset)
- [ ] Run Postgres with pgvector in Docker; add a table with an `embedding vector(N)` column
- [ ] Ingestion script: embed in batches, handle rate limits, store the results
- [ ] `GET /search?q=`: embed the query, then `ORDER BY embedding <=> $query LIMIT 10`
- [ ] Add an HNSW index and measure latency before and after with `EXPLAIN ANALYZE`
- [ ] Simple search UI showing results and their similarity scores
- [ ] Combine vector search with metadata filters (category, date)

### Keyword vs vector vs hybrid search
- [ ] Add Postgres full-text search (`tsvector`) as the keyword search
- [ ] Build hybrid search that merges both rankings with Reciprocal Rank Fusion (RRF)
- [ ] Write 30 test queries, each with its expected best result. Include exact-match queries (IDs, error codes, names) and reworded ones.
- [ ] Measure hit@1 and hit@5 for keyword, vector and hybrid search, and record them in a table

### You can explain
- [ ] What an embedding is, and why similar meanings land close together
- [ ] Cosine similarity vs dot product vs Euclidean distance
- [ ] What approximate nearest-neighbor search (HNSW) does, and its trade-off between recall and speed
- [ ] Why vector search misses exact strings like `ERR_4021`, and why hybrid search fixes that
- [ ] Why changing embedding models means re-embedding everything

### Done when
- [ ] A search API and UI over a real dataset, with the keyword / vector / hybrid comparison table in the README

---

## Phase 3 — RAG from scratch, with evals (Weeks 6–9) — the phase that gets you hired

**Goal:** build a chat-with-your-docs system and prove with numbers that it works.

**Guide:** [GUIDE.md → Phase 3](GUIDE.md#phase-3--rag-from-scratch-with-evals)

Pipeline: parse → chunk → embed → store → retrieve → rerank → generate with citations → stream

### Pick a corpus
- [ ] Choose 50–500 documents you know well enough to judge the answers (framework docs, a handbook, tax or legal docs, your notes). Mix formats: PDF, HTML and Markdown.

### Ingestion
- [ ] A parser for each format (pymupdf for PDF, BeautifulSoup for HTML), or try docling or unstructured
- [ ] Clean the text (headers, footers, whitespace) and keep metadata: source, page, section heading
- [ ] Chunker v1: fixed size in tokens, with overlap
- [ ] Chunker v2: split on structure (headings, paragraphs) first, then by size
- [ ] Store chunks, metadata and embeddings in pgvector
- [ ] Make re-ingestion idempotent: hash each document's content and skip unchanged ones

### Retrieval and generation
- [ ] Retrieve the top-k chunks with your hybrid search from Phase 2
- [ ] Prompt template: instructions, numbered sources, the question, and "answer only from the sources; otherwise say you don't know"
- [ ] Citations: the model cites [1], [2], and the UI links each one to its chunk and page
- [ ] Stream the answer to a Next.js UI with a sources panel
- [ ] Handle "nothing relevant found" gracefully, using a similarity threshold

### Evals
- [ ] Golden set: 50 questions, each with its expected answer and source chunk. Write 30 by hand; generate 20 with an LLM and review every one.
- [ ] Include hard cases: questions that need two documents, questions the corpus can't answer, and exact-term questions
- [ ] Retrieval metrics script: recall@5, recall@10 and MRR
- [ ] Answer metrics: correctness and faithfulness, scored by an LLM judge with a written rubric (use `openai/gpt-oss-120b` as the judge, and a different model for answering)
- [ ] Retry with backoff on 429s, and cache judge results on disk, so a full eval run fits within Groq's free-tier limits
- [ ] Hand-label 20 of the judge's verdicts and check how often you agree (aim for over 80%)
- [ ] One command runs the whole eval and appends a results row (`uv run eval.py`)
- [ ] Optional: compare your numbers with the Ragas library's metrics

### Experiments (change one thing at a time and log every run)
- [ ] Record the baseline
- [ ] Chunk size 256 vs 512 vs 1024 tokens; overlap 0 vs 15%
- [ ] Vector-only vs hybrid search
- [ ] Add a reranker: a local cross-encoder like `BAAI/bge-reranker-base` through `sentence-transformers` (Cohere and Voyage offer hosted ones), top 30 → top 5
- [ ] Query rewriting: an LLM rewrites the question before the search
- [ ] Contextual chunk headers: prepend the doc title and section (or LLM-written context) to each chunk before embedding. See Anthropic's "Contextual Retrieval" post.
- [ ] Number of chunks sent to the model: 3 vs 5 vs 10, and the effect on correctness and cost
- [ ] Long-context baseline: put whole documents into the prompt. When does it beat RAG, and at what cost?

### Experiment log (copy into your project README)

| Run | Change | Recall@5 | MRR | Correctness | Faithfulness | Cost/query | p50 latency |
|---|---|---|---|---|---|---|---|
| 1 | Baseline | | | | | | |

### You can explain
- [ ] Every step of the RAG pipeline, and how to tell a retrieval miss from a generation error
- [ ] The trade-offs in chunk size and overlap
- [ ] What a reranker (cross-encoder) is, and why it orders results better than embeddings
- [ ] How you evaluate RAG, and how you checked that the LLM judge can be trusted
- [ ] RAG vs long context vs fine-tuning

### Done when
- [ ] A deployed chat-with-your-docs app with citations
- [ ] A README with an architecture diagram and an experiment table showing the gain over the baseline
- [ ] An engineering log post: "How I took recall@5 from X to Y"

---

## Phase 4 — Tool calling, agents and MCP (Weeks 10–13)

**Goal:** build agents from the raw loop up, then build an MCP server.

**Guide:** [GUIDE.md → Phase 4](GUIDE.md#phase-4--tool-calling-agents-and-mcp)

### Tool calling by hand (no framework)
- [ ] Define 3 tools with JSON schemas: `get_weather`, `calculator`, `search_docs` (your Phase 3 retriever)
- [ ] Write the loop: call the model → if it asks for a tool, run it → append the result → repeat until it answers
- [ ] Support several tool calls in one turn
- [ ] Send tool errors back to the model as results and watch it recover
- [ ] Add a step limit, and log every step (tool, arguments, result)
- [ ] Run the same loop on a local Ollama model and note where it breaks

### Agent project: data analyst agent
- [ ] Postgres with a sample database (Chinook, Northwind or Pagila)
- [ ] A read-only database user (the agent never gets write access)
- [ ] Tools: `list_tables`, `describe_table`, `run_sql` (with a row limit and timeout), `make_chart`
- [ ] The agent fixes its own SQL from the error messages
- [ ] Web UI that shows the steps live, then the final answer and the chart
- [ ] Follow-up questions work ("now split that by country")

### Agent evals
- [ ] 20 test questions with known correct results
- [ ] Measure success rate, average steps, cost per task and latency
- [ ] Improve one thing (tool descriptions, schema hints, examples) and measure again

### MCP
- [ ] Do the official quickstart at modelcontextprotocol.io (a server in Python or TypeScript)
- [ ] Build an MCP server for one of your real apps (tools and resources)
- [ ] Connect it to Claude Code, Claude Desktop or Cursor and use it for a real task
- [ ] Write an MCP client too (connect, list tools, call one), then let a Groq model call the server's tools through your own agent loop

### Safety and production concerns
- [ ] Human approval before any destructive tool (sending email, deleting, paying)
- [ ] A cost budget and a timeout for each task
- [ ] Prompt-injection test: hide "ignore previous instructions and …" in a document or database row the agent reads. Write down what happens and how you stopped it.
- [ ] Cut down or summarize long tool output so it doesn't flood the context

### Frameworks (only now)
- [ ] Rebuild the data analyst agent in one framework that works with Groq: LangGraph, Pydantic AI, OpenAI Agents SDK, or Vercel AI SDK (TypeScript, `@ai-sdk/groq`)
- [ ] Write down what it saved you, what it hid, and what got harder
- [ ] Optional: a multi-agent version (one planner, several workers). Measure whether it actually beats one agent.

### You can explain
- [ ] How tool calling works: the model never runs anything; your code does
- [ ] The agent loop and how it fails (loops, wrong tool, invented arguments, an overfull context)
- [ ] When a fixed workflow beats an autonomous agent
- [ ] What MCP standardizes and why it exists
- [ ] Why an agent that has private data, reads untrusted content and can act externally is dangerous

### Done when
- [ ] The data analyst agent is deployed, with eval numbers in its README
- [ ] The MCP server is on GitHub with setup instructions

---

## Phase 5 — Production AI engineering (Weeks 14–16)

**Goal:** make your Phase 3 or Phase 4 project production-grade.

**Guide:** [GUIDE.md → Phase 5](GUIDE.md#phase-5--production-ai-engineering)

### Observability
- [ ] Trace every LLM and tool call with Langfuse (or Arize Phoenix, or LangSmith)
- [ ] Dashboard: requests, tokens, cost per day, p50 and p95 latency, error rate
- [ ] Thumbs-up and thumbs-down feedback linked to traces
- [ ] Review 20 real traces and turn the failures into new eval cases

### Evals in CI
- [ ] An eval suite as tests (promptfoo or pytest)
- [ ] A GitHub Action that runs the evals on PRs that change prompts or retrieval
- [ ] The build fails when a metric drops below its threshold
- [ ] Prompts live in versioned files under git, not as strings in the code

### Cost and latency
- [ ] Prompt caching: Groq caches repeated prompt prefixes automatically on gpt-oss models (cached input tokens cost 50% less). Put the fixed parts of the prompt first, then measure cached tokens in `usage`, cost and latency.
- [ ] Model routing: `llama-3.1-8b-instant` for easy queries, `openai/gpt-oss-120b` for hard ones. Measure quality and cost.
- [ ] Cache repeated and near-identical queries; measure the hit rate
- [ ] Use batch APIs for offline jobs (ingestion, evals)
- [ ] Track time to first token, and stream everything the user sees

### Reliability
- [ ] Retries with exponential backoff on 429 and 5xx errors, and a timeout on every call
- [ ] Fallback behind one interface: Groq → local Ollama (or a second hosted provider)
- [ ] Rate limits and spend caps for each user
- [ ] Graceful degradation (for example, show search results without an answer if the LLM is down)

### Safety and security
- [ ] Input checks: off-topic and abusive requests
- [ ] Prompt-injection detection with Groq's `meta-llama/llama-prompt-guard-2-86m`; measure it on the injection tests from Phase 4
- [ ] Output checks: PII redaction, and verifying that each cited chunk supports its claim
- [ ] Prompt-injection defenses: keep untrusted content separate, give tools the least access they need, use allowlists
- [ ] Never log secrets; redact PII in traces
- [ ] Check your app against the OWASP Top 10 for LLM Applications (genai.owasp.org)

### Context engineering
- [ ] Audit what goes into each prompt: order, length, and what's actually needed
- [ ] Compress long sessions (summarize, keep the key facts)
- [ ] Memory: store user facts across sessions and bring them back when relevant

### Done when
- [ ] The app runs with a tracing dashboard, evals in CI that have caught at least one regression, and documented cost per request

---

## Phase 6 — Under the hood: build a GPT yourself (Weeks 17–20)

**Goal:** understand how LLMs work inside by writing one.

**Guide:** [GUIDE.md → Phase 6](GUIDE.md#phase-6--build-a-gpt-yourself)

### Setup
- [ ] Install PyTorch and confirm `torch.backends.mps.is_available()` returns `True` on your Mac, or use a free Colab GPU
- [ ] Watch 3Blue1Brown's neural network series, including the chapters on transformers and attention (visual, about 2–3 hours)

### Karpathy's "Neural Networks: Zero to Hero" (karpathy.ai/zero-to-hero.html). Type every line yourself.
- [ ] micrograd: autograd and a tiny neural net from scratch
- [ ] makemore part 1: bigram model
- [ ] makemore part 2: MLP
- [ ] makemore part 3: activations, gradients, BatchNorm
- [ ] makemore part 4: backprop by hand
- [ ] makemore part 5: WaveNet
- [ ] Let's build GPT: from scratch, in code
- [ ] Let's build the GPT tokenizer (BPE)
- [ ] Optional: Let's reproduce GPT-2 (124M)

### Your own variations
- [ ] Train your mini-GPT on a corpus you pick (song lyrics, your own code, a book in another language)
- [ ] Change context length, layers, heads and embedding size; log loss curves and sample outputs
- [ ] Visualize the attention weights for one input
- [ ] Load GPT-2 with Hugging Face `transformers` and inspect the probabilities of the next token
- [ ] Write greedy, temperature, top-k and top-p sampling yourself
- [ ] Pull vectors out of a model's embedding layer and compare them with your Phase 2 embeddings
- [ ] Optional: work through Raschka's *Build a Large Language Model (From Scratch)* (github.com/rasbt/LLMs-from-scratch), including its instruction fine-tuning chapter

### Math you pick up through the code
- [ ] Vectors, dot products and matrix multiplication (and their shapes)
- [ ] Softmax and cross-entropy loss
- [ ] Gradients, gradient descent, and what an optimizer like AdamW does
- [ ] Debugging a PyTorch shape error calmly

### You can explain
- [ ] Training vs inference
- [ ] BPE tokenization, and why odd tokenization causes odd model behavior
- [ ] The embedding layer, self-attention, multi-head attention, MLP block, residuals and layer norm, at the code level
- [ ] Why attention cost grows with the square of the length, and what a KV cache is
- [ ] Pretraining vs instruction tuning vs preference tuning (RLHF, DPO), at a high level
- [ ] How temperature and top-p act on the softmax output you wrote

### Done when
- [ ] A repo with your trained mini-GPT, your tokenizer, and a README that explains the architecture in your own words, with a diagram

---

## Phase 7 — Open models and fine-tuning (Weeks 21–23)

**Goal:** run, serve and fine-tune open-weight models, and know with numbers when fine-tuning is worth it.

**Guide:** [GUIDE.md → Phase 7](GUIDE.md#phase-7--open-models-and-fine-tuning)

### Running open models
- [ ] Run 3 open-weight models of different sizes in Ollama; compare speed (tokens/second) and quality on your Phase 1 test inputs
- [ ] Compare quantization levels of the same model (for example Q4 vs Q8): quality, speed, memory
- [ ] Run `llama3.1:8b` in Ollama and `llama-3.1-8b-instant` on Groq (the same model), compare tokens per second, and find out why Groq's custom LPU hardware is faster
- [ ] Run one model with llama.cpp directly and learn what GGUF is
- [ ] Load a model with Hugging Face `transformers`: tokenize and generate in Python

### Serving
- [ ] Rent a GPU (Modal, RunPod or similar) and serve a model with vLLM (OpenAI-compatible API)
- [ ] Load-test it (k6 or locust) and measure throughput and latency at 1, 10 and 50 concurrent users
- [ ] Work out cost per 1M tokens against Groq's pricing for a similar model and find the break-even point

### Fine-tuning
- [ ] Pick a narrow task with output you can check: text-to-SQL for your Phase 4 schema, ticket classification, or extraction into fixed JSON
- [ ] Build a dataset of 500–2,000 examples (real, or generated by a large model and reviewed by hand) and split it into train, validation and test sets
- [ ] Baselines first: small model with a prompt, small model with few-shot examples, large model with a prompt (`openai/gpt-oss-120b` on Groq)
- [ ] LoRA or QLoRA fine-tune a small model (1–8B) with Unsloth on Colab (docs.unsloth.ai has ready notebooks)
- [ ] Evaluate the fine-tuned model against the baselines on the same held-out test set
- [ ] Vary LoRA rank, epochs and dataset size; watch validation loss for overfitting
- [ ] Merge the adapters, export to GGUF, and run your model in Ollama
- [ ] Optional: preference tuning with DPO on a small dataset
- [ ] Optional: fine-tune an embedding model on your Phase 3 corpus and rerun the retrieval evals

### You can explain
- [ ] When to fine-tune vs prompt vs use RAG, backed by your own numbers
- [ ] LoRA in one paragraph: what gets trained and why it's cheap
- [ ] What quantization trades away
- [ ] Serving basics: batching, KV cache, throughput vs latency
- [ ] Why data quality matters more than data quantity for fine-tuning

### Done when
- [ ] A repo with a dataset card, the training notebook, an eval table (base vs fine-tuned vs API model), and the model running locally

---

## Phase 8 — Capstone and job prep (Weeks 24–26+)

**Goal:** one serious product, a portfolio that shows numbers, and interview readiness.

**Guide:** [GUIDE.md → Phase 8](GUIDE.md#phase-8--capstone-and-job-prep)

### Capstone
- [ ] Pick a problem in a domain you know (an AI assistant inside an app you've built, a codebase Q&A agent, a support agent that hands off to humans, a meeting-notes copilot)
- [ ] Write a 1-page design doc: users, requirements, architecture, eval plan, cost estimate, risks
- [ ] Combine RAG, at least one agent workflow, evals, observability and guardrails
- [ ] A polished frontend (your strength; make it look like a real product)
- [ ] Auth, rate limits and cost caps
- [ ] Deployed with a public demo link (or a demo video if access is gated)
- [ ] README: problem, architecture diagram, eval table, cost per query, latency, limitations, next steps
- [ ] A 2-minute demo video

### Portfolio
- [ ] Pin these on your GitHub profile: the Phase 3 RAG app, the Phase 4 agent and MCP server, the capstone, and the fine-tuning repo
- [ ] Every pinned repo has a one-line pitch, a demo link or GIF, eval numbers, and a 3-command setup
- [ ] Publish 3 engineering posts from your weekly logs (personal blog, dev.to, Medium or LinkedIn)
- [ ] Make at least 1 open-source contribution to an AI tool you used (a docs fix, a bug fix, an example)

### Resume and positioning
- [ ] Headline: "Full-stack engineer building production LLM applications"
- [ ] Rewrite bullets with numbers, e.g. "Built RAG over 12k docs; raised recall@5 from 0.61 to 0.87 with hybrid search and reranking; cut cost per query 40% with caching"
- [ ] Put the AI projects section above older experience if needed
- [ ] Update LinkedIn and share each project post

### Interview prep: LLM system design
Practice each one out loud in 45 minutes: requirements → architecture → retrieval → evals → cost and latency → failure modes → safety.
- [ ] A support bot over 1M help-center docs
- [ ] Company-wide search across Slack, Drive and Confluence that respects permissions
- [ ] A coding assistant for a large monorepo
- [ ] An agent that books meetings across calendars and email
- [ ] An extraction pipeline for 100k invoices a day
- [ ] Content moderation with LLMs at scale

### Interview prep: practical builds
- [ ] Timed: a minimal RAG endpoint from an empty folder in 90 minutes
- [ ] Timed: a tool-calling agent with 2 tools in 60 minutes
- [ ] Timed: an eval harness for a given prompt in 45 minutes
- [ ] Keep regular coding (data structures, algorithms, backend) sharp; many interview loops still include it

### Interview prep: concepts (answer each out loud in 2 minutes)
- [ ] How does an LLM generate text?
- [ ] What are embeddings, and how does vector search work?
- [ ] How would you reduce hallucinations?
- [ ] How do you evaluate an LLM app, and why do you trust your LLM judge?
- [ ] RAG vs fine-tuning vs long context: when do you use each?
- [ ] How do you cut the cost and latency of an LLM feature?
- [ ] What is prompt injection, and how do you defend against it?
- [ ] When is an agent worth it, and when is a fixed workflow better?
- [ ] Walk me through your best project. How did you know it was better?

### Applying
- [ ] List 30 target companies (AI-native startups, product companies adding AI features, consultancies)
- [ ] Tailor your resume for each kind of role (AI engineer, applied AI, LLM engineer, full-stack AI)
- [ ] Apply to 5–10 roles a week and track them in a table
- [ ] Ask for referrals; reach out to engineers whose posts and repos you learned from
- [ ] After each interview, write down the questions and your gaps, and practice those

---

## Weekly rhythm (10–15 hours)

- **2 weekday evenings (1.5–2 hours each):** build.
- **1 weekday evening (1 hour):** learn only the thing you got stuck on.
- **Weekend (4–5 hours):** one long build session, then fill in the weekly log below.

## Weekly log

| Week | Dates | Hours | What I built or shipped | Numbers that changed | Stuck on |
|---|---|---|---|---|---|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |

---

## Resources (hands-on only)

| Phase | Resource | Where |
|---|---|---|
| 1 | Anthropic's interactive prompt engineering tutorial | GitHub: `anthropics/prompt-eng-interactive-tutorial` |
| All | Groq docs (models, tool use, structured outputs, rate limits) | console.groq.com/docs |
| 1–4 | Groq API cookbook (runnable notebooks) | GitHub: `groq/groq-api-cookbook` |
| 1–4 | Anthropic and OpenAI cookbooks (techniques carry over to any provider) | GitHub, under the `anthropics` and `openai` orgs |
| 2 | pgvector docs | github.com/pgvector/pgvector |
| 3 | Anthropic's "Contextual Retrieval" post | anthropic.com |
| 3, 5 | Hamel Husain on evals (the one exception to "no articles") | hamel.dev |
| 4 | MCP quickstarts | modelcontextprotocol.io |
| 4, 7 | Hugging Face LLM course and Agents course | huggingface.co/learn |
| 5 | Langfuse, promptfoo | langfuse.com, promptfoo.dev |
| 5 | OWASP Top 10 for LLM Applications | genai.owasp.org |
| 6 | Karpathy's Neural Networks: Zero to Hero | karpathy.ai/zero-to-hero.html |
| 6 | Raschka's LLMs from scratch | github.com/rasbt/LLMs-from-scratch |
| 6 | fast.ai Practical Deep Learning (code-first, for broader deep learning) | course.fast.ai |
| 7 | Unsloth fine-tuning notebooks | docs.unsloth.ai |
| All | Chip Huyen, *AI Engineering* (reference: read the chapter for your current phase) | O'Reilly |

## What to skip

- Math courses and textbooks up front. Learn the math when the code needs it.
- Learning LangChain first.
- Chasing every new model or framework release. Retrieval, evals, context and tool loops carry over between them.
- Certificates. Hiring managers look for shipped projects with numbers.
- Classical ML (scikit-learn, XGBoost). It's useful but optional for AI engineer roles; a weekend later is enough.

## If you want the research path later

After Phase 6–7: reimplement papers in PyTorch (start with the original Transformer, LoRA and DPO papers), reproduce their results at small scale, write up what you found, and learn the linear algebra, probability and optimization behind them properly. Expect a multi-year path.
