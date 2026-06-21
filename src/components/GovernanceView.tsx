import React from 'react';
import { motion } from 'motion/react';
import { BookOpen, Shield, Rocket, TrendingUp, Terminal, Cpu, Database, Layers, RefreshCw, Zap } from 'lucide-react';
import { cn } from '../utils';

export default function GovernanceView() {
  const onboarding = [
    { step: 'Prerequisites', items: ['Docker + Docker Compose', 'Python 3.11', 'Node.js 20', 'Redis CLI', 'Postgres Client'] },
    { step: 'Setup Steps', items: ['Clone repo', 'Copy .env.example → .env', 'Run docker-compose up', 'Access API @ :8000', 'Access Frontend @ :3000', 'Run pytest'] },
    { step: 'Dev Containers', items: ['Prebuilt images with dependencies', 'Hot reload enabled for API + UI', 'Integrated Redis/PG clients'] }
  ];

  const onboardingSteps = [
    'Tenant signs up via dashboard',
    'Tenant config stored in DB',
    'Keys generated + stored in secrets',
    'Default YAML flow provisioned',
    'Simulator run for baseline KPIs'
  ];

  const hitlWorkflow = [
    { step: 'Ingestion', desc: 'Parser produces structured order + confidence score.' },
    { step: 'Threshold', desc: 'If confidence < 0.85, push to correction queue.' },
    { step: 'Correction', desc: 'Mobile agent opens order & edits fields via UI.' },
    { step: 'Re-validation', desc: 'Corrections saved, parser audit updated, invoice generated.' }
  ];

  const runbooks = [
    { 
      name: 'Backup Runbook', 
      steps: ['Trigger backup job', 'Verify snapshot integrity', 'Store in S3 bucket', 'Log completion'] 
    },
    { 
      name: 'Failover Runbook', 
      steps: ['Detect DB node failure', 'Promote replica to primary', 'Update DNS records', 'Validate via health checks'] 
    },
    { 
      name: 'Scaling Runbook', 
      steps: ['Monitor Redis queue length', 'If > threshold, scale workers', 'Validate throughput', 'Log event'] 
    }
  ];

  const future = [
    { goal: 'AI Forecasting (Deep Dive)', desc: 'LSTM / Prophet pipeline to predict demand spikes using historical orders, weather, and holidays.' },
    { goal: 'POS Integration (Deep Dive)', desc: 'SKU mapping engine & POS connector microservice for real-time stock sync & unified reporting.' },
    { goal: 'Regional expansion', desc: 'Localized flows for SG, ID with PDPA/GDPR hardcoded safeguards.' },
    { goal: 'Flow Marketplace', desc: 'Monetized YAML microflows for specific merchant domains.' }
  ];

  const lifecycle = [
    'Tenant Onboarding', 'Flow Configuration', 'Parser Training', 
    'Simulator Validation', 'Production Rollout', 'Monitoring & Alerts', 
    'Corrections & Learning', 'Billing & Compliance', 'Continuous Improvement'
  ];

  const slos = [
    { type: 'SLI', label: 'API Latency', target: 'p95 < 150ms' },
    { type: 'SLI', label: 'Parser Accuracy', target: '≥ 90%' },
    { type: 'SLI', label: 'Invoice Delivery', target: '≥ 99%' },
    { type: 'SLO', label: 'API Uptime', target: '99.9%' },
    { type: 'SLO', label: 'Webhook Ingestion', target: '99% Success' },
    { type: 'SLA', label: 'P1 Response', target: '< 15 mins' },
    { type: 'SLA', label: 'P2 Response', target: '< 4 hours' },
    { type: 'SLA', label: 'P3 Response', target: '< 24 hours' }
  ];

  const migration001 = `def upgrade():
    op.create_table(
        'tenant',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(255)),
        sa.Column('config', sa.JSON),
        sa.Column('keys', sa.JSON),
    )
    op.create_table(
        'order',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('tenant_id', sa.Integer, sa.ForeignKey('tenant.id')),
        sa.Column('customer_name', sa.String(255)),
        sa.Column('items_json', sa.JSON),
        sa.Column('status', sa.String(50)),
        sa.Column('created_at', sa.DateTime),
    )`;

  const calendar = [
    { period: 'Daily', tasks: ['Parser Accuracy Check', 'Queue Health Check', 'Invoice Reconciliation', 'Error Log Review'] },
    { period: 'Weekly', tasks: ['Simulator Baseline Run', 'Flow Validation', 'DB Vacuum/Analyze'] },
    { period: 'Monthly', tasks: ['Tenant Usage Reports', 'Security Patch Review', 'Model Drift Analysis'] },
    { period: 'Quarterly', tasks: ['Key Rotation', 'Penetration Test', 'Compliance Audit'] }
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-12 pb-24"
    >
      <div className="flex justify-between items-end">
        <div>
          <h2 className="text-xl font-bold text-[#E0E0E0] tracking-tight">Onboarding & Governance</h2>
          <p className="text-[10px] text-[#444] font-mono mt-1 uppercase tracking-widest italic">Standardized Developer & Release Protocol v2.1</p>
        </div>
      </div>

      <div className="bg-[#0A0A0A] border border-[#222] p-8 rounded-sm">
         <h3 className="text-xs font-bold uppercase tracking-[0.2em] text-[#666] mb-8 flex items-center gap-3 border-b border-[#111] pb-4">
            <Layers size={14} className="text-emerald-500" />
            End-to-End Operational Lifecycle
         </h3>
         <div className="flex flex-wrap gap-4">
            {lifecycle.map((s, i) => (
               <div key={i} className="flex items-center gap-3 bg-[#080808] border border-[#111] px-4 py-2 group hover:border-[#00FF9C]/20 transition-all">
                  <span className="text-[9px] font-mono text-[#222] group-hover:text-[#00FF9C] transition-colors">{i+1}</span>
                  <p className="text-[10px] font-bold text-[#444] group-hover:text-[#E0E0E0] uppercase tracking-tighter transition-colors">{s}</p>
               </div>
            ))}
         </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
         {/* Database Migrations */}
         <div className="space-y-8">
            <h3 className="text-xs font-bold uppercase tracking-[0.2em] text-[#666] flex items-center gap-3 border-b border-[#111] pb-4">
               <Database size={14} className="text-emerald-500" />
               Schema Migrations (Alembic)
            </h3>
            <div className="bg-black border border-[#222] p-6 rounded-sm">
               <p className="text-[9px] font-bold text-[#E0E0E0] uppercase mb-4 font-mono">001_initial_core.py</p>
               <pre className="text-[9px] font-mono text-[#444] leading-relaxed overflow-x-auto whitespace-pre">
                  {migration001}
               </pre>
               <div className="mt-6 pt-4 border-t border-[#111]">
                  <p className="text-[8px] text-[#333] font-mono uppercase">Migration 002 adds parser_audit with confidence scoring & HITL correlation.</p>
               </div>
            </div>
         </div>

         {/* SLO/SLA Definitions */}
         <div className="space-y-8">
            <h3 className="text-xs font-bold uppercase tracking-[0.2em] text-[#666] flex items-center gap-3 border-b border-[#111] pb-4">
               <TrendingUp size={14} className="text-indigo-400" />
               Service Level Indicators (SLI/SLO/SLA)
            </h3>
            <div className="grid grid-cols-2 gap-4">
               {slos.map((s, i) => (
                  <div key={i} className="p-4 bg-[#0A0A0A] border border-[#222] rounded-sm group hover:border-indigo-500/20 transition-colors">
                     <div className="flex justify-between items-center mb-1">
                        <span className={cn(
                           "text-[7px] font-bold px-1 rounded-sm",
                           s.type === 'SLI' ? "bg-emerald-500/10 text-emerald-400" :
                           s.type === 'SLO' ? "bg-indigo-500/10 text-indigo-400" : "bg-red-500/10 text-red-400"
                        )}>{s.type}</span>
                        <span className="text-[9px] font-mono text-[#E0E0E0]">{s.target}</span>
                     </div>
                     <p className="text-[9px] text-[#444] uppercase tracking-tight font-bold">{s.label}</p>
                  </div>
               ))}
            </div>
         </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
         {/* Onboarding */}
         <div className="space-y-8">
            <h3 className="text-xs font-bold uppercase tracking-[0.2em] text-[#666] flex items-center gap-3 border-b border-[#111] pb-4">
               <BookOpen size={14} className="text-[#00FF9C]" />
               Developer & Tenant Initiation
            </h3>
            <div className="grid grid-cols-1 gap-6">
               <div className="bg-[#0A0A0A] border border-[#222] p-6 rounded-sm">
                  <p className="text-[10px] font-bold text-[#E0E0E0] uppercase mb-4 border-b border-[#111] pb-2">Tenant Onboarding Sequence</p>
                  <div className="space-y-4">
                     {onboardingSteps.map((s, i) => (
                        <div key={i} className="flex items-center gap-3">
                           <span className="text-[9px] font-mono text-[#222] w-4">0{i+1}</span>
                           <p className="text-[10px] text-[#444] font-mono uppercase tracking-tighter">{s}</p>
                        </div>
                     ))}
                  </div>
               </div>
               {onboarding.slice(0, 2).map((s, i) => (
                 <div key={i} className="bg-[#0A0A0A] border border-[#222] p-6 rounded-sm">
                    <p className="text-[10px] font-bold text-[#E0E0E0] uppercase mb-4 border-b border-[#111] pb-2">{s.step}</p>
                    <ul className="space-y-2">
                       {s.items.map((item, idx) => (
                         <li key={idx} className="flex items-center gap-3 text-[10px] text-[#444] font-mono">
                            <span className="text-[#00FF9C]">→</span>
                            {item}
                         </li>
                       ))}
                    </ul>
                 </div>
               ))}
            </div>
         </div>

         {/* HITL Pipeline + Sync Details */}
         <div className="space-y-8">
            <h3 className="text-xs font-bold uppercase tracking-[0.2em] text-[#666] flex items-center gap-3 border-b border-[#111] pb-4">
               <Shield size={14} className="text-indigo-400" />
               HITL & Mobile Offline Sync
            </h3>
            <div className="bg-[#0A0A0A] border border-[#222] p-8 rounded-sm space-y-6">
               <div className="space-y-4">
                  {hitlWorkflow.map((s, i) => (
                    <div key={i} className="flex gap-4">
                       <span className="text-[10px] font-mono text-indigo-400 shrink-0">{s.step}</span>
                       <p className="text-[9px] text-[#444] italic leading-relaxed">{s.desc}</p>
                    </div>
                  ))}
               </div>
               <div className="pt-4 border-t border-[#111]">
                  <p className="text-[8px] font-bold text-[#333] uppercase mb-2">SQLite Partition Schema</p>
                  <pre className="text-[8px] font-mono text-[#222] bg-black p-3 rounded-sm leading-tight">
{`{
  "orders": [{
    "id": "123",
    "dirty": true,
    "fields": { "item": "...", "qty": 0 }
  }]
}`}
                  </pre>
               </div>
               <div className="p-4 bg-black border border-[#111] border-dashed rounded-sm">
                  <p className="text-[8px] font-bold text-[#333] uppercase mb-2">Conflict Resolution</p>
                  <p className="text-[9px] text-[#444] italic uppercase leading-relaxed font-mono">
                     Server wins Structural // Client wins Corrections // Timestamps break ties.
                  </p>
               </div>
            </div>
         </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 pt-12 border-t border-[#111]">
         {/* SRE Playbooks */}
         <div className="space-y-8">
            <h3 className="text-xs font-bold uppercase tracking-[0.2em] text-[#666] flex items-center gap-3 border-b border-[#111] pb-4">
               <Terminal size={14} className="text-red-400" />
               Alerting & SRE Playbooks
            </h3>
            <div className="space-y-4">
               {[
                 { alert: 'Latency > 200ms', action: 'Scale workers if queue depth > threshold.' },
                 { alert: 'Accuracy < 85%', action: 'Rollback parser, evaluate model drift triggers.' },
                 { alert: 'Callback Failure', action: 'Validate payment keys, retry with backoff.' }
               ].map((a, i) => (
                 <div key={i} className="p-4 bg-[#0A0A0A] border border-[#222] rounded-sm">
                    <p className="text-[10px] font-bold text-red-500/80 uppercase mb-1">{a.alert}</p>
                    <p className="text-[9px] text-[#444] italic leading-relaxed">Action: {a.action}</p>
                 </div>
               ))}
            </div>
         </div>

         {/* UX Writing */}
         <div className="space-y-8">
            <h3 className="text-xs font-bold uppercase tracking-[0.2em] text-[#666] flex items-center gap-3 border-b border-[#111] pb-4">
               <BookOpen size={14} className="text-emerald-500" />
               UX Writing & Canonical Labels
            </h3>
            <div className="bg-[#0A0A0A] border border-[#222] p-6 rounded-sm">
               <div className="grid grid-cols-2 gap-6">
                  <div>
                     <p className="text-[9px] font-bold text-[#E0E0E0] uppercase mb-3">Principles</p>
                     <ul className="space-y-1 text-[9px] text-[#444] italic font-mono uppercase tracking-tighter">
                        <li>• Clarity (No Jargon)</li>
                        <li>• Brevity (Short sentences)</li>
                        <li>• Neutral (No emojis)</li>
                     </ul>
                  </div>
                  <div className="text-[9px] font-mono text-[#222] leading-loose uppercase">
                    "Order received."<br/>
                    "Invoice sent."<br/>
                    "Correction needed."<br/>
                    "Payment confirmed."
                  </div>
               </div>
            </div>
         </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
         {/* ML Lifecycle */}
         <div className="bg-[#0A0A0A] border border-[#222] p-8 rounded-sm">
            <h3 className="text-xs font-bold uppercase tracking-[0.2em] text-[#666] flex items-center gap-3 border-b border-[#111] pb-4">
               <Cpu size={14} className="text-indigo-400" />
               ML Model Lifecycle
            </h3>
            <div className="grid grid-cols-4 gap-2 mb-6">
               {['Collect', 'Process', 'Train', 'Eval', 'Verson', 'Deploy', 'Monitor', 'Retrain'].map((s, i) => (
                  <div key={i} className="p-2 bg-[#080808] border border-[#111] rounded-sm text-center">
                     <p className="text-[7px] font-bold text-[#333] uppercase font-mono">{s}</p>
                  </div>
               ))}
            </div>
            <p className="text-[8px] font-bold text-[#222] uppercase tracking-widest text-center mt-4">
               Drift Detection: Confidence Shift // Error Spikes // Queue Vol Spikes
            </p>
         </div>

         {/* Maintenance Calendar */}
         <div className="bg-[#0A0A0A] border border-[#222] p-8 rounded-sm">
            <h3 className="text-xs font-bold uppercase tracking-[0.2em] text-[#666] flex items-center gap-3 border-b border-[#111] pb-4">
               <RefreshCw size={14} className="text-indigo-400" />
               Maintenance Calendar
            </h3>
            <div className="grid grid-cols-2 gap-4">
               {calendar.map((c, i) => (
                  <div key={i} className="p-3 bg-[#080808] border border-[#111] rounded-sm">
                     <p className="text-[9px] font-bold text-[#E0E0E0] uppercase mb-1">{c.period}</p>
                     <p className="text-[8px] text-[#444] font-mono uppercase truncate">{c.tasks[0]} & more</p>
                  </div>
               ))}
            </div>
         </div>
      </div>

      <div className="bg-[#050505] border-t border-[#111] pt-8 flex justify-between items-center opacity-30 grayscale hover:opacity-100 hover:grayscale-0 transition-all">
         <div className="flex gap-12">
            {[
              { label: 'SIMPLICITY', val: 'Few services, clear separation' },
              { label: 'CLARITY', val: 'File structure mirrors logic' },
              { label: 'ESTHETIC', val: 'Neutral UI, deep green highlights' }
            ].map((p, i) => (
              <div key={i}>
                 <p className="text-[9px] font-bold text-[#E0E0E0] uppercase tracking-[0.2em] mb-1">{p.label}</p>
                 <p className="text-[8px] text-[#444] uppercase font-mono italic">{p.val}</p>
              </div>
            ))}
         </div>
         <p className="text-[8px] text-[#222] font-mono uppercase tracking-[0.5em] select-none">ARCHITECTURE_HONESTY_MANIFESTO</p>
      </div>
    </motion.div>
  );
}
