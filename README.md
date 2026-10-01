# ☤ Hermes Full Content Pipeline Blueprint

An autonomous end-to-end content collection, deduplication, AI filtering, drafting, review, and publishing pipeline built for **Hermes Agent** (Nous Research).

---

## 🚀 Quick Start (Running Locally for Free)

Hermes Agent and this pipeline are already installed, verified, and running on your system!

### 1. Run the Full Pipeline Live
```powershell
python "c:\AI Projects\hermes-pipeline\run_pipeline.py"
```

### 2. Autonomous Mode (Auto-Approve & Publish)
```powershell
python "c:\AI Projects\hermes-pipeline\run_pipeline.py" --auto-approve
```
*Outputs will be saved in `output/published/` and consolidated into `daily_digest_<YYYY-MM-DD>.md`.*

### 3. Interactive Review Queue
Review, approve, or reject pending drafts before publishing:
```powershell
python "c:\AI Projects\hermes-pipeline\run_pipeline.py" --review
```

### 4. Check Pipeline Metrics & Database Stats
```powershell
python "c:\AI Projects\hermes-pipeline\run_pipeline.py" --stats
```

---

## 🧠 Pipeline Architecture (The 6 Stages)

```
[1. Collection]  --> [2. Deduplication] --> [3. AI Filter] --> [4. AI Writer] --> [5. Review Queue] --> [6. Publishing]
 (RSS/Web Feeds)     (URL Hash + Jaccard)     (Materiality)     (Briefs+Social)    (queue/review/)     (output/published/)
```

1. **Stage 1: Content Collection (`collector.py`)**  
   Fetches raw items from configured RSS, Atom, ArXiv, TechCrunch, and Hacker News sources with zero paid dependencies.
2. **Stage 2: Deduplication Engine (`deduplicator.py`)**  
   Strips tracking query parameters (`utm_*`, `ref`), hashes canonical URLs, and computes word-set Jaccard similarity against a persistent SQLite database (`data/pipeline.db`). Duplicate stories across feeds or days are rejected instantly with 0 token waste.
3. **Stage 3: AI Filtering & Materiality Scoring (`ai_filter.py`)**  
   Evaluates stories against target technical topics (autonomous agents, open-source LLMs, cloud architecture) and discards clickbait/noise with a materiality threshold (1–10).
4. **Stage 4: Writing & Deliverable Synthesis (`writer.py`)**  
   Generates executive summaries (BLUF), 3 bulleted technical takeaways, and social broadcast drafts.
5. **Stage 5: Review Queue Staging (`review_queue.py`)**  
   Stages candidate drafts as Markdown documents with YAML metadata in `queue/review/` for human review.
6. **Stage 6: Publishing & Delivery (`publisher.py`)**  
   Archives approved articles into `output/published/`, generates a unified daily markdown briefing digest, and supports webhooks (Telegram/Discord).

---

## 🔑 Free LLM Keys & Inference

The pipeline works out of the box using built-in structural synthesis, but to unlock deep LLM reasoning completely for free:

1. **OpenRouter Free Tier (Recommended)**:
   - Go to [openrouter.ai/keys](https://openrouter.ai/keys) and generate a free API key (no credit card required).
   - Set in your environment or `.env`:
     ```powershell
     $env:OPENROUTER_API_KEY="sk-or-v1-..."
     ```
   - Free models available:
     - `meta-llama/llama-3.3-70b-instruct:free`
     - `google/gemini-2.0-flash-exp:free`
     - `qwen/qwen-2.5-coder-32b-instruct:free`
     - `deepseek/deepseek-r1:free`

2. **Google AI Studio (Gemini Free Tier)**:
   - Go to [aistudio.google.com](https://aistudio.google.com/) and grab a free Gemini API key.
   - Set in environment: `$env:GEMINI_API_KEY="AIzaSy..."`

3. **Local Models (Ollama)**:
   - Run `ollama run llama3.3` on your PC.
   - Point `base_url` in `config.json` to `http://localhost:11434/v1`.

---

## 🤖 Using with Hermes Agent Directly

This pipeline is installed as a native Hermes skill (`hermes-content-pipeline`).

To interact with Hermes in the terminal:
```powershell
cd "c:\AI Projects\hermes-agent"
.\activate.ps1
hermes
```

Inside Hermes, you can trigger the pipeline directly:
```text
/skill-hermes-content-pipeline
Run the content pipeline and generate today's briefing.
```
