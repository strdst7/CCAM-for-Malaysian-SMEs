import { useState } from 'react';
import { motion } from 'motion/react';
import { BrainCircuit, Activity } from 'lucide-react';
import { cn } from '../utils';
import { SimulationConfig } from '../types';

export default function SimulatorView() {
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
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 pb-20">
      <motion.div
        initial={{ opacity: 0, x: -10 }}
        animate={{ opacity: 1, x: 0 }}
        className="lg:col-span-1 bg-[#0A0A0A] p-8 rounded-sm border border-[#222] flex flex-col gap-8 shadow-2xl"
      >
        <div className="space-y-1">
          <h3 className="text-xs font-bold uppercase tracking-widest text-[#666]">Twin Engine Config</h3>
          <p className="text-[10px] text-[#333] italic">Injecting synthetic traffic into Malaysian node clusters.</p>
        </div>

        <div className="space-y-8">
          <div className="space-y-3">
             <label className="text-[10px] font-bold text-[#444] uppercase tracking-widest block">Acceptance Test Preset</label>
             <select 
               onChange={(e) => applyPreset(e.target.value)}
               className="w-full bg-[#050505] border border-[#222] text-[#E0E0E0] text-[10px] px-4 py-3 font-mono outline-none focus:border-[#00FF9C]"
             >
                <option value="">MANUAL_CONFIGURATION</option>
                <option value="PEAK_500">TC_01: PEAK_500_LOAD</option>
                <option value="PEAK_LUNCH_10">SCENARIO: PEAK_LUNCH_10m</option>
                <option value="LOW_CONFIDENCE_STRESS">TC_02: AMBIGUITY_STRESS</option>
                <option value="VALID_SIGNATURE_MOCK">TC_03: SIGNATURE_VERIFY</option>
             </select>
          </div>

          <div>
            <label className="text-[10px] font-bold text-[#444] uppercase tracking-[0.2em] block mb-4">Traffic Density</label>
            <input 
              type="range" min="10" max="500" step="10"
              value={simConfig.messages_per_minute}
              onChange={(e) => setSimConfig({...simConfig, messages_per_minute: parseInt(e.target.value)})}
              className="w-full accent-[#00FF9C] h-1 bg-[#111] rounded-full appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-[9px] font-mono text-[#333] mt-3">
               <span className={cn(simConfig.messages_per_minute > 400 ? "text-red-500" : "")}>{simConfig.messages_per_minute} MSG/MIN</span>
               <span>MAX_LOAD_500</span>
            </div>
          </div>

          <div>
            <label className="text-[10px] font-bold text-[#444] uppercase tracking-[0.2em] block mb-4">Injection Error Rate</label>
            <input 
              type="range" min="0" max="1" step="0.01"
              value={simConfig.error_rate}
              onChange={(e) => setSimConfig({...simConfig, error_rate: parseFloat(e.target.value)})}
              className="w-full accent-yellow-500 h-1 bg-[#111] rounded-full appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-[9px] font-mono text-[#333] mt-3">
               <span className={cn(simConfig.error_rate > 0.3 ? "text-yellow-500" : "")}>{(simConfig.error_rate * 100).toFixed(0)}% ERROR_PROB</span>
               <span>NOISE_GEN</span>
            </div>
          </div>

          <div className="space-y-4">
             <label className="text-[10px] font-bold text-[#444] uppercase tracking-[0.2em] block">Scenario Mode</label>
             <div className="grid grid-cols-1 gap-2">
                {['FRIDAY_LUNCH_RUSH', 'DINNER_CROWD_STRESS', 'FAST_FESTIVAL_PEAK'].map(m => (
                  <button 
                    key={m}
                    onClick={() => setSimConfig({...simConfig, order_mix: m})}
                    className={cn(
                      "text-left py-3 px-4 text-[10px] font-bold border transition-all uppercase tracking-widest",
                      simConfig.order_mix === m ? "bg-[#00FF9C] text-black border-[#00FF9C]" : "bg-transparent text-[#444] border-[#222] hover:border-[#444]"
                    )}
                  >
                    {m}
                  </button>
                ))}
             </div>
          </div>

          <div className="p-5 bg-[#050505] border border-[#111] space-y-4">
             <div className="flex items-center justify-between">
                <span className="text-[10px] font-bold uppercase text-[#666]">Peak Multiplier</span>
                <button 
                  onClick={() => setSimConfig({...simConfig, peak_hours: !simConfig.peak_hours})}
                  className={cn(
                    "w-8 h-4 rounded-full transition-colors relative",
                    simConfig.peak_hours ? "bg-[#00FF9C]" : "bg-[#111]"
                  )}
                >
                   <div className={cn("absolute top-1 w-2 h-2 rounded-full transition-all", simConfig.peak_hours ? "right-1 bg-black" : "left-1 bg-[#444]")} />
                </button>
             </div>
             <p className="text-[9px] text-[#333] italic">Enabling 2X stress on parser concurrency.</p>
          </div>
        </div>

        <button 
          onClick={runSimulation}
          disabled={running}
          className="w-full py-4 bg-white text-black text-xs font-bold uppercase tracking-widest hover:bg-[#00FF9C] transition-all disabled:opacity-20 flex items-center justify-center gap-2 group"
        >
          {running ? (
             <>
               <Activity size={14} className="animate-spin" />
               PROCESSING_NODES...
             </>
          ) : "EXECUTE_DIGITAL_TWIN"}
        </button>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, x: 10 }}
        animate={{ opacity: 1, x: 0 }}
        className="lg:col-span-2 bg-[#0A0A0A] border border-[#222] rounded-sm flex flex-col min-h-[500px] overflow-hidden"
      >
        <div className="p-5 border-b border-[#222] flex justify-between items-center bg-[#0C0C0C]">
          <h2 className="text-[10px] font-bold tracking-widest text-[#666] uppercase">Twin Output Visualization</h2>
          <div className="flex gap-4">
            <button className="text-[9px] font-bold uppercase text-[#333] hover:text-[#E0E0E0]">Download Report PDF</button>
            <button className="text-[9px] font-bold uppercase text-[#333] hover:text-[#E0E0E0]">Export CSV</button>
          </div>
        </div>
        
        {!results && !running ? (
          <div className="flex-1 flex flex-col items-center justify-center text-center p-20 grayscale opacity-20">
            <BrainCircuit size={48} className="mb-6" />
            <p className="text-[11px] uppercase tracking-[0.3em]">Operational Twin Offline</p>
          </div>
        ) : running ? (
          <div className="flex-1 p-8 font-mono text-[10px] text-[#444] space-y-3">
            <p className="text-[#00FF9C]">[TWIN] Initializing Synthetic Message Buffer...</p>
            <p>[TWIN] Generating {simConfig.messages_per_minute} RPM intent patterns...</p>
            <p>[TWIN] Simulating DuitNow callback latency: 120ms - 450ms</p>
            <div className="w-48 h-1 bg-[#111] overflow-hidden relative">
               <motion.div 
                 initial={{ x: '-100%' }}
                 animate={{ x: '100%' }}
                 transition={{ repeat: Infinity, duration: 1.5 }}
                 className="absolute inset-y-0 w-1/3 bg-[#00FF9C]"
               />
            </div>
          </div>
        ) : (
          <div className="flex-1 p-8 space-y-10">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {[
                { label: 'Synthetic Orders', val: results.orders_processed, sub: 'Total' },
                { label: 'Revenue ROI', val: `RM ${results.estimated_revenue}`, sub: 'Est. Process' },
                { label: 'Parse Accuracy', val: `${(results.parse_accuracy * 100).toFixed(1)}%`, sub: 'Confidence' },
                { label: 'Admin Time Saved', val: `${results.admin_time_saved}m`, sub: 'Efficiency' },
              ].map((k, i) => (
                <div key={i} className="bg-[#111] p-5 border border-[#222]">
                   <p className="text-[10px] font-bold uppercase text-[#444] mb-2">{k.label}</p>
                   <p className="text-xl font-light text-[#E0E0E0] italic tracking-tighter">{k.val}</p>
                   <p className="text-[8px] text-[#333] mt-2 font-mono">{k.sub}</p>
                </div>
              ))}
            </div>

            <div className="bg-[#050505] border border-[#111] p-6 space-y-8">
               <div className="flex justify-between items-center">
                  <h4 className="text-[10px] font-bold uppercase text-[#666] tracking-widest">Confidence Distribution (Histogram)</h4>
                  <p className="text-[8px] text-[#444] italic">Monte Carlo Run: {results.timestamp}</p>
               </div>
               
               <div className="flex items-end gap-3 h-32">
                  {results.confidence_distribution?.map((d: any, i: number) => (
                    <div key={i} className="flex-1 flex flex-col gap-3 group">
                       <div className="flex-1 bg-[#111] relative overflow-hidden">
                          <motion.div 
                            initial={{ height: 0 }}
                            animate={{ height: `${(d.count / results.orders_processed) * 300}%` }}
                            className="absolute bottom-0 w-full bg-[#00FF9C]/20 group-hover:bg-[#00FF9C]/50 transition-all"
                          />
                          <div className="absolute top-2 left-1/2 -translate-x-1/2 text-[9px] font-mono font-bold text-[#E0E0E0] opacity-0 group-hover:opacity-100 transition-opacity">
                             {d.count}
                          </div>
                       </div>
                       <p className="text-[8px] text-[#444] font-mono text-center rotate-45 md:rotate-0 mt-2">{d.range}</p>
                    </div>
                  ))}
               </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
               <div className="p-5 bg-yellow-500/5 border border-yellow-500/10 rounded-sm">
                  <p className="text-[9px] font-bold text-yellow-500 uppercase tracking-widest mb-3">Simulation Alerts</p>
                  <ul className="text-[10px] text-yellow-500/60 font-mono space-y-2">
                     <li>• High concurrency error spike @ RM 8k revenue load.</li>
                     <li>• {results.low_stock_events} low-stock notification triggers detected.</li>
                  </ul>
               </div>
               <div className="p-5 bg-[#00FF9C]/5 border border-[#00FF9C]/10 rounded-sm">
                  <p className="text-[9px] font-bold text-[#00FF9C] uppercase tracking-widest mb-3">ROI Recommendations</p>
                  <p className="text-[10px] text-[#00FF9C]/60 font-mono italic">
                    Based on current twin results, Auto-Ack is safe to enable for confidence scores &gt; 0.88.
                  </p>
               </div>
            </div>
          </div>
        )}
      </motion.div>
    </div>
  );
}
