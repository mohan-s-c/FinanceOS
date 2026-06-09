# packages/connectors

Abstract connector **contracts** for the three integration classes the agent layer
and API depend on, plus **mock adapters** that keep the system runnable offline.

| Contract | Reads | Writes (side-effectful) | Mock adapter |
|---|---|---|---|
| `ERPConnector` | open exceptions, PO, goods receipt, open invoices | post resolution / approval | `MockERPConnector` |
| `BankConnector` | incoming deposits + remittance | (none yet) | `MockBankConnector` |
| `IngestionConnector` | parsed invoices from email/upload | (none yet) | `MockIngestionConnector` |

Design rules (see `V2_DESIGN_SPEC.md` §5 and `CLAUDE.md`):

- Agents and the API only ever import the **interface**, never a concrete vendor.
- Every write method is clearly marked side-effectful and returns an audit record.
- Credentials resolve from secret storage (`infra/`), never code.

Phase 0 ships only the mock adapters. Real vendor adapters (NetSuite/SAP/QuickBooks,
a bank aggregator, a document-AI service) plug in behind the same interfaces later.
