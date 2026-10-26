# AI Engineer Guide

Companion to [ROADMAP.md](ROADMAP.md). For every tool, library and idea in the roadmap: what it is, how it works, and how to call it.

**How to use this file:** open the section for the phase you're in. When a roadmap item names something you don't recognize, look it up here. The snippets show how to call each library. The exercises themselves (the chat loop, the agent loop, the metrics, the sampler) are left for you to write.

**Contents:** [Big picture](#the-big-picture) · [Phase 0](#phase-0--setup) · [Phase 1](#phase-1--llm-app-basics) · [Phase 2](#phase-2--embeddings-and-semantic-search) · [Phase 3](#phase-3--rag-from-scratch-with-evals) · [Phase 4](#phase-4--tool-calling-agents-and-mcp) · [Phase 5](#phase-5--production-ai-engineering) · [Phase 6](#phase-6--build-a-gpt-yourself) · [Phase 7](#phase-7--open-models-and-fine-tuning) · [Phase 8](#phase-8--capstone-and-job-prep)

---

## The big picture

Every app in this roadmap has the same shape. The model is one stateless function call in the middle; everything around it is ordinary backend work.

```
Browser (Next.js)
   │  POST /chat                 ▲  answer streams back token by token (SSE)
   ▼                             │
Backend (FastAPI)
   ├─ 1. load chat history ............ Postgres
   ├─ 2. find relevant text ........... embedding model + pgvector       (Phases 2–3)
   ├─ 3. build the prompt ............. system + history + sources + question
   ├─ 4. call the model ............... Groq API or local Ollama          (Phases 0–1)
   ├─ 5. run any tools it asks for .... SQL, APIs, MCP servers            (Phase 4)
   └─ 6. record and test everything ... Langfuse traces, evals in CI      (Phase 5)
```

Phases 6–7 open up the box in step 4: how the model itself works, and how to run and fine-tune your own.

---

## Phase 0 — Setup

### What's in `phase-0-setup/`

| File | What it is | JS equivalent |
|---|---|---|
| `pyproject.toml` | Project name, Python version and dependencies | `package.json` |
| `uv.lock` | Exact version of every installed package | `package-lock.json` |
| `.python-version` | Which Python uv uses for this project (3.12) | `.nvmrc` |
| `.venv/` | The project's own Python and packages. Never commit it. | `node_modules/` |
| `.env` | Your secrets, read when the program runs. Gitignored. | `.env` |
| `.env.example` | A template with **empty** values that shows which variables are needed. It gets committed, so it must never hold a real key. | `.env.example` |
| `check_groq.py` | Lists the models your key can use, to prove the key works | — |

### Tools and libraries

**uv** — a fast Python package and project manager (written in Rust). It replaces pip, venv, pyenv and poetry.
- `uv add <pkg>` installs a package and records it (like `npm install <pkg>`).
- `uv run <script.py>` runs inside the project's `.venv`, with no "activate" step.
- `uv sync` installs exactly what `uv.lock` says (like `npm ci`).
- `uv python pin 3.12` picks the Python version; uv downloads it if needed.

**Why Python 3.12 and not 3.15:** libraries like PyTorch ship compiled builds for each Python version, and support for a new version arrives months later. 3.12 is supported by everything in this roadmap.

**python-dotenv** — `load_dotenv()` reads `.env` and puts each line into `os.environ`, the same as the `dotenv` npm package.

**openai (Python SDK)** — the official client for OpenAI's API format. Many providers (Groq, Ollama, vLLM and others) accept the same HTTP format, called "OpenAI-compatible", so one SDK talks to all of them; you only change `base_url`. It retries failed calls on its own (`max_retries`, 2 by default) and has a `timeout` option.

**Groq** — a company that runs other people's open-weight models (Llama, gpt-oss, Qwen, Whisper) on its own chips, called LPUs. It's known for speed: often hundreds of tokens per second. The free tier is limited by requests and tokens per minute and per day rather than billed.

| Groq model ID | Size | Use it for |
|---|---|---|
| `llama-3.1-8b-instant` | 8B | Fast and cheap: routing, simple extraction, high-volume calls |
| `llama-3.3-70b-versatile` | 70B | General chat; much better quality than 8B |
| `openai/gpt-oss-20b` | 21B, mixture of experts | Reasoning on a budget; strict structured outputs |
| `openai/gpt-oss-120b` | 117B, mixture of experts | Hardest tasks, LLM judge, agents. Strict structured outputs, reasoning effort, prompt caching. |

"8B" means 8 billion parameters (the numbers learned in training). "Mixture of experts" means only part of the model runs for each token, so a big model can still be fast.

**Ollama** — runs open models on your Mac. It downloads compressed ("quantized") models and serves them at `http://localhost:11434`, including an OpenAI-compatible API at `/v1`. Under the hood it uses llama.cpp (Phase 7).
- `ollama pull llama3.1:8b` downloads a model; `ollama list` shows downloaded models; `ollama ps` shows running ones.
- Rough memory rule: an 8B model at 4-bit needs about 5 GB of RAM.

**tiktoken** — OpenAI's tokenizer library. It turns text into the token IDs a model reads. Each model family has its own tokenizer, so counts for Llama models are approximate (Phase 6 shows you how to get exact ones).

```python
import tiktoken
enc = tiktoken.get_encoding("o200k_base")
ids = enc.encode("Unbelievable!")
print(len(ids), [enc.decode([i]) for i in ids])   # how many tokens, and what each one is
```

**Jupyter and ipykernel** — notebooks: code in cells, with variables kept in memory between cells, so you can experiment without rerunning everything. `uv run jupyter lab` opens it in the browser. VS Code can also open `.ipynb` files; choose `.venv` as the kernel. `ipykernel` is what lets Jupyter use this project's environment.

### How `check_groq.py` works

1. `load_dotenv()` copies `GROQ_API_KEY` from `.env` into the environment.
2. `os.getenv("GROQ_API_KEY")` reads it; the script stops with a clear message if it's missing.
3. `OpenAI(api_key=..., base_url="https://api.groq.com/openai/v1")` creates a client that talks to Groq instead of OpenAI.
4. `client.models.list()` calls `GET /models`. A list back proves that the key is valid and the network works.

### Python for JS developers

| JavaScript / TypeScript | Python |
|---|---|
| `arr.map(x => x * 2)` | `[x * 2 for x in arr]` (list comprehension) |
| `arr.filter(x => x > 0)` | `[x for x in arr if x > 0]` |
| `` `Hi ${name}` `` | `f"Hi {name}"` (f-string) |
| `arr.slice(-3)` | `arr[-3:]` |
| `obj.key`, `{...a, ...b}` | `d["key"]`, `{**a, **b}` |
| `null` / `undefined` | `None` |
| `try { } catch (e) { }` | `try: ... except Exception as e: ...` |
| `JSON.parse` / `JSON.stringify` | `json.loads` / `json.dumps` |
| Zod schema | Pydantic model |
| TypeScript types | Type hints: `def f(x: int) -> str:` |
| `async function` / `await` | `async def` / `await`, run by `asyncio` |
| `function*` with `yield` | Any `def` that uses `yield` is a generator |
| `npm` / `package.json` / `node_modules` | `uv` / `pyproject.toml` / `.venv` |

### Calling the model: request and response

```python
resp = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {"role": "system", "content": "You are a concise assistant."},
        {"role": "user", "content": "What is an embedding?"},
    ],
    temperature=0.7,
)
resp.choices[0].message.content    # the reply text
resp.usage.prompt_tokens           # input tokens you pay for
resp.usage.completion_tokens       # output tokens you pay for
```

- **Roles:** `system` sets behavior, `user` is the person, `assistant` is the model's earlier replies. In Phase 4 you add `tool`.
- **Streaming:** pass `stream=True` and you get an iterator of chunks. Each chunk's new text is in `chunk.choices[0].delta.content`. It can be `None`, and some chunks have an empty `choices` list, so check before printing.

### Concepts

**Statelessness and "memory"** — the model remembers nothing between calls. A chat works because you send the whole `messages` list every time, with the new message added at the end. So every turn costs more than the last, and a long chat eventually overflows the context window (Phase 1).

**Tokens and cost** — providers charge per million tokens, with separate prices for input and output. Cost of one call = (prompt_tokens × input price + completion_tokens × output price) ÷ 1,000,000. Groq's pricing page lists the prices; work out the cost even on the free tier, because that habit matters in production.

**Temperature** — for every next token, the model produces a probability for each possible token. Temperature reshapes those probabilities before one is picked. Low temperature almost always picks the most likely token (consistent, repetitive); high temperature spreads the choice out (varied, more mistakes). Groq turns `0` into `1e-8`.

**Rate limits and HTTP 429** — the limits are requests per minute and per day (RPM, RPD) and tokens per minute and per day (TPM, TPD). Going over returns status 429. The response headers tell you where you stand:

```python
raw = client.chat.completions.with_raw_response.create(model="llama-3.1-8b-instant", messages=messages)
print(raw.headers.get("x-ratelimit-remaining-requests"), raw.headers.get("retry-after"))
resp = raw.parse()   # the normal response object
```

---

## Phase 1 — LLM app basics

Install: `uv add "fastapi[standard]" "psycopg[binary]" pydantic`

### Backend tools

**FastAPI** — a Python web framework, like Express with Zod built in. Each route is a type-hinted function; request bodies are checked against Pydantic models automatically; interactive API docs appear at `/docs`. Run it with `uv run fastapi dev main.py`, which starts **Uvicorn** (the server underneath, like `node` running Express).

**StreamingResponse and server-sent events (SSE)** — `StreamingResponse` sends each value your generator yields as soon as it's ready. SSE is a plain-text format on top of that: each event is a `data: ...` line followed by a blank line.

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

app = FastAPI()

@app.post("/chat")
def chat():
    def events():
        for piece in ["Hel", "lo", "!"]:            # in your app: chunks from the model
            yield f"data: {piece}\n\n"
        yield "data: [DONE]\n\n"
    return StreamingResponse(events(), media_type="text/event-stream")
```

Send JSON in each `data:` line (`json.dumps({"token": ...})`) so that newlines inside tokens can't break the format.

**psycopg 3** — the standard Postgres driver for Python (like `pg` for Node). `psycopg.connect(url)` gives a connection, and `conn.execute(sql, params)` runs queries with `%s` placeholders. SQLAlchemy or SQLModel are optional ORMs on top; the raw driver is enough here.

**Pydantic** — data models with validation, Python's version of Zod. You'll use it for request bodies and for checking model output.

```python
from pydantic import BaseModel, ValidationError

class LineItem(BaseModel):
    description: str
    amount: float

class Invoice(BaseModel):
    vendor: str
    date: str
    items: list[LineItem]
    total: float

try:
    invoice = Invoice.model_validate_json(model_output)     # parse and check in one step
except ValidationError as e:
    print(e)        # send this back to the model and ask it to fix its JSON
schema = Invoice.model_json_schema()                         # JSON Schema for structured outputs or tools
```

### Frontend notes (Next.js)

- **Reading the stream:** the browser's `EventSource` only does GET, so for `POST /chat` use `fetch`, then `res.body.getReader()` plus a `TextDecoder`. Split the text on blank lines (`"\n\n"`), and keep any partial event for the next read.
- **Stop button:** create an `AbortController`, pass its `signal` to `fetch`, and call `abort()`.
- **Markdown in replies:** `react-markdown`, plus `rehype-highlight` or `shiki` for code blocks.
- **Vercel AI SDK** (optional, later): its `useChat` hook does all of this for you. Build it by hand first so you know what it hides.

### Deploying

The frontend goes on Vercel. The FastAPI backend goes on a host that runs long-lived processes (Railway, Fly.io or Render), with a managed Postgres (Neon, Supabase or the host's own). Put `GROQ_API_KEY` in the host's environment variables, never in the code.

### Concepts

**Context window management** — every model has a token limit per request (131,072 for the Groq models above). Before each call, count the tokens in the history.
- **Sliding window:** drop the oldest messages until it fits. Simple, but the model forgets the start of the chat.
- **Summarize:** replace old messages with a short summary written by a cheap model. Keeps the gist, costs an extra call, and loses details.
- Always keep the system prompt, and drop a user message together with its reply.

**Why JSON output breaks** — the model writes one token at a time and nothing forces valid JSON. It may wrap the JSON in Markdown fences, add a sentence before it, leave out a field, or get cut off at `max_tokens`. The three fixes from weakest to strongest:
1. **Asking in the prompt.** It works most of the time, which isn't good enough.
2. **JSON mode** (`response_format={"type": "json_object"}`). The output is always valid JSON, but it may not match your schema. Works on Groq's Llama models.
3. **Strict structured outputs.** The provider restricts which tokens the model is allowed to pick, so the output must match your schema. On Groq this works with the gpt-oss models:

```python
resp = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=messages,
    response_format={"type": "json_schema",
                     "json_schema": {"name": "invoice", "strict": True, "schema": Invoice.model_json_schema()}},
)
```

Strict mode has extra rules for schemas (usually every field required and no extra properties). If Groq rejects your schema, add `model_config = ConfigDict(extra="forbid")` to each Pydantic model, and check Groq's structured outputs docs.

A **tool schema** (Phase 4) is a fourth way: define a fake tool whose arguments are your schema and read the arguments the model sends.

**Prompt engineering techniques**
- **Role and task:** say who the model is and exactly what to produce, including the format.
- **Few-shot examples:** show 2–5 input → output pairs. This is the strongest fix for format and tone problems.
- **XML tags:** wrap parts of the prompt in `<instructions>`, `<document>`, `<example>` so the model can't confuse your instructions with the data.
- **Step by step:** asking the model to reason before answering helps on multi-step problems, but costs more tokens.
- **Measure:** a prompt change is only better if it scores better on your test inputs.

**Reasoning models** — gpt-oss writes hidden reasoning tokens before its answer. On Groq, `reasoning_effort` (`"low"`, `"medium"`, `"high"`) controls how much. More effort is usually more accurate on hard problems, and slower and more expensive (reasoning tokens are billed as output).

**SSE vs WebSockets** — LLM output flows one way, server to client, which is exactly what SSE does over plain HTTP. It passes through proxies and load balancers easily. WebSockets are two-way and only needed for things like live voice.

---

## Phase 2 — Embeddings and semantic search

Install: `uv add sentence-transformers numpy scikit-learn umap-learn matplotlib "psycopg[binary]" pgvector`

### Tools and libraries

**sentence-transformers** — runs embedding models locally. The first call downloads the model from Hugging Face and caches it in `~/.cache/huggingface`.

```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("all-MiniLM-L6-v2")             # 384 numbers per text, fast
vecs = model.encode(sentences, normalize_embeddings=True)    # numpy array, shape (n, 384)
```

`BAAI/bge-small-en-v1.5` is also 384-dimensional and usually ranks better than MiniLM.

**Hugging Face Hub** — GitHub for models and datasets. Model names like `BAAI/bge-small-en-v1.5` are `organization/model` on huggingface.co.

**Ollama embeddings** — `ollama pull nomic-embed-text` (768 numbers per text). Call it through the same `openai` SDK, pointed at Ollama: `client.embeddings.create(model="nomic-embed-text", input=[...])`.

**NumPy** — fast arrays and math. `a @ b` is a dot product (or matrix multiply), `np.linalg.norm(a)` is a vector's length, and `np.argsort(-scores)` gives indices from highest score to lowest.

**PCA and UMAP** — squash 384 dimensions to 2 so you can plot them. PCA (`sklearn.decomposition.PCA`) is a fast linear projection. UMAP (`umap.UMAP`, from the `umap-learn` package) is slower but keeps neighbors close, so clusters show up better. Plot with matplotlib (`plt.scatter`).

**Postgres with pgvector, in Docker**

```bash
docker run -d --name pg -e POSTGRES_PASSWORD=dev -p 5432:5432 pgvector/pgvector:pg17
```

```sql
CREATE EXTENSION IF NOT EXISTS vector;
CREATE TABLE docs (id bigserial PRIMARY KEY, content text, category text, embedding vector(384));
CREATE INDEX ON docs USING hnsw (embedding vector_cosine_ops);

