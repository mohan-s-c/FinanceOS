"""Seed data for the mock adapters.

Mirrors apps/web/src/data/mock.ts so the backend serves the exact dataset the V1 UI
was built against. This is the offline "mock seam": deterministic, credential-free.
"""
from __future__ import annotations

import copy

_EXCEPTIONS: list[dict] = [
    {
        "id": "INV-44903", "vendor": "Sparkle Facilities", "vinit": "SF", "amount": 8420,
        "amountStr": "$8,420.00", "location": "SFO-Terminal-2",
        "reason": "Price variance vs PO (+12%)", "confidence": 61, "tone": "warn",
        "agent": "Exception Agent", "status": "Needs Review", "date": "May 28, 2026",
        "po": "PO-3391", "terms": "Net 30",
        "lineItems": [
            {"desc": "Janitorial service — May (Terminal 2)", "qty": 1, "unit": "$7,520.00", "total": "$7,520.00", "flag": False},
            {"desc": "After-hours deep clean — surcharge", "qty": 1, "unit": "$900.00", "total": "$900.00", "flag": True},
        ],
        "match": {
            "po": {"rate": "$7,520.00", "label": "Contracted rate"},
            "gr": {"rate": "Received", "label": "Goods receipt"},
            "inv": {"rate": "$8,420.00", "label": "Invoiced", "mismatch": True},
        },
        "reasoning": "Invoiced amount is 12% above the contracted rate in PO #PO-3391. Contract #C-2024-0142 allows a 5% variance ceiling; the after-hours surcharge line is not covered by the rate schedule.",
        "sources": [
            {"type": "Contract", "ref": "C-2024-0142", "note": "rate schedule"},
            {"type": "PO", "ref": "PO-3391", "note": "Terminal-2 janitorial"},
        ],
    },
    {
        "id": "INV-44871", "vendor": "SecureGuard Inc", "vinit": "SG", "amount": 15200,
        "amountStr": "$15,200.00", "location": "Multiple",
        "reason": "Missing PO reference", "confidence": 48, "tone": "bad",
        "agent": "Exception Agent", "status": "Needs Review", "date": "May 28, 2026",
        "po": "—", "terms": "Net 45",
        "lineItems": [
            {"desc": "Security staffing — 4 locations (May)", "qty": 4, "unit": "$3,200.00", "total": "$12,800.00", "flag": False},
            {"desc": "Equipment rental — monitoring", "qty": 1, "unit": "$2,400.00", "total": "$2,400.00", "flag": True},
        ],
        "match": {
            "po": {"rate": "Not found", "label": "PO reference", "mismatch": True},
            "gr": {"rate": "Partial", "label": "Goods receipt"},
            "inv": {"rate": "$15,200.00", "label": "Invoiced"},
        },
        "reasoning": "No purchase-order reference could be matched to this invoice. Vendor SecureGuard Inc has 3 active POs, but none match the line items or amount. Policy requires a PO for invoices above $10,000.",
        "sources": [
            {"type": "Policy", "ref": "AP-POL-07", "note": "PO threshold $10k"},
            {"type": "Vendor", "ref": "V-2207", "note": "SecureGuard Inc"},
        ],
    },
    {
        "id": "INV-44850", "vendor": "Metro Maintenance Co", "vinit": "MM", "amount": 2100,
        "amountStr": "$2,100.00", "location": "DEN-Lot-A",
        "reason": "Possible duplicate", "confidence": 55, "tone": "warn",
        "agent": "Anomaly Agent", "status": "Needs Review", "date": "May 27, 2026",
        "po": "PO-3288", "terms": "Net 30",
        "lineItems": [
            {"desc": "HVAC preventive maintenance — DEN Lot A", "qty": 1, "unit": "$2,100.00", "total": "$2,100.00", "flag": True},
        ],
        "match": {
            "po": {"rate": "$2,100.00", "label": "Contracted"},
            "gr": {"rate": "Received", "label": "Goods receipt"},
            "inv": {"rate": "$2,100.00", "label": "Invoiced", "mismatch": True},
        },
        "reasoning": "This invoice closely matches #INV-44612 (same vendor, amount, and service period) paid on May 12, 2026. 94% field similarity suggests a possible duplicate submission.",
        "sources": [
            {"type": "Invoice", "ref": "INV-44612", "note": "prior payment"},
            {"type": "PO", "ref": "PO-3288", "note": "DEN-Lot-A HVAC"},
        ],
    },
    {
        "id": "INV-44912", "vendor": "Brightline Electric", "vinit": "BE", "amount": 24680,
        "amountStr": "$24,680.00", "location": "LAX-Structure-3",
        "reason": "Amount exceeds approval limit", "confidence": 72, "tone": "warn",
        "agent": "Exception Agent", "status": "Needs Review", "date": "May 29, 2026",
        "po": "PO-3404", "terms": "Net 30",
        "lineItems": [
            {"desc": "EV charger install — 12 stalls", "qty": 12, "unit": "$1,840.00", "total": "$22,080.00", "flag": False},
            {"desc": "Permit & inspection fees", "qty": 1, "unit": "$2,600.00", "total": "$2,600.00", "flag": False},
        ],
        "match": {
            "po": {"rate": "$24,680.00", "label": "Contracted"},
            "gr": {"rate": "Received", "label": "Goods receipt"},
            "inv": {"rate": "$24,680.00", "label": "Invoiced"},
        },
        "reasoning": "3-way match is clean, but the total exceeds the $20,000 auto-approval limit for capital projects. Routed for human sign-off per policy AP-POL-11.",
        "sources": [
            {"type": "Policy", "ref": "AP-POL-11", "note": "capex sign-off $20k"},
            {"type": "PO", "ref": "PO-3404", "note": "LAX EV install"},
        ],
    },
    {
        "id": "INV-44888", "vendor": "Acme Janitorial", "vinit": "AJ", "amount": 3180,
        "amountStr": "$3,180.00", "location": "ORD-Garage-B",
        "reason": "Duplicate of #INV-44602", "confidence": 41, "tone": "bad",
        "agent": "Anomaly Agent", "status": "Needs Review", "date": "May 28, 2026",
        "po": "PO-3120", "terms": "Net 30",
        "lineItems": [
            {"desc": "Daily porter service — May (Garage B)", "qty": 1, "unit": "$3,180.00", "total": "$3,180.00", "flag": True},
        ],
        "match": {
            "po": {"rate": "$3,180.00", "label": "Contracted"},
            "gr": {"rate": "Received", "label": "Goods receipt"},
            "inv": {"rate": "$3,180.00", "label": "Invoiced", "mismatch": True},
        },
        "reasoning": "Near-identical to invoice #INV-44602 already paid this period (98% similarity on vendor, amount, service window). High-confidence duplicate — recommend reject.",
        "sources": [
            {"type": "Invoice", "ref": "INV-44602", "note": "paid May 9"},
            {"type": "Vendor", "ref": "V-1180", "note": "Acme Janitorial"},
        ],
    },
    {
        "id": "INV-44929", "vendor": "Pacific Signage", "vinit": "PS", "amount": 6740,
        "amountStr": "$6,740.00", "location": "SEA-Lot-C",
        "reason": "Tax jurisdiction mismatch", "confidence": 67, "tone": "warn",
        "agent": "Exception Agent", "status": "Needs Review", "date": "May 29, 2026",
        "po": "PO-3399", "terms": "Net 30",
        "lineItems": [
            {"desc": "Wayfinding signage refresh — SEA Lot C", "qty": 1, "unit": "$6,200.00", "total": "$6,200.00", "flag": False},
            {"desc": "Sales tax (10.25% — applied)", "qty": 1, "unit": "$540.00", "total": "$540.00", "flag": True},
        ],
        "match": {
            "po": {"rate": "$6,200.00", "label": "Pre-tax"},
            "gr": {"rate": "Received", "label": "Goods receipt"},
            "inv": {"rate": "$6,740.00", "label": "Invoiced", "mismatch": True},
        },
        "reasoning": "Tax rate applied (10.25%) corresponds to Seattle, but the ship-to location maps to a tax-exempt municipal lease. Expected tax is $0.00.",
        "sources": [
            {"type": "Lease", "ref": "L-SEA-0033", "note": "tax-exempt"},
            {"type": "PO", "ref": "PO-3399", "note": "SEA signage"},
        ],
    },
]

