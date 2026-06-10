# Finance OS / APAR — VC Demo Script & Storyboard
**Runtime target:** ~12–14 min · **Voice:** co-founder/CEO · **Format:** screen recording of the app (`http://127.0.0.1:8000/app/`) + voiceover.
Cues: **[SHOW]** = what's on screen · **[DO]** = the click to perform · *(timing)* = elapsed.

---

## 0 · Cold open — the hook  *(0:00–0:45)*
**[SHOW] Command Center (Dashboard).**

> "Every company with vendors and customers runs the same invisible factory in the back office: thousands of invoices to match, payments to apply, accounts to chase. It's manual, it's slow, and it's where money quietly leaks.
>
> This is Finance OS. It's an AP/AR system where software agents do the routine work — matching invoices, applying cash, chasing collections, flagging fraud — and a human supervises by exception instead of doing data entry. Let me show you a finance team that runs itself, with a person in the loop only where judgment is actually needed."

## 1 · The problem & who it's for  *(0:45–2:00)*
**[SHOW] Command Center KPI row + AP/AR health tiles.**

> "Accounts Payable and Receivable are high-volume, rules-heavy, and audited. A mid-size company processes tens of thousands of invoices a month. Today that's armies of analysts keying data, reconciling spreadsheets, and three-way-matching by hand. Errors and duplicate payments alone are a multi-billion-dollar leak across the economy.
>
> Our user is Dana, an AP/AR analyst. Her old job was processing. Her new job — with Finance OS — is supervising agents and resolving the few percent that need a human. Up top you can see the outcome metrics that matter to a CFO: touchless rate, open exceptions, close-cycle time, cash position, and leakage recovered."

**[SHOW] the 'Agents at work' strip.**
> "And right here on the home screen is the fleet of agents working live — AP Matching, Cash Application, Anomaly Detection, Collections, and more — each with its own confidence threshold."

## 2 · Exception Queue — the core AP loop  *(2:00–4:30)*
**[DO] Click 'Exception Queue'. [SHOW] the queue.**

> "Here's the heart of Accounts Payable. The AP Matching agent ingested the invoices, ran a deterministic three-way match — purchase order, goods receipt, invoice — and auto-cleared everything that was clean. What you're looking at is only what it *couldn't* safely approve. The volume a human touches drops by an order of magnitude."

**[DO] Open INV-44903 (price variance). [SHOW] the drawer: 3-way match, line items, sources.**
> "Open one and you get the agent's full reasoning. This invoice is twelve percent over the contracted rate. The agent shows the PO, the goods receipt, the invoice side-by-side, flags the offending line, cites the contract and policy it's grounded in, and gives a confidence score. Nothing is a black box — every decision carries its evidence. That's non-negotiable in a finance system: auditability beats cleverness."

**[DO] Click 'Explain with AI'. [SHOW] the AI narrative + model badge.**
> "And when an analyst wants it in plain English, the reasoning agent drafts a controls-analyst explanation and a recommended disposition — here, 'confirm the surcharge was pre-authorized, otherwise adjust to the contracted rate.' Notice the model badge. Because this is financial data, the language model can run fully local — on Ollama or your own vLLM — so the data never leaves your infrastructure. The deterministic engine still owns the decision; the model only explains the gray areas."

**[DO] Click the agent-recommendation 'Accept'.**
> "Dana can accept the agent's recommendation in one click, or override it. Either way it's logged."

## 3 · Human-in-the-loop & control  *(4:30–5:30)*
**[DO] Switch role to 'Controller' in the top bar, then back to 'Analyst'.**
> "Control is real, not cosmetic. We have role-based access with segregation of duties: an analyst clears the routine queue, but tuning an agent's autonomy, or signing off a high-value item over twenty thousand dollars, requires a Controller. Try it as an analyst and you're blocked. This is how you get automation a CFO and an auditor will actually sign off on."

## 4 · Cash Application — the AR loop  *(5:30–7:00)*
**[DO] Click 'Cash Application'. [SHOW] deposits + match labels.**
> "The mirror image on Accounts Receivable. Incoming deposits, automatically matched to open invoices — exact match, remittance hints, then fuzzy reconciliation. High-confidence matches auto-apply; the rest come here."

**[DO] Open DEP-90412. [SHOW] remittance match + candidate invoices.**
> "This deposit reconciled to its invoices from the remittance advice — ninety-seven percent confidence, ready to post to the sub-ledger. The unmatched ACH at the bottom is exactly the kind of thing a human should look at — and only that."

## 5 · Collections & Anomalies — judgment work  *(7:00–8:30)*
**[DO] Click 'Collections'. [SHOW] risk-ranked accounts.**
> "Collections: the agent risk-scores overdue accounts by days-past-due and balance, prioritizes them, and drafts the outreach — but a human sends it. Agents draft; people decide on anything customer-facing."

