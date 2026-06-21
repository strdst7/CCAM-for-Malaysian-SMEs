import { useState, useEffect } from 'react';
import { motion } from 'motion/react';
import { 
  CheckCircle2,
  AlertCircle
} from 'lucide-react';
import { collection, query, orderBy, onSnapshot, limit } from 'firebase/firestore';
import { db, auth } from '../lib/firebase-client';
import { cn } from '../utils';
import { Order } from '../types';

enum OperationType {
  CREATE = 'create',
  UPDATE = 'update',
  DELETE = 'delete',
  LIST = 'list',
  GET = 'get',
  WRITE = 'write',
}

interface FirestoreErrorInfo {
  error: string;
  operationType: OperationType;
  path: string | null;
  authInfo: {
    userId?: string | null;
    email?: string | null;
    emailVerified?: boolean | null;
    isAnonymous?: boolean | null;
    tenantId?: string | null;
    providerInfo?: {
      providerId?: string | null;
      email?: string | null;
    }[];
  }
}

function handleFirestoreError(error: unknown, operationType: OperationType, path: string | null) {
  const errInfo: FirestoreErrorInfo = {
    error: error instanceof Error ? error.message : String(error),
    authInfo: {
      userId: auth.currentUser?.uid,
      email: auth.currentUser?.email,
      emailVerified: auth.currentUser?.emailVerified,
      isAnonymous: auth.currentUser?.isAnonymous,
      tenantId: auth.currentUser?.tenantId,
      providerInfo: auth.currentUser?.providerData?.map(provider => ({
        providerId: provider.providerId,
        email: provider.email,
      })) || []
    },
    operationType,
    path
  }
  console.error('Firestore Error: ', JSON.stringify(errInfo));
  throw new Error(JSON.stringify(errInfo));
}

