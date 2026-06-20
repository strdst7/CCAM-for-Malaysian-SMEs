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
      className="bg-[#0A0A0A] border border-[#222] rounded-md overflow-hidden pb-10"
    >
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
                 placeholder="Search customer/phone..."
                 value={searchQuery}
                 onChange={(e) => setSearchQuery(e.target.value)}
                 className="bg-[#050505] border border-[#111] text-[#E0E0E0] text-[10px] px-4 py-1 font-mono focus:border-[#00FF9C] outline-none rounded-sm min-w-[200px]"
               />
               <select 
                 value={statusFilter}
                 onChange={(e) => setStatusFilter(e.target.value)}
                 className="bg-[#050505] border border-[#111] text-[#E0E0E0] text-[10px] px-3 py-1 font-mono focus:border-[#00FF9C] outline-none rounded-sm"
               >
                  <option value="ALL">ALL_STATUS</option>
                  <option value="NEW">NEW</option>
                  <option value="CONFIRMED">CONFIRMED</option>
                  <option value="CANCELLED">CANCELLED</option>
               </select>
            </div>
        </div>
        <div className="flex items-center gap-4">
           <span className="text-[10px] text-[#444] uppercase font-mono italic">Node: msia-west-1</span>
           <div className="w-2 h-2 rounded-full bg-[#00FF9C] shadow-[0_0_8px_#00FF9C]" />
        </div>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-xs text-left border-collapse">
          <thead>
            <tr className="text-[#444] border-b border-[#222] text-left uppercase font-mono">
              <th className="px-6 py-4 font-normal">Customer Info</th>
              <th className="px-6 py-4 font-normal text-center">Items (Intent)</th>
              <th className="px-6 py-4 font-normal text-center">Confidence</th>
              <th className="px-6 py-4 font-normal text-center">Process Status</th>
              <th className="px-6 py-4 font-normal text-right">HITL</th>
            </tr>
          </thead>
          <tbody className="font-mono divide-y divide-[#111]">
            {loading ? (
              [1, 2, 3, 4].map(i => (
                <tr key={i} className="animate-pulse">
                  <td colSpan={5} className="px-6 py-8 bg-[#0F0F0F]/50" />
                </tr>
              ))
            ) : filteredOrders.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-6 py-20 text-center text-[#222] italic text-[10px] uppercase tracking-[0.3em]">
                   Empty_Buffer_Node_Idle
                </td>
              </tr>
            ) : filteredOrders.map((order) => (
              <tr key={order.id} className="hover:bg-[#0F0F0F] transition-colors group">
                <td className="px-6 py-5">
                  <p className="text-[#E0E0E0] font-bold">{order.customer_name || 'ANON_CLIENT'}</p>
                  <p className="text-[10px] text-[#444] mt-1 italic tracking-tighter">{order.customer_phone}</p>
                </td>
                <td className="px-6 py-5">
                  <div className="flex flex-col items-center gap-1.5">
                    {order.items.map((item, idx) => (
                      <span key={idx} className="text-[10px] px-2 py-0.5 bg-[#111] border border-[#222] text-[#888] rounded-sm">
                        {item.qty}x {item.name}
                      </span>
                    ))}
                  </div>
                </td>
                <td className="px-6 py-5">
                  <div className="flex flex-col items-center gap-2">
                    <div className="w-16 h-1 bg-[#111] rounded-full overflow-hidden shrink-0">
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
                      "text-[10px] font-bold font-mono",
                      order.confidence >= 0.85 ? "text-[#00FF9C]" : order.confidence >= 0.5 ? "text-yellow-500" : "text-red-500"
                    )}>{(order.confidence * 100).toFixed(0)}%</span>
                  </div>
                </td>
                <td className="px-6 py-5 text-center">
                  <span className={cn(
                    "text-[9px] font-bold tracking-widest uppercase border px-2 py-0.5 rounded-full",
                    order.status === 'confirmed' ? "text-[#00FF9C] border-[#00FF9C]/20" : "text-yellow-500 border-yellow-500/20"
                  )}>
                    {order.status === 'confirmed' ? 'ACK_DELIVERED' : 'AWAIT_CORRECTION'}
                  </span>
                </td>
                <td className="px-6 py-5 text-right">
                  <button 
                    onClick={() => onCorrect(order)}
                    disabled={order.status === 'confirmed'}
                    className={cn(
                      "transition-all p-2 rounded border",
                      order.status === 'confirmed' ? "text-[#222] border-transparent" : "text-[#E0E0E0] border-[#222] hover:border-[#00FF9C] hover:text-[#00FF9C]"
                    )}
                  >
                    <CheckCircle2 size={14} />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="p-4 bg-[#080808] border-t border-[#222] flex justify-between items-center px-10">
        <div className="flex items-center gap-8">
          <div className="text-[9px] text-[#444] uppercase tracking-widest">Active Sink: <span className="text-[#E0E0E0]">Malaysian Cloud</span></div>
          <div className="text-[9px] text-[#444] uppercase tracking-widest">Parser Health: <span className="text-[#00FF9C]">Stable</span></div>
          <div className="text-[9px] text-[#333] italic font-mono">Federated Learning: OPT_IN</div>
        </div>
        <div className="flex items-center gap-4">
           {orders.some(o => o.status !== 'confirmed' && o.confidence < 0.85) && (
              <div className="flex items-center gap-2 px-3 py-1 bg-yellow-500/5 border border-yellow-500/20 rounded-sm animate-pulse">
                <AlertCircle size={10} className="text-yellow-500" />
                <span className="text-[9px] text-yellow-500 font-bold uppercase">HITL Action Required</span>
              </div>
           )}
           <button className="px-6 py-2 bg-transparent border border-[#222] text-[#E0E0E0] text-[10px] font-bold rounded-sm uppercase tracking-widest hover:border-[#00FF9C] transition-all">
             Refresh Buffer
           </button>
        </div>
      </div>
    </motion.div>
  );
}
