"""Run the triage evaluation harness and print a scorecard.

    $env:PYTHONPATH="."; python scripts\\run_eval.py
"""
from app.schemas import Category, Priority
from app.eval.harness import (
    load_golden,
    run_eval,
    accuracy,
    confusion_matrix,
    per_class_metrics,
)

CATEGORIES = [c.value for c in Category]
PRIORITIES = [p.value for p in Priority]
PRI_ORDINAL = {p: i for i, p in enumerate(PRIORITIES)}  # Low=0 .. Critical=3
_ABBR = {
    "Billing": "Bill",
    "Technical": "Tech",
    "Account": "Acct",
    "Feature Request": "Feat",
    "Complaint": "Comp",
}


def main() -> None:
    golden = load_golden()
    print(f"Loaded {len(golden)} golden examples. Running triage (batched)...\n")
    rows = run_eval(golden)

    # --- Headline accuracy ---
    cat_acc = accuracy(rows, "exp_cat", "pred_cat")
    pri_acc = accuracy(rows, "exp_pri", "pred_pri")
    within1 = sum(
        1 for r in rows
        if abs(PRI_ORDINAL[r["exp_pri"]] - PRI_ORDINAL[r["pred_pri"]]) <= 1
    ) / len(rows)

    print("== ACCURACY ==")
    print(f"  Category            : {cat_acc:6.1%}")
    print(f"  Priority (exact)    : {pri_acc:6.1%}")
    print(f"  Priority (within 1) : {within1:6.1%}  (priority is ordinal + subjective)")

    # --- Per-category precision / recall / F1 ---
    cm = confusion_matrix(rows, "exp_cat", "pred_cat", CATEGORIES)
    pcm = per_class_metrics(cm, CATEGORIES)
    print("\n== PER-CATEGORY ==")
    print(f"  {'category':<16} {'prec':>5} {'recall':>7} {'F1':>5} {'n':>3}")
    for c in CATEGORIES:
        m = pcm[c]
        print(f"  {c:<16} {m['precision']:>5.2f} {m['recall']:>7.2f} "
              f"{m['f1']:>5.2f} {m['support']:>3}")

    # --- Confusion matrix (rows = expected, cols = predicted) ---
    print("\n== CONFUSION MATRIX (row=expected, col=predicted) ==")
    print("  exp\\pred " + "".join(f"{_ABBR[c]:>6}" for c in CATEGORIES))
    for e in CATEGORIES:
        cells = "".join(f"{cm[e][p]:>6}" for p in CATEGORIES)
        print(f"  {_ABBR[e]:<7} {cells}")

    # --- Misclassifications (the interesting part to read) ---
    misses = [r for r in rows if r["exp_cat"] != r["pred_cat"]]
    print(f"\n== CATEGORY MISSES ({len(misses)}/{len(rows)}) ==")
    for r in misses:
        print(f"  expected {r['exp_cat']:<16} got {r['pred_cat']:<16} | {r['text'][:55]}")


if __name__ == "__main__":
    main()
