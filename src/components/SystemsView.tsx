import React from 'react';
import { motion } from 'motion/react';
import { Server, Cpu, Globe, Terminal, ShieldCheck, Database, Layers } from 'lucide-react';
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
    { unit: 'Parser Service', strategy: 'Stateless, horizontal POD scaling via HPA.' },
    { unit: 'Worker Cluster', strategy: 'Scale based on Redis queue depth (Length-Aware).' },
    { unit: 'Database Tier', strategy: 'Tenant partitioning + Read replicas for BI analytics.' },
    { unit: 'Twin Simulator', strategy: 'Isolated batch jobs, zero impact on production ingress.' }
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
                 <Cpu size={14} className="text-[#00FF9C]" />
                 Scaling & Elasticity
              </h3>
              <div className="grid grid-cols-1 gap-4">
                 {scaling.map((s, i) => (
                   <div key={i} className="p-4 bg-[#080808] border border-[#111] rounded-sm group hover:border-[#222] transition-colors">
                      <p className="text-[9px] font-bold text-[#666] uppercase tracking-widest mb-1 group-hover:text-[#E0E0E0] transition-colors">{s.unit}</p>
                      <p className="text-[10px] text-[#333] italic group-hover:text-[#444] transition-colors">Strategy: {s.strategy}</p>
                   </div>
                 ))}
              </div>
           </div>
        </div>

        <div className="space-y-8">
           <div className="bg-[#0A0A0A] border border-[#222] p-8 rounded-sm">
              <div className="flex justify-between items-center mb-10 border-b border-[#111] pb-4">
                 <h3 className="text-xs font-bold uppercase tracking-widest text-[#666] flex items-center gap-3">
                    <Terminal size={14} className="text-emerald-500" />
                    API Specifications
                 </h3>
                 <span className="text-[9px] text-[#444] font-mono">OAS 3.0</span>
              </div>
              
              <div className="space-y-6">
                 {[
                   { method: 'POST', path: '/webhook', desc: 'Entry point for WhatsApp JSON payloads. HMAC Required.' },
                   { method: 'GET', path: '/orders', desc: 'List tenant orders with status/date filter logic.' },
                   { method: 'POST', path: '/simulate/run', desc: 'Trigger twin engine scenario execution.' },
                   { method: 'POST', path: '/invoices', desc: 'Generate DuitNow compatible financial records.' }
                 ].map((api, i) => (
                   <div key={i} className="group">
                      <div className="flex items-center gap-3 mb-2">
                         <span className={cn(
                           "text-[8px] font-bold px-1.5 py-0.5 rounded-sm font-mono",
                           api.method === 'POST' ? "bg-indigo-500/20 text-indigo-400" : "bg-emerald-500/20 text-emerald-400"
                         )}>
                            {api.method}
                         </span>
                         <span className="text-[10px] font-bold text-[#E0E0E0] font-mono tracking-tight group-hover:text-[#00FF9C] transition-colors">{api.path}</span>
                      </div>
                      <p className="text-[10px] text-[#444] leading-relaxed italic pl-0 group-hover:pl-2 transition-all">{api.desc}</p>
                   </div>
                 ))}
              </div>
           </div>

           <div className="bg-[#0A0A0A] border border-[#222] p-8 rounded-sm">
              <h3 className="text-xs font-bold uppercase tracking-widest text-[#666] mb-8 flex items-center gap-3">
                 <ShieldCheck size={14} />
                 Compliance Sign-Off
              </h3>
              <div className="space-y-4">
                 <div className="flex items-center gap-5 p-4 bg-[#080808] border border-[#111] rounded-sm">
                    <div className="w-1.5 h-10 bg-[#00FF9C]" />
                    <div>
                       <p className="text-[9px] font-bold text-[#E0E0E0] uppercase">PDPA Data Residency</p>
                       <p className="text-[9px] text-[#444] italic">Housed in Malaysia North (MY-N1) Regional Cluster.</p>
                    </div>
                 </div>
                 <div className="flex items-center gap-5 p-4 bg-[#080808] border border-[#111] rounded-sm opacity-50">
                    <div className="w-1.5 h-10 bg-[#333]" />
                    <div>
                       <p className="text-[9px] font-bold text-[#666] uppercase">SOC2 Compliance</p>
                       <p className="text-[9px] text-[#222] italic">Pending annual renewal (target: 2026.Q4).</p>
                    </div>
                 </div>
              </div>
           </div>

           <div className="p-6 bg-white/[0.02] border border-[#222] rounded-sm shadow-xl">
              <p className="text-[10px] text-[#333] italic leading-relaxed uppercase tracking-tighter">
                Infrastructure as Code verification status: <span className="text-[#00FF9C]">Verified_Synchronized</span>
              </p>
              <div className="mt-4 flex gap-4">
                 <div className="h-1 flex-1 bg-[#111] rounded-full overflow-hidden">
                    <div className="h-full w-[94%] bg-[#00FF9C] shadow-[0_0_8px_#00FF9C]" />
                 </div>
                 <span className="text-[9px] font-mono text-[#00FF9C]">94.2%</span>
              </div>
           </div>
        </div>
      </div>
    </motion.div>
  );
}
