import { useState, useEffect } from 'react';
import { 
  BarChart3, 
  MessageSquare, 
  BrainCircuit, 
  Settings as SettingsIcon, 
  History,
  CreditCard,
  Menu,
  X,
  Activity,
  Code,
  ShieldCheck as ShieldCheckIcon,
  Shield,
  Server
} from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { cn } from './utils';
import { Order } from './types';
import { doc, getDocFromServer } from 'firebase/firestore';
import { db } from './lib/firebase-client';

// Components
import DashboardView from './components/DashboardView';
import OrdersView from './components/OrdersView';
import SimulatorView from './components/SimulatorView';
import FinancialsView from './components/FinancialsView';
import FlowsView from './components/FlowsView';
import ComplianceView from './components/ComplianceView';
import SettingsView from './components/SettingsView';
import ReportsView from './components/ReportsView';
import QAView from './components/QAView';
import SystemsView from './components/SystemsView';
import HitlModal from './components/HitlModal';

const MENU_ITEMS = [
  { id: 'dashboard', label: 'Dashboard', icon: BarChart3, category: 'Insights' },
  { id: 'reports', label: 'Pilot Tracking', icon: Activity, category: 'Insights' },
  { id: 'qa', label: 'Acceptance Tests', icon: ShieldCheckIcon, category: 'Governance' },
  { id: 'compliance', label: 'Compliance Lab', icon: Shield, category: 'Governance' },
  { id: 'systems', label: 'Topology', icon: Server, category: 'Governance' },
  { id: 'orders', label: 'Order Queue', icon: MessageSquare, category: 'Operations' },
  { id: 'invoices', label: 'Financials', icon: CreditCard, category: 'Insights' },
  { id: 'flows', label: 'Workflow DSL', icon: Code, category: 'Automation' },
  { id: 'simulator', label: 'Digital Twin', icon: BrainCircuit, category: 'Automation' },
  { id: 'settings', label: 'Settings', icon: SettingsIcon, category: 'Governance' },
];

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [correctingOrder, setCorrectingOrder] = useState<Order | null>(null);
  const [syncStatus, setSyncStatus] = useState<'live' | 'offline'>('live');

  useEffect(() => {
    const testConnection = async () => {
      try {
        await getDocFromServer(doc(db, 'system', 'health'));
      } catch (error) {
        if(error instanceof Error && error.message.includes('offline')) {
          setSyncStatus('offline');
        }
      }
    };
    testConnection();

    const checkHealth = async () => {
      try {
        const res = await fetch('/api/health');
        setSyncStatus(res.ok ? 'live' : 'offline');
      } catch {
        setSyncStatus('offline');
      }
    };

    const interval = setInterval(checkHealth, 15000);
    return () => clearInterval(interval);
  }, []);

  const handleCorrect = async (id: string, updates: any) => {
    try {
      await fetch(`/api/orders/${id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...updates, status: 'confirmed', confidence: 1.0 })
      });
      setCorrectingOrder(null);
    } catch (e) {
      console.error(e);
    }
  };

  const categories = Array.from(new Set(MENU_ITEMS.map(i => i.category)));

  return (
    <div className="flex h-screen bg-[#050505] text-[#E0E0E0] font-sans selection:bg-[#00FF9C]/20 overflow-hidden">
      {/* Sidebar */}
      <motion.aside
        initial={false}
        animate={{ width: sidebarOpen ? 240 : 80 }}
        className="bg-[#080808] border-r border-[#222] flex flex-col z-20 shrink-0 transition-all duration-300 ease-in-out"
      >
        <div className="h-16 flex items-center px-6 border-b border-[#222] justify-between">
          <AnimatePresence mode="wait">
            {sidebarOpen ? (
              <motion.div
                key="logo-full"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="flex items-center gap-3"
              >
                <div className="w-8 h-8 bg-[#00FF9C] rounded flex items-center justify-center text-black font-black italic shadow-[0_0_15px_rgba(0,255,156,0.3)]">C</div>
                <span className="font-bold text-lg tracking-tight">CCAM</span>
              </motion.div>
            ) : (
              <div key="logo-short" className="w-8 h-8 bg-[#00FF9C] rounded flex items-center justify-center text-black font-black italic mx-auto shadow-[0_0_15px_rgba(0,255,156,0.3)]">C</div>
            )}
          </AnimatePresence>
        </div>

        <div className="flex-1 px-4 py-8 overflow-y-auto scrollbar-none">
          {categories.map((category) => (
            <div key={category} className="mb-8 last:mb-0">
              {sidebarOpen && <p className="text-[10px] uppercase tracking-[0.2em] text-[#333] font-bold mb-4 px-2">{category}</p>}
              <nav className="space-y-1">
                {MENU_ITEMS.filter(i => i.category === category).map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={cn(
                      "w-full flex items-center gap-3 px-3 py-2.5 rounded transition-all duration-200 group relative",
                      activeTab === tab.id 
                        ? "text-[#00FF9C]" 
                        : "text-[#666] hover:text-[#E0E0E0] hover:bg-white/[0.02]"
                    )}
                  >
                    {activeTab === tab.id && <motion.span layoutId="active-indicator" className="absolute left-0 w-1 h-4 bg-[#00FF9C] shadow-[0_0_8px_#00FF9C]"></motion.span>}
                    <tab.icon size={18} className={cn(
                      "flex-shrink-0 transition-transform group-hover:scale-110",
                      activeTab === tab.id ? "text-[#00FF9C]" : "text-[#444]"
                    )} />
                    {sidebarOpen && <span className="text-sm font-medium whitespace-nowrap">{tab.label}</span>}
                  </button>
                ))}
              </nav>
            </div>
          ))}
        </div>

        <div className="p-4 border-t border-[#222]">
           <button 
             onClick={() => setSidebarOpen(!sidebarOpen)}
             className="w-full flex items-center justify-center p-2 text-[#444] hover:text-[#E0E0E0] transition-colors"
           >
             {sidebarOpen ? <X size={18} /> : <Menu size={18} />}
           </button>
        </div>
      </motion.aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col relative overflow-hidden bg-[#050505] p-6 lg:p-10">
        <header className="flex justify-between items-center mb-10 pb-6 border-b border-[#111]">
          <div>
            <h1 className="text-xl font-light tracking-tight text-[#E0E0E0] flex items-center gap-3 uppercase italic">
              {MENU_ITEMS.find(t => t.id === activeTab)?.label}
              <span className="text-[10px] text-[#333] font-mono not-italic tracking-[0.3em] font-bold">V1.0.3-BETA</span>
            </h1>
          </div>
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-4">
              <div className={cn(
                "flex items-center gap-2 px-3 py-1 bg-[#151515] border rounded text-[10px] font-mono transition-colors duration-500",
                syncStatus === 'live' ? "border-[#00FF9C]/20 text-[#00FF9C]" : "border-red-500/20 text-red-500"
              )}>
                <span className={cn(
                  "w-1.5 h-1.5 rounded-full shadow-[0_0_8px_currentColor]",
                  syncStatus === 'live' ? "bg-[#00FF9C] animate-pulse" : "bg-red-500"
                )}></span>
                {syncStatus === 'live' ? 'SYNC_LIVE' : 'CONNECTION_OFFLINE'}
              </div>
              <div className="flex items-center gap-2 px-3 py-1 bg-[#151515] border border-[#333] rounded text-[10px] font-mono text-[#666]">
                NODE: KUALA_LUMPUR_01
              </div>
            </div>
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-[#333] to-[#111] border border-[#444] shadow-inner"></div>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto scrollbar-thin pr-2">
          <AnimatePresence mode="wait">
             <motion.div
               key={activeTab}
               initial={{ opacity: 0, y: 10 }}
               animate={{ opacity: 1, y: 0 }}
               exit={{ opacity: 0, y: -10 }}
               transition={{ duration: 0.2 }}
             >
                {activeTab === 'dashboard' && <DashboardView />}
                {activeTab === 'reports' && <ReportsView />}
                {activeTab === 'qa' && <QAView />}
                {activeTab === 'orders' && <OrdersView onCorrect={setCorrectingOrder} />}
                {activeTab === 'simulator' && <SimulatorView />}
                {activeTab === 'invoices' && <FinancialsView />}
                {activeTab === 'flows' && <FlowsView />}
                {activeTab === 'compliance' && <ComplianceView />}
                {activeTab === 'systems' && <SystemsView />}
                {activeTab === 'settings' && <SettingsView />}
             </motion.div>
          </AnimatePresence>
        </div>

        {/* Global Overlays */}
        <AnimatePresence>
          {correctingOrder && (
            <HitlModal 
              order={correctingOrder} 
              onClose={() => setCorrectingOrder(null)} 
              onSave={handleCorrect}
            />
          )}
        </AnimatePresence>

        {/* Backdrop Ambient Accents */}
        <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-[#00FF9C]/[0.02] blur-[120px] rounded-full pointer-events-none -z-10" />
        <div className="absolute bottom-0 left-0 w-[300px] h-[300px] bg-white/[0.01] blur-[100px] rounded-full pointer-events-none -z-10" />
      </main>
    </div>
  );
}