SELECT id, content, 1 - (embedding <=> $1) AS similarity      -- <=> is cosine distance
FROM docs
WHERE category = 'faq'                                          -- metadata filter
ORDER BY embedding <=> $1
LIMIT 10;
```

The distance operators: `<=>` cosine, `<->` Euclidean, `<#>` negative inner product.

**pgvector Python package** — `register_vector(conn)` (from `pgvector.psycopg`) lets you pass numpy arrays straight into queries as vectors.

**HNSW index** — HNSW builds a layered graph that links each vector to its near neighbors. A search starts at the top layer and hops toward the query, so it checks a small part of the table instead of every row. It's approximate: it can miss a true neighbor in exchange for a large speed-up. `m` and `ef_construction` (at build time) and `hnsw.ef_search` (at query time) trade recall against speed.

**Postgres full-text search** — keyword search that's built in:

```sql
ALTER TABLE docs ADD COLUMN tsv tsvector GENERATED ALWAYS AS (to_tsvector('english', content)) STORED;
CREATE INDEX ON docs USING gin (tsv);

SELECT id, ts_rank(tsv, q) AS rank
FROM docs, websearch_to_tsquery('english', $1) AS q
WHERE tsv @@ q
ORDER BY rank DESC
LIMIT 10;
```

`ts_rank` isn't quite BM25, the standard keyword-ranking formula. Extensions such as ParadeDB's `pg_search` add true BM25 if you want to compare.