**[DO] Click 'Anomalies & Leakage'. [SHOW] severity-ranked anomalies + leakage trend.**
> "And this is where the money comes back. The Anomaly agent watches the ledger for duplicate-invoice clusters, validation abuse, charge-capture faults, off-contract spend — severity-ranked, with the dollars at risk. That leakage-recovered line is the ROI story: this pays for itself."

## 6 · The Agents console — autonomy you dial up  *(8:30–10:30)*
**[DO] Click 'Agents'. [SHOW] roster + AP Matching detail (pipeline, decisions, threshold).**
> "This is the part that makes it a *platform*, not a script. Every agent in one place. Pick one and you see its pipeline — intake, match, decide, act, escalate — its recent decisions with reasons and sources, and its confidence threshold.
>
> The key idea: agents earn trust. Every agent starts in *suggest-only* mode — it recommends, a human approves. As it proves itself, you promote it toward auto-action."

**[DO] As Controller, toggle AP Matching to 'Auto'. [DO] Go to Analytics.**
> "Watch what happens when I promote AP Matching to auto." **[SHOW] Analytics 'Live this session' strip moving.**
> "On the Analytics screen, live from the audit trail: auto-actions go up, the touchless rate climbs, the open queue drops. You are literally watching the human workload shrink as autonomy increases — and you control the dial. There's also a global kill switch to force everything back to suggest-only in an incident."

## 7 · Audit & trust  *(10:30–11:15)*
**[DO] Click 'Agent & Audit Trail'. [SHOW] the live trail.**
> "Everything — every auto-action, every human resolution, every threshold change, every AI explanation and the model that produced it — lands in an immutable, append-only audit trail. This is the SOX story. When an auditor asks 'why was this paid,' the answer is one click, with the evidence attached."

## 8 · It runs on YOUR data  *(11:15–12:15)*
**[DO] On Exception Queue, click 'Template', then 'Import AP CSV'. [SHOW] queue rebuild.**
> "And this isn't a canned demo. Finance OS reads real data. Download a template, drop in your invoices, POs and receipts — and the agents re-run on your numbers in seconds. The same connector interface that reads a CSV today plugs into NetSuite, SAP, or QuickBooks tomorrow — we never hard-wire a vendor. Bank feeds and OCR invoice intake sit behind the same seam."

## 9 · Why we win  *(12:15–13:15)*
**[SHOW] back to Command Center.**
> "Three things make this defensible. One — deterministic where it matters, AI where it helps. We don't ask a language model to approve a payment; rules do the math, the model explains the edge cases. Two — human-in-the-loop and auditable by design, so it's deployable in a regulated finance function, not just a demo. Three — your data stays yours: local models, swappable connectors, no lock-in.
>
> The wedge is AP exceptions and cash application — the highest-pain, highest-volume work — and we expand across the whole back office from there."

## 10 · Status & the ask  *(13:15–14:00)*
> "What you saw is real and running: a working agent layer, persistence, role-based access, an audit trail, CSV and ERP ingestion, and local-LLM reasoning — all live. From here it's real vendor integrations, design partners, and pilots.
>
> We're raising [amount] to land our first [N] design partners and turn touchless rate into a number CFOs put in their board decks. We'd love to have you in. Thank you."

---

## Recording recipe
1. Start the API in the Code tab: `cd services/api && uvicorn app.main:app --port 8000` (add `LLM_PROVIDER=ollama OLLAMA_MODEL=qwen2.5` to demo the local model live). Open `http://127.0.0.1:8000/app/`.
2. For a clean baseline, reseed first: stop server → delete `financeos.db*` → restart.
3. Screen-record at 1440×900 (or full screen). Read the script section by section; pause between sections so edits are easy.
4. Voiceover options: (a) record your own narration over the screen capture; or (b) paste each section into a text-to-speech tool and lay the audio under the matching clip.
5. Keep each section's clip to its timing budget above; total ≈ 13–14 min.

## Storyboard (shot list)
| # | Screen | Action | ~secs |
|---|--------|--------|------|
| 1 | Command Center | hold on KPIs + Agents strip | 90 |
| 2 | Exception Queue | open INV-44903, Explain with AI, Accept | 150 |
| 3 | Top bar | switch Analyst↔Controller (show 403) | 60 |
| 4 | Cash Application | open DEP-90412 (remittance match) | 90 |
| 5 | Collections | risk-ranked list + a draft | 45 |
| 6 | Anomalies | severity cards + leakage trend | 45 |
| 7 | Agents | AP Matching detail; toggle to Auto | 120 |
| 8 | Analytics | live-session strip moving | 30 |
| 9 | Audit | immutable trail incl. AI explanations | 45 |
| 10 | Exception Queue | Template → Import AP CSV → rebuild | 60 |
| 11 | Command Center | close on the vision + ask | 90 |
