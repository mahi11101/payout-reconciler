"""Payout reconciliation checker.

Matches payouts sent by the payment provider against the internal ledger and
reports only the real exceptions, so a person reviews 3 rows instead of 3,000.

Usage: python reconcile.py ledger.csv payouts.csv exceptions.csv
"""
import csv
import sys
from decimal import Decimal

TOLERANCE = Decimal("0.01")  # rounding differences under 1 paisa/cent are ignored


def load(path, key="payout_id"):
    with open(path, newline="") as f:
        return {r[key]: r for r in csv.DictReader(f)}


def reconcile(ledger, payouts):
    exceptions = []
    for pid, row in ledger.items():
        sent = payouts.get(pid)
        expected = Decimal(row["amount"])
        if sent is None:
            exceptions.append((pid, row["payee"], expected, "", "Missing: in ledger, not paid"))
            continue
        paid = Decimal(sent["amount"])
        if abs(paid - expected) > TOLERANCE:
            exceptions.append((pid, row["payee"], expected, paid, f"Amount mismatch ({paid - expected:+})"))
        elif sent.get("currency") != row.get("currency"):
            exceptions.append((pid, row["payee"], expected, paid, "Currency mismatch"))
        elif sent.get("status", "").lower() == "failed":
            exceptions.append((pid, row["payee"], expected, paid, "Payout failed at provider"))
    for pid, sent in payouts.items():
        if pid not in ledger:
            exceptions.append((pid, sent.get("payee", ""), "", Decimal(sent["amount"]), "Unexpected: paid, not in ledger"))
    return exceptions


if __name__ == "__main__":
    ledger_path, payout_path = (sys.argv[1:3] if len(sys.argv) > 2 else ("ledger.csv", "payouts.csv"))
    out = sys.argv[3] if len(sys.argv) > 3 else "exceptions.csv"
    ledger, payouts = load(ledger_path), load(payout_path)
    ex = reconcile(ledger, payouts)
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["payout_id", "payee", "expected", "paid", "reason"])
        w.writerows(ex)
    matched = len(ledger) - sum(1 for e in ex if not e[4].startswith("Unexpected"))
    print(f"{len(ledger)} ledger rows, {len(payouts)} payouts, {matched} matched, {len(ex)} exceptions")
    for e in ex:
        print(f"  {e[0]:<8} {e[1]:<16} {e[4]}")