### Concepts

**How embedding models are made** — a neural network is trained on huge numbers of related text pairs (a question and its answer, two paraphrases) so that related texts come out with similar vectors and unrelated ones don't. The vector is the model's internal representation of the text, squeezed into one fixed-length array.

**Cosine similarity** — cosine(a, b) = (a · b) ÷ (|a| × |b|). It's 1 for the same direction, 0 for unrelated, and negative for opposite. If the vectors are normalized (length 1), cosine equals the dot product, and all three distance measures rank results the same way.

**Why vector search misses exact strings** — an embedding captures meaning, not spelling. `ERR_4021` and `ERR_4012` look almost the same to an embedding model, while keyword search matches the exact token. That's why hybrid search exists.

**Reciprocal Rank Fusion (RRF)** — a way to merge two ranked lists without comparing their scores (cosine and `ts_rank` are on different scales). Each document scores the sum of 1 ÷ (k + rank) over each list it appears in, with k = 60 by convention. A document ranked 1st in one list and 3rd in the other scores 1/61 + 1/63. Sort by that score.

**hit@k** — the share of test queries whose expected result appears in the top k. hit@1 asks "was the best result first?"; hit@5 asks "was it on the first screen?"

**Switching embedding models** — vectors from different models live in different spaces and can't be compared. Changing models means re-embedding every row, so store the model name next to each vector.

