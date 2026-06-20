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
      className="space-y-6 pb-20"
    >
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {[
          { label: 'Unpaid Receivables', val: 'RM 2,450', sub: '12 active invoices', icon: Clock, color: 'text-yellow-500' },
          { label: 'Settled (24h)', val: 'RM 4,120', sub: '98% automation rate', icon: CheckCircle2, color: 'text-[#00FF9C]' },
          { label: 'DuitNow Latency', val: '1.2s', sub: 'Avg provider response', icon: Activity, color: 'text-white' }
        ].map((k, i) => (
          <div key={i} className="bg-[#0A0A0A] border border-[#222] p-6 rounded-sm">
            <div className="flex justify-between items-start mb-4">
              <p className="text-[9px] font-bold text-[#444] uppercase tracking-widest">{k.label}</p>
              <k.icon size={14} className={k.color} />
            </div>
            <p className={cn("text-2xl font-light italic tracking-tight", k.color)}>{k.val}</p>
            <p className="text-[9px] text-[#333] font-mono mt-1">{k.sub}</p>
          </div>
        ))}
      </div>

      <div className="bg-[#0A0A0A] border border-[#222] rounded-md overflow-hidden">
        <div className="p-5 border-b border-[#222] flex justify-between items-center bg-[#0C0C0C]">
          <h2 className="text-[10px] font-bold tracking-widest text-[#666] uppercase">Invoicing & Settlement Buffer</h2>
          <div className="flex gap-4">
             <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-[#333]" size={12} />
                <input 
                  placeholder="Search invoice #" 
                  className="bg-[#050505] border border-[#222] text-[10px] py-1.5 pl-8 pr-4 outline-none focus:border-[#00FF9C] text-[#E0E0E0]"
                />
             </div>
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-xs text-left border-collapse">
            <thead>
              <tr className="text-[#444] border-b border-[#222] text-left uppercase font-mono">
                <th className="px-6 py-4 font-normal">Customer</th>
                <th className="px-6 py-4 font-normal">Amount</th>
                <th className="px-6 py-4 font-normal">Payment Link</th>
                <th className="px-6 py-4 font-normal">Status</th>
                <th className="px-6 py-4 font-normal text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="font-mono divide-y divide-[#111]">
              {loading ? (
                [1, 2, 3].map(i => <tr key={i}><td colSpan={5} className="px-6 py-8 animate-pulse bg-[#0F0F0F]/50" /></tr>)
              ) : invoices.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-6 py-20 text-center text-[#222] italic text-[10px] uppercase tracking-[0.3em]">
                     No_Settlement_Events_Logged
                  </td>
                </tr>
              ) : invoices.map((inv) => (
                <tr key={inv.id} className="hover:bg-[#0F0F0F] transition-colors">
                  <td className="px-6 py-5">
                    <p className="text-[#E0E0E0] font-bold">{inv.customer_name}</p>
                    <p className="text-[10px] text-[#444] mt-1">ORD-{inv.order_id.slice(-6).toUpperCase()}</p>
                  </td>
                  <td className="px-6 py-5 text-[#E0E0E0] font-bold">RM {inv.amount.toFixed(2)}</td>
                  <td className="px-6 py-5 text-[10px] text-[#00FF9C] underline truncate max-w-[150px]">
                     {inv.payment_link}
                  </td>
                  <td className="px-6 py-5">
                    <span className={cn(
                      "text-[9px] font-bold tracking-widest uppercase border px-2 py-0.5 rounded-full",
                      inv.status === 'paid' ? "text-[#00FF9C] border-[#00FF9C]/20 bg-[#00FF9C]/5" : "text-yellow-500 border-yellow-500/20 bg-yellow-500/5"
                    )}>
                      {inv.status}
                    </span>
                  </td>
                  <td className="px-6 py-5 text-right">
                     <button className="text-[9px] font-bold text-[#444] hover:text-[#00FF9C] uppercase tracking-widest border border-transparent hover:border-[#00FF9C]/20 px-3 py-1 transition-all">Resend WhatsApp</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </motion.div>
  );
}
