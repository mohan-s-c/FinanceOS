"""Build the Finance OS / APAR V2 user manual PDF (reportlab).
Embeds screenshots from demo/screens/<name>.png when present; otherwise draws a
labeled placeholder. Re-run after dropping the PNGs in to get the final PDF.
"""
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, PageBreak,
                                Image, Table, TableStyle, HRFlowable, ListFlowable, ListItem)

HERE = os.path.dirname(os.path.abspath(__file__))
SCREENS = os.path.join(HERE, "screens")
OUT = os.path.join(HERE, "FinanceOS-V2-User-Manual.pdf")

INK = colors.HexColor("#1B150F")
AMBER = colors.HexColor("#9A6A12")
MUTE = colors.HexColor("#6B6358")
BAND = colors.HexColor("#F4F1EA")
LINE = colors.HexColor("#D9D2C5")
USABLE_W = letter[0] - 2 * inch  # ~6.5in

ss = getSampleStyleSheet()
def S(name, **kw):
    return ParagraphStyle(name, parent=ss["Normal"], **kw)

title_s = S("t", fontName="Helvetica-Bold", fontSize=26, leading=30, textColor=INK)
sub_s   = S("s", fontName="Helvetica", fontSize=13, leading=18, textColor=MUTE)
h1_s    = S("h1", fontName="Helvetica-Bold", fontSize=17, leading=21, textColor=INK, spaceBefore=6, spaceAfter=8)
h2_s    = S("h2", fontName="Helvetica-Bold", fontSize=12.5, leading=16, textColor=AMBER, spaceBefore=10, spaceAfter=4)
body_s  = S("b", fontName="Helvetica", fontSize=10.5, leading=15.5, textColor=INK, spaceAfter=6)
cap_s   = S("c", fontName="Helvetica-Oblique", fontSize=9, leading=12, textColor=MUTE, alignment=TA_CENTER, spaceBefore=4)
small_s = S("sm", fontName="Helvetica", fontSize=9, leading=13, textColor=MUTE)
ey_s    = S("ey", fontName="Helvetica-Bold", fontSize=8.5, leading=11, textColor=AMBER)

def img(fname, caption, w=USABLE_W):
    path = os.path.join(SCREENS, fname)
    flow = []
    if os.path.exists(path):
        iw, ih = ImageReader(path).getSize()
        flow.append(Image(path, width=w, height=w * ih / iw))
    else:
        t = Table([[Paragraph(f"Screenshot placeholder<br/><font size=8>save <b>demo/screens/{fname}</b></font>", cap_s)]],
                  colWidths=[w], rowHeights=[2.0 * inch])
        t.setStyle(TableStyle([("BOX", (0,0),(-1,-1), 0.8, LINE), ("BACKGROUND",(0,0),(-1,-1), BAND),
                               ("VALIGN",(0,0),(-1,-1),"MIDDLE")]))
        flow.append(t)
    flow.append(Paragraph(caption, cap_s))
    flow.append(Spacer(1, 10))
    return flow

def bullets(items):
    return ListFlowable([ListItem(Paragraph(x, body_s), leftIndent=10, value="•") for x in items],
                        bulletType="bullet", start="•", leftIndent=12)

story = []

# ---- cover ----
story += [Spacer(1, 1.6*inch),
          Paragraph("Finance OS / APAR", title_s),
          Paragraph("Accounts Payable &amp; Receivable — autonomous, supervised by exception", sub_s),
          Spacer(1, 10), HRFlowable(width=USABLE_W, color=AMBER, thickness=2),
          Spacer(1, 10),
          Paragraph("Product Overview &amp; User Guide", S("v", fontName="Helvetica-Bold", fontSize=14, textColor=INK)),
          Paragraph("Version 2.0 · research build · June 2026", small_s),
          Spacer(1, 24),
          Paragraph("An AI/agentic finance back office: software agents ingest invoices and payments, "
                    "perform 3-way matching, apply incoming cash, drive collections, and flag anomalies — "
                    "while a human analyst supervises by exception rather than doing manual data entry.", body_s),
          PageBreak()]

