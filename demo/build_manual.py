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
USABLE_W = letter[0] - 1 * inch  # 0.5in margins each side -> 7.5in

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
          Paragraph("Accounts Payable &amp; Receivable — autonomously managed by AI agents, human-supervised by exception", sub_s),
          Spacer(1, 10), HRFlowable(width=USABLE_W, color=AMBER, thickness=2),
          Spacer(1, 10),
          Paragraph("Product Overview &amp; User Guide", S("v", fontName="Helvetica-Bold", fontSize=14, leading=20, textColor=INK)),
          Spacer(1, 6),
          Paragraph("Version 2.0 · research build · June 2026", small_s),
          Spacer(1, 16),
          Paragraph("Built &amp; authored by <b>Mohan Chandolu</b>", S("auth", fontName="Helvetica", fontSize=12, leading=16, textColor=INK)),
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
          Spacer(1, 10)]

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
 ("2.5  Applying a deposit", "05-cash-drawer.png",
  "The AR detail drawer: the agent's proposed invoice set for a deposit, ready for one-click apply.",
  "Opening a deposit shows the remittance match — the open invoices the agent believes it pays, each with its own confidence — summing to the deposit amount. Apply posts the reconciliation to the AR sub-ledger and the audit trail; the human is the check on the agent, not the data-entry clerk."),
 ("2.6  Collections", "06-collections.png",
  "Risk-ranked overdue accounts with agent-drafted outreach (a human sends).",
  "The Collections agent scores each overdue account by days-past-due and balance, prioritizes them, and drafts the outreach message — but a person sends anything customer-facing. The risk distribution shows the book at a glance."),
 ("2.7  Anomalies &amp; Leakage", "07-anomalies.png",
  "Where the money comes back: duplicate clusters, validation abuse, charge-capture faults, off-contract spend.",
  "The Anomaly agent watches the ledger and surfaces severity-ranked signals with the dollars at risk, plus a leakage-recovered trend — the ROI story for the program."),
 ("2.8  Agents console — autonomy", "08-agents.png",
  "Every agent in one place; promote each from suggest-only to auto as it earns trust.",
  "Each agent shows its pipeline (intake → match → decide → act → escalate), recent decisions with reasons and sources, and an editable confidence threshold. Agents start in <b>suggest-only</b> mode and are dialed toward auto-action; a global kill switch forces everything back to suggest-only in an incident. Changing autonomy requires the Controller role (segregation of duties)."),
 ("2.9  Analytics", "09-analytics.png",
  "Historical trends plus a live-this-session block computed from the audit trail.",
  "Touchless rate, cost per invoice, close-cycle time, DSO, and human-override rate over time — alongside a live panel that reflects this session's real agent activity. Promote an agent to auto and you watch the touchless rate climb and the open queue fall."),
 ("2.10  Agent &amp; Audit Trail", "10-audit.png",
  "The SOX story: an immutable, queryable log of every action and who took it.",
  "Every auto-action, human resolution, threshold change, and AI explanation — with the model that produced it — is appended here, never edited. Confidence thresholds are co-owned with the Controller. When an auditor asks 'why was this paid,' the answer is one click with the evidence attached."),
]
for i,(title, fn, cap, body) in enumerate(steps):
    story += [Paragraph(title, h2_s), Paragraph(body, body_s)] + img(fn, cap)
    story.append(Spacer(1, 8))

# Importing your data (text)
story += [Paragraph("2.11  Importing your data (CSV / ERP)", h2_s),
          Paragraph("Finance OS reads real data, not just the bundled sample. Download a CSV template from the "
                    "Exception Queue or Cash Application screen, fill in your invoices, POs, receipts, open "
                    "invoices, or deposits, and import — the agents re-run on your numbers in seconds (duplicate "
                    "invoices are auto-detected by vendor and amount). The same connector interface that reads a "
                    "CSV today plugs into NetSuite, SAP, or QuickBooks tomorrow; bank feeds and OCR intake sit "
                    "behind the same seam, and nothing is hard-wired to a vendor.", body_s),
          Spacer(1, 10)]

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
story += [Spacer(1, 12),
          Paragraph("The reasoning model — why local Ollama + Qwen2.5", h2_s),
          Paragraph("Deterministic rules own every disposition; the language model is used only to <b>explain</b> "
                    "gray-area exceptions in a controls-analyst voice and suggest a disposition — it never "
                    "approves a payment. Because the input is financial data, the model runs <b>locally</b> rather "
                    "than calling an outside API.", body_s)]
