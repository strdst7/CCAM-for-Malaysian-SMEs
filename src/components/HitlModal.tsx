import { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { X, Save, AlertCircle } from 'lucide-react';
import { Order } from '../types';

interface HitlModalProps {
  order: Order;
  onClose: () => void;
  onSave: (id: string, updates: any) => void;
}

export default function HitlModal({ order, onClose, onSave }: HitlModalProps) {
  const [editedOrder, setEditedOrder] = useState({...order});

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-6 bg-black/90 backdrop-blur-sm">
      <motion.div
        initial={{ opacity: 0, scale: 0.9, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        className="w-full max-w-2xl bg-[#0A0A0A] border border-[#222] shadow-[0_0_50px_rgba(0,0,0,0.5)] overflow-hidden"
      >
        <div className="p-6 border-b border-[#222] flex justify-between items-center bg-[#0C0C0C]">
          <div className="flex items-center gap-4">
             <div className="w-10 h-10 rounded-full border border-yellow-500/20 bg-yellow-500/5 flex items-center justify-center">
                <AlertCircle size={20} className="text-yellow-500" />
             </div>
             <div>
                <h2 className="text-xs font-bold uppercase tracking-widest text-[#E0E0E0]">Human-In-The-Loop Correction</h2>
                <p className="text-[10px] text-[#444] font-mono mt-1 uppercase">Order_ID: {order.id?.slice(-8).toUpperCase()} • Confidence: {(order.confidence * 100).toFixed(1)}%</p>
             </div>
          </div>
          <button onClick={onClose} className="p-2 text-[#444] hover:text-[#E0E0E0] transition-colors">
            <X size={20} />
          </button>
        </div>

        <div className="p-8 space-y-8 max-h-[70vh] overflow-y-auto scrollbar-thin">
           <div className="grid grid-cols-2 gap-8">
              <div className="space-y-4">
                 <label className="text-[9px] font-bold text-[#444] uppercase tracking-widest block">Customer Name</label>
                 <input 
                    className="w-full bg-[#050505] border border-[#222] py-2.5 px-4 text-xs font-bold text-[#E0E0E0] outline-none focus:border-[#00FF9C]"
                    value={editedOrder.customer_name}
                    onChange={(e) => setEditedOrder({...editedOrder, customer_name: e.target.value})}
                 />
              </div>
              <div className="space-y-4">
                 <label className="text-[9px] font-bold text-[#444] uppercase tracking-widest block">Customer Phone</label>
                 <input 
                    className="w-full bg-[#050505] border border-[#222] py-2.5 px-4 text-xs font-mono text-[#444] outline-none"
                    value={editedOrder.customer_phone}
                    onChange={(e) => setEditedOrder({...editedOrder, customer_phone: e.target.value})}
                 />
              </div>
           </div>

           <div className="p-6 bg-[#050505] border border-[#111]">
              <label className="text-[9px] font-bold text-[#444] uppercase tracking-widest block mb-4 border-b border-[#111] pb-2">Extracted Items (Editable Intent)</label>
              <div className="space-y-3">
                 {editedOrder.items.map((item, idx) => (
                   <div key={idx} className="flex gap-4 items-center">
                      <input 
                        type="number"
                        className="w-16 bg-[#111] border border-[#222] py-2 px-3 text-xs text-center text-[#00FF9C] outline-none focus:border-[#00FF9C]"
                        value={item.qty}
                        onChange={(e) => {
                           const newItems = [...editedOrder.items];
                           newItems[idx].qty = parseInt(e.target.value) || 0;
                           setEditedOrder({...editedOrder, items: newItems});
                        }}
                      />
                      <input 
                        className="flex-1 bg-[#111] border border-[#222] py-2 px-3 text-xs text-[#E0E0E0] outline-none focus:border-[#00FF9C]"
                        value={item.name}
                        onChange={(e) => {
                           const newItems = [...editedOrder.items];
                           newItems[idx].name = e.target.value;
                           setEditedOrder({...editedOrder, items: newItems});
                        }}
                      />
                   </div>
                 ))}
              </div>
           </div>

           <div className="space-y-4">
              <label className="text-[9px] font-bold text-[#444] uppercase tracking-widest block">Delivery Address (Spatial Extract)</label>
              <textarea 
                 className="w-full bg-[#050505] border border-[#222] py-3 px-4 text-xs italic text-[#666] outline-none focus:border-[#00FF9C] min-h-[80px]"
                 value={editedOrder.delivery_address}
                 onChange={(e) => setEditedOrder({...editedOrder, delivery_address: e.target.value})}
              />
           </div>

           <div className="p-5 border border-yellow-500/10 bg-yellow-500/5 space-y-3">
              <p className="text-[9px] font-bold text-yellow-500 uppercase tracking-widest">Raw Input Audit</p>
              <p className="text-[10px] text-yellow-500/60 leading-relaxed font-mono">"{order.raw_message}"</p>
           </div>
        </div>

        <div className="p-6 border-t border-[#222] flex gap-4 bg-[#0C0C0C]">
           <button 
              onClick={onClose}
              className="px-6 py-3 border border-[#222] text-[#444] text-[10px] font-bold uppercase tracking-widest hover:text-[#E0E0E0] hover:border-[#444] transition-all"
           >
              Discard Changes
           </button>
           <button 
              onClick={() => setEditedOrder({...editedOrder, status: 'cancelled'})}
              className="px-6 py-3 border border-red-500/20 text-red-500/60 text-[10px] font-bold uppercase tracking-widest hover:bg-red-500/5 transition-all"
           >
              Reject Order
           </button>
           <button 
              onClick={() => onSave(order.id!, editedOrder)}
              className="flex-1 bg-[#00FF9C] text-black py-3 px-6 text-[10px] font-bold uppercase tracking-widest hover:bg-[#00D784] transition-all flex items-center justify-center gap-3"
           >
              <Save size={14} />
              VERIFY_&_ACK_ORDER
           </button>
        </div>
      </motion.div>
    </div>
  );
}
