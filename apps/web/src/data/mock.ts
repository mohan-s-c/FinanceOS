/* Finance OS — seed/mock data.
 * V2: the domain *types* now live in @financeos/shared (the shared schema).
 * This module keeps the seed data (MOCK) and re-exports the types so existing
 * `import { Exception } from '../data/mock'` call-sites keep working unchanged.
 * The mock seam stays intact: when the API is unreachable, the web app falls
 * back to MOCK so it remains demoable offline (see src/api/client.ts). */

import type {
  User, Metric, APHealth, ARHealth, FeedItem,
  Exception, Deposit, SuggestedMatch, Collection, RiskDist, Settlement,
  Anomaly, AuditEntry, Threshold, Analytics, AnalyticsCard,
} from "@financeos/shared";

export type {
  User, Metric, APHealth, ARHealth, FeedItem, LineItem, MatchCell, Source,
  Exception, Deposit, SuggestedMatch, Collection, RiskDist, Settlement,
  Anomaly, AuditEntry, Threshold, Analytics, AnalyticsCard,
  ResolutionKind, ResolveRequest, ResolveResponse,
} from "@financeos/shared";

export const MOCK = {
  user: { name: "Dana Okafor", role: "AP/AR Analyst", initials: "DO" } as User,

  metrics: [
    { id:"touchless", label:"Touchless Rate", value:"82", suffix:"%", delta:"+4.1 pts", dir:"up", foot:"vs. last month", tone:"ok", spark:[62,64,68,67,71,74,73,78,80,82], icon:"zap" },
    { id:"exceptions", label:"Open Exceptions", value:"47", delta:"+11 today", dir:"down", foot:"awaiting human review", tone:"warn", spark:[91,84,79,73,68,63,57,54,50,47], icon:"alert" },
    { id:"close", label:"Close Cycle", value:"1.2", suffix:" days", delta:"−4.3 days", dir:"up", foot:"from 5.5-day baseline", tone:"ok", spark:[5.5,5.1,4.4,3.8,3.1,2.6,2.0,1.7,1.4,1.2], icon:"calendar" },
    { id:"cash", label:"Cash Position", value:"$48.2", suffix:"M", delta:"+$2.1M", dir:"up", foot:"across all accounts", tone:"flat", spark:[44,45,44,46,47,46,47,48,48,48.2], icon:"wallet" },
    { id:"leakage", label:"Leakage Recovered", value:"$1.3", suffix:"M", delta:"MTD", dir:"flat", foot:"by Anomaly Detection", tone:"ok", spark:[0.1,0.3,0.4,0.6,0.7,0.85,1.0,1.1,1.2,1.3], icon:"shield" },
  ] as Metric[],

  apHealth: { processedToday:"1,284", autoApproved:"1,042", inReview:"47", avgTime:"3.2 hrs", touchless:81 } as APHealth,
  arHealth: { paymentsApplied:"$3.1M", autoApplied:"94", overdue:"212", dso:"28.4" } as ARHealth,

  feed: [
    { id:1, type:"ok", agent:"PO Matching Agent", action:"Auto-approved", html:"Auto-approved invoice <b class='t-mono'>#INV-44821</b> — 3-way match clean", amt:"$4,200", time:"just now", live:true },
    { id:2, type:"bad", agent:"Anomaly Detection Agent", action:"Flagged", html:"Flagged a <b>duplicate invoice</b> from Acme Janitorial Services", amt:"$3,180", time:"2 min ago" },
    { id:3, type:"ok", agent:"Cash Application Agent", action:"Matched", html:"Matched deposit to <b>14 open invoices</b> — auto-applied", amt:"$182,400", time:"6 min ago" },
    { id:4, type:"agent", agent:"Collections Agent", action:"Outreach", html:"Sent payment reminders to <b>38 overdue tenants</b>", amt:null, time:"14 min ago" },
    { id:5, type:"warn", agent:"Exception Agent", action:"Escalated", html:"Escalated <b class='t-mono'>#INV-44903</b> — price variance exceeds tolerance", amt:"$8,420", time:"22 min ago" },
    { id:6, type:"ok", agent:"Revenue Classification Agent", action:"Classified", html:"Classified <b>62 revenue lines</b> under ASC 606 — no exceptions", amt:null, time:"31 min ago" },
    { id:7, type:"agent", agent:"Cash Flow Forecast Agent", action:"Forecast", html:"Updated 30-day forecast — projected net inflow <b>+$6.4M</b>", amt:null, time:"44 min ago" },
    { id:8, type:"ok", agent:"Payment Agent", action:"Scheduled", html:"Scheduled <b>214 approved payments</b> for Friday run", amt:"$1.94M", time:"1 hr ago" },
  ] as FeedItem[],

  forecast: {
    labels: ["Now","+5d","+10d","+15d","+20d","+25d","+30d"],
    inflow: [2.1,3.4,2.8,4.1,3.6,4.8,5.2],
    outflow: [1.8,2.2,3.1,2.4,3.8,2.9,3.4],
  },

  exceptions: [
    {
      id:"INV-44903", vendor:"Sparkle Facilities", vinit:"SF", amount:8420, amountStr:"$8,420.00",
      location:"SFO-Terminal-2", reason:"Price variance vs PO (+12%)", confidence:61, tone:"warn",
      agent:"Exception Agent", status:"Needs Review", date:"May 28, 2026", po:"PO-3391", terms:"Net 30",
      lineItems:[
        {desc:"Janitorial service — May (Terminal 2)", qty:1, unit:"$7,520.00", total:"$7,520.00", flag:false},
        {desc:"After-hours deep clean — surcharge", qty:1, unit:"$900.00", total:"$900.00", flag:true},
      ],
      match:{ po:{rate:"$7,520.00", label:"Contracted rate"}, gr:{rate:"Received", label:"Goods receipt"}, inv:{rate:"$8,420.00", label:"Invoiced", mismatch:true} },
      reasoning:"Invoiced amount is 12% above the contracted rate in PO #PO-3391. Contract #C-2024-0142 allows a 5% variance ceiling; the after-hours surcharge line is not covered by the rate schedule.",
      sources:[{type:"Contract", ref:"C-2024-0142", note:"rate schedule"},{type:"PO", ref:"PO-3391", note:"Terminal-2 janitorial"}],
    },
    {
      id:"INV-44871", vendor:"SecureGuard Inc", vinit:"SG", amount:15200, amountStr:"$15,200.00",
      location:"Multiple", reason:"Missing PO reference", confidence:48, tone:"bad",
      agent:"Exception Agent", status:"Needs Review", date:"May 28, 2026", po:"—", terms:"Net 45",
      lineItems:[
        {desc:"Security staffing — 4 locations (May)", qty:4, unit:"$3,200.00", total:"$12,800.00", flag:false},
        {desc:"Equipment rental — monitoring", qty:1, unit:"$2,400.00", total:"$2,400.00", flag:true},
      ],
      match:{ po:{rate:"Not found", label:"PO reference", mismatch:true}, gr:{rate:"Partial", label:"Goods receipt"}, inv:{rate:"$15,200.00", label:"Invoiced"} },
      reasoning:"No purchase-order reference could be matched to this invoice. Vendor SecureGuard Inc has 3 active POs, but none match the line items or amount. Policy requires a PO for invoices above $10,000.",
      sources:[{type:"Policy", ref:"AP-POL-07", note:"PO threshold $10k"},{type:"Vendor", ref:"V-2207", note:"SecureGuard Inc"}],
    },
    {
      id:"INV-44850", vendor:"Metro Maintenance Co", vinit:"MM", amount:2100, amountStr:"$2,100.00",
      location:"DEN-Lot-A", reason:"Possible duplicate", confidence:55, tone:"warn",
      agent:"Anomaly Agent", status:"Needs Review", date:"May 27, 2026", po:"PO-3288", terms:"Net 30",
      lineItems:[{desc:"HVAC preventive maintenance — DEN Lot A", qty:1, unit:"$2,100.00", total:"$2,100.00", flag:true}],
      match:{ po:{rate:"$2,100.00", label:"Contracted"}, gr:{rate:"Received", label:"Goods receipt"}, inv:{rate:"$2,100.00", label:"Invoiced", mismatch:true} },
      reasoning:"This invoice closely matches #INV-44612 (same vendor, amount, and service period) paid on May 12, 2026. 94% field similarity suggests a possible duplicate submission.",
      sources:[{type:"Invoice", ref:"INV-44612", note:"prior payment"},{type:"PO", ref:"PO-3288", note:"DEN-Lot-A HVAC"}],
    },
    {
      id:"INV-44912", vendor:"Brightline Electric", vinit:"BE", amount:24680, amountStr:"$24,680.00",
      location:"LAX-Structure-3", reason:"Amount exceeds approval limit", confidence:72, tone:"warn",
      agent:"Exception Agent", status:"Needs Review", date:"May 29, 2026", po:"PO-3404", terms:"Net 30",
      lineItems:[
        {desc:"EV charger install — 12 stalls", qty:12, unit:"$1,840.00", total:"$22,080.00", flag:false},
        {desc:"Permit & inspection fees", qty:1, unit:"$2,600.00", total:"$2,600.00", flag:false},
      ],
      match:{ po:{rate:"$24,680.00", label:"Contracted"}, gr:{rate:"Received", label:"Goods receipt"}, inv:{rate:"$24,680.00", label:"Invoiced"} },
      reasoning:"3-way match is clean, but the total exceeds the $20,000 auto-approval limit for capital projects. Routed for human sign-off per policy AP-POL-11.",
      sources:[{type:"Policy", ref:"AP-POL-11", note:"capex sign-off $20k"},{type:"PO", ref:"PO-3404", note:"LAX EV install"}],
    },
    {
      id:"INV-44888", vendor:"Acme Janitorial", vinit:"AJ", amount:3180, amountStr:"$3,180.00",
      location:"ORD-Garage-B", reason:"Duplicate of #INV-44602", confidence:41, tone:"bad",
      agent:"Anomaly Agent", status:"Needs Review", date:"May 28, 2026", po:"PO-3120", terms:"Net 30",
      lineItems:[{desc:"Daily porter service — May (Garage B)", qty:1, unit:"$3,180.00", total:"$3,180.00", flag:true}],
      match:{ po:{rate:"$3,180.00", label:"Contracted"}, gr:{rate:"Received", label:"Goods receipt"}, inv:{rate:"$3,180.00", label:"Invoiced", mismatch:true} },
      reasoning:"Near-identical to invoice #INV-44602 already paid this period (98% similarity on vendor, amount, service window). High-confidence duplicate — recommend reject.",
      sources:[{type:"Invoice", ref:"INV-44602", note:"paid May 9"},{type:"Vendor", ref:"V-1180", note:"Acme Janitorial"}],
    },
    {
      id:"INV-44929", vendor:"Pacific Signage", vinit:"PS", amount:6740, amountStr:"$6,740.00",
      location:"SEA-Lot-C", reason:"Tax jurisdiction mismatch", confidence:67, tone:"warn",
      agent:"Exception Agent", status:"Needs Review", date:"May 29, 2026", po:"PO-3399", terms:"Net 30",
      lineItems:[
        {desc:"Wayfinding signage refresh — SEA Lot C", qty:1, unit:"$6,200.00", total:"$6,200.00", flag:false},
        {desc:"Sales tax (10.25% — applied)", qty:1, unit:"$540.00", total:"$540.00", flag:true},
      ],
      match:{ po:{rate:"$6,200.00", label:"Pre-tax"}, gr:{rate:"Received", label:"Goods receipt"}, inv:{rate:"$6,740.00", label:"Invoiced", mismatch:true} },
      reasoning:"Tax rate applied (10.25%) corresponds to Seattle, but the ship-to location maps to a tax-exempt municipal lease. Expected tax is $0.00.",
      sources:[{type:"Lease", ref:"L-SEA-0033", note:"tax-exempt"},{type:"PO", ref:"PO-3399", note:"SEA signage"}],
    },
  ] as Exception[],

  unappliedTotal: "$340,200",
  unappliedCount: 6,
  deposits: [
    { id:"DEP-90412", amount:"$182,400", payer:"JPMorgan ACH batch", invoices:"14 invoices", confidence:97, status:"Auto-applied", tone:"ok", agent:true },
    { id:"DEP-90418", amount:"$96,200", payer:"Wells Fargo wire", invoices:"3 invoices", confidence:93, status:"Auto-applied", tone:"ok", agent:true },
    { id:"DEP-90421", amount:"$54,800", payer:"Lockbox #2241", invoices:"Suggested: 5", confidence:64, status:"Needs Review", tone:"warn", agent:false },
    { id:"DEP-90427", amount:"$41,300", payer:"Stripe payout", invoices:"8 invoices", confidence:91, status:"Auto-applied", tone:"ok", agent:true },
    { id:"DEP-90433", amount:"$22,150", payer:"Check #88142", invoices:"Suggested: 2", confidence:52, status:"Needs Review", tone:"warn", agent:false },
    { id:"DEP-90440", amount:"$18,900", payer:"ACH — unidentified", invoices:"No match", confidence:31, status:"Unmatched", tone:"bad", agent:false },
  ] as Deposit[],
  suggestedMatches: [
    { inv:"INV-AR-7741", customer:"Hertz Corporate Mobility", amount:"$24,600", confidence:88 },
    { inv:"INV-AR-7726", customer:"Hertz Corporate Mobility", amount:"$18,200", confidence:71 },
    { inv:"INV-AR-7702", customer:"Hertz Corporate Mobility", amount:"$12,000", confidence:54 },
  ] as SuggestedMatch[],

  collections: [
    { account:"Lattice Logistics", loc:"DFW-Lot-E", balance:"$48,200", days:62, risk:84, action:"Payment plan offered", agent:true, tone:"bad" },
    { account:"Cobalt Retail Group", loc:"PHX-Garage-A", balance:"$31,450", days:47, risk:71, action:"2 reminders sent", agent:true, tone:"bad" },
    { account:"Northwind Hotels", loc:"SEA-Structure-1", balance:"$26,800", days:38, risk:58, action:"Reminder sent", agent:true, tone:"warn" },
    { account:"Vertex Events LLC", loc:"LAS-Lot-B", balance:"$19,900", days:31, risk:49, action:"Reminder scheduled", agent:true, tone:"warn" },
    { account:"Harborview Medical", loc:"BOS-Garage-C", balance:"$14,300", days:22, risk:28, action:"Monitoring", agent:true, tone:"ok" },
    { account:"Summit Airlines Crew", loc:"DEN-Lot-A", balance:"$11,750", days:18, risk:22, action:"Monitoring", agent:true, tone:"ok" },
  ] as Collection[],
  riskDist: [
    { label:"High risk", value:32, color:"var(--bad)" },
    { label:"Medium risk", value:58, color:"var(--warn)" },
    { label:"Low risk", value:122, color:"var(--ok)" },
  ] as RiskDist[],

  settlements: [
    { owner:"Gateway Real Estate", loc:"6 locations · West", payout:"$214,800", perf:"+8.2%", status:"Paid", tone:"ok" },
    { owner:"Meridian Property Trust", loc:"11 locations · Central", payout:"$348,500", perf:"+3.1%", status:"Approved", tone:"agent" },
    { owner:"Cardinal Holdings", loc:"4 locations · East", payout:"$96,200", perf:"−1.4%", status:"Calculated", tone:"warn" },
    { owner:"Lakeshore Ventures", loc:"7 locations · Midwest", payout:"$172,400", perf:"+5.6%", status:"Paid", tone:"ok" },
    { owner:"Summit Airports Auth.", loc:"3 locations · Hubs", payout:"$420,100", perf:"+11.0%", status:"Approved", tone:"agent" },
  ] as Settlement[],

  anomalies: [
    { id:1, sev:"high", title:"Duplicate invoice cluster — Acme Janitorial", sub:"3 invoices with 94–98% field similarity submitted within 17 days across ORD & SFO.", risk:"$9,540", agent:"Anomaly Detection Agent", icon:"copy" },
    { id:2, sev:"high", title:"Validation abuse pattern — DEN-Lot-A", sub:"218 sessions validated with the same merchant code in a 9-day window. Expected baseline ≈ 40.", risk:"$14,200", agent:"Anomaly Detection Agent", icon:"ticket" },
    { id:3, sev:"med", title:"Failed-charge pattern — exit lane 4, SFO-T2", sub:"Charge-capture failures up 3.4× vs. trailing 30-day mean. Possible LPR camera fault.", risk:"$6,820", agent:"Anomaly Detection Agent", icon:"camera" },
    { id:4, sev:"med", title:"Rate discrepancy — Brightline Electric", sub:"Invoiced labor rate $1,840/stall vs. contracted $1,720/stall across 12 line items.", risk:"$1,440", agent:"Reconciliation Agent", icon:"trending" },
    { id:5, sev:"low", title:"Off-contract vendor spend — Pacific Signage", sub:"Two POs issued outside the approved vendor list for signage category.", risk:"$3,260", agent:"Anomaly Detection Agent", icon:"flag" },
  ] as Anomaly[],
  leakageTrend: [0.12,0.31,0.44,0.58,0.71,0.86,0.97,1.08,1.19,1.3],
  leakageMonths: ["Aug","Sep","Oct","Nov","Dec","Jan","Feb","Mar","Apr","May"],

  audit: [
    { time:"14:32:08", agent:"PO Matching Agent", action:"Auto-approved INV-44821", conf:96, outcome:"auto", src:"PO-3360, GR-8841" },
    { time:"14:30:55", agent:"Anomaly Detection Agent", action:"Flagged INV-44888 (duplicate)", conf:41, outcome:"escalated", src:"INV-44602" },
    { time:"14:28:13", agent:"Cash Application Agent", action:"Applied DEP-90412 → 14 invoices", conf:97, outcome:"auto", src:"Remittance #R-2241" },
    { time:"14:22:41", agent:"Exception Agent", action:"Escalated INV-44903 (price variance)", conf:61, outcome:"escalated", src:"C-2024-0142, PO-3391" },
    { time:"14:19:02", agent:"Payment Agent", action:"Scheduled 214 payments", conf:99, outcome:"auto", src:"Batch PB-0528" },
    { time:"14:15:37", agent:"Revenue Classification Agent", action:"Classified 62 lines (ASC 606)", conf:95, outcome:"auto", src:"Rule set RC-606-v4" },
    { time:"14:09:50", agent:"Reconciliation Agent", action:"Override: rate corrected INV-44912", conf:72, outcome:"overridden", src:"PO-3404", by:"D. Okafor" },
    { time:"14:02:18", agent:"Collections Agent", action:"Offered payment plan — Lattice Logistics", conf:84, outcome:"auto", src:"Policy COL-04" },
    { time:"13:58:44", agent:"Cash Flow Forecast Agent", action:"Updated 30-day forecast", conf:90, outcome:"auto", src:"Model CF-v7" },
    { time:"13:51:09", agent:"Invoice Ingestion Agent", action:"Extracted 41 invoices from inbox", conf:93, outcome:"auto", src:"OCR batch OCR-1190" },
  ] as AuditEntry[],

  thresholds: [
    { agent:"PO Matching Agent", value:85, desc:"3-way match auto-approve" },
    { agent:"Cash Application Agent", value:90, desc:"Auto-apply deposits" },
    { agent:"Revenue Classification Agent", value:88, desc:"ASC 606 auto-classify" },
    { agent:"Payment Agent", value:95, desc:"Schedule without review" },
    { agent:"Collections Agent", value:80, desc:"Auto-send outreach" },
  ] as Threshold[],

  analytics: {
    touchlessTrend: [58,61,64,67,69,72,74,77,79,80,81,82],
    costPerInvoice: [4.10,3.85,3.60,3.20,2.95,2.70,2.40,2.15,1.90,1.70,1.55,1.42],
    closeCycle: [5.5,5.1,4.6,4.0,3.4,2.9,2.4,2.0,1.7,1.5,1.3,1.2],
    dso: [41,40,38,37,36,34,33,32,31,30,29,28.4],
    overrideRate: [12,11,10,9.5,8.8,8.0,7.2,6.5,6.0,5.4,5.0,4.6],
    months: ["Jun","Jul","Aug","Sep","Oct","Nov","Dec","Jan","Feb","Mar","Apr","May"],
  } as Analytics,

  analyticsCards: [
    { label:"Touchless Rate", value:"82%", target:"Target 85%", pct:96, dir:"up", delta:"+24 pts YoY" },
    { label:"Cost / Invoice", value:"$1.42", target:"Target $1.25", pct:88, dir:"up", delta:"−65% YoY" },
    { label:"Close Cycle", value:"1.2 days", target:"Target 1.0 day", pct:83, dir:"up", delta:"−78% YoY" },
    { label:"DSO", value:"28.4 days", target:"Target 26 days", pct:91, dir:"up", delta:"−12.6 days YoY" },
    { label:"Leakage Recovered", value:"$1.3M", target:"YTD $7.8M", pct:74, dir:"up", delta:"+$0.4M MTD" },
    { label:"Human Override Rate", value:"4.6%", target:"Target <5%", pct:92, dir:"up", delta:"−7.4 pts YoY" },
  ] as AnalyticsCard[],
};