story += [bullets([
    "<b>Ollama (local / self-hosted).</b> Ollama runs open-weight models on your own hardware behind an OpenAI-compatible endpoint (it also works against vLLM/TGI). Data never leaves your infrastructure — the key requirement for AP/AR documents — and there's no per-token cost or external dependency.",
    "<b>Qwen2.5:3b is the default.</b> Among locally-runnable models it hit the best latency/quality balance on CPU: clean three-way-match and duplicate-invoice narratives at roughly 7–8 seconds per explanation. The larger Qwen2.5 (7B) is higher quality but about 3× slower, and the 0.5B variant is fast but unreliable — so the 3B is the sweet spot for a responsive reviewer drawer.",
    "<b>Repeatable for audit.</b> The model runs at temperature 0 so the same exception yields the same explanation, and the exact model string (e.g. <i>ollama:qwen2.5:3b</i>) is written to the audit trail with every explanation.",
    "<b>Data-minimized.</b> Only the structured discrepancy is sent to the model — never the vendor or customer master.",
    "<b>Swappable &amp; safe to fail.</b> A single setting (LLM_PROVIDER) switches between local Ollama, a hosted provider (Anthropic), or a dependency-free offline narrator; if the chosen model is unreachable the system falls back to the offline narrator and never errors.",
])]
story += [Spacer(1, 12),
          Paragraph("Technology glossary", h2_s),
          Paragraph("Plain-English notes on the tools named above, for non-engineering readers.", body_s),
          Spacer(1, 6)]
