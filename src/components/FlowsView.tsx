import { useState, useEffect } from 'react';
import { motion } from 'motion/react';
import { Play, Rocket, Settings, Code, Activity, Trash2 } from 'lucide-react';
import { cn } from '../utils';
import { FlowDefinition } from '../types';

export default function FlowsView() {
  const [flows, setFlows] = useState<FlowDefinition[]>([]);
  const [newFlow, setNewFlow] = useState({ 
    name: '', 
    definition: `# CCAM Microflow DSL v1.0
flow:
  - trigger: message_received
  - action: parse_message
  - condition: confidence >= 0.85
    then:
      - action: send_ack
      - action: create_invoice
      - action: notify_kitchen
    else:
      - action: route_to_correction` 
  });
  const [loading, setLoading] = useState(true);

  const fetchFlows = async () => {
    try {
      const res = await fetch('/api/flows');
      const data = await res.json();
      if (Array.isArray(data)) setFlows(data);
      setLoading(false);
    } catch (e) {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFlows();
  }, []);

  const saveFlow = async () => {
    if (!newFlow.name) return;
    try {
      await fetch('/api/flows', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...newFlow, is_active: true })
      });
      fetchFlows();
      setNewFlow({ ...newFlow, name: '' });
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 pb-20">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="lg:col-span-2 space-y-6"
      >
        <div className="bg-[#0A0A0A] border border-[#222] p-8 rounded-sm flex flex-col h-[650px]">
          <div className="flex justify-between items-center mb-6">
            <div>
              <h3 className="text-xs font-bold uppercase tracking-widest text-[#666]">Workflow Studio</h3>
              <p className="text-[10px] text-[#333] mt-1 italic">Microflow DSL Designer - Malaysian Node Cluster 01</p>
            </div>
            <div className="flex gap-3">
               <button className="p-2 border border-[#222] text-[#444] hover:text-[#E0E0E0] transition-colors"><Code size={14}/></button>
               <button className="p-2 border border-[#222] text-[#444] hover:text-[#E0E0E0] transition-colors"><Activity size={14}/></button>
            </div>
          </div>
          
          <div className="space-y-4 flex-1 flex flex-col">
            <div className="space-y-2">
              <label className="text-[9px] font-bold text-[#444] uppercase tracking-widest">Flow Name</label>
              <input 
                className="w-full bg-[#050505] border border-[#222] py-3 px-4 text-xs outline-none text-[#E0E0E0] focus:border-[#00FF9C] transition-colors"
                value={newFlow.name}
                onChange={e => setNewFlow({...newFlow, name: e.target.value})}
                placeholder="e.g. F&B Takeaway Flow (Friday Rush)"
              />
            </div>
            <div className="space-y-2 flex-1 flex flex-col relative overflow-hidden">
              <label className="text-[9px] font-bold text-[#444] uppercase tracking-widest flex items-center justify-between">
                YAML_DEFINITION
                <span className="text-[8px] text-[#00FF9C]/40 font-mono tracking-tighter">Schema_v1.0.3_Valid</span>
              </label>
              <textarea 
                className="flex-1 w-full bg-[#050505] border border-[#222] py-4 px-5 text-[11px] font-mono text-[#00FF9C] outline-none focus:border-[#00FF9C] transition-colors resize-none scrollbar-thin"
                value={newFlow.definition}
                onChange={e => setNewFlow({...newFlow, definition: e.target.value})}
              />
              <div className="absolute bottom-4 right-4 flex gap-2">
                 <div className="px-2 py-1 bg-black/60 border border-[#222] rounded-sm text-[8px] font-mono text-[#444]">L: 14</div>
                 <div className="px-2 py-1 bg-black/60 border border-[#222] rounded-sm text-[8px] font-mono text-[#444]">UTF-8</div>
              </div>
            </div>
            <button 
              onClick={saveFlow}
              className="w-full py-4 bg-[#00FF9C] text-black text-[10px] font-bold uppercase tracking-widest hover:bg-[#00D784] transition-all flex items-center justify-center gap-3 group"
            >
              <Rocket size={14} className="group-hover:translate-x-1 group-hover:-translate-y-1 transition-transform" />
              DEPLOY_FLOW_TO_EDGE_REPLICAS
            </button>
          </div>
        </div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, x: 10 }}
        animate={{ opacity: 1, x: 0 }}
        className="lg:col-span-1 space-y-6"
      >
        <div className="bg-[#0A0A0A] border border-[#222] p-8 rounded-sm">
          <h3 className="text-xs font-bold uppercase tracking-widest text-[#666] mb-8">Node Ingress Mesh</h3>
          <div className="space-y-6">
            <div>
              <label className="text-[9px] font-bold text-[#444] uppercase tracking-[0.2em] block mb-2">Edge Callback URL</label>
              <div className="flex gap-2">
                <input 
                  type="text" 
                  readOnly 
                  value="https://ccam-mesh.malaysia.ais/edge/v1/trigger"
                  className="flex-1 bg-[#050505] border border-[#222] py-2 px-3 rounded-none text-[10px] font-mono text-[#666] outline-none"
                />
              </div>
            </div>
            <div className="p-4 bg-[#111] border border-[#222] rounded-sm">
               <div className="flex items-center justify-between mb-2">
                  <span className="text-[10px] font-bold text-[#E0E0E0] uppercase tracking-wide">MALAY_MOCK_INGRESS</span>
                  <div className="w-1.5 h-1.5 rounded-full bg-[#00FF9C] animate-pulse"></div>
               </div>
               <p className="text-[9px] text-[#444] italic leading-relaxed">External webhook simulation node listening for WhatsApp Business API HMAC signatures.</p>
            </div>
          </div>
        </div>

        <div className="bg-[#0A0A0A] border border-[#222] p-8 rounded-sm">
           <h3 className="text-xs font-bold uppercase tracking-widest text-[#666] mb-8">Active Deployment Registry</h3>
           <div className="space-y-3">
              {loading ? (
                <div className="animate-pulse space-y-3">
                  {[1, 2].map(i => <div key={i} className="h-12 bg-[#111] border border-[#222]" />)}
                </div>
              ) : flows.length === 0 ? (
                <div className="py-10 text-center border border-dashed border-[#111]">
                   <p className="text-[9px] uppercase tracking-widest text-[#333]">Registry Empty</p>
                </div>
              ) : flows.map(f => (
                <div key={f.id} className="p-4 bg-[#111] border border-[#222] flex justify-between items-center group">
                  <div>
                    <p className="text-[10px] font-bold text-[#E0E0E0] uppercase tracking-wider">{f.name}</p>
                    <p className="text-[8px] text-[#444] font-mono mt-1">ID: {f.id?.slice(-8).toUpperCase()}</p>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-[8px] px-2 py-0.5 bg-[#00FF9C]/10 text-[#00FF9C] border border-[#00FF9C]/20 rounded-full font-bold uppercase">LIVE</span>
                    <button className="text-[#333] hover:text-red-500 transition-colors opacity-0 group-hover:opacity-100"><Trash2 size={12} /></button>
                  </div>
                </div>
              ))}
           </div>
        </div>

        <div className="bg-[#00FF9C]/5 border border-[#00FF9C]/20 p-6 rounded-sm">
           <h4 className="text-[10px] font-bold text-[#00FF9C] uppercase tracking-widest mb-2 flex items-center gap-2">
              <Play size={10} />
              DSL Cheat-Sheet
           </h4>
           <div className="space-y-3 text-[9px] text-[#00FF9C]/60 font-mono italic leading-relaxed">
              <p>• trigger: [message_received, payment_ack]</p>
              <p>• action: [parse, create_invoice, send_whatsapp]</p>
              <p>• condition: [confidence_threshold, stock_level]</p>
           </div>
        </div>
      </motion.div>
    </div>
  );
}