_DEPOSITS: list[dict] = [
    {"id": "DEP-90412", "amount": "$182,400", "payer": "JPMorgan ACH batch", "invoices": "14 invoices", "confidence": 97, "status": "Auto-applied", "tone": "ok", "agent": True},
    {"id": "DEP-90418", "amount": "$96,200", "payer": "Wells Fargo wire", "invoices": "3 invoices", "confidence": 93, "status": "Auto-applied", "tone": "ok", "agent": True},
    {"id": "DEP-90421", "amount": "$54,800", "payer": "Lockbox #2241", "invoices": "Suggested: 5", "confidence": 64, "status": "Needs Review", "tone": "warn", "agent": False},
    {"id": "DEP-90427", "amount": "$41,300", "payer": "Stripe payout", "invoices": "8 invoices", "confidence": 91, "status": "Auto-applied", "tone": "ok", "agent": True},
    {"id": "DEP-90433", "amount": "$22,150", "payer": "Check #88142", "invoices": "Suggested: 2", "confidence": 52, "status": "Needs Review", "tone": "warn", "agent": False},
    {"id": "DEP-90440", "amount": "$18,900", "payer": "ACH — unidentified", "invoices": "No match", "confidence": 31, "status": "Unmatched", "tone": "bad", "agent": False},
]


