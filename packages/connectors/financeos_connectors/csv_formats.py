"""CSV formats for ERP/file ingestion — parsers + downloadable templates.

Shared by the File ERP adapter and the API ingest endpoints so the upload format and
the file-boot format are identical. Stdlib csv only.
"""
from __future__ import annotations

import csv
import io

DEFAULT_POLICIES = {
    "po_required_above": 10000, "capex_signoff_above": 20000,
    "po_policy_ref": "AP-POL-07", "capex_policy_ref": "AP-POL-11",
}


def _num(v, default=0.0):
    v = (v or "").strip().replace("$", "").replace(",", "")
    try:
        return float(v)
    except ValueError:
        return default


def _bool(v) -> bool:
    return str(v or "").strip().lower() in {"1", "true", "yes", "y"}


def _rows(text: str) -> list[dict]:
    return list(csv.DictReader(io.StringIO(text.lstrip("﻿"))))


def parse_ap_invoices(text: str) -> tuple[list[dict], list[dict]]:
    """Return (ap_documents, paid_invoices). One CSV row = one invoice + its PO/GR summary."""
    docs, paid = [], []
    for r in _rows(text):
        inv_id = (r.get("invoice_id") or "").strip()
        if not inv_id:
            continue
        amount = _num(r.get("amount"))
        tax = _num(r.get("tax"))
        base = round(amount - tax, 2)
        vendor = (r.get("vendor") or "").strip()
        line_items = [{"desc": f"{vendor} — invoice", "qty": 1, "unit": base, "total": base, "flag": False}]
        if tax > 0:
            line_items.append({"desc": "Tax", "qty": 1, "unit": tax, "total": tax, "flag": True})
        po_ref = (r.get("po_ref") or "").strip() or None
        po_total = _num(r.get("po_total"), default=-1)
        po = None
        if po_ref and po_total >= 0:
            po = {"id": po_ref, "total": po_total,
                  "variance_ceiling": _num(r.get("variance_ceiling"), default=0.05) or 0.05,
                  "contract_ref": (r.get("contract_ref") or "").strip() or None,
                  "tax_exempt": _bool(r.get("tax_exempt")),
                  "lease_ref": (r.get("lease_ref") or "").strip() or None}
        invoice = {"id": inv_id, "vendor": vendor, "vinit": (r.get("vinit") or vendor[:2]).strip().upper(),
                   "location": (r.get("location") or "—").strip(), "date": (r.get("date") or "").strip(),
                   "terms": (r.get("terms") or "").strip(), "po_ref": po_ref, "amount": amount,
                   "tax": tax, "lineItems": line_items}
        docs.append({"invoice": invoice, "po": po, "gr": {"status": (r.get("gr_status") or "received").strip() or "received"}})
        dup_of = (r.get("dup_of") or "").strip()
        if dup_of:
            paid.append({"id": dup_of, "vendor": vendor, "amount": amount, "similarity": int(_num(r.get("dup_similarity"), default=95))})
    return docs, paid


def parse_ar_open_invoices(text: str) -> list[dict]:
    out = []
    for r in _rows(text):
        iid = (r.get("invoice_id") or "").strip()
        if not iid:
            continue
        out.append({"id": iid, "customer": (r.get("customer") or "").strip(),
                    "amount": _num(r.get("amount")), "age": int(_num(r.get("age")))})
    return out


def parse_ar_deposits(text: str) -> list[dict]:
    out = []
    for r in _rows(text):
        did = (r.get("deposit_id") or "").strip()
        if not did:
            continue
        rem = (r.get("remittance") or "").replace(";", " ").split()
        out.append({"id": did, "amount": _num(r.get("amount")), "payer": (r.get("payer") or "").strip(),
                    "customer": (r.get("customer") or "").strip() or None, "remittance": rem})
    return out


TEMPLATES: dict[str, str] = {
    "ap": (
        "invoice_id,vendor,vinit,location,date,terms,po_ref,amount,tax,po_total,variance_ceiling,gr_status,contract_ref,tax_exempt,lease_ref,dup_of,dup_similarity\n"
        "INV-5001,Sparkle Facilities,SF,SFO-Terminal-2,Jun 02 2026,Net 30,PO-5001,8420,0,7520,0.05,received,C-2024-0142,false,,,\n"
        "INV-5002,SecureGuard Inc,SG,Multiple,Jun 02 2026,Net 45,,15200,0,,0.05,partial,,false,,,\n"
        "INV-5003,Cardinal HVAC,CH,ORD-Garage-A,Jun 03 2026,Net 30,PO-5003,4200,0,4200,0.05,received,,false,,,\n"
        "INV-5004,Acme Janitorial,AJ,ORD-Garage-B,Jun 03 2026,Net 30,PO-5004,3180,0,3180,0.05,received,,false,,INV-4460,98\n"
    ),
    "ar-invoices": (
        "invoice_id,customer,amount,age\n"
        "AR-9001,Hertz Corporate Mobility,24600,40\n"
        "AR-9002,Hertz Corporate Mobility,18200,30\n"
        "AR-9003,Northwind Hotels,26800,25\n"
    ),
    "ar-deposits": (
        "deposit_id,payer,amount,customer,remittance\n"
        "DEP-5001,JPMorgan ACH batch,42800,Hertz Corporate Mobility,AR-9001;AR-9002\n"
        "DEP-5002,Wells Fargo wire,26800,,\n"
        "DEP-5003,ACH — unidentified,18900,,\n"
    ),
}
