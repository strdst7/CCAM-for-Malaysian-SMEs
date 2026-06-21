import { useState, useEffect } from 'react';
import { motion } from 'motion/react';
import { BrainCircuit, Activity } from 'lucide-react';
import { cn } from '../utils';
import { SimulationConfig } from '../types';

interface SimulatorViewProps {
  triggerRun?: number;
}

export default function SimulatorView({ triggerRun }: SimulatorViewProps) {
  const [simConfig, setSimConfig] = useState<SimulationConfig>({
    messages_per_minute: 45,
    order_mix: 'FRIDAY_LUNCH_RUSH',
    error_rate: 0.12,
    peak_hours: true
  });
  const [running, setRunning] = useState(false);
  const [results, setResults] = useState<any>(null);

  const runSimulation = async () => {
    setRunning(true);
    setResults(null);
    try {
      const res = await fetch('/api/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(simConfig)
      });
      const data = await res.json();
      setTimeout(() => {
        setResults(data.results);
        setRunning(false);
      }, 1800);
    } catch (e) {
      setRunning(false);
    }
  };

  useEffect(() => {
    if (triggerRun && triggerRun > 0 && !running) {
      runSimulation();
    }
  }, [triggerRun]);

  const applyPreset = (preset: string) => {
     switch(preset) {
        case 'PEAK_500':
           setSimConfig({ ...simConfig, messages_per_minute: 500, order_mix: 'FAST_FESTIVAL_PEAK', error_rate: 0.05 });
           break;
        case 'PEAK_LUNCH_10':
           setSimConfig({ ...simConfig, messages_per_minute: 100, order_mix: 'FRIDAY_LUNCH_RUSH', error_rate: 0.1 });
           break;
        case 'LOW_CONFIDENCE_STRESS':
           setSimConfig({ ...simConfig, messages_per_minute: 100, order_mix: 'DINNER_CROWD_STRESS', error_rate: 0.45 });
           break;
        case 'VALID_SIGNATURE_MOCK':
           setSimConfig({ ...simConfig, messages_per_minute: 20, order_mix: 'FRIDAY_LUNCH_RUSH', error_rate: 0.01 });
           break;
     }
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-8 pb-24"
    >
      <div className="bg-[#0A0A0A] border border-[#222] p-6 rounded-sm flex flex-col md:flex-row justify-between items-center gap-6">
         <div className="flex flex-col gap-1">
            <h3 className="text-[10px] font-bold text-[#666] uppercase tracking-[0.2em]">Scenario Selection</h3>
            <div className="flex gap-2 mt-2">
               {['PEAK_500', 'PEAK_LUNCH_10', 'LOW_CONFIDENCE_STRESS'].map(p => (
                 <button 
                   key={p} 
                   onClick={() => applyPreset(p)}
                   className="px-3 py-1 bg-[#111] border border-[#222] text-[8px] font-bold text-[#444] hover:text-[#E0E0E0] hover:border-[#444] uppercase tracking-widest transition-all"
                 >
                   TC: {p}
                 </button>
               ))}
            </div>
         </div>
         <div className="flex gap-4 items-center">
            <div className="text-right">
               <p className="text-[10px] font-bold text-[#E0E0E0] uppercase">{simConfig.messages_per_minute} RPM</p>
               <p className="text-[8px] text-[#444] uppercase tracking-tighter">Current Stress Load</p>
            </div>
            <button 
              onClick={runSimulation}
              disabled={running}
              className="px-8 py-3 bg-[#00FF9C] text-black text-[10px] font-bold uppercase tracking-widest hover:brightness-110 transition-all disabled:opacity-20 flex items-center gap-2"
            >
              {running ? <Activity size={12} className="animate-spin" /> : <BrainCircuit size={12} />}
              Execute_Run
            </button>
         </div>
      </div>

      <div className="flex flex-col lg:flex-row gap-8">
        <div className="flex-1 space-y-8">
           <div className="bg-[#0A0A0A] border border-[#222] p-8 rounded-sm min-h-[400px] flex flex-col">
              <div className="flex justify-between items-center mb-8 border-b border-[#111] pb-4">
                 <h3 className="text-xs font-bold uppercase tracking-widest text-[#666]">Twin Performance Summary</h3>
                 <span className="text-[9px] text-[#333] font-mono uppercase">Node: Twin_Active</span>
              </div>

              {!results && !running ? (
                <div className="flex-1 flex flex-col items-center justify-center text-[#222]">
                   <BrainCircuit size={48} className="mb-4 opacity-50" />
                   <p className="text-[10px] uppercase tracking-widest italic">Digital Twin Awaiting Execution Path</p>
                </div>
              ) : running ? (
                <div className="flex-1 space-y-4 font-mono text-[9px] text-[#444]">
                   <p className="text-[#00FF9C]">INITIALIZING_MESSAGE_BUFFER...</p>
                   <p>COLLECT_INTENT_PATTERNS_RPM_{simConfig.messages_per_minute}...</p>
                   <div className="w-full h-0.5 bg-[#111] relative overflow-hidden">
                      <motion.div 
                         initial={{ x: '-100%' }}
                         animate={{ x: '100%' }}
                         transition={{ repeat: Infinity, duration: 1 }}
                         className="absolute inset-y-0 w-1/4 bg-[#00FF9C]"
                      />
                   </div>
                </div>
              ) : (
                <div className="space-y-10">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {[
                      { label: 'Synthetic', val: results.orders_processed },
                      { label: 'ROI Est.', val: `RM ${results.estimated_revenue}` },
                      { label: 'Parse Accuracy', val: `${(results.parse_accuracy * 100).toFixed(1)}%` },
                      { label: 'Time Saved', val: `${results.admin_time_saved}m` },
                    ].map((k, i) => (
                      <div key={i} className="bg-black/40 p-4 border border-[#111]">
                         <p className="text-[8px] font-bold uppercase text-[#444] mb-2">{k.label}</p>
                         <p className="text-lg font-light text-[#E0E0E0] italic">{k.val}</p>
                      </div>
                    ))}
                  </div>

                  <div className="h-48 flex items-end gap-2">
                     {results.confidence_distribution?.map((d: any, i: number) => (
                       <div key={i} className="flex-1 bg-[#080808] border border-[#111] relative group h-full">
                          <motion.div 
                             initial={{ height: 0 }}
                             animate={{ height: `${(d.count / results.orders_processed) * 100}%` }}
                             className="absolute bottom-0 w-full bg-[#00FF9C]/10 group-hover:bg-[#00FF9C] transition-all"
                          />
                          <div className="absolute -bottom-6 left-1/2 -translate-x-1/2 text-[7px] text-[#222] rotate-45 transform origin-top-left transition-colors group-hover:text-[#666]">{d.range}</div>
                       </div>
                     ))}
                  </div>
                </div>
              )}
           </div>

           <div className="bg-[#0A0A0A] border border-[#222] p-4 rounded-sm flex justify-between items-center px-8">
              <p className="text-[9px] font-bold text-[#444] uppercase tracking-widest italic">Monte Carlo Simulation Logs Stored Successfully</p>
              <div className="flex gap-4">
                 <button className="text-[9px] font-bold uppercase text-[#333] hover:text-[#00FF9C] transition-colors">Export CSV</button>
                 <button className="text-[9px] font-bold uppercase text-[#333] hover:text-[#00FF9C] transition-colors">Download PDF</button>
              </div>
           </div>
        </div>

        <div className="w-full lg:w-80 space-y-8">
           <div className="bg-[#0A0A0A] border border-[#222] p-8 rounded-sm">
              <h3 className="text-xs font-bold uppercase tracking-widest text-[#666] mb-8 border-b border-[#111] pb-4">Error Breakdown</h3>
              <div className="space-y-6">
                 {[
                   { label: 'Intent Ambiguity', val: 64, color: 'bg-yellow-500' },
                   { label: 'Signature fail', val: 24, color: 'bg-red-500' },
                   { label: 'Network Timeout', val: 12, color: 'bg-[#111]' }
                 ].map((e, i) => (
                   <div key={i}>
                      <div className="flex justify-between text-[9px] font-bold text-[#E0E0E0] mb-2 uppercase">
                         <span>{e.label}</span>
                         <span>{e.val}%</span>
                      </div>
                      <div className="h-1 bg-[#111] rounded-full overflow-hidden">
                         <div className={cn("h-full", e.color)} style={{ width: `${e.val}%` }} />
                      </div>
                   </div>
                 ))}
              </div>
           </div>

           <div className="bg-[#0A0A0A] border border-[#222] p-8 rounded-sm">
              <h3 className="text-xs font-bold uppercase tracking-widest text-[#666] mb-6 border-b border-[#111] pb-4">KPI Deterministic Formulas</h3>
              <div className="space-y-4">
                 {[
                   { kpi: 'Parse Accuracy', formula: 'Correctly Parsed / Total Orders' },
                   { kpi: 'Error Rate', formula: '1 - Accuracy' },
                   { kpi: 'Admin Time Saved', formula: '(Base Time - Auto Time) * N' },
                   { kpi: 'Payment Conv.', formula: 'Paid Invoices / Total Invoices' },
                   { kpi: 'Revenue Impact', formula: 'N * AOV * Conversion_Lift' }
                 ].map((f, i) => (
                   <div key={i}>
                      <p className="text-[9px] font-bold text-[#E0E0E0] uppercase mb-1">{f.kpi}</p>
                      <p className="text-[9px] font-mono text-[#444] italic">{f.formula}</p>
                   </div>
                 ))}
              </div>
           </div>

           <div className="bg-[#050505] border border-dashed border-[#222] p-6 rounded-sm">
              <p className="text-[9px] font-bold text-[#444] uppercase tracking-widest mb-4">ROI Recommendation</p>
              {results ? (
                <p className="text-[10px] text-[#00FF9C]/60 font-mono italic leading-relaxed">
                  System stable under current load. Auto-ack threshold of &gt; 0.88 recommended for {simConfig.order_mix}.
                </p>
              ) : (
                <p className="text-[10px] text-[#333] font-mono italic leading-relaxed">
                  Run simulation to generate localized ROI optimization tokens.
                </p>
              )}
           </div>
        </div>
      </div>
    </motion.div>
  );
}
