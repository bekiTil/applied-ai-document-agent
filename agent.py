from __future__ import annotations
import json
from dataclasses import dataclass, field
from typing import List, Dict
import os
from openai import OpenAI
from prompts import (
    SYSTEM_INSTRUCTIONS,
    EXTRACT_PROMPT,
    SYNTHESIS_PROMPT,
    EVAL_PROMPT,
    REVIEW_REPORT
)
from tools import chunk_text
from dotenv import load_dotenv


load_dotenv()



client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"),base_url="https://api.groq.com/openai/v1",)  

@dataclass
class AgentState:
    task: str
    docs: List[Dict] = field(default_factory=list)
    per_doc_extracts: List[Dict] = field(default_factory=list)
    draft_report: str = ""
    review_feedback: str = ""
    final_report: str = ""
    eval_json: Dict = field(default_factory=dict)


def llm_markdown(instructions: str, user_input: str, model: str = "openai/gpt-oss-20b") -> str:
    # Responses API (recommended for new projects) :contentReference[oaicite:2]{index=2}
    resp = client.responses.create(
        model=model,
        instructions=instructions,
        input=user_input,
    )
    return resp.output_text or ""

def llm_json(instructions: str, user_input: str, model: str = "openai/gpt-oss-20b") -> Dict:
    text = llm_markdown(instructions, user_input, model=model).strip()
    # Best-effort JSON parse
    try:
        return json.loads(text)
    except Exception:
        return {"score": 0, "issues": ["Invalid JSON from evaluator"], "improvements": [text[:500]]}

def step_extract(state: AgentState) -> AgentState:
    extracts = []
    for d in state.docs:
        chunks = chunk_text(d["text"])
        # If doc is long, extract each chunk then merge (simple approach)
        chunk_extracts = []
        for idx, ch in enumerate(chunks, start=1):
            out = llm_markdown(
                SYSTEM_INSTRUCTIONS,
                f"{EXTRACT_PROMPT}\n\nDocument: {d['name']} (chunk {idx}/{len(chunks)})\n\n{ch}"
            )
            chunk_extracts.append(out)

        merged = llm_markdown(
            SYSTEM_INSTRUCTIONS,
            f"Merge the following chunk-level extracts into ONE coherent extract for document '{d['name']}'. "
            f"Keep the same headings.\n\n" + "\n\n---\n\n".join(chunk_extracts)
        )

        extracts.append({"name": d["name"], "extract": merged})
    state.per_doc_extracts = extracts
    return state

def step_synthesize(state: AgentState) -> AgentState:
    joined = "\n\n---\n\n".join(
        [f"Document: {x['name']}\n\n{x['extract']}" for x in state.per_doc_extracts]
    )
    report = llm_markdown(
        SYSTEM_INSTRUCTIONS,
        f"Task: {state.task}\n\n{SYNTHESIS_PROMPT}\n\nPer-document extracts:\n\n{joined}"
    )
    state.final_report = report
    return state

def step_review(state: AgentState) -> AgentState:
    feedback = llm_markdown(
        SYSTEM_INSTRUCTIONS,
        f"{REVIEW_REPORT}\n\nREPORT TO REVIEW:\n{state.draft_report}",
        model="llama-3.1-8b-instant"
    )
    state.review_feedback = feedback

    print("feedback,    ", feedback )
    return state
def step_revise(state: AgentState) -> AgentState:
    revised = llm_markdown(
        SYSTEM_INSTRUCTIONS,
        f"""You previously wrote this report:

{state.draft_report}

A reviewer gave the following feedback:

{state.review_feedback}

Revise the report by:
- Fixing issues
- Adding missing sections
- Making recommendations more specific
- Removing unsupported claims

Return the FULL revised report in markdown.
"""
    )
    state.final_report = revised
    return state

def step_evaluate(state: AgentState) -> AgentState:
    eval_obj = llm_json(
        "You are a strict evaluator.",
        f"{EVAL_PROMPT}\n\nREPORT:\n{state.final_report}"
    )
    state.eval_json = eval_obj
    return state

def run_agent(task: str, docs: List[Dict]) -> AgentState:
    state = AgentState(task=task, docs=docs)
    state = step_extract(state)
    state = step_synthesize(state)
    state.draft_report = state.final_report

    state = step_review(state)
    state = step_revise(state)

    state = step_evaluate(state)
    return state
