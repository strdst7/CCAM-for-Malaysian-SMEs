import React from 'react';
import { motion } from 'motion/react';
import { FileBarChart, Download, TrendingUp, Users, Clock, Percent } from 'lucide-react';
import { cn } from '../utils';

export default function ReportsView() {
  const reports = [
    { 
      id: 'REP-001', 
      type: 'WEEKLY_KPI_SNAPSHOT', 
      date: '2026.06.19', 
      status: 'FINALIZED',
      metrics: {
        accuracy: '94.2%',
        volume: '1,240',
        conversion: '88.5%',
        time_saved: '56%'
      }
    },
    { 
      id: 'ROI-FINAL', 
      type: 'FINAL_ROI_REPORT', 
      date: '2026.06.12', 
      status: 'ARCHIVED',
      metrics: {
        accuracy: '93.8%',
        volume: '4,890',
        conversion: '86.2%',
        time_saved: '52%'
      }
    }
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-8 pb-20"
    >
      <div className="flex justify-between items-end">
        <div>
          <h2 className="text-xl font-bold text-[#E0E0E0] tracking-tight">Pilot Intelligence & ROI</h2>
          <p className="text-[10px] text-[#444] font-mono mt-1 uppercase tracking-widest">Repository_Node: /reports/pilot_2026_q2</p>
        </div>
        <div className="flex gap-2">
           <button className="px-4 py-2 bg-[#00FF9C] text-[#050505] text-[10px] font-bold uppercase tracking-widest rounded-sm flex items-center gap-2 hover:bg-[#00D180] transition-colors">
              <Download size={14} />
              Export_Full_Dataset
           </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[
          { label: 'Admin Time Saved', value: '54.2%', sub: 'Target: 50%', trend: '+4.2%', icon: Clock },
          { label: 'Error Reduction', value: '68.5%', sub: 'Target: 60%', trend: '+8.5%', icon: Percent },
          { label: 'Payment Conv', value: '22.8%', sub: 'Target: 20%', trend: '+2.8%', icon: TrendingUp },
          { label: 'SME Pilot NPS', value: '8.4', sub: 'Target: 8.0', trend: '+0.4', icon: Users }
        ].map((kpi, i) => (
          <div key={i} className="bg-[#0A0A0A] border border-[#111] p-6 rounded-sm relative overflow-hidden group">
            <div className="absolute top-0 right-0 p-6 opacity-[0.03] group-hover:opacity-[0.07] transition-opacity">
              <kpi.icon size={48} className="text-white" />
            </div>
            <div className="text-[9px] font-bold text-[#444] uppercase tracking-widest mb-4">{kpi.label}</div>
            <div className="text-3xl font-bold text-[#E0E0E0] font-mono leading-none">{kpi.value}</div>
            <div className="mt-4 flex justify-between items-center text-[10px] font-mono">
               <span className="text-[#333]">{kpi.sub}</span>
               <span className="text-[#00FF9C] font-bold">{kpi.trend}</span>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-6">
           <div className="bg-[#0A0A0A] border border-[#222] p-8 rounded-sm">
              <div className="flex justify-between items-center mb-8 border-b border-[#111] pb-4">
                 <h3 className="text-xs font-bold uppercase tracking-widest text-[#666] flex items-center gap-3">
                    <FileBarChart size={14} className="text-indigo-500" />
                    Generated Reports Artifacts
                 </h3>
                 <span className="text-[8px] font-mono text-[#333]">Total: {reports.length}</span>
              </div>

              <div className="space-y-4">
                 {reports.map((report) => (
                   <div key={report.id} className="flex flex-col md:flex-row md:items-center justify-between p-6 bg-[#080808] border border-[#111] group hover:border-[#333] transition-colors gap-6">
                      <div className="flex items-center gap-6">
                         <div className="w-10 h-10 bg-[#111] border border-[#222] rounded-sm flex items-center justify-center">
                            <FileBarChart size={16} className="text-[#444] group-hover:text-indigo-400" />
                         </div>
                         <div>
                            <div className="flex items-center gap-3">
                               <p className="text-[10px] font-bold text-[#E0E0E0] tracking-wide">{report.type}</p>
                               <span className="text-[8px] px-2 py-0.5 border border-[#222] rounded-full text-[#444]">{report.id}</span>
                            </div>
                            <p className="text-[9px] text-[#444] mt-1 font-mono uppercase italic">{report.date} • {report.status}</p>
                         </div>
                      </div>

                      <div className="grid grid-cols-4 gap-4 px-6 border-x border-[#111]">
                         {Object.entries(report.metrics).map(([key, val]) => (
                           <div key={key} className="text-center">
                              <p className="text-[7px] text-[#333] uppercase font-bold mb-1">{key.replace('_', ' ')}</p>
                              <p className="text-[10px] font-mono text-[#888]">{val}</p>
                           </div>
                         ))}
                      </div>

                      <button className="flex-none p-4 hover:bg-[#111] transition-colors rounded-sm group/btn">
                         <Download size={14} className="text-[#333] group-hover/btn:text-[#00FF9C]" />
                      </button>
                   </div>
                 ))}
              </div>
           </div>
        </div>

        <div className="space-y-8">
           <div className="bg-[#0A0A0A] border border-[#222] p-8 rounded-sm">
              <h3 className="text-xs font-bold uppercase tracking-widest text-[#666] mb-8">Baseline Analysis</h3>
              <div className="space-y-6">
                 <div className="p-4 bg-[#080808] border border-[#111] rounded-sm">
                    <p className="text-[9px] text-[#444] uppercase font-bold mb-3 tracking-widest">Manual Process Baseline</p>
                    <div className="space-y-4">
                       <div className="flex justify-between items-center">
                          <span className="text-[10px] text-[#666]">Avg Error Rate</span>
                          <span className="text-[11px] font-mono font-bold text-red-500/80">32.4%</span>
                       </div>
                       <div className="flex justify-between items-center">
                          <span className="text-[10px] text-[#666]">Staff Time / Order</span>
                          <span className="text-[11px] font-mono font-bold text-red-500/80">8.5 min</span>
                       </div>
                       <div className="flex justify-between items-center">
                          <span className="text-[10px] text-[#666]">Payment Delay</span>
                          <span className="text-[11px] font-mono font-bold text-red-500/80">2.4 days</span>
                       </div>
                    </div>
                 </div>
                 
                 <div className="text-[9px] text-[#333] italic leading-relaxed text-center px-4">
                    Comparison calculated against CCAM PH1 pilot metrics (June 2026). Baseline captured from 200 manual transactions.
                 </div>

                 <button className="w-full py-4 bg-[#111] text-[#666] text-[10px] font-bold uppercase tracking-widest border border-[#222] hover:text-[#E0E0E0] hover:bg-[#151515] transition-all">
                    Rerun_Baseline_Diff
                 </button>
              </div>
           </div>
        </div>
      </div>
    </motion.div>
  );
}
