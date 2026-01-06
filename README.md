# Document Analyzer Agent (Multi-Agent) — Applied AI Orchestration

A small, **applied AI** project that analyzes a folder of documents and produces a **decision-ready report**.

This repo demonstrates the practical skills most “Applied AI / ML Engineering” roles care about:
- **Orchestration** (multi-step pipeline, state passing)
- **Tool calling** (load + chunk documents via code tools)
- **Context management** (chunking + structured per-doc extraction)
- **Multi-agent feedback loop** (Analyzer → Reviewer → Revision)
- **Evaluation** (LLM-as-judge style scoring + issues)

---

## What it does

Given a folder of documents (`docs/`), the system:

1. **Loads documents** (`.txt`, `.md`)
2. **Chunks** long docs
3. **Extracts** per-document insights (summary, key points, risks, action items)
4. **Synthesizes** a single draft report across all documents
5. **Reviewer agent** critiques the draft (missing sections, unsupported claims, vagueness)
6. **Revises** the report using reviewer feedback
7. **Evaluates** the final report and saves a JSON score + improvement suggestions

Outputs are saved in `outputs/` as:
- `report_*.md` — final revised report
- `eval_*.json` — evaluation output

---

## Repository structure

```
.
├── agent.py        # Orchestration + LLM calls + multi-agent steps
├── tools.py        # Tool functions (load_documents, chunk_text)
├── prompts.py      # Prompts for extraction, synthesis, review, evaluation
├── main.py         # Entry point (runs pipeline, saves outputs)
├── docs/           # Input documents (your .txt/.md files)
└── outputs/        # Generated reports + eval JSON (ignored by git)
```

---

## Requirements

- Python 3.10+ recommended
- An LLM API key (set via environment variable)

---

## Setup

### 1) Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate
```

### 2) Install dependencies

If you have a `requirements.txt`:

```bash
pip install -r requirements.txt
```

Or install directly:

```bash
pip install openai python-dotenv pydantic
```

### 3) Add your API key

Create a `.env` file:

```env
OPENAI_API_KEY=your_key_here
```




## Run

```bash
python main.py
```

You’ll see:
- a preview of the report in terminal
- files written to `outputs/`

---

## How the “multi-agent” part works

This project uses **two agents**:

### Agent 1: Analyzer
- Extracts structured info per doc
- Synthesizes a draft report

### Agent 2: Reviewer
- Critiques the draft report for:
  - missing required sections
  - unsupported claims / hallucination risk
  - vague recommendations
  - logical inconsistencies
- Provides actionable fixes

Then Agent 1 revises using that feedback.

This is a common real-world pattern for improving reliability without changing the model.

---

## Evaluation

The pipeline includes an evaluation step that returns JSON with:
- `score` (0–10)
- `issues`
- `improvements`

This is a lightweight “LLM-as-judge” style check to:
- surface weak structure
- reduce overconfident claims
- guide iteration




## License

MIT (or choose your preferred license).
