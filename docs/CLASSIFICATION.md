# Non-LLM Transaction Classification Architecture

## 1. Overview
The classification engine operates strictly without generative AI or external LLM APIs. It combines:
1. **Layer 0 — Text Normalization & Canonicalization**: Strips card masks, long transaction reference hashes, and normalizes payment rail prefixes (PayID, Osko, EFTPOS, BACS, Faster Payments, Direct Debit).
2. **Layer 1 — Deterministic Rule Engine**: Inverted index of high-frequency merchant patterns with word-boundary matching and direction constraints.
3. **Layer 2 — Traditional Machine Learning**: Calibrated scikit-learn TF-IDF + Logistic Regression baseline model.
4. **Layer 3 — Confidence-Driven Human Review**: Transparent uncertainty gating. When confidence falls below configured thresholds ($\ge 0.80$ for Rules, $\ge 0.60$ for ML), transactions fall back to `Other / Unclassified` and are flagged with `LOW_CONFIDENCE`.

---

## 2. Leakage-Free Benchmark Evaluation

To prevent data leakage, evaluation is conducted against a separate, hand-curated **held-out test set** featuring merchants and narrations not present in the training set or rule keyword dictionary.

### Comparative Metrics (Held-Out Benchmark)

| Classification Strategy | Accuracy | Macro F1-Score | Weighted F1-Score | Coverage at Threshold |
| :--- | :---: | :---: | :---: | :---: |
| **Rule-Only** | 43.7% | 0.382 | 0.415 | 43.7% |
| **ML-Only (Baseline)** | 68.8% | 0.625 | 0.671 | 100.0% |
| **Hybrid (Rules + Calibrated ML)** | **81.2%** | **0.784** | **0.805** | **87.5%** |

*Note: Benchmark evaluation is automated via `evaluate_on_benchmark()` in `backend/app/classification/hybrid.py`.*

---

## 3. Decision Hierarchy

```text
Incoming Transaction
         │
         ▼
[Is Manual User Edit?] ──Yes──► Keep Manual Category (Confidence: 100%)
         │ No
         ▼
[Rule Match >= 0.80?]  ──Yes──► Assign Rule Category (Source: RULE)
         │ No
         ▼
[ML Proba >= 0.60?]    ──Yes──► Assign ML Category (Source: ML)
         │ No
         ▼
Assign "Other / Unclassified" (Source: UNCLASSIFIED, Flag: LOW_CONFIDENCE)
```
