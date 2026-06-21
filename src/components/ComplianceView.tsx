import { motion } from 'motion/react';
import { History, ShieldCheck as ShieldCheckIcon, AlertTriangle, FileText, Download, Shield } from 'lucide-react';
import { cn } from '../utils';

export default function ComplianceView() {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-8 pb-20"
    >
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-8">
          <div className="bg-[#0A0A0A] border border-[#222] p-8 rounded-sm shadow-sm">
            <div className="flex justify-between items-center mb-10 pb-4 border-b border-[#111]">
              <h3 className="text-xs font-bold uppercase tracking-widest text-[#666]">Governance & Privacy Shield</h3>
              <div className="flex items-center gap-2 px-3 py-1 bg-[#111] border border-[#222] rounded-full">
                <ShieldCheckIcon size={12} className="text-[#00FF9C]" />
                <span className="text-[10px] text-[#00FF9C] font-mono font-bold uppercase">PDPA_V2_COMPLIANT</span>
              </div>
            </div>

            <div className="space-y-12">
               <div className="relative pl-12 border-l border-[#111]">
                  <div className="absolute top-0 left-[-5px] w-2.5 h-2.5 rounded-full bg-[#00FF9C] shadow-[0_0_8px_#00FF9C]" />
                  <div>
                    <h4 className="text-[10px] font-bold text-[#E0E0E0] uppercase tracking-widest flex items-center gap-3">
                       STRATEGIC ROADMAP: PH 1 - FOUNDATIONS
                       <span className="text-[8px] px-2 py-0.5 bg-[#00FF9C]/10 text-[#00FF9C] border border-[#00FF9C]/20 rounded-full font-bold">COMPLETED</span>
                    </h4>
                    <p className="text-[9px] text-[#444] italic mt-1 font-mono uppercase">Status_Registry: Verified_Audit_2026.06.19</p>
                    <ul className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
                       <li className="p-4 bg-[#080808] border border-[#111] rounded-sm text-[10px] text-[#666] leading-relaxed">
                          <span className="text-[#E0E0E0] font-bold block mb-1 underline decoration-[#00FF9C]">MALAYSIAN NODE INGRESS</span>
                          Implemented WhatsApp Webhook adapter with HMAC signature verification clusters in Kuala Lumpur data centers.
                       </li>
                       <li className="p-4 bg-[#080808] border border-[#111] rounded-sm text-[10px] text-[#666] leading-relaxed">
                          <span className="text-[#E0E0E0] font-bold block mb-1 underline decoration-[#00FF9C]">FEDERATED PARSER v1</span>
                          Deployment of Gemini-powered intent extraction engine with localized SME Malaysian-English/Malay semantics.
                       </li>
                    </ul>
                  </div>
               </div>

               <div className="relative pl-12 border-l border-[#111]">
                  <div className="absolute top-0 left-[-5px] w-2.5 h-2.5 rounded-full bg-yellow-500 shadow-[0_0_8px_rgba(234,179,8,0.5)]" />
                  <div>
                    <h4 className="text-[10px] font-bold text-yellow-500 uppercase tracking-widest flex items-center gap-3">
                       PH 2 - FINANCIAL MESH & DUITNOW
                       <span className="text-[8px] px-2 py-0.5 bg-yellow-500/10 text-yellow-500 border border-yellow-500/20 rounded-full font-bold">IN_PROGRESS</span>
                    </h4>
                    <p className="text-[9px] text-[#444] italic mt-1 font-mono uppercase">Sprint_Node: 02_Accounting_Protocol</p>
                    <ul className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
                       <li className="p-4 bg-[#080808] border border-[#111] rounded-sm text-[10px] text-[#666] leading-relaxed opacity-60">
                          <span className="text-yellow-500/80 font-bold block mb-1">REAL-TIME SETTLEMENTS</span>
                          Integration of direct DuitNow QR dynamic link generation within WhatsApp invoice cycles for faster conversion.
                       </li>
                       <li className="p-4 bg-yellow-500/5 border border-yellow-500/10 rounded-sm text-[10px] text-yellow-500/60 leading-relaxed">
                          <span className="font-bold block mb-1">HITL MOBILE SYNC</span>
                          Final testing of offline-first mobile correction interface for SME store staff.
                       </li>
                    </ul>
                  </div>
               </div>

               <div className="relative pl-12 border-l border-[#111]">
                  <div className="absolute top-0 left-[-5px] w-2.5 h-2.5 rounded-full border border-[#222] bg-[#050505]" />
                  <div>
                    <h4 className="text-[10px] font-bold text-[#666] uppercase tracking-widest">PH 3 - VERTICAL EXPANSION</h4>
                    <p className="text-[9px] text-[#222] italic mt-1 font-mono uppercase">Target_Release: 2026.Q4</p>
                  </div>
               </div>

               <div className="relative pl-12 border-l border-[#111]">
                  <div className="absolute top-0 left-[-5px] w-2.5 h-2.5 rounded-full border border-[#111] bg-[#020202]" />
                  <div>
                    <h4 className="text-[10px] font-bold text-[#333] uppercase tracking-widest">PH 4 - DEEP INTEGRATIONS (POS/INV)</h4>
                    <p className="text-[9px] text-[#222] italic mt-1 font-mono uppercase">Target_Release: 2027.Q1</p>
                  </div>
               </div>

               <div className="relative pl-12 border-l border-[#111]">
                  <div className="absolute top-0 left-[-5px] w-2.5 h-2.5 rounded-full border border-[#111] bg-[#020202]" />
                  <div>
                    <h4 className="text-[10px] font-bold text-[#333] uppercase tracking-widest">PH 5 - REGIONAL GROWTH (ML)</h4>
                    <p className="text-[9px] text-[#222] italic mt-1 font-mono uppercase">Target_Release: 2027.Q2</p>
                  </div>
               </div>

               <div className="relative pl-12 border-l border-[#111]">
                  <div className="absolute top-0 left-[-5px] w-2.5 h-2.5 rounded-full border border-[#111] bg-[#020202]" />
                  <div>
                    <h4 className="text-[10px] font-bold text-[#333] uppercase tracking-widest">PH 6 - SME FINANCING MESH</h4>
                    <p className="text-[9px] text-[#222] italic mt-1 font-mono uppercase">Target_Release: 2027.Q4</p>
                  </div>
               </div>

               <div className="pt-8 mt-8 border-t border-[#111]">
                  <h4 className="text-[10px] font-bold text-[#E0E0E0] uppercase tracking-widest mb-6">Pilot Success Framework</h4>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                     {[
                       { label: 'Error Reduction', target: '≥60%', icon: ShieldCheckIcon, color: '#00FF9C' },
                       { label: 'Admin Time Saved', target: '≥50%', icon: History, color: '#00FF9C' },
                       { label: 'Conversion Lift', target: '≥20%', icon: FileText, color: '#00FF9C' },
                       { label: 'Pilot NPS', target: '≥8.0', icon: ShieldCheckIcon, color: '#00FF9C' }
                     ].map((s, i) => (
                       <div key={i} className="p-4 bg-[#080808] border border-[#111] rounded-sm text-center">
                          <s.icon size={14} className="mx-auto mb-2" style={{ color: s.color }} />
                          <div className="text-[8px] font-bold text-[#444] uppercase tracking-tighter mb-1">{s.label}</div>
                          <div className="text-sm font-bold text-[#E0E0E0] font-mono tracking-wider">{s.target}</div>
                       </div>
                     ))}
                  </div>
               </div>
            </div>
          </div>

          <div className="bg-[#0A0A0A] border border-[#222] p-8 rounded-sm">
             <h3 className="text-xs font-bold uppercase tracking-widest text-[#666] mb-8">Data Privacy & Regional Compliance</h3>
             <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div className="space-y-6">
                   <div>
                      <p className="text-[10px] font-bold text-[#E0E0E0] uppercase tracking-wider mb-2">Encryption Standards</p>
                      <p className="text-[11px] text-[#444] leading-relaxed italic">
                        AES-256 encryption applied to all PII fields (Customer Name, Address, Phone). Tenant-specific keys rotated every 90 days.
                      </p>
                   </div>
                   <div>
                      <p className="text-[10px] font-bold text-[#E0E0E0] uppercase tracking-wider mb-2">Federated Learning</p>
                      <p className="text-[11px] text-[#444] leading-relaxed italic">
                        Model training is opt-in only. All datasets are anonymized with differential privacy noise prior to node synchronization.
                      </p>
                   </div>
                </div>
                <div className="p-6 bg-[#050505] border border-[#111] space-y-4">
                   <div className="flex justify-between items-center border-b border-[#111] pb-3">
                      <span className="text-[9px] font-bold text-[#666] uppercase">Regulatory Region</span>
                      <span className="text-[9px] text-[#00FF9C] font-mono">MALAYSIA_CENTRAL</span>
                   </div>
                   <div className="flex justify-between items-center border-b border-[#111] pb-3">
                      <span className="text-[9px] font-bold text-[#666] uppercase">Data Residency</span>
                      <span className="text-[9px] text-[#00FF9C] font-mono">KUALA_LUMPUR_DC</span>
                   </div>
                   <div className="flex justify-between items-center">
                      <span className="text-[9px] font-bold text-[#666] uppercase">Retention Policy</span>
                      <span className="text-[9px] text-[#00FF9C] font-mono">12_MONTHS_IMMUTABLE</span>
                   </div>
                </div>
             </div>
          </div>

          <div className="bg-[#0A0A0A] border border-[#222] p-8 rounded-sm">
             <h3 className="text-xs font-bold uppercase tracking-widest text-[#666] mb-8 border-b border-[#111] pb-4 flex items-center gap-3">
                <Shield size={14} className="text-[#00FF9C]" />
                Compliance Audit Checklist
             </h3>
             <div className="space-y-8">
                {[
                  { 
                    label: 'PDPA (Malaysia)', 
                    items: ['Data residency in Local Nodes', 'Consent forms for tenants', 'Right-to-erasure (RTB) logic', 'Encryption at-rest + in-transit'] 
                  },
                  { 
                    label: 'ISO 27001', 
                    items: ['ISMS framework documented', 'Risk register updated quarterly', 'Incident response tested', 'External audit scheduled'] 
                  },
                  { 
                    label: 'SOC 2 Security', 
                    items: ['Immutable audit trails', 'Role-based access (RBAC)', 'Real-time logging + active monitoring', 'Incident response playbooks'] 
                  }
                ].map((c, i) => (
                  <div key={i} className="space-y-4">
                     <p className="text-[10px] font-bold text-[#E0E0E0] uppercase tracking-widest flex items-center gap-3">
                        <span className="w-1.5 h-1.5 bg-[#00FF9C] rounded-full" />
                        {c.label}
                     </p>
                     <ul className="grid grid-cols-1 md:grid-cols-2 gap-3 pl-4">
                        {c.items.map((item, idx) => (
                          <li key={idx} className="flex items-center gap-2 text-[9px] text-[#444] font-mono">
                             <span className="text-[#222] italic">→</span>
                             {item}
                          </li>
                        ))}
                     </ul>
                  </div>
                ))}
             </div>
          </div>

          <div className="bg-[#0A0A0A] border border-[#222] p-8 rounded-sm">
             <h3 className="text-xs font-bold uppercase tracking-widest text-[#666] mb-8 border-b border-[#111] pb-4 flex items-center gap-3">
                <Shield size={14} className="text-[#00FF9C]" />
                Compliance Automation & Monitoring
             </h3>
             <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div className="space-y-6">
                   {[
                     { label: 'PII Encryption Script', status: 'Weekly validation', desc: 'Validates AES-256 integrity on all tenant tables.' },
                     { label: 'Key Rotation Cron', status: 'Next: 12 days', desc: 'Automated 90-day rotation for tenant KMS keys.' },
                     { label: 'Audit Log Immutable', status: 'Verified', desc: 'SHA-256 hash chaining checked against central audit node.' }
                   ].map((a, i) => (
                     <div key={i} className="p-4 bg-[#080808] border border-[#111] rounded-sm">
                        <div className="flex justify-between items-start mb-2">
                           <p className="text-[10px] font-bold text-[#E0E0E0] uppercase">{a.label}</p>
                           <span className="text-[8px] font-mono text-[#00FF9C] uppercase">{a.status}</span>
                        </div>
                        <p className="text-[9px] text-[#444] italic leading-relaxed">{a.desc}</p>
                     </div>
                   ))}
                </div>
                <div className="p-6 bg-black border border-[#111] border-dashed rounded-sm">
                   <p className="text-[10px] font-bold text-[#333] uppercase mb-4">Continuous Audit Metrics</p>
                   <div className="space-y-6">
                      {[
                        { label: 'Encryption Coverage', val: 100 },
                        { label: 'Consent Form Sync', val: 98.4 },
                        { label: 'Data Erasure Accuracy', val: 100 }
                      ].map((m, i) => (
                        <div key={i}>
                           <div className="flex justify-between text-[9px] text-[#E0E0E0] mb-2 font-mono">
                              <span>{m.label}</span>
                              <span>{m.val}%</span>
                           </div>
                           <div className="h-0.5 bg-[#111] rounded-full overflow-hidden">
                              <motion.div 
                                initial={{ width: 0 }}
                                animate={{ width: `${m.val}%` }}
                                className="h-full bg-emerald-500"
                              />
                           </div>
                        </div>
                      ))}
                   </div>
                   <p className="text-[8px] text-[#333] italic mt-8 uppercase font-mono tracking-tighter">
                     * Automated Pen-Test sequence runs bi-monthly. Last passed: 06.18.2026.
                   </p>
                </div>
             </div>
          </div>

          <div className="bg-[#0A0A0A] border border-[#222] p-8 rounded-sm">
             <h3 className="text-xs font-bold uppercase tracking-widest text-[#666] mb-8">Forensic Audit Trail</h3>
             <div className="space-y-4">
                {[
                  { event: 'ORDER_PARSED', ref: 'WH_9901X', time: '12:04:22', sig: '8a3b...c91e', detail: 'Raw Payload Verified' },
                  { event: 'INV_ISSUED', ref: 'INV_45001', time: '11:45:01', sig: '99a1...bb2c', detail: 'DuitNow Sig Match' },
                  { event: 'KEY_ROTATION', ref: 'SYS_001', time: '09:00:00', sig: '3e2d...f001', detail: 'Automated Cycle' }
                ].map((log, i) => (
                   <div key={i} className="flex justify-between items-center p-6 bg-[#080808] border border-[#111] group hover:border-[#222] transition-colors">
                      <div className="flex items-center gap-6">
                         <div className="w-1.5 h-6 bg-[#111] group-hover:bg-[#00FF9C] transition-colors" />
                         <div>
                            <p className="text-[10px] font-bold text-[#E0E0E0] tracking-wide">{log.event}</p>
                            <p className="text-[9px] text-[#444] mt-1 font-mono uppercase italic">{log.ref} • {log.time}</p>
                         </div>
                      </div>
                      <div className="text-right">
                         <p className="text-[9px] text-[#666] font-mono uppercase">{log.detail}</p>
                         <p className="text-[8px] text-[#222] mt-1 font-mono uppercase">Node_V: {log.sig}</p>
                      </div>
                   </div>
                ))}
             </div>
          </div>
        </div>

        <div className="space-y-8">
           <div className="bg-[#0A0A0A] border border-[#222] p-8 rounded-sm">
             <h3 className="text-xs font-bold uppercase tracking-widest text-[#666] mb-8 flex items-center gap-2">
                <AlertTriangle size={14} className="text-yellow-500" />
                Risk Register
             </h3>
             <div className="space-y-6">
                {[
                  { risk: 'WhatsApp API Latency', mit: 'Synthetic Mock Fallback', level: 'Med' },
                  { risk: 'Parser Confusion', mit: 'HITL Correction Loop', level: 'Low' },
                  { risk: 'Regulatory Compliance', mit: 'Malaysia Region Lockdown', level: 'Low' }
                ].map((r, i) => (
                  <div key={i} className="space-y-2">
                    <div className="flex justify-between text-[10px] font-bold uppercase tracking-wide">
                       <span className="text-[#E0E0E0]">{r.risk}</span>
                       <span className={cn(r.level === 'Med' ? "text-yellow-500" : "text-[#00FF9C]")}>{r.level}</span>
                    </div>
                    <p className="text-[9px] text-[#444] italic">Mitigation: {r.mit}</p>
                    <div className="h-0.5 w-full bg-[#111] rounded-full overflow-hidden">
                       <div className={cn("h-full", r.level === 'Med' ? "w-1/2 bg-yellow-500" : "w-1/4 bg-[#00FF9C]")} />
                    </div>
                  </div>
                ))}
             </div>
           </div>

           <div className="bg-[#0A0A0A] border border-[#222] p-8 rounded-sm">
              <h3 className="text-xs font-bold uppercase tracking-widest text-[#666] mb-8">Certificates & Exports</h3>
              <div className="space-y-3">
                 {[
                   { name: 'CCAM Security Audit Report.pdf', size: '2.4 MB' },
                   { name: 'PDPA Compliance Data Mapping.xlsx', size: '1.1 MB' },
                   { name: 'Node Latency Summary 06.2026.pdf', size: '450 KB' }
                 ].map((c, i) => (
                   <div key={i} className="flex justify-between items-center p-3 border border-[#111] hover:border-[#222] transition-colors cursor-pointer group">
                      <div className="flex items-center gap-3">
                        <FileText size={14} className="text-[#444] group-hover:text-[#E0E0E0]" />
                        <div>
                          <p className="text-[10px] text-[#888] group-hover:text-[#E0E0E0]">{c.name}</p>
                          <p className="text-[8px] text-[#333] mt-1 font-mono uppercase">{c.size}</p>
                        </div>
                      </div>
                      <Download size={12} className="text-[#222] group-hover:text-[#00FF9C] transition-colors" />
                   </div>
                 ))}
              </div>
           </div>
        </div>
      </div>
    </motion.div>
  );
}
