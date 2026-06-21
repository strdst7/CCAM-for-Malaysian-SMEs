import { useState } from 'react';
import { motion } from 'motion/react';
import { Settings, Shield, Globe, Zap, Database, RefreshCw, CheckCircle2, UserPlus } from 'lucide-react';
import { cn } from '../utils';
import { db } from '../lib/firebase-client';
import { collection, addDoc, serverTimestamp } from 'firebase/firestore';
import OnboardingWizard from './OnboardingWizard';

export default function SettingsView() {
  const [showWizard, setShowWizard] = useState(false);
  const [seeding, setSeeding] = useState(false);
  const [seedResult, setSeedResult] = useState<'idle' | 'success' | 'error'>('idle');

  const initializeSampleData = async () => {
    setSeeding(true);
    setSeedResult('idle');
    try {
      const orders = [
        {
          customer_name: "Siti Nurhaliza",
          customer_phone: "+60123456789",
          items: [{ name: "Nasi Lemak Ayam", qty: 2 }, { name: "Teh Tarik", qty: 2 }],
          delivery_address: "Jalan Ampang 12, KL",
          status: "confirmed",
          confidence: 0.98,
          raw_message: "Hi, I want 2 nasi lemak ayam and 2 teh tarik to Jalan Ampang 12. Thanks Siti.",
          payment_status: 'pending',
          created_at: serverTimestamp(),
          updated_at: serverTimestamp()
        },
        {
          customer_name: "Ah Keong",
          customer_phone: "+60198765432",
          items: [{ name: "Char Kway Teow", qty: 1 }],
          delivery_address: "Petaling Jaya Sec 14",
          status: "new",
          confidence: 0.72,
          raw_message: "Char kway teow 1, send to PJ sec 14. How much?",
          payment_status: 'pending',
          created_at: serverTimestamp(),
          updated_at: serverTimestamp()
        }
      ];

      const flows = [
        {
          name: "Standard F&B Takeaway",
          definition: "trigger: message_received\nactions:\n  - type: parser\n    engine: gemini_flash_low_latency\n    confidence_threshold: 0.85\n  - type: logic\n    condition: stock_available\n    true:\n      - create_invoice\n      - send_whatsapp_ack",
          created_at: serverTimestamp()
        }
      ];

      for (const order of orders) {
        await addDoc(collection(db, "orders"), order);
      }
      for (const flow of flows) {
        await addDoc(collection(db, "flows"), flow);
      }
      
      setSeedResult('success');
    } catch (error) {
      console.error('Seed Error:', error);
      setSeedResult('error');
    } finally {
      setSeeding(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="max-w-4xl space-y-8 pb-20"
    >
      <div className="bg-[#0A0A0A] border border-[#222] p-8 rounded-sm">
        <div className="flex justify-between items-center mb-8">
          <h3 className="text-xs font-bold uppercase tracking-widest text-[#666] flex items-center gap-3">
            <UserPlus size={14} className="text-emerald-400" />
            Provisioning & Onboarding
          </h3>
          <button 
            onClick={() => setShowWizard(!showWizard)}
            className="text-[9px] font-bold text-[#444] uppercase tracking-widest border border-[#222] px-3 py-1 hover:bg-[#111] hover:text-[#E0E0E0] transition-colors"
          >
            {showWizard ? 'Hide_Wizard' : 'Launch_Onboarding_Flow'}
          </button>
        </div>
        
        {showWizard ? (
          <OnboardingWizard />
        ) : (
          <div className="p-6 bg-[#050505] border border-[#111] border-dashed rounded-sm text-center">
            <p className="text-[10px] text-[#333] uppercase font-mono mb-4">No active onboarding sequence. New merchant registration required?</p>
            <button 
              onClick={() => setShowWizard(true)}
              className="text-[9px] font-bold text-emerald-500 hover:text-emerald-400 uppercase tracking-[0.2em] transition-colors"
            >
              [ Initialize_Sequence ]
            </button>
          </div>
        )}
      </div>

      <div className="bg-[#0A0A0A] border border-[#222] p-8 rounded-sm">
        <h3 className="text-xs font-bold uppercase tracking-widest text-[#666] mb-8 flex items-center gap-3">
          <Database size={14} className="text-indigo-400" />
          Data Initialization
        </h3>
        <div className="p-6 bg-[#050505] border border-[#111] rounded-sm space-y-4">
           <p className="text-[10px] text-[#444] leading-relaxed uppercase font-mono tracking-wider">
              System detected empty collections. Populate Malaysian F&B pilot set for verification?
           </p>
           <button 
             onClick={initializeSampleData}
             disabled={seeding}
             className={cn(
               "flex items-center gap-3 px-6 py-3 text-[10px] font-bold uppercase tracking-widest transition-all",
               seedResult === 'success' ? "bg-[#00FF9C]/10 text-[#00FF9C] border border-[#00FF9C]/20" : 
               "bg-white text-black hover:bg-[#00FF9C]"
             )}
           >
              {seeding ? <RefreshCw size={14} className="animate-spin" /> : 
               seedResult === 'success' ? <CheckCircle2 size={14} /> : <Database size={14} />}
              {seeding ? 'Initializing_Buffer...' : 
               seedResult === 'success' ? 'Database_Initialized' : 'Populate_Pilot_Dataset'}
           </button>
           {seedResult === 'error' && (
             <p className="text-[9px] text-red-500 font-mono italic">PERMISSION_DENIED: Verification node failed. Check environment variables.</p>
           )}
        </div>
      </div>
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
             <div className="space-y-2">
                <label className="text-[9px] font-bold text-[#444] uppercase tracking-[0.2em] block">Malaysian Data Registry</label>
                <div className="px-4 py-3 bg-[#050505] border border-[#222] text-[10px] font-mono text-[#00FF9C]">
                   REGION: asia-southeast1 (KL)
                </div>
             </div>
             <div className="space-y-2">
                <label className="text-[9px] font-bold text-[#444] uppercase tracking-[0.2em] block">Node Status</label>
                <div className="px-4 py-3 bg-[#050505] border border-[#222] text-[10px] font-mono text-[#00FF9C] flex items-center gap-2">
                   <div className="w-1.5 h-1.5 rounded-full bg-[#00FF9C] shadow-[0_0_8px_#00FF9C]" />
                   HEALTHY_&_SHIELDED
                </div>
             </div>
          </div>
          <div>
            <label className="text-[9px] font-bold text-[#444] uppercase tracking-[0.2em] block mb-2">Webhook Ingress Point</label>
            <div className="flex gap-2">
              <input 
                type="text" 
                readOnly 
                value="https://ccam-mesh.malaysia.ais/v1/webhook"
                className="flex-1 bg-[#050505] border border-[#222] py-2 px-3 rounded-none text-[10px] font-mono text-[#444] outline-none"
              />
              <button className="px-4 py-2 bg-[#111] border border-[#333] text-[#666] text-[10px] font-bold uppercase hover:text-[#E0E0E0] transition-colors">Copy</button>
            </div>
          </div>
        </div>

      <div className="bg-[#0A0A0A] border border-[#222] p-8 rounded-sm">
        <h3 className="text-xs font-bold uppercase tracking-widest text-[#666] mb-8 flex items-center gap-3">
          <Shield size={14} />
          Security Matrix
        </h3>
        <div className="space-y-6">
          <div className="flex items-center justify-between p-4 bg-[#080808] border border-[#111]">
             <div>
                <p className="text-[10px] font-bold text-[#E0E0E0] uppercase tracking-wider">PII Encryption (AES-256)</p>
                <p className="text-[9px] text-[#444] mt-1 italic">Automatically scrubbing phone numbers and addresses unless HITL-verified.</p>
             </div>
             <div className="w-10 h-10 rounded border border-[#222] flex items-center justify-center">
                <Zap size={14} className="text-[#00FF9C]" />
             </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
             <button className="py-3 px-4 bg-[#050505] border border-[#222] text-[9px] font-bold text-[#444] uppercase tracking-[0.2em] hover:border-[#00FF9C] hover:text-[#00FF9C] transition-all">Rotate API Keys</button>
             <button className="py-3 px-4 bg-[#050505] border border-[#222] text-[9px] font-bold text-[#444] uppercase tracking-[0.2em] hover:border-[#00FF9C] hover:text-[#00FF9C] transition-all">Audit Security Logs</button>
          </div>
        </div>
      </div>

      <div className="p-6 bg-red-500/5 border border-red-500/10 rounded-sm">
         <h4 className="text-[10px] font-bold text-red-500 uppercase tracking-widest mb-4">Danger Zone</h4>
         <button className="text-[10px] font-bold text-red-500/60 hover:text-red-500 underline uppercase tracking-tighter transition-colors">Purge All Operational Twin Data</button>
      </div>
    </motion.div>
  );
}
