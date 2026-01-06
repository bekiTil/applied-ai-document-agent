from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path

from tools import load_documents
from agent import run_agent

def main():
    docs = load_documents("docs")
    if not docs:
        raise SystemExit("No docs found in ./docs (add .txt or .md files)")

    task = "Analyze the documents and produce a decision-ready report for a busy manager."
    state = run_agent(task=task, docs=docs)

    outdir = Path("outputs")
    outdir.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    report_path = outdir / f"report_{ts}.md"
    eval_path = outdir / f"eval_{ts}.json"

    report_path.write_text(state.final_report, encoding="utf-8")
    eval_path.write_text(json.dumps(state.eval_json, indent=2), encoding="utf-8")

    print("\n=== REPORT ===\n")
    print(state.final_report[:3000])
    print("\n=== EVAL ===\n")
    print(json.dumps(state.eval_json, indent=2))
    print(f"\nSaved:\n- {report_path}\n- {eval_path}")

if __name__ == "__main__":
    main()
