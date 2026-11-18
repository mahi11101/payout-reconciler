# Payout reconciliation checker

When you pay thousands of contributors or vendors, the hard part isn't sending the money. It's proving every payout matches what you owed. This script compares the internal ledger with the provider's payout report and surfaces only the rows a person actually needs to look at.

## What it flags

- **Missing**: in the ledger but never paid
- **Unexpected**: paid but not in the ledger
- **Amount mismatch**: beyond a 0.01 rounding tolerance
- **Currency mismatch**
- **Failed** at the provider

Exact matches and tiny rounding differences are cleared automatically.

## Run it

```bash
python reconcile.py ledger.csv payouts.csv exceptions.csv
```

```
6 ledger rows, 6 payouts, 3 matched, 4 exceptions
  P1003    Contributor C    Amount mismatch (-13500.00)
  P1004    Contributor D    Payout failed at provider
  P1005    Contributor E    Missing: in ledger, not paid
  P1007    Contributor G    Unexpected: paid, not in ledger
```

No dependencies, Python 3.9+. Uses `Decimal` so money is never rounded by floating-point maths. Sample data is made up.

Built by Mahesh Kumar with AI coding tools.
