import React from 'react';
import { motion } from 'motion/react';
import { Server, Cpu, Globe, Terminal, ShieldCheck, Database, Layers, Zap, Activity } from 'lucide-react';
import { cn } from '../utils';

export default function SystemsView() {
  const topologies = [
    { 
      env: 'Development', 
      type: 'Docker Compose', 
      desc: 'Single network ccam_net. Local containers: api, db, redis, worker, frontend.',
      details: 'Volumes: db_data, redis_data. Local .env management.'
    },
    { 
      env: 'Staging', 
      type: 'Kubernetes (K8s)', 
      desc: 'Namespace: ccam-staging. StatefulSets for Postgres/Redis.',
      details: 'ConfigMaps for YAML flows, K8s Secrets for keys.'
    },
    { 
      env: 'Production', 
      type: 'K8s Multi-Tenant', 
      desc: 'Namespace: ccam-prod. HA PostgreSQL with streaming replication.',
      details: 'HPA for parser + worker. Object storage for reports.'
    }
  ];

  const scaling = [
    { unit: 'Parser Service', strategy: 'Stateless, horizontal POD scaling via HPA.', benchmark: '200 orders/sec per pod' },
    { unit: 'Worker Cluster', strategy: 'Scale based on Redis queue depth (Length-Aware).', benchmark: '500 jobs/sec per pod' },
    { unit: 'Database Tier', strategy: 'Tenant partitioning + Read replicas for BI analytics.', benchmark: '2,000 tps (3-node HA)' },
    { unit: 'Caches', strategy: 'Redis sharding for queue distribution.', benchmark: '50,000 ops/sec' }
  ];

  const iacManifests = [
    { kind: 'Deployment', desc: 'Defines replicas, container images (ccam-api), resource limits.' },
    { kind: 'Service', desc: 'Exposes API, worker, and frontend pods via ClusterIP.' },
    { kind: 'Ingress', desc: 'TLS termination via Let\'s Encrypt + routing rules (Argon-2).' },
    { kind: 'HPA', desc: 'Scaling parser + worker based on CPU/Queue metrics.' },
    { kind: 'ConfigMap', desc: 'Store YAML flows and simulator scenario templates.' }
  ];

  const logFields = [
    { field: 'timestamp', desc: 'ISO 8601 UTC' },
    { field: 'tenant_id', desc: 'Anonymized UUID' },
    { field: 'action', desc: 'parse/ack/invoice' },
    { field: 'latency_ms', desc: 'Execution time' }
  ];

  const threats = [
    { name: 'Spoofing (S)', mitigation: 'HMAC validation + Tenant Scoped Keys' },
    { name: 'Tampering (T)', mitigation: 'Immutable Audit Logs + Signed Payloads' },
    { name: 'Repudiation (R)', mitigation: 'Correlation IDs + Non-editable Trails' },
    { name: 'Info Disclosure (I)', mitigation: 'AES-256 Encryption + Tenant Keys' },
    { name: 'DoS (D)', mitigation: 'Rate Limiting + Queue Backpressure' },
    { name: 'Elevation (E)', mitigation: 'RBAC Roles + Zero-Trust Networking' }
  ];

  const jobTaxonomy = [
    { job: 'parse_job', desc: 'Atomic WhatsApp message extraction' },
    { job: 'invoice_job', desc: 'Financial record generation' },
    { job: 'notify_job', desc: 'Kitchen/Staff real-time notification' },
    { job: 'simulate_job', desc: 'Digital twin scenario execution' },
    { job: 'rotate_keys_job', desc: 'Automated tenant credential rotation' }
  ];

  const posArchi = [
    { component: 'POS Connector Service', desc: 'Stateless microservice syncing SKUs, stock, prices.' },
    { component: 'SKU Mapping Engine', desc: 'Maps parsed items → POS SKUs.' },
    { component: 'Webhook Listener', desc: 'Receives real-time stock/price updates.' },
    { component: 'POS Adapter Layer', desc: 'Vendor-specific bridges (StoreHub, Slurp, Qashier).' }
  ];

  const mlModelCard = {
    name: 'Parser Model (DistilBERT Fine-Tuned)',
    architecture: 'DistilBERT base + SME Malay/English order patterns.',
    metrics: [
      { label: 'Entity F1', val: '0.92' },
      { label: 'Address F1', val: '0.88' },
      { label: 'Item/Qty F1', val: '0.95' }
    ],
    ethics: 'No PII stored in training. Opt-in federated learning only.'
  };

  const mobileSync = [
    { step: 'Local Store', desc: 'SQLite partition for offline correction queue.' },
    { step: 'Delta Sync', desc: 'Batch sync of corrected entities to API.' },
    { step: 'Conflict Resolver', desc: 'Deterministic version-based reconciliation.' }
  ];

  const errorCodes = [
    { code: '4001', label: 'Invalid Payload', desc: 'WhatsApp message malformed.' },
    { code: '4011', label: 'Unauthorized', desc: 'Invalid HMAC signature.' },
    { code: '5001', label: 'Parser Failure', desc: 'Regex/ML error in extraction.' },
    { code: '5003', label: 'Worker Timeout', desc: 'Background job exceeded limit.' }
  ];

  const k8sDeployment = `apiVersion: apps/v1
kind: Deployment
metadata:
  name: ccam-api
  namespace: ccam-prod
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ccam-api
  template:
    metadata:
      labels:
        app: ccam-api
    spec:
      containers:
      - name: api
        image: registry/ccam-api:latest
        resources:
          limits:
            cpu: "500m"
            memory: "1Gi"`;

  const sequence = [
    'Customer → WhatsApp API',
    'WhatsApp API → Webhook Adapter',
    'Webhook Adapter → Parser Service',
    'Parser Service → Confidence Check',
    '[>=0.85] → Auto-Ack → Invoice',
    '[<0.85] → Correction → Invoice'
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-12 pb-24"
    >
      <div className="flex justify-between items-end">
        <div>
          <h2 className="text-xl font-bold text-[#E0E0E0] tracking-tight">System Topology & Scaling</h2>
          <p className="text-[10px] text-[#444] font-mono mt-1 uppercase tracking-widest italic">Global Infrastructure Registry v1.4.2</p>
        </div>
        <div className="flex gap-4">
           <div className="px-3 py-1 bg-[#111] border border-[#222] rounded-full flex items-center gap-2">
              <Globe size={10} className="text-[#00FF9C]" />
              <span className="text-[8px] font-bold text-[#00FF9C] uppercase font-mono">Region: MSIA_SOUTH</span>
           </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="space-y-8">
           <div className="bg-[#0A0A0A] border border-[#222] p-8 rounded-sm">
              <h3 className="text-xs font-bold uppercase tracking-widest text-[#666] mb-8 border-b border-[#111] pb-4 flex items-center gap-3">
                 <Layers size={14} className="text-indigo-500" />
                 Deployment Topology
              </h3>
              <div className="space-y-6">
                 {topologies.map((t, i) => (
                   <div key={i} className="relative pl-8 border-l border-[#111]">
                      <div className="absolute top-0 left-[-4px] w-2 h-2 rounded-full bg-[#111] border border-[#222]" />
                      <div className="flex justify-between items-start mb-2">
                         <p className="text-[10px] font-bold text-[#E0E0E0] uppercase tracking-wider">{t.env}</p>
                         <span className="text-[9px] font-mono text-[#444] bg-[#111] px-2 py-0.5 rounded-sm">{t.type}</span>
                      </div>
                      <p className="text-[10px] text-[#888] leading-relaxed italic mb-1">{t.desc}</p>
                      <p className="text-[9px] text-[#333] font-mono uppercase">{t.details}</p>
                   </div>
                 ))}
              </div>
           </div>

           <div className="bg-[#0A0A0A] border border-[#222] p-8 rounded-sm">
              <h3 className="text-xs font-bold uppercase tracking-widest text-[#666] mb-8 border-b border-[#111] pb-4 flex items-center gap-3">
                 <Database size={14} className="text-emerald-500" />
                 Detailed Relational Model (ERD)
              </h3>
              <div className="space-y-8">
                 <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {[
                      { name: 'Tenant', fields: 'id (PK), name, config, keys' },
                      { name: 'Order', fields: 'id (PK), tenant_id (FK), customer, items_json, status, timestamps' },
                      { name: 'Item', fields: 'id (PK), order_id (FK), sku, name, qty, unit_price' },
                      { name: 'Invoice', fields: 'id (PK), order_id (FK), amount, link, status, due_date' },
                      { name: 'ParserAudit', fields: 'id (PK), order_id (FK), msg_id, raw, parsed, confidence' }
                    ].map((e, i) => (
                      <div key={i} className="p-4 bg-black/40 border border-[#111] rounded-sm group hover:border-[#222] transition-colors">
                         <p className="text-[10px] font-bold text-[#E0E0E0] uppercase mb-2 flex items-center gap-2">
                            <span className="w-1 h-1 bg-emerald-500 rounded-full" />
                            {e.name}
                         </p>
                         <p className="text-[9px] font-mono text-[#444] leading-relaxed italic">{e.fields}</p>
                      </div>
                    ))}
                 </div>
                 <div className="p-4 border border-dashed border-[#222] rounded-sm bg-[#050505]">
                    <p className="text-[9px] font-bold text-[#333] uppercase mb-3">Relationship Graph</p>
                    <div className="grid grid-cols-2 gap-4 font-mono text-[8px] text-[#444] uppercase">
                       <p>Tenant → Order (1:N)</p>
                       <p>Order → Item (1:N)</p>
                       <p>Order → Invoice (1:1)</p>
                       <p>Order → ParserAudit (1:N)</p>
                    </div>
                 </div>
              </div>
           </div>

           <div className="bg-[#0A0A0A] border border-[#222] p-8 rounded-sm">
              <h3 className="text-xs font-bold uppercase tracking-widest text-[#666] mb-8 border-b border-[#111] pb-4 flex items-center gap-3">
                 <Server size={14} className="text-[#00FF9C]" />
                 POS Connector Architecture
              </h3>
              <div className="space-y-6">
                 <div className="grid grid-cols-1 gap-4">
                    {posArchi.map((p, i) => (
                      <div key={i} className="p-4 bg-black/40 border border-[#111] rounded-sm group hover:border-[#222] transition-colors">
                         <p className="text-[10px] font-bold text-[#E0E0E0] uppercase mb-1 tracking-tight">{p.component}</p>
                         <p className="text-[9px] text-[#444] leading-relaxed italic">{p.desc}</p>
                      </div>
                    ))}
                 </div>
                 <div className="p-4 border border-dashed border-[#222] rounded-sm bg-[#050505]">
                    <p className="text-[8px] font-bold text-[#333] uppercase mb-2">Unified Flow</p>
                    <p className="text-[10px] text-[#444] font-mono leading-relaxed italic uppercase tracking-tighter">
                      Customer → WhatsApp → CCAM Parser → Microflow → Invoice → Payment
                      <span className="block mt-1 text-[#222]">POS SKU Sync ← POS Connector ← POS System</span>
                    </p>
                 </div>
              </div>
           </div>

           <div className="bg-[#0A0A0A] border border-[#222] p-8 rounded-sm">
              <h3 className="text-xs font-bold uppercase tracking-widest text-[#666] mb-8 border-b border-[#111] pb-4 flex items-center gap-3">
                 <Cpu size={14} className="text-indigo-400" />
                 ML Model Card: {mlModelCard.name}
              </h3>
              <div className="space-y-6">
                 <div>
                    <p className="text-[9px] font-bold text-[#666] uppercase mb-1">Architecture</p>
                    <p className="text-[10px] text-[#444] italic leading-relaxed">{mlModelCard.architecture}</p>
                 </div>
                 <div className="grid grid-cols-3 gap-4">
                    {mlModelCard.metrics.map((m, i) => (
                      <div key={i} className="p-3 bg-[#080808] border border-[#111] rounded-sm text-center">
                         <p className="text-[8px] font-bold text-[#333] uppercase mb-1">{m.label}</p>
                         <p className="text-xs font-bold text-[#E0E0E0] font-mono">{m.val}</p>
                      </div>
                    ))}
                 </div>
                 <div className="p-4 border border-dashed border-red-500/20 bg-red-500/5 rounded-sm">
                    <p className="text-[8px] font-bold text-red-500/40 uppercase mb-1">Ethics & Privacy</p>
                    <p className="text-[9px] text-red-500/60 italic leading-relaxed">{mlModelCard.ethics}</p>
                 </div>
              </div>
           </div>
           <div className="bg-[#0A0A0A] border border-[#222] p-8 rounded-sm">
              <h3 className="text-xs font-bold uppercase tracking-widest text-[#666] mb-8 border-b border-[#111] pb-4 flex items-center gap-3">
                 <Activity size={14} className="text-[#00FF9C]" />
                 End-to-End Sequence logic
              </h3>
              <div className="space-y-4">
                 {sequence.map((s, i) => (
                   <div key={i} className="flex items-center gap-4">
                      <span className="text-[8px] font-mono text-[#222] w-4">0{i+1}</span>
                      <p className="text-[10px] font-medium text-[#888] font-mono tracking-tight">{s}</p>
                   </div>
                 ))}
              </div>
           </div>

           <div className="bg-[#0A0A0A] border border-[#222] p-8 rounded-sm">
              <div className="flex justify-between items-center mb-10 border-b border-[#111] pb-4">
                 <h3 className="text-xs font-bold uppercase tracking-widest text-[#666] flex items-center gap-3">
                    <Zap size={14} className="text-yellow-500" />
                    CI/CD Pipeline (GitHub Actions)
                 </h3>
                 <div className="flex gap-2">
                    <div className="w-2 h-2 rounded-full bg-[#00FF9C] shadow-[0_0_8px_#00FF9C]" />
                    <span className="text-[8px] font-bold text-[#00FF9C] uppercase font-mono">Workflow: PASSED</span>
                 </div>
              </div>
              <div className="space-y-4">
                 {[
                   { step: 'CI_BUILD', status: 'SUCCESS', time: '1m 12s', desc: 'Docker images pushed to registry/ccam-api' },
                   { step: 'UNIT_TEST', status: 'SUCCESS', time: '45s', desc: 'Pytest/Vitest coverage @ 92.4%' },
                   { step: 'SEC_SCAN', status: 'SUCCESS', time: '30s', desc: 'Trivy: 0 Critical Vulnerabilities' },
                   { step: 'K8S_DEPLOY', status: 'SUCCESS', time: '2m 04s', desc: 'Applied manifests to ccam-prod namespace' }
                 ].map((step, i) => (
                   <div key={i} className="flex justify-between items-center p-4 bg-[#080808] border border-[#111] rounded-sm">
                      <div>
                         <p className="text-[10px] font-bold text-[#E0E0E0] uppercase">{step.step}</p>
                         <p className="text-[9px] text-[#444] italic">{step.desc}</p>
                      </div>
                      <span className="text-[9px] font-mono text-[#00FF9C]">{step.time}</span>
                   </div>
                 ))}
              </div>
           </div>
        </div>

        <div className="space-y-8">
           <div className="bg-[#0A0A0A] border border-[#222] p-8 rounded-sm">
              <h3 className="text-xs font-bold uppercase tracking-widest text-[#666] mb-8 border-b border-[#111] pb-4 flex items-center gap-3">
                 <Activity size={14} className="text-[#00FF9C]" />
                 Real-time Telemetry (Prometheus)
              </h3>
              <div className="space-y-6">
                 {[
                   { label: 'API Latency', val: '240ms', color: '#00FF9C', type: 'line' },
                   { label: 'Worker Queue', val: '12 depth', color: '#444', type: 'bars' },
                   { label: 'DB Connections', val: '45 active', color: '#222', type: 'thin-line' },
                   { label: 'Redis Ops/sec', val: '1.2k', color: '#00FF9C', type: 'sparkline' },
                   { label: 'Error Rate', val: '0.04%', color: '#EF4444', type: 'dot' }
                 ].map((m, i) => (
                   <div key={i} className="flex items-center justify-between group">
                      <div className="w-24 shrink-0">
                         <p className="text-[9px] font-bold text-[#E0E0E0] uppercase tracking-tighter">{m.label}</p>
                         <p className="text-[8px] text-[#444] font-mono">{m.val}</p>
                      </div>
                      <div className="flex-1 h-8 flex items-center px-4">
                         {m.type === 'line' && (
                            <div className="w-full h-[1px] bg-[#111] relative">
                               <div className="absolute top-0 left-0 w-3/4 h-full bg-[#00FF9C]" />
                            </div>
                         )}
                         {m.type === 'bars' && (
                            <div className="flex gap-0.5 items-end h-4">
                               {[0.4, 0.7, 0.5, 0.9, 0.3, 0.6].map((h, idx) => (
                                 <div key={idx} className="w-1 bg-[#222]" style={{ height: `${h * 100}%` }} />
                               ))}
                            </div>
                         )}
                         {m.type === 'thin-line' && (
                            <div className="w-full h-[1px] bg-[#111]">
                               <div className="w-1/2 h-full bg-[#333]" />
                            </div>
                         )}
                         {m.type === 'sparkline' && (
                            <svg className="w-full h-4 stroke-[#00FF9C]/20 fill-none" viewBox="0 0 100 20">
                               <path d="M0 10 L10 15 L20 5 L30 12 L40 18 L50 8 L60 14 L70 2 L80 10 L90 15 L100 5" strokeWidth="0.5" />
                            </svg>
                         )}
                         {m.type === 'dot' && (
                            <div className="flex items-center gap-2">
                               <div className={cn("w-1.5 h-1.5 rounded-full", parseFloat(m.val) > 0 ? "bg-red-500 shadow-[0_0_8px_red]" : "bg-[#111]")} />
                               <span className="text-[7px] text-[#222] uppercase font-mono">NOMINAL</span>
                            </div>
                         )}
                      </div>
                   </div>
                 ))}
              </div>
           </div>

           <div className="bg-[#0A0A0A] border border-[#222] p-8 rounded-sm">
              <h3 className="text-xs font-bold uppercase tracking-widest text-[#666] mb-8 border-b border-[#111] pb-4 flex items-center gap-3">
                 <Globe size={14} className="text-indigo-500" />
                 Multi-Region Failover (DR)
              </h3>
              <div className="space-y-6">
                 <div className="grid grid-cols-2 gap-4">
                    <div className="p-4 bg-[#080808] border border-[#111] rounded-sm text-center">
                       <p className="text-[8px] font-bold text-[#333] uppercase mb-1">RTO</p>
                       <p className="text-xs font-bold text-[#E0E0E0] font-mono">15-30m</p>
                    </div>
                    <div className="p-4 bg-[#080808] border border-[#111] rounded-sm text-center">
                       <p className="text-[8px] font-bold text-[#333] uppercase mb-1">RPO</p>
                       <p className="text-xs font-bold text-[#E0E0E0] font-mono">&lt; 5m</p>
                    </div>
                 </div>
                 <div className="space-y-3 text-[9px] font-mono">
                    {[
                      { component: 'PostgreSQL WAL', desc: 'Streaming replication to Secondary (SG).' },
                      { component: 'Redis Sentinel', desc: 'Auto-promotion of replicas during partition.' },
                      { component: 'ArgoCD Sync', desc: 'Workload mirroring to secondary K8s namespace.' }
                    ].map((r, i) => (
                       <div key={i} className="flex justify-between items-center border-b border-[#111] pb-2">
                          <span className="text-[#444] uppercase">{r.component}</span>
                          <span className="text-[#222] italic">{r.desc}</span>
                       </div>
                    ))}
                 </div>
              </div>
           </div>

           <div className="bg-black border border-[#222] p-8 rounded-sm">
              <h3 className="text-xs font-bold uppercase tracking-widest text-[#666] mb-6 border-b border-[#111] pb-4 flex items-center gap-3">
                 <Terminal size={14} className="text-indigo-400" />
                 POSAdapter Interface (Vendor Agnostic)
              </h3>
              <pre className="text-[9px] font-mono text-emerald-500/60 leading-relaxed overflow-x-auto whitespace-pre">
{`class POSAdapter:
    def authenticate(credentials): ...
    def fetch_skus(): ...
    def update_stock(sku_id, qty): ...
    def fetch_prices(): ...
    def push_order(order): ...
    def health_check(): ...`}
              </pre>
              <div className="mt-6 flex flex-wrap gap-2">
                 {['StoreHub', 'Slurp', 'Qashier', 'Vend'].map(v => (
                    <span key={v} className="text-[8px] font-bold text-[#333] border border-[#111] px-2 py-0.5 rounded-sm uppercase">{v}</span>
                 ))}
              </div>
           </div>

           <div className="bg-[#0A0A0A] border border-[#222] p-8 rounded-sm">
              <div className="flex justify-between items-center mb-10 border-b border-[#111] pb-4">
                 <h3 className="text-xs font-bold uppercase tracking-widest text-[#666] flex items-center gap-3">
                    <Terminal size={14} className="text-emerald-500" />
                    API Endpoints (REST)
                 </h3>
                 <span className="text-[9px] text-[#444] font-mono uppercase tracking-widest">OAS 3.1</span>
              </div>
              
              <div className="space-y-8">
                 {[
                   { group: 'Webhook', items: [{ method: 'POST', path: '/webhook', desc: 'Validates HMAC, queues parse job.' }] },
                   { group: 'Orders', items: [
                     { method: 'GET', path: '/orders', desc: 'List with cursor pagination.' },
                     { method: 'POST', path: '/orders', desc: 'Manual order creation.' },
                     { method: 'GET', path: '/orders/{id}', desc: 'Retrieve single record detail.' }
                   ]},
                   { group: 'Invoices', items: [
                     { method: 'POST', path: '/invoices', desc: 'Generate financial record.' },
                     { method: 'GET', path: '/invoices/{id}', desc: 'Retrieve invoice metadata.' },
                     { method: 'POST', path: '/invoices/{id}/remind', desc: 'Trigger manual payment reminder.' }
                   ]},
                   { group: 'Simulator', items: [
                     { method: 'POST', path: '/simulate/run', desc: 'Execute scenario.' },
                     { method: 'GET', path: '/simulate/results/{id}', desc: 'Fetch twin-engine report.' }
                   ]},
                   { group: 'Dashboard', items: [
                     { method: 'GET', path: '/dashboard/kpis', desc: 'Global performance metrics.' },
                     { method: 'GET', path: '/dashboard/alerts', desc: 'Real-time operational warnings.' }
                   ]}
                 ].map((group, i) => (
                   <div key={i} className="space-y-4">
                      <p className="text-[9px] font-bold text-[#333] uppercase tracking-widest">{group.group}</p>
                      <div className="space-y-3">
                        {group.items.map((api, idx) => (
                          <div key={idx} className="group">
                             <div className="flex items-center gap-3 mb-1">
                                <span className={cn(
                                  "text-[7px] font-bold px-1.5 py-0.5 rounded-sm font-mono",
                                  api.method === 'POST' ? "bg-indigo-500/20 text-indigo-400" : "bg-emerald-500/20 text-emerald-400"
                                )}>
                                   {api.method}
                                </span>
                                <span className="text-[10px] font-bold text-[#E0E0E0] font-mono tracking-tight">{api.path}</span>
                             </div>
                             <p className="text-[9px] text-[#444] italic leading-relaxed">{api.desc}</p>
                          </div>
                        ))}
                      </div>
                   </div>
                 ))}

                 <div className="pt-6 border-t border-[#111]">
                    <p className="text-[8px] font-bold text-[#222] uppercase tracking-[0.3em] mb-4">OpenAPI Design Principles</p>
                    <div className="grid grid-cols-2 gap-4">
                       {[
                         'No nested resources',
                         'No unnecessary verbs',
                         'Minimal response bodies',
                         'Consistent error schema'
                       ].map((p, i) => (
                         <div key={i} className="flex items-center gap-2">
                            <div className="w-1 h-1 bg-[#111] rounded-full" />
                            <p className="text-[9px] text-[#333] uppercase font-mono tracking-tighter">{p}</p>
                         </div>
                       ))}
                    </div>
                 </div>
              </div>
           </div>

           <div className="bg-[#0A0A0A] border border-[#222] p-8 rounded-sm">
              <h3 className="text-xs font-bold uppercase tracking-widest text-[#666] mb-8 border-b border-[#111] pb-4 flex items-center gap-3">
                 <Cpu size={14} className="text-indigo-400" />
                 Scalability & Benchmarks
              </h3>
              <div className="grid grid-cols-1 gap-4">
                 {scaling.map((s, i) => (
                    <div key={i} className="p-4 bg-[#080808] border border-[#111] rounded-sm group hover:border-[#222] transition-colors">
                       <div className="flex justify-between items-center mb-1">
                          <p className="text-[9px] font-bold text-[#666] uppercase tracking-widest group-hover:text-[#E0E0E0] transition-colors">{s.unit}</p>
                          <span className="text-[8px] font-mono text-[#00FF9C]">{s.benchmark}</span>
                       </div>
                       <p className="text-[10px] text-[#333] italic group-hover:text-[#444] transition-colors">Strategy: {s.strategy}</p>
                    </div>
                 ))}
                 <div className="flex justify-between items-center bg-[#050505] border border-[#111] p-4 rounded-sm">
                    <span className="text-[8px] font-bold text-[#333] uppercase">HPA Threshold</span>
                    <span className="text-[8px] font-mono text-[#E0E0E0]">CPU {" > "} 70% // Mem {" > "} 85%</span>
                 </div>
              </div>
           </div>

           <div className="bg-[#0A0A0A] border border-[#222] p-8 rounded-sm">
              <h3 className="text-xs font-bold uppercase tracking-widest text-[#666] mb-8 border-b border-[#111] pb-4 flex items-center gap-3">
                 <Terminal size={14} className="text-emerald-500" />
                 Operational Error Catalog
              </h3>
              <div className="grid grid-cols-1 gap-4">
                 {errorCodes.map((e, i) => (
                   <div key={i} className="flex justify-between items-start border-b border-[#111] pb-3 last:border-0 hover:bg-[#050505] transition-colors">
                      <div className="flex gap-4">
                         <span className="text-[9px] font-mono text-red-500/80 font-bold">{e.code}</span>
                         <div>
                            <p className="text-[10px] font-bold text-[#E0E0E0] uppercase">{e.label}</p>
                            <p className="text-[9px] text-[#444] italic">{e.desc}</p>
                         </div>
                      </div>
                   </div>
                 ))}
              </div>
           </div>

           <div className="bg-black border border-[#222] p-8 rounded-sm">
              <h3 className="text-xs font-bold uppercase tracking-widest text-[#666] mb-6 border-b border-[#111] pb-4 flex items-center gap-3">
                 <Layers size={14} className="text-indigo-400" />
                 UI Component Library Specification
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                 <div className="space-y-4">
                    <p className="text-[9px] font-bold text-[#E0E0E0] uppercase">Visual DNA</p>
                    <ul className="text-[9px] text-[#444] space-y-2 font-mono uppercase">
                       <li>• Typography: Inter (UI) / JetBrains Mono (Data)</li>
                       <li>• Theme: High-Contrast Dark (Cosmic Slate)</li>
                       <li>• Grid: 8px Incremental Baseline</li>
                       <li>• Shadows: 0px (Flat Design Architecture)</li>
                    </ul>
                 </div>
                 <div className="space-y-4">
                    <p className="text-[9px] font-bold text-[#E0E0E0] uppercase">Atomic Patterns</p>
                    <div className="grid grid-cols-2 gap-2">
                       {['Button_Primary', 'Card_Container', 'Data_Indicator', 'Input_Field'].map(c => (
                          <div key={c} className="p-2 border border-[#111] text-[8px] text-[#222] font-mono text-center">
                             {c}
                          </div>
                       ))}
                    </div>
                 </div>
              </div>
              <div className="mt-8 p-4 border border-dashed border-[#111] rounded-sm">
                 <p className="text-[8px] font-bold text-[#333] uppercase">Accessibility</p>
                 <p className="text-[9px] text-[#333] italic mt-1 uppercase font-mono">
                   WCAG 2.1 AA Compliant // 4.5:1 Contrast Ratio // Focus State: 2px Solid Emerald
                 </p>
              </div>
           </div>

           <div className="bg-black border border-[#222] p-8 rounded-sm">
              <h3 className="text-xs font-bold uppercase tracking-widest text-[#666] mb-6 border-b border-[#111] pb-4 flex items-center gap-3">
                 <ShieldCheck size={14} className="text-emerald-500" />
                 Mobile Offline-Sync Architecture
              </h3>
              <div className="space-y-6">
                 {mobileSync.map((s, i) => (
                   <div key={i} className="flex gap-4">
                      <div className="w-1.5 h-1.5 bg-[#00FF9C] rounded-full mt-1 shrink-0" />
                      <div>
                         <p className="text-[10px] font-bold text-[#E0E0E0] uppercase tracking-tight">{s.step}</p>
                         <p className="text-[9px] text-[#444] italic leading-relaxed">{s.desc}</p>
                      </div>
                   </div>
                 ))}
                 <div className="pt-4 border-t border-[#111]">
                    <p className="text-[8px] font-bold text-[#222] uppercase tracking-widest">Mobile UI Specs</p>
                    <p className="text-[9px] text-[#333] italic mt-1 uppercase font-mono">
                      Correction Queue // Order Detail // Sync Status // 8px Grid // Flat Theme (No Shadows)
                    </p>
                 </div>
              </div>
           </div>

           <div className="bg-[#0A0A0A] border border-[#222] p-8 rounded-sm">
              <h3 className="text-xs font-bold uppercase tracking-widest text-[#666] mb-8 border-b border-[#111] pb-4 flex items-center gap-3">
                 <Terminal size={14} className="text-emerald-500" />
                 API Pagination & Sorting Spec
              </h3>
              <div className="space-y-6">
                 <div className="p-4 bg-black/40 border border-[#111] rounded-sm">
                    <p className="text-[9px] font-bold text-[#E0E0E0] uppercase mb-2">Cursor-Based Pagination</p>
                    <p className="text-[10px] text-[#444] italic leading-relaxed mb-3">Minimalist, O(log n) lookup, no offset degradation.</p>
                    <div className="grid grid-cols-2 gap-4 font-mono text-[8px] text-[#666] uppercase">
                       <div>• cursor (string)</div>
                       <div>• limit (max 200)</div>
                    </div>
                 </div>
                 <div className="grid grid-cols-2 gap-4">
                    <div className="p-4 bg-[#080808] border border-[#111] rounded-sm">
                       <p className="text-[9px] font-bold text-[#E0E0E0] uppercase mb-2">Filters</p>
                       <p className="text-[8px] text-[#444] font-mono uppercase">status // date_range // tenant_id // payment_status</p>
                    </div>
                    <div className="p-4 bg-[#080808] border border-[#111] rounded-sm">
                       <p className="text-[9px] font-bold text-[#E0E0E0] uppercase mb-2">Sorting</p>
                       <p className="text-[8px] text-[#444] font-mono uppercase">created_at // total_estimate // confidence</p>
                    </div>
                 </div>
              </div>
           </div>

           <div className="bg-[#0A0A0A] border border-[#222] p-8 rounded-sm">
              <h3 className="text-xs font-bold uppercase tracking-widest text-[#666] mb-8 border-b border-[#111] pb-4 flex items-center gap-3">
                 <Cpu size={14} className="text-emerald-500" />
                 Worker Job Taxonomy
              </h3>
              <div className="space-y-4">
                 {jobTaxonomy.map((j, i) => (
                   <div key={i} className="flex justify-between items-center border-b border-[#111] pb-3 last:border-0 hover:bg-[#050505] transition-colors p-2">
                      <span className="text-[9px] font-mono text-emerald-400 font-bold">{j.job}</span>
                      <p className="text-[9px] text-[#444] italic text-right max-w-[200px]">{j.desc}</p>
                   </div>
                 ))}
                 <div className="p-4 bg-black/40 border border-[#111] rounded-sm mt-4">
                    <p className="text-[8px] font-bold text-[#333] uppercase">Guarantees</p>
                    <p className="text-[9px] text-[#444] italic leading-relaxed">At-least-once execution // Idempotency via key hashing // Exp. Backoff retries.</p>
                 </div>
              </div>
           </div>

           <div className="bg-[#0A0A0A] border border-[#222] p-8 rounded-sm">
              <h3 className="text-xs font-bold uppercase tracking-widest text-[#666] mb-8 border-b border-[#111] pb-4 flex items-center gap-3">
                 <ShieldCheck size={14} className="text-red-400" />
                 STRIDE Threat Model
              </h3>
              <div className="grid grid-cols-1 gap-3">
                 {threats.map((t, i) => (
                   <div key={i} className="p-4 bg-[#080808] border border-[#111] rounded-sm flex justify-between items-center group">
                      <p className="text-[9px] font-bold text-[#E0E0E0] uppercase">{t.name}</p>
                      <span className="text-[8px] font-mono text-[#00FF9C] uppercase bg-[#00FF9C]/5 px-2 py-0.5 border border-[#00FF9C]/10">{t.mitigation}</span>
                   </div>
                 ))}
                 <div className="mt-4 p-4 border border-dashed border-[#222] rounded-sm">
                    <p className="text-[9px] text-[#333] leading-relaxed uppercase">
                      Security Posture: Zero-trust networking // Immutable audit logs // Automated vulnerability scanning via GH-Actions.
                    </p>
                 </div>
              </div>
           </div>
        </div>
      </div>
    </motion.div>
  );
}