glos = [
 ["React", "A JavaScript library for building user interfaces out of reusable components; it keeps what's on screen in sync with the underlying data."],
 ["TypeScript", "JavaScript with type checking added — it catches mistakes (e.g. a wrong field name) before the app runs, which matters in a finance UI."],
 ["Vite", "The build tool/dev server for the front-end: it bundles the React/TypeScript code into the fast static site the browser loads."],
 ["Zustand", "A small state-management library for React — the single place the UI keeps shared data (the current queue, the logged-in role) so screens stay consistent."],
 ["Python", "The programming language the back-end and the agents are written in; widely used for data and AI work."],
 ["FastAPI", "A Python framework for building web APIs — the layer the browser calls to read data and send commands (approve, apply, send)."],
 ["BFF (Backend-for-Frontend)", "An API shaped specifically for this UI: it returns exactly the data each screen needs rather than raw database tables."],
 ["SQLite", "A lightweight, file-based database (no separate server) used here to store exceptions, deposits, and the audit log; swappable for Postgres later."],
 ["Postgres", "A full client–server relational database for production scale — the upgrade path from SQLite when volume grows."],
 ["Ollama / vLLM", "Runtimes that let a large language model run on your own hardware, so the AI explanations work without sending data to an outside service. The default model here is Qwen2.5:3b."],
 ["LLM", "Large Language Model — the AI that drafts the plain-English explanation of a gray-area exception (it explains, it never approves a payment)."],
 ["RBAC", "Role-Based Access Control — permissions tied to a role (Analyst vs Controller) so only authorized people can change thresholds or approve large items."],
 ["CORS", "A browser security rule controlling which web origins may call the API; locked to an allow-list here."],
 ["ERP", "Enterprise Resource Planning system (e.g. NetSuite, SAP, QuickBooks) — the system of record for invoices and payments the connectors read from."],
 ["3-way match", "The AP control that checks a purchase order, the goods receipt, and the invoice agree before paying — the core rule the AP agent automates."],
]
gt = Table([[Paragraph(f"<b>{a}</b>", small_s), Paragraph(b, small_s)] for a,b in glos], colWidths=[1.6*inch, USABLE_W-1.6*inch])
gt.setStyle(TableStyle([("BACKGROUND",(0,0),(0,-1), BAND), ("BOX",(0,0),(-1,-1),0.5,LINE),
                        ("INNERGRID",(0,0),(-1,-1),0.5,LINE), ("VALIGN",(0,0),(-1,-1),"TOP"),
                        ("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6),
                        ("LEFTPADDING",(0,0),(-1,-1),8),("RIGHTPADDING",(0,0),(-1,-1),8)]))
story += [gt]
story += [Spacer(1, 10)]

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
story += [Spacer(1, 6), Paragraph("Next product priorities (PM view)", h2_s),
          Paragraph("The top three features that would move the product furthest from here \u2014 each extends "
                    "autonomy into a part of the workflow the agents don\u2019t yet own end-to-end.", body_s)]
story += [bullets([
    "<b>1 \u00b7 Autonomous payment execution &amp; run orchestration.</b> Today the agents approve invoices but stop short of paying them. Close the AP loop: schedule and execute payment runs over real rails (ACH / wire / virtual card) with dual-approval, positive-pay, and automatic early-payment-discount capture. This turns &lsquo;approved&rsquo; into &lsquo;paid&rsquo; untouched and converts the touchless rate into hard cash savings &mdash; the single biggest unlock.",
    "<b>2 \u00b7 Two-way supplier &amp; customer portal.</b> A branded portal where suppliers submit invoices and check payment status, and where the Collections agent&rsquo;s outreach becomes a conversation \u2014 customers dispute, promise-to-pay, or self-serve a payment plan. Cuts inbound &lsquo;where&rsquo;s my payment?&rsquo; volume and shortens DSO by removing the email back-and-forth; it also feeds the agents structured intake instead of PDFs.",
    "<b>3 \u00b7 Closed-loop learning from analyst decisions.</b> Every human override is training signal. Use it to auto-tune each agent&rsquo;s confidence thresholds and refine the match / risk models, so the touchless rate climbs on its own and the same exception is rarely escalated twice. This is the compounding moat of an agentic system \u2014 the product gets more autonomous the longer it runs.",
])]
story += [Spacer(1, 6), Paragraph("Platform &amp; infrastructure (deferred — needs real credentials / infra)", h2_s)]
story += [bullets([
    "Real vendor-SDK ERP / bank / OCR adapters (the swap seam is a single file).",
    "Real identity provider + JWT, TLS / rate limiting, Postgres, async intake for volume, and deployment.",
])]

# ---- Appendix C: project files & layout ----
story += [Spacer(1, 12), Paragraph("Appendix C \u00b7 Project files &amp; layout", h1_s),
          Paragraph("What every file and folder in the repository is for. The project is an npm + Python "
                    "monorepo: a React front-end, a FastAPI back-end, the agent layer, and shared packages, "
                    "with sample data and docs around them.", body_s),
          Spacer(1, 6),
          Paragraph("Root &mdash; docs &amp; config", h2_s)]
rootfiles = [
 ["CLAUDE.md", "The standing &lsquo;how to work here&rsquo; brief: what the project is, the stack, conventions, guardrails, and the phase-by-phase status. Read first in any session."],
 ["V2_DESIGN_SPEC.md", "The V2 architecture and roadmap &mdash; the target layout, the agent/threshold model, and the phased plan this build follows."],
 ["V1_HANDOFF.md", "Snapshot of where the V1 prototype left off (the front-end-only mock app), carried over as context for the extend."],
 ["README.md", "How to install and run the project (front-end and back-end), for a new developer."],
 ["SECURITY.md", "The security review &mdash; what&rsquo;s hardened (RBAC, immutable audit, parameterized SQL, secrets, CORS) vs. deferred, plus the connector vendor-swap guide."],
 ["CHANGELOG.md", "Human-readable log of what changed across the phases."],
 ["package.json / package-lock.json", "npm workspace manifest (root) tying the front-end and shared packages together, plus the locked dependency versions."],
 [".gitignore", "Files Git ignores &mdash; build output, node_modules, the local SQLite DB, virtualenvs, secrets."],
 ["APAR FinanceOS.html", "A standalone single-file export of the UI (a self-contained preview artifact)."],
]
def kvtable(rows, c0=1.9):
    t = Table([[Paragraph(f"<b>{a}</b>", small_s), Paragraph(b, small_s)] for a,b in rows],
              colWidths=[c0*inch, USABLE_W-c0*inch])
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(0,-1), BAND), ("BOX",(0,0),(-1,-1),0.5,LINE),
                           ("INNERGRID",(0,0),(-1,-1),0.5,LINE), ("VALIGN",(0,0),(-1,-1),"TOP"),
                           ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
                           ("LEFTPADDING",(0,0),(-1,-1),8),("RIGHTPADDING",(0,0),(-1,-1),8)]))
    return t
story += [kvtable(rootfiles), Spacer(1, 10),
          Paragraph("apps/web &mdash; the front-end (React + Vite + TypeScript)", h2_s)]