---

## Phase 3 — RAG from scratch, with evals

Install: `uv add pymupdf beautifulsoup4 sentence-transformers "psycopg[binary]" pgvector` (later, optionally, `ragas`)

### How RAG fits together

```
OFFLINE (ingestion, run when documents change)
  files ─► parse to text ─► split into chunks ─► embed each chunk ─► store in pgvector

ONLINE (every question)
  question ─► hybrid search (top 30) ─► rerank (top 5) ─► prompt with numbered sources
           ─► model answers and cites [1] [2] ─► stream to UI with source links
```

### Tools and libraries

**PyMuPDF** (`import pymupdf`) — fast PDF text extraction, page by page. `pymupdf.open(path)` gives a document; `page.get_text()` gives that page's text. Keep the page number with every piece of text so citations can point to it.

**BeautifulSoup** (`beautifulsoup4`) — parses HTML. `BeautifulSoup(html, "html.parser").get_text()` gives the text, and `soup.find_all(["h1", "h2", "h3"])` gives the headings for section metadata.

**docling and unstructured** — heavier parsers that understand layout: tables, headings and multi-column pages. Try them when PyMuPDF's plain text loses structure that matters.

**Cross-encoder rerankers** (`sentence_transformers.CrossEncoder`)

```python
from sentence_transformers import CrossEncoder
reranker = CrossEncoder("BAAI/bge-reranker-base")
scores = reranker.predict([(question, chunk_text) for chunk_text in candidates])   # one score per pair
```

An embedding model (a bi-encoder) embeds the question and each chunk separately, which is fast because chunk vectors are computed ahead of time. A cross-encoder reads the question and the chunk together, so it judges relevance much better but must run once per pair at query time. So you retrieve about 30 candidates cheaply, then rerank them down to 5.

**hashlib** — `hashlib.sha256(text.encode()).hexdigest()` fingerprints a document. Store the hash, and on the next ingestion skip any document whose hash hasn't changed.

**Ragas** — a library of ready-made RAG metrics (faithfulness, answer relevance, context recall) that uses an LLM as the judge. Write your own metrics first, then compare.

### Concepts

**Chunking** — chunks are what you retrieve and paste into the prompt.
- **Too small** (around 100 tokens): a chunk lacks the context needed to answer.
- **Too big** (2,000 tokens): its embedding blurs several topics together, and you pay to send irrelevant text.
- **Overlap** (10–15%): a sentence cut at a boundary still appears whole in one chunk.
- **Structure-aware splitting** (by heading, then paragraph) keeps ideas together. Store the document title and section heading with every chunk.

**The grounded prompt**

```
Answer the question using only the sources below.
Cite sources like [1] after each claim. If the sources don't contain the answer, say "I don't know."

<sources>
[1] (handbook.pdf, page 4) Employees get 20 days of paid leave per year...
[2] (leave-policy.md, "Carry-over") Up to 5 unused days carry over...
</sources>

Question: How many leave days do I get?
```

Numbered sources let the UI turn `[1]` into a link to the chunk and its page.

**The "nothing relevant" case** — if the best similarity score is below a threshold you choose by looking at real scores, don't call the model. Say nothing was found. It's cheaper, and it removes a common cause of hallucination.

**Retrieval miss vs generation error** — for every wrong answer, check whether the right chunk was in what you retrieved.
- **No:** it's a retrieval problem. Fix chunking, search or reranking.
- **Yes:** it's a generation problem. Fix the prompt, the model, or the number of chunks you send.

**Golden set** — a fixed list of questions, each with its expected answer and source chunk, that every experiment is scored against. LLM-generated questions are fine if you review each one. Include questions the corpus can't answer; the right response is "I don't know."

