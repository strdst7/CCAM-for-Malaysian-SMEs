import { motion } from 'motion/react';
import { cn } from '../utils';

export default function DashboardView() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-8 pb-20"
    >
      <div className="bg-black/40 border border-[#222] p-8 rounded-sm mb-12">
         <p className="text-xs font-bold uppercase tracking-[0.3em] text-[#666] mb-4">Core Architecture Manifest</p>
         <p className="text-lg md:text-xl font-light italic text-[#E0E0E0] leading-relaxed max-w-4xl tracking-tight">
           CCAM is a privacy-first, Docker-native, microflow-driven automation mesh that transforms WhatsApp chaos into structured, auditable, simulatable workflows — with the absolute minimum number of moving parts.
         </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[
          { label: 'Parse Accuracy', val: '94.2%', sub: '+2.4% vs Last WK', color: 'text-[#00FF9C]' },
          { label: 'Queue Clearance', val: '12m', sub: '-4m avg response', color: 'text-[#00FF9C]' },
          { label: 'Revenue Flow', val: 'RM 14.5k', sub: 'Last 24hrs', color: 'text-white' },
          { label: 'HITL Load', val: '12.5%', sub: 'Target: <15%', color: 'text-yellow-500' }
        ].map((k, i) => (
          <div key={i} className="bg-[#0A0A0A] border border-[#222] p-6 rounded-sm shadow-sm hover:border-[#333] transition-colors relative overflow-hidden group">
            <motion.div 
               initial={{ scale: 0.8, opacity: 0 }}
               animate={{ scale: 1, opacity: 1 }}
               transition={{ delay: i * 0.1 }}
               className="absolute -top-4 -right-4 w-12 h-12 bg-white/[0.02] rounded-full group-hover:scale-150 transition-transform" 
            />
            <p className="text-[10px] font-bold text-[#444] uppercase tracking-[0.2em] mb-4">{k.label}</p>
            <p className={cn("text-3xl font-light italic tracking-tight mb-2", k.color)}>{k.val}</p>
            <p className="text-[9px] text-[#333] font-mono">{k.sub}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 bg-[#0A0A0A] border border-[#222] rounded-sm p-8">
           <div className="flex justify-between items-center mb-10 pb-4 border-b border-[#111]">
              <h3 className="text-xs font-bold uppercase tracking-widest text-[#666]">Tier 1: Operational Efficiency</h3>
              <span className="text-[10px] text-[#333] font-mono">Live_Data_Stream</span>
           </div>
           
           <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
              <div className="bg-[#050505] p-6 border border-[#111] relative">
                 <p className="text-[9px] font-bold text-[#444] uppercase tracking-widest mb-6 border-b border-[#111] pb-2">Parse Volume / Time</p>
                 <div className="flex items-end gap-1.5 h-24">
                    {[34, 45, 23, 67, 89, 45, 92, 12, 56, 32].map((v, i) => (
                      <div key={i} className="flex-1 bg-[#111] relative group">
                         <motion.div 
                            initial={{ height: 0 }}
                            animate={{ height: `${v}%` }}
                            className="absolute bottom-0 w-full bg-[#00FF9C]"
                         />
                         <div className="absolute -bottom-4 left-1/2 -translate-x-1/2 text-[8px] text-[#333] font-mono">H{i}</div>
                      </div>
                    ))}
                 </div>
              </div>

              <div className="bg-[#050505] p-6 border border-[#111] relative">
                 <p className="text-[9px] font-bold text-[#444] uppercase tracking-widest mb-6 border-b border-[#111] pb-2">Confidence Heatmap</p>
                 <div className="flex items-end gap-1.5 h-20">
                    {[12, 18, 45, 89, 92, 98, 85].map((h, i) => (
                      <div key={i} className="flex-1 bg-[#111] relative group">
                         <motion.div 
                           initial={{ height: 0 }}
                           animate={{ height: `${h}%` }}
                           className="absolute bottom-0 w-full bg-[#00FF9C]/20 group-hover:bg-[#00FF9C]/40 transition-colors"
                         />
                         <div className="absolute -bottom-4 left-1/2 -translate-x-1/2 text-[8px] text-[#333] font-mono">D{i+1}</div>
                      </div>
                    ))}
                 </div>
              </div>
           </div>
        </div>

        <div className="bg-[#0A0A0A] border border-[#222] rounded-sm p-8">
           <h3 className="text-xs font-bold uppercase tracking-widest text-[#666] mb-10 border-b border-[#111] pb-4">Tier 2: Financial ROI</h3>
           <div className="space-y-8">
              <div className="flex justify-between items-end border-b border-[#111] pb-6">
                 <div>
                    <p className="text-[9px] font-bold text-[#444] uppercase tracking-wider mb-2">Payment Conversion</p>
                    <p className="text-2xl font-light text-[#E0E0E0]">22.8%</p>
                 </div>
                 <span className="text-[9px] text-[#00FF9C] font-mono">+2.8% vs Target</span>
              </div>
              <div className="flex justify-between items-end border-b border-[#111] pb-6">
                 <div>
                    <p className="text-[9px] font-bold text-[#444] uppercase tracking-wider mb-2">Avg Days to Payment</p>
                    <p className="text-2xl font-light text-[#E0E0E0]">1.2</p>
                 </div>
                 <span className="text-[9px] text-[#00FF9C] font-mono">DuitNow Direct</span>
              </div>
              <div>
                 <p className="text-[9px] font-bold text-[#444] uppercase tracking-wider mb-2">Revenue Impact</p>
                 <p className="text-2xl font-light text-[#E0E0E0]">RM 14,500</p>
                 <p className="text-[8px] text-[#333] font-mono mt-1 uppercase">Processed_via_CCAM</p>
              </div>
           </div>
        </div>
      </div>

      <div className="bg-[#0A0A0A] border border-[#222] p-8 rounded-sm">
         <div className="flex justify-between items-center mb-8 pb-4 border-b border-[#111]">
            <h3 className="text-xs font-bold uppercase tracking-widest text-[#666]">System Efficiency Impact</h3>
            <div className="flex gap-4">
               <button className="text-[9px] font-bold uppercase text-[#444] hover:text-[#E0E0E0]">Download ROI PDF</button>
               <button className="text-[9px] font-bold uppercase text-[#444] hover:text-[#E0E0E0]">Export CSV</button>
            </div>
         </div>
         <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
            <div className="flex gap-8 items-center bg-[#050505] p-6 border border-[#111]">
               <div className="w-16 h-16 rounded-full border-2 border-[#111] border-r-[#00FF9C] flex items-center justify-center shrink-0">
                  <span className="text-lg font-light text-[#00FF9C]">64%</span>
               </div>
               <div>
                  <p className="text-[10px] font-bold text-[#E0E0E0] uppercase tracking-widest">Error Reduction</p>
                  <p className="text-[9px] text-[#666] italic mt-1">Successfully meeting Phase 1 Pilot target of {'>'}60% improvement in parse consistency.</p>
               </div>
            </div>
            <div className="flex gap-8 items-center bg-[#050505] p-6 border border-[#111]">
               <div className="w-16 h-16 rounded-full border-2 border-[#111] border-t-[#00FF9C] flex items-center justify-center shrink-0">
                  <span className="text-lg font-light text-[#00FF9C]">52%</span>
               </div>
               <div>
                  <p className="text-[10px] font-bold text-[#E0E0E0] uppercase tracking-widest">Staff Time Saved</p>
                  <p className="text-[9px] text-[#666] italic mt-1">Order entry automation saving ~4.5 minutes per transaction vs manual SME logging.</p>
               </div>
            </div>
         </div>
      </div>
    </motion.div>
  );
}