web = [
 ["src/screens/", "The seven screens: Command Center, Exception Queue, Cash Application, Collections, Anomalies, Agents, Audit, Analytics."],
 ["src/chrome/", "App shell &mdash; the sidebar (with the V2.0 tag) and the top bar (search, role switcher)."],
 ["src/components/", "Reusable UI pieces &mdash; charts, status pills, confidence bars, the CSV-import control."],
 ["src/store/", "Zustand store: shared client state (current role/user, queues, async actions like resolve)."],
 ["src/api/", "The client that calls the back-end (auth token, fetch/command functions, CSV upload)."],
 ["src/data/", "The bundled mock seed data + re-exported types &mdash; lets the UI run offline if the API is down."],
 ["src/styles/", "The Espresso theme (CSS variables, component classes)."],
 ["index.html, vite.config.ts, tsconfig*.json, eslint.config.js", "Entry HTML, Vite build config (pinned dev port), TypeScript settings, and lint rules."],
 [".env.example", "Sample front-end environment (e.g. the API base URL); copy to .env locally."],
 ["dist/", "The built static site Vite produces &mdash; what the API serves at /app."],
]
story += [kvtable(web, c0=2.4), Spacer(1, 10),
          Paragraph("services/ &mdash; the back-end &amp; agents (Python)", h2_s)]
svc = [
 ["api/app/main.py", "FastAPI app entry &mdash; wires the routers, serves the built UI, seeds the DB on startup."],
 ["api/app/routers/", "One file per endpoint group: exceptions, deposits, collections, agents, anomalies, analytics, auth, ingest, health."],
 ["api/app/db.py, repo.py, store.py", "SQLite schema, the single persistence layer (repo.py &mdash; the Postgres-swap point), and an in-memory helper."],
 ["api/app/auth.py, config.py, models.py", "RBAC roles/tokens, settings (e.g. the $20k segregation-of-duties limit), and the API data shapes (Pydantic)."],
 ["api/requirements.txt, pyproject.toml", "Back-end Python dependencies and project metadata."],
 ["api/financeos.db", "The local SQLite database file (created/seeded at runtime; gitignored)."],
 ["agents/financeos_agents/matching.py, cash_matching.py", "The deterministic engines: tolerance-aware 3-way match (AP) and deposit&rarr;invoice match (AR)."],
 ["agents/.../ap_matching.py, cash_application.py, collections.py, anomaly.py", "The agents that run those engines under a confidence-threshold gate and produce the queues."],
 ["agents/.../llm.py, reasoning.py", "The swappable LLM provider (local Ollama / hosted / offline narrator) and the explain logic."],
 ["agents/.../thresholds.py, pipeline.py", "The threshold gate (suggest-only vs auto) and the intake&rarr;decide&rarr;act&rarr;audit pipeline scaffold."],
 ["agents/tests/", "Unit tests for the match engines (run with python -m unittest)."],
]
story += [kvtable(svc, c0=2.6), Spacer(1, 10),
          Paragraph("packages/ &mdash; shared code", h2_s)]
pkg = [
 ["shared/src/types.ts", "The domain schema (Exception, Deposit, Collection, Anomaly, Audit, Threshold &hellip;) shared by the web app and the API &mdash; the single source of truth for data shapes."],
 ["connectors/financeos_connectors/", "Abstract ERP / bank / ingestion contracts plus adapters: a mock seam for offline demos and a file/CSV adapter; real vendor SDKs slot in behind the same interfaces."],
]
story += [kvtable(pkg, c0=2.4), Spacer(1, 10),
          Paragraph("infra/, demo/, design/", h2_s)]
misc = [
 ["infra/.env.example", "Back-end environment/secrets template (DB path, ERP mode, LLM provider, SoD limit) &mdash; secrets live here, never in code."],
 ["infra/data/*.csv", "Sample AP invoices, AR open invoices, deposits, and overdue accounts &mdash; used in file/CSV mode and as import templates."],
 ["demo/", "This user manual and its build script (build_manual.py), the screenshots (screens/), and the VC demo script."],
 ["design/agents-ux-wireframes.html", "The Espresso wireframes explored for the Agents screen before it was built."],
]
story += [kvtable(misc, c0=2.0)]

story += [Spacer(1, 14), HRFlowable(width=USABLE_W, color=LINE), Spacer(1,6),
          Paragraph("Finance OS / APAR — V2 research build. Generated from the live product.", small_s)]

def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8); canvas.setFillColor(MUTE)
    canvas.drawString(0.5*inch, 0.3*inch, "Finance OS / APAR — V2 User Guide")
    canvas.drawRightString(letter[0]-0.5*inch, 0.3*inch, f"{doc.page}")
    canvas.restoreState()

doc = SimpleDocTemplate(OUT, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch,
                        leftMargin=0.5*inch, rightMargin=0.5*inch, title="Finance OS / APAR — V2 User Guide")
doc.build(story, onFirstPage=footer, onLaterPages=footer)
print("PDF written:", OUT)
missing = [s[1] for s in steps if not os.path.exists(os.path.join(SCREENS, s[1]))]
print("screenshots present:", len(steps)-len(missing), "/", len(steps), "| missing:", missing)