# ---- 1. overview ----
story += [Paragraph("1 · Overview", h1_s),
          Paragraph("The problem", h2_s),
          Paragraph("Accounts Payable and Receivable are high-volume, rules-heavy, and audited. A mid-size "
                    "company processes tens of thousands of invoices a month — today largely by hand: keying "
                    "data, reconciling spreadsheets, three-way-matching, chasing overdue accounts. It is slow, "
                    "error-prone, and where money quietly leaks through duplicate payments and missed terms.", body_s),
          Paragraph("What Finance OS does", h2_s),
          Paragraph("Finance OS turns that back office into a supervised, agentic system. Each workflow has a "
                    "dedicated agent that does the routine work and escalates only what needs judgment. The "
                    "analyst — our persona, Dana Okafor — reviews exceptions and tunes the agents instead of "
                    "processing every line.", body_s),
          Paragraph("Principles", h2_s)]
story += [bullets([
    "<b>Supervise by exception.</b> Agents auto-handle the clean majority; humans see only what's ambiguous or high-value.",
    "<b>Deterministic where it matters, AI where it helps.</b> Rules do the math (matching, reconciliation); a language model only explains the gray-area cases — it never approves a payment.",
    "<b>Every action gated &amp; logged.</b> Auto-actions fire only above an agent's confidence threshold; everything lands in an immutable audit trail with its reason and source documents.",
    "<b>Your data stays yours.</b> The reasoning model can run locally (Ollama / vLLM); connectors are vendor-swappable; the system runs offline on a mock seam.",
])]
story += [Spacer(1, 6),
          Paragraph("Who it's for", h2_s),
          Paragraph("AP/AR analysts and controllers in finance teams; the platform is generic and resellable "
                    "to any organization once hosted.", body_s),
          PageBreak()]

# ---- 2. walkthrough ----
story += [Paragraph("2 · Guided walkthrough", h1_s),
          Paragraph("The product is seven screens grouped as Overview, Accounts Payable, Accounts Receivable, "
                    "and Autonomy. Each runs on live, persisted, agent-computed data.", body_s),
          Spacer(1, 8)]

steps = [
 ("2.1  Command Center", "01-command-center.png",
  "The home view: outcome KPIs a CFO cares about (touchless rate, open exceptions, close cycle, cash position, leakage recovered).",
  "The Command Center opens with fleet-level metrics and an <b>Agents at work</b> strip showing every agent live, its mode and threshold, and today's touchless rate. AP and AR health tiles and a 30-day cash-flow forecast give an at-a-glance read of the back office."),
 ("2.2  Exception Queue (AP)", "02-exception-queue.png",
  "What the AP Matching agent couldn't safely auto-approve — the only invoices a human needs to touch.",
  "The agent ingests invoices, runs a deterministic three-way match (PO ↔ goods receipt ↔ invoice), and auto-clears the clean ones. The queue holds the exceptions — price variances, missing POs, duplicates, over-limit and tax-jurisdiction cases — each with a flag reason, amount at risk, confidence, and the agent that raised it."),
 ("2.3  Reviewing an exception", "03-exception-drawer.png",
  "The detail drawer: 3-way match evidence, the agent's recommendation, and an AI-drafted explanation.",
  "Opening an exception shows the PO/GR/invoice side-by-side with the mismatch highlighted, the line items, a confidence ring, and the contract/policy it's grounded in. The agent gives a recommendation (Accept in one click, or Override). <b>Explain with AI</b> drafts a controls-analyst narrative and a suggested disposition; the model badge shows which model produced it (local Ollama or hosted), and only the discrepancy — never the vendor master — is sent to it."),
 ("2.4  Cash Application (AR)", "04-cash-application.png",
  "Incoming deposits matched to open invoices — exact, remittance-hint, then fuzzy.",
  "The Cash Application agent reconciles deposits against open AR invoices. High-confidence matches auto-apply; the rest — partial matches, unidentified ACH — come here for a human, pre-filled with the agent's proposed invoice set and confidence."),
 ("2.5  Collections", "06-collections.png",
  "Risk-ranked overdue accounts with agent-drafted outreach (a human sends).",
  "The Collections agent scores each overdue account by days-past-due and balance, prioritizes them, and drafts the outreach message — but a person sends anything customer-facing. The risk distribution shows the book at a glance."),
 ("2.6  Anomalies &amp; Leakage", "07-anomalies.png",
  "Where the money comes back: duplicate clusters, validation abuse, charge-capture faults, off-contract spend.",
  "The Anomaly agent watches the ledger and surfaces severity-ranked signals with the dollars at risk, plus a leakage-recovered trend — the ROI story for the program."),
 ("2.7  Agents console — autonomy", "08-agents.png",
  "Every agent in one place; promote each from suggest-only to auto as it earns trust.",
  "Each agent shows its pipeline (intake → match → decide → act → escalate), recent decisions with reasons and sources, and an editable confidence threshold. Agents start in <b>suggest-only</b> mode and are dialed toward auto-action; a global kill switch forces everything back to suggest-only in an incident. Changing autonomy requires the Controller role (segregation of duties)."),
 ("2.8  Analytics", "09-analytics.png",
  "Historical trends plus a live-this-session block computed from the audit trail.",
  "Touchless rate, cost per invoice, close-cycle time, DSO, and human-override rate over time — alongside a live panel that reflects this session's real agent activity. Promote an agent to auto and you watch the touchless rate climb and the open queue fall."),
 ("2.9  Agent &amp; Audit Trail", "10-audit.png",
  "The SOX story: an immutable, queryable log of every action and who took it.",
  "Every auto-action, human resolution, threshold change, and AI explanation — with the model that produced it — is appended here, never edited. Confidence thresholds are co-owned with the Controller. When an auditor asks 'why was this paid,' the answer is one click with the evidence attached."),
]
for i,(title, fn, cap, body) in enumerate(steps):
    story += [Paragraph(title, h2_s), Paragraph(body, body_s)] + img(fn, cap)
    if i in (2,5):   # break after drawer & anomalies to keep images tidy
        story.append(PageBreak())

