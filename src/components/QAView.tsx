import React from 'react';
import { motion } from 'motion/react';
import { ShieldCheck as ShieldCheckIcon, FileCheck, Search, Database, ListFilter } from 'lucide-react';
import { cn } from '../utils';

export default function QAView() {
  const testCases = [
    { section: 'Ingestion', id: 'TC-I-01', title: 'Valid Signature Ingestion', status: 'PASSED', evidence: 'Signature verified via HSA256' },
    { section: 'Parser', id: 'TC-P-02', title: 'Mee Goreng Mixed Language', status: 'PASSED', evidence: 'Parsed with 0.89 confidence' },
    { section: 'Parser', id: 'TC-P-03', title: 'Ambiguous Message Routing', status: 'PASSED', evidence: 'Confidence 0.42 -> HITL Queue' },
    { section: 'Simulation', id: 'TC-S-01', title: 'Peak Load 500 MSG/MIN', status: 'PASSED', evidence: 'Latency stable at 240ms' },
    { section: 'Audit', id: 'TC-A-01', title: 'Immutable Audit Log Link', status: 'PASSED', evidence: 'SHA-256 Chain Verified' }
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-12 pb-24"
    >
      <div className="flex justify-between items-end">
        <div>
          <h2 className="text-xl font-bold text-[#E0E0E0] tracking-tight">QA Factory & Acceptance Tracking</h2>
          <p className="text-[10px] text-[#444] font-mono mt-1 uppercase tracking-widest">Environment: MSIA_PILOT_VERIFY_V2</p>
        </div>
        <div className="flex gap-4">
           <div className="flex items-center gap-2 px-4 py-2 border border-[#111] bg-[#050505] rounded-sm">
              <div className="w-2 h-2 rounded-full bg-[#00FF9C]" />
              <span className="text-[9px] font-bold text-[#666] uppercase">All_Systems_Nominal</span>
           </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-6">
           <div className="bg-[#0A0A0A] border border-[#222] p-8 rounded-sm">
              <h3 className="text-xs font-bold uppercase tracking-widest text-[#666] mb-8 border-b border-[#111] pb-4 flex items-center gap-3">
                 <ShieldCheckIcon size={14} className="text-emerald-500" />
                 Sign-off Matrix (PH1 Pilots)
              </h3>
              
              <div className="overflow-x-auto">
                 <table className="w-full text-left">
                    <thead>
                       <tr className="text-[8px] font-mono text-[#333] uppercase border-b border-[#111]">
                          <th className="py-4 font-normal">Section</th>
                          <th className="py-4 font-normal">Verification Task</th>
                          <th className="py-4 font-normal text-center">Outcome</th>
                          <th className="py-4 font-normal text-right">Evidence_Link</th>
                       </tr>
                    </thead>
                    <tbody className="divide-y divide-[#111]">
                       {testCases.map((tc, i) => (
                         <tr key={i} className="group hover:bg-[#080808]">
                            <td className="py-5">
                               <span className="text-[9px] text-[#444] font-mono bg-[#111] px-2 py-0.5 rounded-sm">{tc.section}</span>
                            </td>
                            <td className="py-5">
                               <p className="text-[10px] font-bold text-[#888]">{tc.title}</p>
                               <p className="text-[8px] text-[#333] font-mono mt-1 uppercase italic">{tc.id}</p>
                            </td>
                            <td className="py-5 text-center">
                               <span className="text-[9px] font-bold text-[#00FF9C] bg-[#00FF9C]/5 border border-[#00FF9C]/20 px-3 py-1 rounded-sm">
                                  {tc.status}
                               </span>
                            </td>
                            <td className="py-5 text-right">
                               <p className="text-[9px] text-[#222] font-mono group-hover:text-[#444] transition-colors">{tc.evidence}</p>
                            </td>
                         </tr>
                       ))}
                    </tbody>
                 </table>
              </div>
           </div>

           <div className="bg-[#0A0A0A] border border-[#222] p-8 rounded-sm">
              <div className="flex justify-between items-center mb-10 border-b border-[#111] pb-4">
                 <h3 className="text-xs font-bold uppercase tracking-widest text-[#666] flex items-center gap-3">
                    <Database size={14} className="text-indigo-400" />
                    Immutable Audit Trail
                 </h3>
                 <div className="flex gap-4">
                    <button className="text-[9px] font-bold text-[#333] hover:text-[#E0E0E0] uppercase tracking-widest flex items-center gap-2">
                       <ListFilter size={12} />
                       Filter_Logs
                    </button>
                    <button className="text-[9px] font-bold text-[#333] hover:text-[#E0E0E0] uppercase tracking-widest flex items-center gap-2">
                       <Search size={12} />
                       Trace_ID
                    </button>
                 </div>
              </div>

              <div className="space-y-4">
                 {[
                   { event: 'ORDER_PARSED', id: 'ord_9901X', actor: 'GEMINI_1.5_FLASH', time: '12:04:22', hash: '8a3b...c91e' },
                   { event: 'HITL_CORRECTION', id: 'ord_9842A', actor: 'SITI_ADMIN', time: '11:58:10', hash: '3e2d...f001' },
                   { event: 'INVOICE_SIG', id: 'inv_45001', actor: 'DUITNOW_ENGINE', time: '11:45:01', hash: '99a1...bb2c' }
                 ].map((log, i) => (
                   <div key={i} className="flex justify-between items-center p-6 bg-[#080808] border border-[#111] group hover:border-[#222] transition-colors">
                      <div className="flex items-center gap-6">
                         <div className="w-1.5 h-6 bg-[#111] group-hover:bg-[#00FF9C] transition-colors" />
                         <div>
                            <p className="text-[10px] font-bold text-[#E0E0E0] tracking-wide">{log.event}</p>
                            <p className="text-[9px] text-[#444] mt-1 font-mono uppercase italic">{log.actor} • {log.time}</p>
                         </div>
                      </div>
                      <div className="text-right">
                         <p className="text-[9px] text-[#666] font-mono uppercase">Ref: {log.id}</p>
                         <p className="text-[8px] text-[#222] mt-1 font-mono uppercase">Hash_V: {log.hash}</p>
                      </div>
                   </div>
                 ))}
              </div>
           </div>
        </div>

        <div className="space-y-8">
           <div className="bg-[#0A0A0A] border border-[#222] p-8 rounded-sm">
              <h3 className="text-xs font-bold uppercase tracking-widest text-[#666] mb-8">Verification Status</h3>
              <div className="space-y-10">
                 <div className="flex justify-between items-center bg-[#080808] border border-[#111] p-5 rounded-sm">
                    <div>
                       <p className="text-[8px] font-bold text-[#333] uppercase mb-1">Pass rate</p>
                       <p className="text-2xl font-light text-[#E0E0E0] font-mono tracking-tighter">100%</p>
                    </div>
                    <FileCheck size={24} className="text-[#00FF9C] opacity-20" />
                 </div>

                 <div className="space-y-6">
                    <p className="text-[9px] font-bold text-[#444] uppercase tracking-widest border-b border-[#111] pb-2">Artifact Retention</p>
                    <div className="space-y-4">
                       <div className="flex justify-between items-center font-mono text-[10px]">
                          <span className="text-[#333]">Raw JSON</span>
                          <span className="text-[#666]">12 MONTHS</span>
                       </div>
                       <div className="flex justify-between items-center font-mono text-[10px]">
                          <span className="text-[#333]">WhatsApp Payload</span>
                          <span className="text-[#666]">ANONYMIZED</span>
                       </div>
                       <div className="flex justify-between items-center font-mono text-[10px]">
                          <span className="text-[#333]">Admin Logs</span>
                          <span className="text-[#666]">IMMUTABLE</span>
                       </div>
                    </div>
                 </div>

                 <button className="w-full py-4 bg-[#111] text-[#666] text-[10px] font-bold uppercase tracking-widest border border-[#222] hover:text-[#E0E0E0] hover:bg-[#222] transition-all">
                    Sign_Binary_Bundle
                 </button>
              </div>
           </div>

           <div className="p-6 bg-[#00FF9C]/5 border border-[#00FF9C]/10 rounded-sm">
              <h4 className="text-[9px] font-bold text-[#00FF9C] uppercase tracking-[0.2em] mb-4">Export for Tax Compliance</h4>
              <p className="text-[10px] text-[#00FF9C]/60 font-mono leading-relaxed italic mb-6">
                 Generates encrypted package containing structured orders, invoices, and hashed audit trails required for regional SME digital grant verification.
              </p>
              <button className="w-full py-3 bg-[#00FF9C]/10 text-[#00FF9C] text-[9px] font-bold uppercase tracking-widest border border-[#00FF9C]/20 hover:bg-[#00FF9C]/20 transition-all">
                 Generate_Tax_Bundle
              </button>
           </div>
        </div>
      </div>
    </motion.div>
  );
}