**Retrieval metrics**
- **recall@k:** the share of questions whose correct chunk is in the top k. Recall@5 of 0.8 means 40 of 50 questions found it in the top 5.
- **MRR (mean reciprocal rank):** the average of 1 ÷ (position of the correct chunk), with 0 when it isn't found. Correct at position 1 counts 1, at position 2 counts 0.5, at position 4 counts 0.25. It rewards ranking the right chunk high.

**LLM-as-judge** — a model grades answers against a written rubric.
- Prefer pass/fail per criterion ("Is every claim supported by the sources? yes/no") over 1–10 scales, which drift.
- Use a strong judge (`openai/gpt-oss-120b`) that differs from the model that wrote the answer.
- Ask for a short reason before the verdict; it improves accuracy and helps you debug.
- Check the judge: label 20 answers yourself and measure how often it agrees with you. Fix the rubric until it agrees at least 80% of the time.

**Faithfulness vs correctness** — faithful means every claim is backed by the retrieved sources (no hallucination). Correct means it matches the expected answer. An answer can be faithful but wrong (the retrieved sources were the wrong ones) or correct but unfaithful (the model knew it from training).

**Query rewriting** — a cheap model rewrites the user's question before the search: expanding abbreviations, or turning "what about for contractors?" into a full question using the chat history.

**Contextual chunk headers** — before embedding, add the document title and section to each chunk ("Leave policy › Carry-over: Up to 5 days..."), or a sentence written by an LLM that places the chunk in its document. Anthropic's "Contextual Retrieval" post measured large drops in failed retrievals with this.

**Long-context baseline** — with a 131k-token window, small corpora fit whole in the prompt. Measure it: it's simple, often accurate, and much more expensive per question. RAG wins as the corpus grows.

---

## Phase 4 — Tool calling, agents and MCP

Install: `uv add mcp` (plus what your tools need, such as `psycopg` and `matplotlib`)

### Tool calling: what goes over the wire

You describe tools with JSON Schema in the request:

```python
tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Current weather for a city. Use for any question about weather now.",
        "parameters": {
            "type": "object",
            "properties": {"city": {"type": "string", "description": "City name, e.g. Pune"}},
            "required": ["city"],
        },
    },
}]
resp = client.chat.completions.create(model="openai/gpt-oss-120b", messages=messages, tools=tools)
```

If the model wants a tool, `resp.choices[0].message.tool_calls` is a list. Each call has an `id`, a `function.name`, and `function.arguments` as a JSON **string** (parse it with `json.loads`). Your code then:
1. Appends the assistant message with its tool calls to `messages`: `{"role": "assistant", "content": ..., "tool_calls": [...]}` with each call's `id`, `type` and `function`.
2. Runs each tool and appends `{"role": "tool", "tool_call_id": call.id, "content": json.dumps(result)}`.
3. Calls the model again with the longer `messages`.

When a response has no `tool_calls`, its `content` is the final answer. That loop is the agent; writing it is your Phase 4 exercise.

- **Parallel tool calls:** the model can request several tools in one turn. Run them all and append one `tool` message per call.
- **Tool descriptions are prompts.** Most agent failures trace back to a vague description or parameter name. Say when to use the tool and what it returns.

### Data analyst agent pieces

**Sample databases** — Chinook (a music store), Northwind (orders and suppliers) and Pagila (DVD rentals) all have Postgres versions on GitHub. They're realistic schemas with joins worth asking questions about.

**A read-only database user** — the agent's SQL runs as a user that can only read, with a time limit:

```sql
CREATE ROLE agent_ro LOGIN PASSWORD 'change-me';
GRANT CONNECT ON DATABASE chinook TO agent_ro;
GRANT USAGE ON SCHEMA public TO agent_ro;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO agent_ro;
ALTER ROLE agent_ro SET statement_timeout = '5s';
```

Also add a `LIMIT` to every query the agent runs, so one bad query can't return a million rows into the context.

**Charts** — the `make_chart` tool takes data and a chart type, draws it with matplotlib or plotly, and returns an image path or URL for the UI. The model never sees the image; it only gets told the chart was made.

### MCP (Model Context Protocol)

MCP is a standard way to offer tools and data to any AI app. You write one server and it works in every app that supports MCP.
- **Host:** the AI app (Claude Code, Claude Desktop, Cursor, or your own agent).
- **Client:** the part of the host that connects to one server.
- **Server:** your program. It exposes **tools** (actions), **resources** (readable data, like files or records) and **prompts** (reusable templates).
- **Transports:** `stdio` (the host starts your server as a subprocess, for local use) or Streamable HTTP (for remote servers).

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("orders")

@mcp.tool()
def get_order(order_id: int) -> dict:
    """Look up an order by its ID."""            # the docstring becomes the tool description
    return {"id": order_id, "status": "shipped"}

if __name__ == "__main__":
    mcp.run()                                     # stdio by default
