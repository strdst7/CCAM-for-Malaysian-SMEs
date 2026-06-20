# CCAM — Conversational Commerce Automation Mesh  
A minimalist, high‑reliability automation platform that transforms unstructured WhatsApp orders into structured, auditable, simulatable workflows.

---

## ✨ Overview  
CCAM ingests WhatsApp messages, parses them into structured orders, runs them through a declarative microflow engine, and automates downstream actions such as invoicing, kitchen notifications, POS updates, procurement, and forecasting.

It is designed around Dieter Rams’ principles: **clarity, simplicity, functionality, honesty**.

---

## 🚀 Features  
- **WhatsApp ingestion** via webhook  
- **Parser engine** (regex + ML hybrid)  
- **Microflow DSL** for automation logic  
- **Digital‑twin simulator** for KPI forecasting  
- **Invoice engine** with DuitNow integration  
- **POS connector** for SKU/stock sync  
- **Procurement automation**  
- **AI‑driven menu engineering**  
- **Multi‑tenant isolation**  
- **Mobile offline‑sync** for corrections  

---

## 🧩 Architecture  
```
WhatsApp → Webhook → Parser → Microflow → Worker → Invoice → Payment
                                   ↓
                               Simulator
                                   ↓
                               Dashboard
                                   ↓
                                 Reports
```

Core services:  
- **API** — FastAPI, async, tenant‑scoped  
- **Worker** — background jobs (parse, invoice, notify, reconcile)  
- **Parser** — ML + rules hybrid  
- **Simulator** — deterministic digital twin  
- **Dashboard** — React minimalist UI  
- **POS Connector** — vendor‑agnostic adapters  
- **Procurement Engine** — supplier automation  

---

## 📦 Directory Structure  
```
ccam/
├─ api/               # REST API
├─ worker/            # Background jobs
├─ parser/            # ML + regex parser
├─ microflow/         # DSL + interpreter
├─ simulator/         # Digital twin engine
├─ pos/               # POS adapters
├─ procurement/       # Supplier connectors
├─ dashboard/         # React frontend
├─ mobile/            # Offline‑sync app
└─ infra/             # Kubernetes manifests
```

---

## 🧠 Microflow DSL  
A declarative YAML‑based automation language.

Example:

```yaml
flow:
  - trigger: message_received
  - action: parse_message
  - condition: confidence >= 0.85
    then:
      - action: send_ack
      - action: create_invoice
    else:
      - action: route_to_correction
```

Full reference: **Microflow DSL**

---

## 🤖 AI‑Driven Menu Engineering  
A full subsystem that optimizes:  
- Profit  
- Prep time  
- Waste  
- Pricing  
- Bundling  
- Supplier ordering  

Technical deep dive: **AI Menu Engineering**

---

## 🧪 Simulator  
The digital‑twin simulator replays synthetic WhatsApp traffic to compute KPIs:

- Parse accuracy  
- Error rate  
- Admin time saved  
- Payment conversion  
- Revenue impact  

Run a scenario:

```bash
POST /simulate/run
```

More: **Simulator**

---

## 🔐 Security  
- HMAC‑signed webhooks  
- Tenant‑scoped encryption keys  
- Zero‑trust networking  
- Immutable audit logs  
- PDPA‑aligned data handling  

Details: **Security Model**

---

## 🧱 Infrastructure  
- Kubernetes (GitOps via ArgoCD)  
- PostgreSQL HA  
- Redis Sentinel  
- Object storage for reports  
- Horizontal autoscaling  

Infra reference: **Kubernetes Architecture**

---

## 📊 Dashboards  
Minimalist UI with:  
- Orders  
- KPIs  
- Payment conversion  
- Menu engineering  
- Procurement  
- Alerts  

More: **Dashboard**

---

## 📱 Mobile Offline‑Sync  
For low‑connectivity kitchens.

- Local SQLite  
- Delta‑sync  
- Conflict resolution  
- Correction queue  

More: **Offline Sync**

---

## 🧾 Billing & Quotas  
- Per‑tenant usage tracking  
- Monthly invoices  
- Quota enforcement  
- Alerts  

More: **Billing System**

---

## 🛠️ Development  
### Requirements  
- Python 3.11  
- Node.js 20  
- Docker + Compose  
- PostgreSQL  
- Redis  

### Setup  
```bash
docker-compose up
```

### Tests  
```bash
pytest
```

---

## 📄 License  
MIT (or your preferred license).

---

## 🤝 Contributing  
Pull requests welcome.  
Please follow the minimalist design philosophy.

---

## 📬 Contact  
For questions, open an issue or start a discussion.

---
