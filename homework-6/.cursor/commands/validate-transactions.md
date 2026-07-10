---
description: Validate sample transactions without running the full pipeline.
---

Validate all transactions in `homework-6/sample-transactions.json` without processing them.

Steps:
1. Run validator in dry-run mode:
   - `cd homework-6 && py agents/transaction_validator.py --dry-run --input sample-transactions.json`
2. Report total count, valid count, invalid count, and rejection reasons.
3. Present results as a compact list/table.