def seed_exceptions() -> list[dict]:
    """Fresh deep copy so each adapter instance owns independent mutable state."""
    return copy.deepcopy(_EXCEPTIONS)


def seed_deposits() -> list[dict]:
    return copy.deepcopy(_DEPOSITS)


# ---- Phase 1: raw AP documents for the 3-way match engine ----
_AP_POLICIES = {
    "po_required_above": 10000, "capex_signoff_above": 20000,
    "po_policy_ref": "AP-POL-07", "capex_policy_ref": "AP-POL-11",
}

_PAID_INVOICES = [
    {"id": "INV-44612", "vendor": "Metro Maintenance Co", "amount": 2100, "similarity": 94},
    {"id": "INV-44602", "vendor": "Acme Janitorial", "amount": 3180, "similarity": 98},
]

_AP_DOCUMENTS = [
    {  # clean — agent recommends approve; suggest-only still routes for confirm
        "invoice": {"id": "INV-44821", "vendor": "Cardinal HVAC", "vinit": "CH", "location": "ORD-Garage-A",
                    "date": "May 29, 2026", "terms": "Net 30", "po_ref": "PO-3360", "amount": 4200,
                    "lineItems": [{"desc": "Quarterly HVAC service — ORD Garage A", "qty": 1, "unit": 4200, "total": 4200, "flag": False}]},
        "po": {"id": "PO-3360", "total": 4200, "variance_ceiling": 0.05}, "gr": {"status": "received"}},
    {  # price variance +12%
        "invoice": {"id": "INV-44903", "vendor": "Sparkle Facilities", "vinit": "SF", "location": "SFO-Terminal-2",
                    "date": "May 28, 2026", "terms": "Net 30", "po_ref": "PO-3391", "amount": 8420,
                    "lineItems": [{"desc": "Janitorial service — May (Terminal 2)", "qty": 1, "unit": 7520, "total": 7520, "flag": False},
                                  {"desc": "After-hours deep clean — surcharge", "qty": 1, "unit": 900, "total": 900, "flag": True}]},
        "po": {"id": "PO-3391", "total": 7520, "variance_ceiling": 0.05, "contract_ref": "C-2024-0142"}, "gr": {"status": "received"}},
    {  # missing PO above threshold
        "invoice": {"id": "INV-44871", "vendor": "SecureGuard Inc", "vinit": "SG", "location": "Multiple",
                    "date": "May 28, 2026", "terms": "Net 45", "po_ref": None, "amount": 15200,
                    "lineItems": [{"desc": "Security staffing — 4 locations (May)", "qty": 4, "unit": 3200, "total": 12800, "flag": False},
                                  {"desc": "Equipment rental — monitoring", "qty": 1, "unit": 2400, "total": 2400, "flag": True}]},
        "po": None, "gr": {"status": "partial"}},
    {  # possible duplicate (94%)
        "invoice": {"id": "INV-44850", "vendor": "Metro Maintenance Co", "vinit": "MM", "location": "DEN-Lot-A",
                    "date": "May 27, 2026", "terms": "Net 30", "po_ref": "PO-3288", "amount": 2100,
                    "lineItems": [{"desc": "HVAC preventive maintenance — DEN Lot A", "qty": 1, "unit": 2100, "total": 2100, "flag": True}]},
        "po": {"id": "PO-3288", "total": 2100, "variance_ceiling": 0.05}, "gr": {"status": "received"}},
    {  # over approval limit (clean)
        "invoice": {"id": "INV-44912", "vendor": "Brightline Electric", "vinit": "BE", "location": "LAX-Structure-3",
                    "date": "May 29, 2026", "terms": "Net 30", "po_ref": "PO-3404", "amount": 24680,
                    "lineItems": [{"desc": "EV charger install — 12 stalls", "qty": 12, "unit": 1840, "total": 22080, "flag": False},
                                  {"desc": "Permit & inspection fees", "qty": 1, "unit": 2600, "total": 2600, "flag": False}]},
        "po": {"id": "PO-3404", "total": 24680, "variance_ceiling": 0.05}, "gr": {"status": "received"}},
    {  # high-confidence duplicate (98%)
        "invoice": {"id": "INV-44888", "vendor": "Acme Janitorial", "vinit": "AJ", "location": "ORD-Garage-B",
                    "date": "May 28, 2026", "terms": "Net 30", "po_ref": "PO-3120", "amount": 3180,
                    "lineItems": [{"desc": "Daily porter service — May (Garage B)", "qty": 1, "unit": 3180, "total": 3180, "flag": True}]},
        "po": {"id": "PO-3120", "total": 3180, "variance_ceiling": 0.05}, "gr": {"status": "received"}},
    {  # tax jurisdiction mismatch
        "invoice": {"id": "INV-44929", "vendor": "Pacific Signage", "vinit": "PS", "location": "SEA-Lot-C",
                    "date": "May 29, 2026", "terms": "Net 30", "po_ref": "PO-3399", "amount": 6740, "tax": 540,
                    "lineItems": [{"desc": "Wayfinding signage refresh — SEA Lot C", "qty": 1, "unit": 6200, "total": 6200, "flag": False},
                                  {"desc": "Sales tax (10.25% — applied)", "qty": 1, "unit": 540, "total": 540, "flag": True}]},
        "po": {"id": "PO-3399", "total": 6200, "variance_ceiling": 0.05, "tax_exempt": True, "lease_ref": "L-SEA-0033"}, "gr": {"status": "received"}},
]