```

- Add it to Claude Code with `claude mcp add orders -- uv run --directory /path/to/project server.py`.
- Debug it with the MCP Inspector (`npx @modelcontextprotocol/inspector`), which lets you list and call tools by hand.

### Frameworks (after you've built the loop yourself)

| Framework | What it is | Good for |
|---|---|---|
| LangGraph | Agents as a graph of steps with shared state; can pause, resume and wait for approval | Complex flows with branches and human approval |
| Pydantic AI | Typed agents in plain Python, with Pydantic for tool inputs and outputs | Clean, typed Python agents |
| OpenAI Agents SDK | Agents, handoffs between agents, and guardrails; works with other OpenAI-compatible providers | Multi-agent setups |
| Vercel AI SDK | TypeScript; tool loops and streaming UI hooks; `@ai-sdk/groq` for Groq | Agents inside a Next.js app |

### Concepts

**Workflows vs agents** — in a workflow, your code fixes the steps (classify → retrieve → answer). In an agent, the model chooses the next step. Workflows are cheaper, faster and easier to test, so use an agent only when the steps can't be known ahead of time. Anthropic's "Building effective agents" post names the common workflow patterns: prompt chaining, routing, parallel calls, orchestrator-workers, and evaluator-optimizer.

**How agents fail**
- Loops: calling the same tool again and again.
- Wrong tool, or invented arguments.
- Context bloat: huge tool outputs push out the instructions.
- Giving up early, or never stopping.

The fixes are step limits, cost budgets, cutting tool output down, clear tool descriptions, and evals.

**Human in the loop** — before any tool with real-world effects (sending, deleting, paying), pause and show the user exactly what will run, and continue only on approval.

**Prompt injection** — any text the agent reads (a web page, an email, a database row) can contain instructions, and the model can't reliably tell your instructions from the data's. Simon Willison's "lethal trifecta" is the dangerous combination: access to private data, exposure to untrusted content, and a way to send data out. Remove at least one of the three, use least-privilege tools, and require approval for outbound actions.

**Agent eval metrics** — success rate (did it get the right result?), average steps, cost per task, and latency, across a fixed set of tasks. Re-run them after every change to prompts or tools.

---

## Phase 5 — Production AI engineering

Install: `uv add langfuse` (promptfoo runs with `npx`, no install needed)

### Observability

**Langfuse** — open-source tracing for LLM apps. A **trace** is one user request; inside it, each LLM call (a **generation**) and each step (a **span**) is recorded with input, output, tokens, cost and latency. Use the free cloud tier or self-host it with Docker. The quickest start is a drop-in replacement for the OpenAI client:

```python
from langfuse.openai import OpenAI   # same client as before; every call is now traced
```

It needs `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY` and `LANGFUSE_HOST` in `.env`. Arize Phoenix and LangSmith are alternatives.

**Metrics that matter**
- **p50 and p95 latency:** the typical and the worst-5% response times.
- **Time to first token (TTFT):** how long until text starts appearing. With streaming, this is what users feel.
- Cost per request, error rate, and the thumbs-down rate.

### Evals in CI

**promptfoo** — a CLI that runs prompts × models × test cases and checks each output with assertions. Config lives in `promptfooconfig.yaml`:

```yaml
prompts:
  - file://prompts/answer.txt
providers:
  - groq:llama-3.1-8b-instant
defaultTest:
  options:
    provider: groq:openai/gpt-oss-120b        # judge model for llm-rubric checks
tests:
  - vars: { question: "How many leave days do I get?" }
    assert:
      - type: contains
        value: "20"
      - type: llm-rubric
        value: "Cites a source and does not invent policy"
