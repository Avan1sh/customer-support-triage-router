"""Evaluation harness: score triage predictions against a golden labeled set.

Design choices that matter:
  - We eval the BASE triage_chain (app/triage.py), NOT the RAG triage. Why:
    the golden tickets resemble tickets already in the vector store, so RAG
    could RETRIEVE a near-identical answer and inflate the score. That's
    'data leakage' / contamination. Eval the model's core ability, cleanly.
  - Pure-Python metrics (no sklearn) so you SEE how accuracy / precision /
    recall / F1 are actually computed.
"""
import json
from pathlib import Path

from app.triage import triage_chain

GOLDEN_PATH = Path("data/eval/golden_set.jsonl")


def load_golden(path: Path = GOLDEN_PATH) -> list[dict]:
    """Read the JSONL golden set (one labeled example per line)."""
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def run_eval(examples: list[dict]) -> list[dict]:
    """Triage every example (batched, concurrency-capped) and pair with labels."""
    inputs = [{"ticket": ex["text"]} for ex in examples]
    # max_concurrency caps parallel calls so we don't trip Groq's rate limit.
    preds = triage_chain.batch(inputs, config={"max_concurrency": 5})
    return [
        {
            "text": ex["text"],
            "exp_cat": ex["category"],
            "pred_cat": pred.category.value,
            "exp_pri": ex["priority"],
            "pred_pri": pred.priority.value,
        }
        for ex, pred in zip(examples, preds)
    ]


def accuracy(rows: list[dict], exp_key: str, pred_key: str) -> float:
    """Fraction of predictions that exactly match the label."""
    if not rows:
        return 0.0
    return sum(1 for r in rows if r[exp_key] == r[pred_key]) / len(rows)


def confusion_matrix(rows, exp_key, pred_key, labels) -> dict:
    """cm[expected][predicted] = count. The diagonal is correct predictions."""
    cm = {e: {p: 0 for p in labels} for e in labels}
    for r in rows:
        cm[r[exp_key]][r[pred_key]] += 1
    return cm


def per_class_metrics(cm: dict, labels: list[str]) -> dict:
    """Precision/recall/F1 per class, derived from the confusion matrix.

    precision = TP / (everything PREDICTED as this class)  [column sum]
    recall    = TP / (everything ACTUALLY this class)       [row sum]
    F1        = harmonic mean of precision and recall
    """
    out = {}
    for c in labels:
        tp = cm[c][c]
        predicted = sum(cm[e][c] for e in labels)  # column total
        actual = sum(cm[c][p] for p in labels)     # row total
        precision = tp / predicted if predicted else 0.0
        recall = tp / actual if actual else 0.0
        f1 = (
            2 * precision * recall / (precision + recall)
            if (precision + recall)
            else 0.0
        )
        out[c] = {"precision": precision, "recall": recall, "f1": f1, "support": actual}
    return out