# Importing your data (text)
story += [Paragraph("2.10  Importing your data (CSV / ERP)", h2_s),
          Paragraph("Finance OS reads real data, not just the bundled sample. Download a CSV template from the "
                    "Exception Queue or Cash Application screen, fill in your invoices, POs, receipts, open "
                    "invoices, or deposits, and import — the agents re-run on your numbers in seconds (duplicate "
                    "invoices are auto-detected by vendor and amount). The same connector interface that reads a "
                    "CSV today plugs into NetSuite, SAP, or QuickBooks tomorrow; bank feeds and OCR intake sit "
                    "behind the same seam, and nothing is hard-wired to a vendor.", body_s),
          PageBreak()]

# ---- Appendix A: architecture ----
story += [Paragraph("Appendix A · Technical architecture", h1_s),
          Paragraph("Four layers, front to back, with a shared schema and an event/audit log cross-cutting all of them.", body_s),
          Spacer(1, 6)]
arch = [["apps/web", "React 19 + Vite + Zustand — the seven-screen UI (Espresso theme), typed against the shared schema"],
        ["services/api", "FastAPI BFF — read models + command endpoints, auth/RBAC, audit write-through, CSV ingestion"],
        ["services/agents", "Agent layer — deterministic engines (3-way match, cash match, risk scoring) + LLM reasoning, under confidence-threshold gates"],
        ["packages/shared", "Domain schema (types) shared by web and API"],
        ["packages/connectors", "Abstract ERP / bank / ingestion contracts + adapters (mock, file/CSV); vendor SDKs slot in here"],
        ["persistence", "stdlib sqlite3 — exceptions, deposits, collections, append-only audit, agent config (Postgres-ready behind repo.py)"]]
at = Table([[Paragraph(f"<b>{a}</b>", small_s), Paragraph(b, small_s)] for a,b in arch], colWidths=[1.5*inch, USABLE_W-1.5*inch])
at.setStyle(TableStyle([("BACKGROUND",(0,0),(0,-1), BAND), ("BOX",(0,0),(-1,-1),0.5,LINE),
                        ("INNERGRID",(0,0),(-1,-1),0.5,LINE), ("VALIGN",(0,0),(-1,-1),"TOP"),
                        ("TOPPADDING",(0,0),(-1,-1),7),("BOTTOMPADDING",(0,0),(-1,-1),7),
                        ("LEFTPADDING",(0,0),(-1,-1),8),("RIGHTPADDING",(0,0),(-1,-1),8)]))