```

Run it with `npx promptfoo@latest eval`, and view the results with `npx promptfoo@latest view`. Your own `pytest` evals work too: each test calls your pipeline and asserts on the metric.

**GitHub Actions** — run the evals on pull requests that change prompts or retrieval code. Store `GROQ_API_KEY` as a repository secret. A failing eval fails the job, so a worse prompt can't be merged.

**Prompts as files** — keep prompts in `prompts/*.txt` under git, not as strings in the code. Diffs then show exactly what changed, and evals can test any version.

### Cost and latency

**Prompt caching (Groq)** — Groq automatically caches the start of your prompt on gpt-oss models. When a new request begins with exactly the same tokens, the cached part costs 50% less and is processed faster. Put the fixed parts first (system prompt, tool definitions, shared documents) and the changing parts last (history, question). Check the `usage` object for how many tokens were cached.

**Model routing** — a cheap classifier (rules, or `llama-3.1-8b-instant`) decides whether a query is easy or hard, then sends it to the small or the big model. Measure quality and cost before and after.

**Caching answers** — an exact cache keys on the normalized query text. A semantic cache embeds the query and returns a saved answer if an earlier query is within a similarity threshold. That's faster and cheaper, but it can return the wrong answer for questions that sound alike and differ in a detail ("leave for contractors" vs "leave for employees"). Test the threshold.

**Batch APIs** — for offline jobs (ingestion, big eval runs), send many requests as one file and collect the results later, at a discount and outside your normal rate limits. Groq has one; see its docs.

### Reliability

- **Retries:** the `openai` SDK already retries on 429 and 5xx errors. Raise `max_retries` and set `timeout`: `OpenAI(..., max_retries=5, timeout=30)`. For your own retry rules, use the `tenacity` library.
- **Fallback:** hide the provider behind one function, and on repeated failures switch from Groq to Ollama.
- **Per-user limits:** a token bucket in Redis, like any API rate limit, plus a daily spend cap per user.

### Safety and security

**Llama Prompt Guard 2** (`meta-llama/llama-prompt-guard-2-86m` on Groq) — a small, fast classifier that flags text that looks like a prompt-injection or jailbreak attempt. Run it on user input and on retrieved documents before they reach your main model.

**gpt-oss-safeguard** (`openai/gpt-oss-safeguard-20b`) — a safety model that follows a policy you write ("flag requests for medical dosage advice") and classifies text against it.

**PII redaction** — Microsoft's Presidio library finds and masks names, emails, phone numbers and similar data before text is logged or sent to a model.

**OWASP Top 10 for LLM Applications** — the standard checklist. It covers prompt injection, sensitive information disclosure, supply chain, data and model poisoning, improper output handling, excessive agency, system prompt leakage, vector and embedding weaknesses, misinformation, and unbounded consumption.

### Context engineering

Deciding what goes into the context window for each call, in what order, and what gets left out.
- **Order:** fixed parts first (for caching), the most important instructions at the start or end rather than buried in the middle.
- **Compaction:** in long sessions, summarize old turns but keep key facts (names, decisions, IDs) word for word.
- **Memory:** save durable user facts ("prefers Python", "works in fintech") in a table, and retrieve the relevant ones into the prompt the way RAG does.

---

## Phase 6 — Build a GPT yourself

Install: `uv add torch transformers matplotlib`

### Tools and libraries

**PyTorch** — the main deep-learning library. It provides three things:
- **Tensors:** NumPy-style arrays that can live on a GPU.
- **Autograd:** it records every operation, so `loss.backward()` computes how each weight affected the loss.
- **`torch.nn`:** building blocks such as `nn.Linear`, `nn.Embedding` and `nn.LayerNorm`.

On Apple Silicon the GPU backend is called MPS:

```python
import torch
device = "mps" if torch.backends.mps.is_available() else "cpu"
x = torch.randn(4, 8, device=device)     # a 4×8 tensor of random numbers on the GPU
```

**Google Colab** — free hosted notebooks with a GPU (when one is available), for runs your Mac is too slow for.

**Karpathy's repos** — micrograd (autograd in about 100 lines), makemore (character-level models), and nanoGPT (a small, readable GPT). The videos build each one live, and the repos are there to compare against.

**Hugging Face Transformers** — loads pretrained models and their exact tokenizers. Good for looking inside a real model:

```python
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

tok = AutoTokenizer.from_pretrained("gpt2")
model = AutoModelForCausalLM.from_pretrained("gpt2")
ids = tok("The capital of France is", return_tensors="pt").input_ids
with torch.no_grad():
    logits = model(ids).logits[0, -1]               # one score per vocabulary token, for the next position
probs = torch.softmax(logits, dim=-1)
top = torch.topk(probs, 5)
for p, i in zip(top.values, top.indices):
    print(f"{tok.decode(i)!r}: {p:.1%}")             # the 5 most likely next tokens
```

This is the "probabilities for the next token" from the cheat sheet, made visible. (Groq's API doesn't return these probabilities, which is one reason to do this locally.)

### Concepts

**The training loop** — every model is trained by repeating four steps:
1. **Forward pass:** run a batch of text through the model to get predictions.
2. **Loss:** measure how wrong the predictions were. For language models this is cross-entropy against the actual next tokens.
3. **Backward pass:** `loss.backward()` computes the gradient (the direction to nudge each weight to lower the loss).
4. **Optimizer step:** `optimizer.step()` nudges every weight a little. AdamW is the standard optimizer.

Watch training and validation loss together: if training loss keeps falling while validation loss rises, the model is memorizing (overfitting).

**Tokenization (BPE)** — byte-pair encoding starts from single bytes and repeatedly merges the most frequent adjacent pair into a new token, until it reaches the vocabulary size. Common words become one token; rare words split into pieces. Tokenization explains several odd behaviors:
- Models are bad at counting letters, because they never see individual letters.
- Arithmetic on long numbers is unreliable, because numbers split unevenly.
- Non-English text costs more tokens.

**The embedding layer** — a lookup table with one learned vector per token ID (`nn.Embedding(vocab_size, d_model)`). It's the first layer of every LLM. Training moves related tokens close together, which is the same idea as your Phase 2 embeddings, but per token.

**Self-attention** — the step where tokens exchange information. Each token produces three vectors: a query ("what am I looking for?"), a key ("what do I contain?") and a value ("what do I pass on?").

```
Attention(Q, K, V) = softmax(Q·Kᵀ / √d) · V
```

Q·Kᵀ scores how relevant every token is to every other token. Softmax turns each row of scores into weights that add up to 1. Multiplying by V gives each token a weighted average of the others' values. A **causal mask** blocks attention to later tokens, so the model can't peek at the answer during training.

**The transformer block** — a GPT is the same block stacked N times:
1. **Multi-head attention:** several attention operations side by side, each free to learn a different relationship (grammar, references, topic).
2. **MLP:** a small feed-forward network applied to each token on its own; much of the model's knowledge is stored here.
3. **Residual connections:** each sub-layer adds its output to its input (`x = x + attn(x)`), so information and gradients flow through deep stacks.
4. **LayerNorm:** keeps the numbers in a stable range.

Position information is added too (learned position embeddings in GPT-2, RoPE in most newer models), because attention by itself ignores word order.

**Why context costs grow fast** — attention compares every token with every other one, so the work grows with the square of the length: twice the context is about four times the attention compute.

**KV cache** — when generating, keys and values for earlier tokens don't change, so they're stored and reused, and each new token only computes its own. That's why generation speeds up after the first token, and why long contexts use a lot of GPU memory.

**Sampling** — turning the final scores (logits) into one chosen token:
- **Greedy:** always pick the highest-probability token.
- **Temperature:** divide the logits by T before softmax. T < 1 sharpens the distribution; T > 1 flattens it.
- **Top-k:** keep only the k most likely tokens, then sample from them.
- **Top-p (nucleus):** keep the smallest set of tokens whose probabilities add up to p (for example 0.9), then sample from them.

Writing these is your Phase 6 exercise.

**From base model to assistant**
1. **Pretraining:** predict the next token over trillions of tokens of text. The result is a base model that continues text but doesn't follow instructions.
2. **Supervised fine-tuning (SFT):** train on examples of instructions and good responses. Now it acts like an assistant.
3. **Preference tuning (RLHF, DPO):** train on pairs of a better and a worse response, so it prefers the kind of answers people rate higher.

---

## Phase 7 — Open models and fine-tuning

Install (on Colab or a GPU machine): Unsloth's notebooks install what they need. Locally, `uv add transformers datasets peft trl` is enough to read and test code.

### Tools and libraries

**Open-weight models** — models whose trained weights you can download and run yourself (Llama, Qwen, Gemma, gpt-oss). Licenses differ: gpt-oss and most Qwen models are Apache 2.0, while Llama has its own community license. Check before using one commercially.

**GGUF and llama.cpp** — llama.cpp is a C++ engine that runs models fast on CPUs and Apple GPUs. GGUF is its single-file model format, which holds the weights (usually quantized) and the tokenizer. Ollama is built on llama.cpp and stores its models as GGUF.

**Quantization levels** — names like `Q4_K_M` and `Q8_0` give the bits per weight (4 or 8) and the method. Memory needed is roughly parameters × bits ÷ 8, plus overhead: 8B parameters at 4 bits is about 4–5 GB. Fewer bits are faster and smaller, at some cost in quality; measure it on your own test set.

**vLLM** — a high-throughput model server for GPUs. It's fast because of two techniques:
- **PagedAttention:** stores the KV cache in small pages, like virtual memory, so little memory is wasted.
- **Continuous batching:** new requests join the running batch at any step instead of waiting for the batch to finish.

`vllm serve <hugging-face-model-id>` starts an OpenAI-compatible API on port 8000, so your existing `openai` code works by changing `base_url`.

**Modal and RunPod** — rent GPUs by the second or hour. Modal is Python-first (decorate a function and it runs on a GPU); RunPod gives you a GPU machine.

**k6 and locust** — load-testing tools (k6 scripts are JavaScript, locust scripts are Python). Ramp up concurrent users and record throughput (tokens per second across all users) and latency.

**Hugging Face Datasets** — loads, splits and transforms training data (`load_dataset`, `train_test_split`).

**PEFT** — Hugging Face's library for parameter-efficient fine-tuning, including LoRA adapters.

**TRL** — Hugging Face's training library for language models. `SFTTrainer` does supervised fine-tuning; `DPOTrainer` does preference tuning.

**Unsloth** — a fine-tuning library built on PEFT and TRL that uses less memory and trains faster. Its free Colab notebooks (docs.unsloth.ai) cover the whole path: load a model → add LoRA → train → evaluate → export to GGUF.

### Concepts

**LoRA** — full fine-tuning updates every weight, which needs a lot of GPU memory. LoRA freezes the original weights and, for chosen weight matrices W, learns two thin matrices B and A so that the effective weight is W + B·A. With rank r (often 8–64), B·A has far fewer parameters than W, so training is cheap, and the result is a small adapter file you can keep separate or merge into the model.

**QLoRA** — LoRA on top of a base model loaded in 4-bit, so a 7–8B model can be fine-tuned on one free Colab GPU.

**Training data format** — chat examples (`system`, `user`, `assistant` messages) run through the model's **chat template**, the exact special-token format the model was trained on. Using the wrong template is one of the most common reasons a fine-tune fails.

**Train, validation and test splits** — train on one part, watch validation loss during training to pick the number of epochs and catch overfitting, and touch the test set only for the final comparison.

**Hyperparameters to vary** — LoRA rank, learning rate, epochs, and dataset size. Change one at a time and log the results, as in Phase 3.

**DPO (Direct Preference Optimization)** — training on pairs (prompt, chosen response, rejected response) that pushes the model toward the chosen style without training a separate reward model as RLHF does.

**When to fine-tune** — this is the decision your Phase 7 numbers should back up:

| Problem | Usually the fix |
|---|---|
| The model doesn't know your facts or documents | RAG |
| Output format or tone is inconsistent | A better prompt and few-shot examples, then fine-tuning |
| A narrow task needs a cheap, fast model at high volume | Fine-tune a small model |
| The model must follow a domain's style or jargon closely | Fine-tuning |
| The task needs current or frequently changing information | RAG; fine-tuning bakes in a snapshot |

**Throughput vs latency** — latency is how long one user waits; throughput is how many tokens per second the server delivers to everyone. Batching raises throughput, but each user's latency can rise. Tune for your traffic.

**Break-even vs an API** — monthly GPU cost ÷ monthly tokens served = your cost per token. Compare it with Groq's price per token for a similar model. Self-hosting usually only wins at high, steady volume, or when data can't leave your servers.

---

## Phase 8 — Capstone and job prep

### The capstone design doc (one page)

1. **Problem and users:** who it's for and what job it does.
2. **Requirements:** what it must do, and limits for latency, cost per query and accuracy.
3. **Architecture:** a diagram with frontend, backend, model calls, retrieval, tools and storage.
4. **Eval plan:** golden set, metrics and pass thresholds.
5. **Cost estimate:** tokens per request × requests per day × price.
6. **Risks:** hallucination, prompt injection, data privacy, provider outage, and how each is handled.

### LLM system design interviews: a structure to follow

1. **Clarify:** users, scale (documents, requests per second), latency and cost targets, accuracy needs.
2. **High-level design:** draw the big-picture diagram from the top of this guide, adapted to the problem.
3. **Deep dive on the data path:** ingestion, chunking, embeddings, index choice, hybrid search, reranking, permissions.
4. **Model choices:** which model for which step, routing, caching.
5. **Evals:** how you'd measure quality before launch and after it.
6. **Failure modes and safety:** hallucination, injection, outages, cost runaway.
7. **Scaling:** batching, caching, async ingestion, sharding the vector index.

### README for each portfolio project

A one-line pitch · demo link or GIF · architecture diagram · eval table with numbers · cost and latency per request · how to run it in 3 commands · limitations and what you'd do next.

### Resume bullets

Use the pattern: **what you built + the scale + the measured result + how.** For example: "Built RAG over 12k docs; raised recall@5 from 0.61 to 0.87 with hybrid search and reranking; cut cost per query 40% with prompt caching." Every number should come from your experiment logs.
