import React, { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Building2, Database, Zap, CheckCircle2, ArrowRight, ArrowLeft, Loader2 } from 'lucide-react';
import { cn } from '../utils';
import { db } from '../lib/firebase-client';
import { collection, addDoc, serverTimestamp } from 'firebase/firestore';

type Step = 'IDENTITY' | 'SCHEMA' | 'FLOW' | 'FINALIZING' | 'COMPLETE';

export default function OnboardingWizard() {
  const [step, setStep] = useState<Step>('IDENTITY');
  const [formData, setFormData] = useState({
    businessName: '',
    industry: 'F&B',
    region: 'Malaysia (KL)',
    schemaTemplate: 'standard_fb',
    flowName: 'Basic WhatsApp Order Flow'
  });

  const industries = ['F&B', 'Retail', 'Service', 'Professional Services'];
  const schemas = [
    { id: 'standard_fb', name: 'F&B Base', desc: 'Pre-config with Tables: Orders, Items, Invoices.' },
    { id: 'retail_base', name: 'Retail Essentials', desc: 'Pre-config with Tables: SKUs, Inventory, Sales.' },
    { id: 'service_pro', name: 'Service Registry', desc: 'Pre-config with Tables: Appointments, Clients.' }
  ];

  const handleIdentitySubmit = () => {
    if (formData.businessName) setStep('SCHEMA');
  };

  const handleSchemaSubmit = () => {
    setStep('FLOW');
  };

  const handleFlowInit = async () => {
    setStep('FINALIZING');
    try {
      // Simulate backend provisioning
      const tenantData = {
        name: formData.businessName,
        industry: formData.industry,
        region: formData.region,
        schema: formData.schemaTemplate,
        onboarded_at: serverTimestamp(),
      };

      const flowDefinition = `name: ${formData.flowName}\ntrigger: whatsapp_message\nactions:\n  - type: parser\n    engine: gemini-1.5-flash\n  - type: notification\n    channel: kitchen_display\n  - type: store_db\n    collection: orders`;

      await addDoc(collection(db, "tenants"), tenantData);
      await addDoc(collection(db, "flows"), {
        name: formData.flowName,
        definition: flowDefinition,
        created_at: serverTimestamp(),
        is_default: true
      });

      setTimeout(() => setStep('COMPLETE'), 2000);
    } catch (error) {
      console.error('Onboarding error:', error);
      setStep('IDENTITY'); // Reset on error for now
    }
  };

  return (
    <div className="bg-[#0A0A0A] border border-[#222] rounded-sm overflow-hidden">
      <div className="p-8 border-b border-[#111] bg-[#080808]">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-xs font-bold uppercase tracking-widest text-[#666] flex items-center gap-3">
            <Building2 size={14} className="text-[#00FF9C]" />
            Tenant Onboarding Wizard
          </h3>
          <div className="flex gap-1">
            {['IDENTITY', 'SCHEMA', 'FLOW'].map((s, i) => (
              <div 
                key={i} 
                className={cn(
                  "w-8 h-1 rounded-full bg-[#111] transition-colors",
                  (step === s || (i === 0 && step !== 'IDENTITY') || (i === 1 && step === 'FLOW')) && "bg-[#00FF9C]"
                )}
              />
            ))}
          </div>
        </div>
        <p className="text-[10px] text-[#444] font-mono uppercase italic">Node Initialization Sequence v.0.1.b</p>
      </div>

      <div className="p-8 min-h-[300px] flex flex-col">
        <AnimatePresence mode="wait">
          {step === 'IDENTITY' && (
            <motion.div
              key="identity"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="space-y-6"
            >
              <div className="space-y-4">
                <div className="space-y-2">
                  <label className="text-[9px] font-bold text-[#444] uppercase tracking-wider">Legal Entity Name</label>
                  <input 
                    type="text"
                    value={formData.businessName}
                    onChange={(e) => setFormData({...formData, businessName: e.target.value})}
                    placeholder="e.g. Kedai Kopi Jaya"
                    className="w-full bg-black border border-[#222] p-3 text-[11px] text-[#E0E0E0] focus:border-[#00FF9C] outline-none transition-colors"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="text-[9px] font-bold text-[#444] uppercase tracking-wider">Industry Vertical</label>
                    <select 
                      className="w-full bg-black border border-[#222] p-3 text-[11px] text-[#E0E0E0] focus:border-[#00FF9C] outline-none"
                      value={formData.industry}
                      onChange={(e) => setFormData({...formData, industry: e.target.value})}
                    >
                      {industries.map(i => <option key={i} value={i}>{i}</option>)}
                    </select>
                  </div>
                  <div className="space-y-2">
                    <label className="text-[9px] font-bold text-[#444] uppercase tracking-wider">Hosting Region</label>
                    <div className="w-full bg-[#050505] border border-[#111] p-3 text-[10px] text-[#666] font-mono">
                      MSIA_SOUTH_1
                    </div>
                  </div>
                </div>
              </div>
              <button 
                onClick={handleIdentitySubmit}
                disabled={!formData.businessName}
                className="mt-4 flex items-center justify-center gap-3 w-full py-4 bg-white text-black text-[10px] font-bold uppercase hover:bg-[#00FF9C] disabled:opacity-50 transition-all"
              >
                Proceed to Schema Mapping <ArrowRight size={14} />
              </button>
            </motion.div>
          )}

          {step === 'SCHEMA' && (
            <motion.div
              key="schema"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="space-y-6"
            >
              <p className="text-[10px] text-[#444] italic border-l-2 border-[#111] pl-4">
                Select a structural template to initialize your relational twin. This maps incoming WhatsApp data to indexed fields.
              </p>
              <div className="grid grid-cols-1 gap-3">
                {schemas.map(s => (
                  <button
                    key={s.id}
                    onClick={() => setFormData({...formData, schemaTemplate: s.id})}
                    className={cn(
                      "p-4 border transition-all text-left",
                      formData.schemaTemplate === s.id ? "bg-[#00FF9C]/5 border-[#00FF9C]" : "bg-black border-[#222] hover:border-[#444]"
                    )}
                  >
                    <div className="flex justify-between items-center mb-1">
                      <span className="text-[10px] font-bold text-[#E0E0E0] uppercase tracking-wider">{s.name}</span>
                      {formData.schemaTemplate === s.id && <Database size={12} className="text-[#00FF9C]" />}
                    </div>
                    <p className="text-[9px] text-[#444]">{s.desc}</p>
                  </button>
                ))}
              </div>
              <div className="flex gap-4">
                <button onClick={() => setStep('IDENTITY')} className="flex-1 py-4 border border-[#222] text-[#444] text-[10px] font-bold uppercase hover:text-[#E0E0E0]">Back</button>
                <button onClick={handleSchemaSubmit} className="flex-2 py-4 bg-white text-black text-[10px] font-bold uppercase hover:bg-[#00FF9C] flex items-center justify-center gap-3">
                  Map Structure <ArrowRight size={14} />
                </button>
              </div>
            </motion.div>
          )}

          {step === 'FLOW' && (
            <motion.div
              key="flow"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="space-y-6"
            >
              <div className="p-4 bg-black border border-[#111] rounded-sm">
                <p className="text-[9px] font-bold text-[#444] uppercase mb-4 flex items-center gap-2">
                  <Zap size={10} className="text-[#00FF9C]" />
                  Default Microflow Initializer (YAML)
                </p>
                <pre className="text-[9px] font-mono text-emerald-500/80 leading-relaxed">
{`name: ${formData.flowName}
trigger: whatsapp_message
actions:
  - type: parser
    engine: gemini-1.5-flash
  - type: notification
    channel: kitchen_display
  - type: store_db
    collection: orders`}
                </pre>
              </div>
              <div className="flex gap-4">
                <button onClick={() => setStep('SCHEMA')} className="flex-1 py-4 border border-[#222] text-[#444] text-[10px] font-bold uppercase hover:text-[#E0E0E0]">Back</button>
                <button onClick={handleFlowInit} className="flex-2 py-4 bg-[#00FF9C] text-black text-[10px] font-bold uppercase flex items-center justify-center gap-3">
                  Initialize & Activate <ArrowRight size={14} />
                </button>
              </div>
            </motion.div>
          )}

          {step === 'FINALIZING' && (
            <motion.div
              key="finalizing"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex flex-col items-center justify-center h-full space-y-4 py-12"
            >
              <Loader2 className="text-[#00FF9C] animate-spin" size={32} />
              <p className="text-[10px] font-mono text-[#00FF9C] uppercase animate-pulse">Provisioning_Digital_Twin...</p>
            </motion.div>
          )}

          {step === 'COMPLETE' && (
            <motion.div
              key="complete"
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              className="flex flex-col items-center justify-center h-full space-y-6 py-12"
            >
              <div className="w-16 h-16 rounded-full bg-[#00FF9C]/10 border border-[#00FF9C]/20 flex items-center justify-center">
                <CheckCircle2 className="text-[#00FF9C]" size={32} />
              </div>
              <div className="text-center">
                <h4 className="text-lg font-bold text-[#E0E0E0] mb-2 uppercase tracking-tighter">Onboarding Complete</h4>
                <p className="text-[10px] text-[#444] font-mono">WORKSPACE_READY_FOR_TRAFFIC</p>
              </div>
              <button 
                onClick={() => setStep('IDENTITY')} 
                className="px-8 py-3 bg-white text-black text-[10px] font-bold uppercase hover:bg-[#00FF9C]"
              >
                Start New Onboarding
              </button>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