story += [at, Spacer(1, 12),
          Paragraph("The agent pipeline", h2_s),
          Paragraph("Intake → Enrich &amp; Match → Decide → (Auto-act | Escalate) → Audit. Clean cases are decided "
                    "by rules; ambiguous ones get an LLM-drafted rationale. Confidence is compared to the agent's "
                    "threshold: above it (and only when not in suggest-only mode) the agent auto-acts via a "
                    "connector and logs; below it the item escalates to the analyst, pre-filled with the "
                    "recommendation.", body_s),
          Paragraph("Security &amp; control", h2_s)]
story += [bullets([
    "<b>RBAC</b> — Analyst (least-privilege) and Controller; tuning autonomy and resolving items ≥ $20k require Controller (segregation of duties).",
    "<b>Immutable audit</b> — append-only; covers agent and human actions, including which model produced each AI explanation.",
    "<b>Secrets</b> via environment / secret manager, never in the repo; parameterized SQL; CORS allow-list; global kill switch.",
    "<b>Data minimization</b> — the LLM sees only the discrepancy; it can run fully local (Ollama / vLLM) so data never leaves your infrastructure.",
])]
story += [PageBreak()]

# ---- Appendix B: built so far ----
story += [Paragraph("Appendix B · What's built so far", h1_s),
          Paragraph("Delivered (Phases 0–4 of the design spec, plus LLM reasoning and ingestion):", body_s)]
story += [bullets([
    "<b>Foundation</b> — monorepo, shared schema, FastAPI, connector contracts + mock seam; all seven screens wired to the API.",
    "<b>AP exceptions</b> — deterministic tolerance-aware 3-way match engine; AP Matching agent (suggest-only); persistence + immutable audit.",
    "<b>AR cash application</b> — deposit→invoice match engine (exact / remittance / batch / fuzzy); apply flow.",
    "<b>Collections, Anomalies, Analytics</b> — risk-scored outreach drafts; severity-ranked leakage detection; analytics with a live-session block from the audit trail.",
    "<b>Autonomy</b> — promote an agent suggest-only → auto and it auto-acts on threshold-clearing items, moving the touchless rate.",
    "<b>Hardening</b> — Auth + RBAC with segregation of duties; security review (SECURITY.md).",
    "<b>Data in</b> — File/CSV ERP adapter + AP/AR/Collections CSV upload with templates and auto duplicate detection.",
    "<b>LLM-assisted reasoning</b> — swappable provider (local Ollama / hosted / offline narrator), data-minimized, audit-logged with the model used.",
    "<b>Quality</b> — 16 unit tests across the match engines; clean web build.",
])]
story += [Spacer(1, 6), Paragraph("Roadmap (deferred — needs real credentials / infra)", h2_s)]
story += [bullets([
    "Real vendor-SDK ERP / bank / OCR adapters (the swap seam is a single file).",
    "Real identity provider + JWT, TLS / rate limiting, Postgres, async intake for volume, and deployment.",
])]
story += [Spacer(1, 14), HRFlowable(width=USABLE_W, color=LINE), Spacer(1,6),
          Paragraph("Finance OS / APAR — V2 research build. Generated from the live product.", small_s)]

def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8); canvas.setFillColor(MUTE)
    canvas.drawString(inch, 0.6*inch, "Finance OS / APAR — V2 User Guide")
    canvas.drawRightString(letter[0]-inch, 0.6*inch, f"{doc.page}")
    canvas.restoreState()

doc = SimpleDocTemplate(OUT, pagesize=letter, topMargin=0.9*inch, bottomMargin=0.9*inch,
                        leftMargin=inch, rightMargin=inch, title="Finance OS / APAR — V2 User Guide")
doc.build(story, onFirstPage=footer, onLaterPages=footer)
print("PDF written:", OUT)
missing = [s[1] for s in steps if not os.path.exists(os.path.join(SCREENS, s[1]))]
print("screenshots present:", len(steps)-len(missing), "/", len(steps), "| missing:", missing)
