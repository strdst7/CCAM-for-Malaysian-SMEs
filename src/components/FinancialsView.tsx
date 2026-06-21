import { useState, useEffect } from 'react';
import { motion } from 'motion/react';
import { 
  CreditCard,
  History,
  Activity,
  Search,
  CheckCircle2,
  Clock
} from 'lucide-react';
import { collection, query, orderBy, onSnapshot, limit } from 'firebase/firestore';
import { db } from '../lib/firebase-client';
import { cn } from '../utils';
import { Invoice } from '../types';

export default function FinancialsView() {
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const q = query(collection(db, 'invoices'), orderBy('created_at', 'desc'), limit(20));
    const unsubscribe = onSnapshot(q, (snapshot) => {
      setInvoices(snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() } as Invoice)));
      setLoading(false);
    }, (error) => {
      console.error(error);
      setLoading(false);
    });
    return () => unsubscribe();
  }, []);

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-8 pb-20"
    >
      <div className="flex flex-col lg:flex-row gap-8">
        <div className="flex-1 space-y-8">
          <div className="bg-[#0A0A0A] border border-[#222] p-8 rounded-sm">
             <div className="flex justify-between items-center mb-10 pb-4 border-b border-[#111]">
                <h3 className="text-xs font-bold uppercase tracking-widest text-[#666]">Payment Conversion Funnel</h3>
                <div className="flex gap-4">
                   <select className="bg-transparent text-[9px] text-[#444] border border-[#222] px-2 py-1 outline-none">
                      <option>Last 30 Days</option>
                      <option>Last 7 Days</option>
                   </select>
                </div>
             </div>
             
             <div className="space-y-4">
                {[
                  { step: 'Order Generated', count: 1240, color: 'bg-indigo-500/20' },
                  { step: 'WhatsApp Sent', count: 1120, color: 'bg-indigo-500/40' },
                  { step: 'DuitNow Link Click', count: 840, color: 'bg-[#00FF9C]/40' },
                  { step: 'Payment Settled', count: 284, color: 'bg-[#00FF9C]' }
                ].map((s, i) => (
                  <div key={i} className="group">
                     <div className="flex justify-between text-[9px] font-bold text-[#E0E0E0] mb-2 uppercase">
                        <span>{s.step}</span>
                        <span>{s.count}</span>
                     </div>
                     <div className="h-4 bg-[#111] overflow-hidden">
                        <motion.div 
                           initial={{ width: 0 }}
                           animate={{ width: `${(s.count / 1240) * 100}%` }}
                           className={cn("h-full transition-all group-hover:brightness-125", s.color)} 
                        />
                     </div>
                  </div>
                ))}
             </div>
          </div>

          <div className="bg-[#0A0A0A] border border-[#222] p-8 rounded-sm">
             <h3 className="text-xs font-bold uppercase tracking-widest text-[#666] mb-8 border-b border-[#111] pb-4 flex items-center gap-3">
                <CreditCard size={14} className="text-[#00FF9C]" />
                DuitNow Invoice Engine Internals
             </h3>
             <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
                {[
                  { step: '01', title: 'ORD_ACK', desc: 'Confirm order & lock price' },
                  { step: '02', title: 'LINK_GEN', desc: 'Dynamic DuitNow QR match' },
                  { step: '03', title: 'CALLBACK', desc: 'Secure bank notify hook' },
                  { step: '04', title: 'SETTLE', desc: 'Auto-reconciliation loop' }
                ].map((s, i) => (
                  <div key={i} className="relative">
                     <span className="text-[40px] font-bold text-[#111] absolute -top-4 -left-2 z-0 font-mono select-none">{s.step}</span>
                     <div className="relative z-10">
                        <p className="text-[10px] font-bold text-[#E0E0E0] uppercase mb-1">{s.title}</p>
                        <p className="text-[9px] text-[#444] leading-relaxed italic">{s.desc}</p>
                     </div>
                  </div>
                ))}
             </div>
          </div>

          <div className="bg-[#0A0A0A] border border-[#222] rounded-md overflow-hidden">
            <div className="p-5 border-b border-[#222] flex justify-between items-center bg-[#0C0C0C]">
              <h2 className="text-[10px] font-bold tracking-widest text-[#666] uppercase">Settlement Buffer</h2>
              <div className="flex gap-2">
                 <button className="text-[8px] font-bold text-[#444] border border-[#111] px-2 py-1 hover:border-[#444]">Filter_Paid</button>
                 <button className="text-[8px] font-bold text-[#444] border border-[#111] px-2 py-1 hover:border-[#444]">Filter_Pending</button>
              </div>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-xs text-left border-collapse">
                <thead>
                  <tr className="text-[#444] border-b border-[#111] text-left uppercase font-mono bg-black/20">
                    <th className="px-6 py-4 font-normal">Entity</th>
                    <th className="px-6 py-4 font-normal">Amount</th>
                    <th className="px-6 py-4 font-normal">Status</th>
                    <th className="px-6 py-4 font-normal text-right">Age</th>
                  </tr>
                </thead>
                <tbody className="font-mono divide-y divide-[#111]">
                  {loading ? (
                    [1, 2, 3].map(i => <tr key={i}><td colSpan={4} className="px-6 py-8 animate-pulse bg-[#0F0F0F]/50" /></tr>)
                  ) : invoices.length === 0 ? (
                    <tr>
                      <td colSpan={4} className="px-6 py-20 text-center text-[#222] italic text-[10px] uppercase tracking-[0.3em]">
                         No_Events
                      </td>
                    </tr>
                  ) : invoices.map((inv) => (
                    <tr key={inv.id} className="hover:bg-white/[0.01] transition-colors">
                      <td className="px-6 py-4">
                        <p className="text-[#E0E0E0] font-bold">{inv.customer_name?.split(' ')[0]}</p>
                        <p className="text-[8px] text-[#444]">INV-{inv.id.slice(-6).toUpperCase()}</p>
                      </td>
                      <td className="px-6 py-4 text-[#E0E0E0]">RM {inv.amount.toFixed(2)}</td>
                      <td className="px-6 py-4">
                        <span className={cn(
                          "text-[8px] font-bold uppercase",
                          inv.status === 'paid' ? "text-[#00FF9C]" : "text-yellow-500"
                        )}>
                          {inv.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-right text-[9px] text-[#333]">2.4h</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div className="w-full lg:w-80 space-y-8">
           <div className="bg-[#0A0A0A] border border-[#222] p-8 rounded-sm">
              <h3 className="text-xs font-bold uppercase tracking-widest text-[#666] mb-8 border-b border-[#111] pb-4">Overdue Invoices</h3>
              <div className="space-y-4">
                 {[
                   { name: 'K. Tan', amt: 450, age: '14d' },
                   { name: 'S. Lim', amt: 1200, age: '8d' },
                   { name: 'J. Doe', amt: 85, age: '5d' }
                 ].map((o, i) => (
                   <div key={i} className="flex justify-between items-center group">
                      <div>
                         <p className="text-[10px] font-bold text-[#E0E0E0] uppercase">{o.name}</p>
                         <p className="text-[9px] text-red-500/60 font-mono">RM {o.amt} // {o.age}</p>
                      </div>
                      <button className="opacity-0 group-hover:opacity-100 transition-opacity text-[8px] font-bold text-[#00FF9C] uppercase">Poke</button>
                   </div>
                 ))}
              </div>
           </div>

           <div className="bg-[#0A0A0A] border border-[#222] p-8 rounded-sm">
              <h3 className="text-xs font-bold uppercase tracking-widest text-[#666] mb-8 border-b border-[#111] pb-4">Avg Days to Payment</h3>
              <div className="flex items-end justify-between h-20 gap-1">
                 {[4.2, 3.8, 3.2, 2.8, 1.2, 1.4, 1.1].map((v, i) => (
                   <div key={i} className="flex-1 bg-black/40 relative group">
                      <div 
                         style={{ height: `${(v / 5) * 100}%` }} 
                         className="absolute bottom-0 w-full bg-[#E0E0E0]/10 group-hover:bg-[#00FF9C] transition-all"
                      />
                   </div>
                 ))}
              </div>
              <p className="text-[9px] text-[#333] font-mono mt-4 uppercase text-center italic tracking-widest">Target: {" < "} 2.0 Days</p>
           </div>
        </div>
      </div>
    </motion.div>
  );
}