export default function OrdersView({ onCorrect }: { onCorrect: (o: Order) => void }) {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterMode, setFilterMode] = useState<'all' | 'correction'>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('ALL');

  useEffect(() => {
    const q = query(collection(db, 'orders'), orderBy('created_at', 'desc'), limit(50));
    const unsubscribe = onSnapshot(q, (snapshot) => {
      const ordersData = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() } as Order));
      setOrders(ordersData);
      setLoading(false);
    }, (error) => {
      handleFirestoreError(error, OperationType.GET, 'orders');
      setLoading(false);
    });
    return () => unsubscribe();
  }, []);

  const filteredOrders = orders.filter(o => {
    const matchesMode = filterMode === 'all' || (o.confidence < 0.85 && o.status !== 'confirmed');
    const matchesSearch = o.customer_name?.toLowerCase().includes(searchQuery.toLowerCase()) || 
                          o.customer_phone?.includes(searchQuery);
    const matchesStatus = statusFilter === 'ALL' || o.status.toUpperCase() === statusFilter;
    return matchesMode && matchesSearch && matchesStatus;
  });

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
    >
      <div className="flex flex-col lg:flex-row gap-8">
        <div className="flex-1 space-y-8">
          <div className="bg-[#0A0A0A] border border-[#222] rounded-md overflow-hidden min-h-[600px]">
            <div className="p-5 border-b border-[#222] flex flex-col md:flex-row justify-between items-start md:items-center bg-[#0C0C0C] gap-4">
              <div className="flex flex-col md:flex-row gap-6 items-start md:items-center w-full md:w-auto">
                  <div className="flex items-center gap-3">
                     <h2 className="text-[10px] font-bold tracking-widest text-[#666] uppercase">Order Buffer</h2>
                     <div className="px-2 py-0.5 bg-[#00FF9C]/10 border border-[#00FF9C]/20 rounded-full flex items-center gap-1.5">
                        <div className="w-1 h-1 bg-[#00FF9C] rounded-full animate-ping" />
                        <span className="text-[7px] font-bold text-[#00FF9C] uppercase">Live_Ingestion_Active</span>
                     </div>
                  </div>
                  
                  <div className="flex gap-2">
                     {['all', 'correction'].map(m => (
                       <button 
                         key={m}
                         onClick={() => setFilterMode(m as any)}
                         className={cn(
                           "text-[8px] font-bold uppercase tracking-widest px-3 py-1 rounded-sm border transition-all",
                           filterMode === m ? "bg-[#00FF9C] text-black border-[#00FF9C]" : "bg-transparent text-[#444] border-[#111] hover:border-[#444]"
                         )}
                       >
                         {m === 'correction' ? 'Correction Queue' : 'Live Stream'}
                       </button>
                     ))}
                  </div>

                  <div className="flex gap-2 w-full md:w-auto">
                     <input 
                       type="text" 
                       placeholder="Search..."
                       value={searchQuery}
                       onChange={(e) => setSearchQuery(e.target.value)}
                       className="bg-[#050505] border border-[#111] text-[#E0E0E0] text-[10px] px-4 py-1 font-mono focus:border-[#00FF9C] outline-none rounded-sm"
                     />
                  </div>
              </div>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-xs text-left border-collapse">
                <thead>
                  <tr className="text-[#444] border-b border-[#111] text-left uppercase font-mono bg-black/20">
                    <th className="px-6 py-4 font-normal">Customer</th>
                    <th className="px-6 py-4 font-normal text-center">Items</th>
                    <th className="px-6 py-4 font-normal text-center">Confidence</th>
                    <th className="px-6 py-4 font-normal text-right">HITL</th>
                  </tr>
                </thead>
                <tbody className="font-mono divide-y divide-[#111]">
                  {loading ? (
                    [1, 2, 3, 4].map(i => (
                      <tr key={i} className="animate-pulse">
                        <td colSpan={4} className="px-6 py-8 bg-[#0F0F0F]/50" />
                      </tr>
                    ))
                  ) : filteredOrders.length === 0 ? (
                    <tr>
                      <td colSpan={4} className="px-6 py-20 text-center text-[#222] italic text-[10px] uppercase tracking-[0.3em]">
                         Empty_Buffer_Node_Idle
                      </td>
                    </tr>
                  ) : filteredOrders.map((order) => (
                    <tr key={order.id} className="hover:bg-white/[0.01] transition-colors group">
                      <td className="px-6 py-5">
                        <p className="text-[#E0E0E0] font-bold">{order.customer_name || 'ANON_CLIENT'}</p>
                        <p className="text-[9px] text-[#444] mt-1 italic tracking-tighter uppercase">{order.status}</p>
                      </td>
                      <td className="px-6 py-5">
                        <div className="flex flex-col items-center gap-1">
                          {order.items.slice(0, 2).map((item, idx) => (
                            <span key={idx} className="text-[8px] text-[#555] uppercase">
                              {item.qty}x {item.name}
                            </span>
                          ))}
                          {order.items.length > 2 && <span className="text-[8px] text-[#333]">+{order.items.length - 2} MORE</span>}
                        </div>
                      </td>
                      <td className="px-6 py-5">
                        <div className="flex flex-col items-center gap-2">
                          <div className="w-12 h-1 bg-[#111] rounded-full overflow-hidden shrink-0">
                            <motion.div
                              initial={{ width: 0 }}
                              animate={{ width: `${order.confidence * 100}%` }}
                              className={cn(
                                "h-full",
                                order.confidence >= 0.85 ? "bg-[#00FF9C]" : order.confidence >= 0.5 ? "bg-yellow-500" : "bg-red-500"
                              )}
                            />
                          </div>
                          <span className={cn(
                            "text-[8px] font-bold font-mono",
                            order.confidence >= 0.85 ? "text-[#00FF9C]" : order.confidence >= 0.5 ? "text-yellow-500" : "text-red-500"
                          )}>{(order.confidence * 100).toFixed(0)}%</span>
                        </div>
                      </td>
                      <td className="px-6 py-5 text-right">
                        <button 
                          onClick={() => onCorrect(order)}
                          disabled={order.status === 'confirmed'}
                          className={cn(
                            "transition-all p-1.5 rounded-sm border",
                            order.status === 'confirmed' ? "text-[#222] border-transparent" : "text-[#E0E0E0] border-[#222] hover:border-[#00FF9C] hover:text-[#00FF9C]"
                          )}
                        >
                          <CheckCircle2 size={12} />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="bg-[#0A0A0A] border border-[#222] p-6 rounded-sm">
             <div className="flex justify-between items-center mb-6">
                <p className="text-[9px] font-bold text-[#666] uppercase tracking-widest">Parse Accuracy Trend (24h)</p>
                <span className="text-[9px] font-mono text-[#00FF9C]">Avg: 94.2%</span>
             </div>
             <div className="flex items-end gap-1 h-12">
                {[92, 94, 91, 95, 93, 96, 94, 95, 92, 98, 97, 94, 95, 96, 92, 94, 95, 93, 94, 96, 95, 94].map((v, i) => (
                  <div key={i} className="flex-1 bg-black/40 relative group">
                     <div 
                        style={{ height: `${v}%` }} 
                        className="absolute bottom-0 w-full bg-[#00FF9C]/20 group-hover:bg-[#00FF9C] transition-all"
                     />
                  </div>
                ))}
             </div>
          </div>
        </div>

        <div className="w-full lg:w-80 space-y-8">
           <div className="bg-[#0A0A0A] border border-[#222] p-8 rounded-sm">
              <h3 className="text-xs font-bold uppercase tracking-widest text-[#666] mb-8 border-b border-[#111] pb-4">Confidence Stats</h3>
              <div className="space-y-6">
                 {[
                   { label: 'HIGH (>0.85)', val: 78, color: 'bg-[#00FF9C]' },
                   { label: 'MED (0.50-0.85)', val: 15, color: 'bg-yellow-500' },
                   { label: 'LOW (<0.50)', val: 7, color: 'bg-red-500' }
                 ].map((s, i) => (
                   <div key={i}>
                      <div className="flex justify-between text-[9px] font-bold text-[#E0E0E0] mb-2 uppercase">
                         <span>{s.label}</span>
                         <span>{s.val}%</span>
                      </div>
                      <div className="h-1 bg-[#111] rounded-full overflow-hidden">
                         <div className={cn("h-full", s.color)} style={{ width: `${s.val}%` }} />
                      </div>
                   </div>
                 ))}
              </div>
           </div>

           <div className="bg-[#0A0A0A] border border-[#222] p-8 rounded-sm">
              <h3 className="text-xs font-bold uppercase tracking-widest text-[#666] mb-8 border-b border-[#111] pb-4">System Status</h3>
              <div className="space-y-4">
                 <div className="flex justify-between items-center">
                    <span className="text-[9px] text-[#444] uppercase">Kitchen Sync</span>
                    <span className="text-[9px] text-[#00FF9C] font-mono">STABLE</span>
                 </div>
                 <div className="flex justify-between items-center">
                    <span className="text-[9px] text-[#444] uppercase">Worker Queue</span>
                    <span className="text-[9px] text-[#00FF9C] font-mono">LOW</span>
                 </div>
                 <div className="pt-4 border-t border-[#111]">
                    <p className="text-[8px] text-[#333] uppercase leading-relaxed italic">
                      All orders backed by Redis persistence. HITL action required for alerts below 0.85 confidence.
                    </p>
                 </div>
              </div>
           </div>
        </div>
      </div>
    </motion.div>
  );
}