def seed_ap_documents() -> list[dict]:
    return copy.deepcopy(_AP_DOCUMENTS)


def ap_policies() -> dict:
    return dict(_AP_POLICIES)


def paid_invoices() -> list[dict]:
    return copy.deepcopy(_PAID_INVOICES)


# ---- Phase 2: raw AR data for the cash-application agent ----
_AR_INVOICES = [
    {"id": "AR-7741", "customer": "Hertz Corporate Mobility", "amount": 24600, "age": 40},
    {"id": "AR-7726", "customer": "Hertz Corporate Mobility", "amount": 18200, "age": 30},
    {"id": "AR-7702", "customer": "Hertz Corporate Mobility", "amount": 12000, "age": 20},
    {"id": "AR-8042", "customer": "Northwind Hotels", "amount": 26800, "age": 25},
    {"id": "AR-8010", "customer": "Cobalt Retail Group", "amount": 9400, "age": 35},
    {"id": "AR-8011", "customer": "Cobalt Retail Group", "amount": 13750, "age": 15},
    {"id": "AR-8101", "customer": "Lattice Logistics", "amount": 48200, "age": 62},
    {"id": "AR-8120", "customer": "Vertex Events LLC", "amount": 19900, "age": 31},
]

_RAW_DEPOSITS = [
    {"id": "DEP-90412", "amount": 54800, "payer": "JPMorgan ACH batch", "customer": "Hertz Corporate Mobility", "remittance": ["AR-7741", "AR-7726", "AR-7702"]},
    {"id": "DEP-90418", "amount": 26800, "payer": "Wells Fargo wire", "customer": None, "remittance": []},
    {"id": "DEP-90421", "amount": 23150, "payer": "Lockbox #2241", "customer": "Cobalt Retail Group", "remittance": []},
    {"id": "DEP-90427", "amount": 30000, "payer": "Stripe payout", "customer": "Hertz Corporate Mobility", "remittance": []},
    {"id": "DEP-90433", "amount": 9000, "payer": "Check #88142", "customer": "Cobalt Retail Group", "remittance": []},
    {"id": "DEP-90440", "amount": 18900, "payer": "ACH — unidentified", "customer": None, "remittance": []},
]


def seed_ar_invoices() -> list[dict]:
    return copy.deepcopy(_AR_INVOICES)


def seed_raw_deposits() -> list[dict]:
    return copy.deepcopy(_RAW_DEPOSITS)


# ---- Phase 3: overdue AR accounts for the collections agent ----
_OVERDUE = [
    {"account": "Lattice Logistics", "loc": "DFW-Lot-E", "balance": 48200, "days": 62},
    {"account": "Cobalt Retail Group", "loc": "PHX-Garage-A", "balance": 31450, "days": 47},
    {"account": "Northwind Hotels", "loc": "SEA-Structure-1", "balance": 26800, "days": 38},
    {"account": "Vertex Events LLC", "loc": "LAS-Lot-B", "balance": 19900, "days": 31},
    {"account": "Harborview Medical", "loc": "BOS-Garage-C", "balance": 14300, "days": 22},
    {"account": "Summit Airlines Crew", "loc": "DEN-Lot-A", "balance": 11750, "days": 18},
]


def seed_overdue_accounts() -> list[dict]:
    return copy.deepcopy(_OVERDUE)


# ---- Phase 3: anomaly/leakage signals ----
_ANOMALY_SIGNALS = [
    {"id": 1, "sev": "high", "title": "Duplicate invoice cluster — Acme Janitorial", "sub": "3 invoices with 94–98% field similarity submitted within 17 days across ORD & SFO.", "risk": 9540, "agent": "Anomaly Detection Agent", "icon": "copy"},
    {"id": 2, "sev": "high", "title": "Validation abuse pattern — DEN-Lot-A", "sub": "218 sessions validated with the same merchant code in a 9-day window. Expected baseline ≈ 40.", "risk": 14200, "agent": "Anomaly Detection Agent", "icon": "ticket"},
    {"id": 3, "sev": "med", "title": "Failed-charge pattern — exit lane 4, SFO-T2", "sub": "Charge-capture failures up 3.4× vs. trailing 30-day mean. Possible LPR camera fault.", "risk": 6820, "agent": "Anomaly Detection Agent", "icon": "camera"},
    {"id": 4, "sev": "med", "title": "Rate discrepancy — Brightline Electric", "sub": "Invoiced labor rate $1,840/stall vs. contracted $1,720/stall across 12 line items.", "risk": 1440, "agent": "Reconciliation Agent", "icon": "trending"},
    {"id": 5, "sev": "low", "title": "Off-contract vendor spend — Pacific Signage", "sub": "Two POs issued outside the approved vendor list for signage category.", "risk": 3260, "agent": "Anomaly Detection Agent", "icon": "flag"},
]
_LEAKAGE_TREND = [0.12, 0.31, 0.44, 0.58, 0.71, 0.86, 0.97, 1.08, 1.19, 1.3]
_LEAKAGE_MONTHS = ["Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar", "Apr", "May"]


def seed_anomaly_signals() -> list[dict]:
    return copy.deepcopy(_ANOMALY_SIGNALS)


def leakage_series() -> tuple[list[float], list[str]]:
    return (list(_LEAKAGE_TREND), list(_LEAKAGE_MONTHS))
