import React, { useState, useEffect, useRef } from 'react';
import { 
  Search, 
  Terminal, 
  Sparkles, 
  ArrowRight,
  Monitor,
  Command,
  HelpCircle,
  Play,
  Settings,
  Code,
  Activity,
  User,
  Power,
  Layers,
  CheckCircle2,
  AlertTriangle
} from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { cn } from '../utils';

interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectTab: (tabId: string) => void;
  onTriggerAction: (actionId: string) => void;
  menuItems: Array<{ id: string; label: string; icon: any; category: string }>;
}

export default function CommandPalette({ 
  isOpen, 
  onClose, 
  onSelectTab, 
  onTriggerAction, 
  menuItems 
}: CommandPaletteProps) {
  const [search, setSearch] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Focus input when opened
  useEffect(() => {
    if (isOpen) {
      setSearch('');
      setSelectedIndex(0);
      setTimeout(() => {
        inputRef.current?.focus();
      }, 50);
    }
  }, [isOpen]);

  // Handle Ctrl+K/Cmd+K to close or other keys
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!isOpen) return;

      if (e.key === 'Escape') {
        e.preventDefault();
        onClose();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  // Click outside listener
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen, onClose]);

  // Build commands list
  const tabCommands = menuItems.map(item => ({
    id: `tab-${item.id}`,
    type: 'nav' as const,
    label: `Switch View: ${item.label}`,
    category: `Views — ${item.category}`,
    icon: item.icon,
    shortcut: '↵',
    action: () => onSelectTab(item.id)
  }));

  const systemActions = [
    {
      id: 'action-create-flow',
      type: 'action' as const,
      label: 'Create New Workflow DSL',
      category: 'Operations & Orchestration',
      icon: Code,
      shortcut: '⌘[',
      action: () => onTriggerAction('create-flow')
    },
    {
      id: 'action-run-sim',
      type: 'action' as const,
      label: 'Run Twin-Engine Simulation',
      category: 'Operations & Orchestration',
      icon: Play,
      shortcut: '⌘R',
      action: () => onTriggerAction('run-sim')
    },
    {
      id: 'action-toggle-sidebar',
      type: 'action' as const,
      label: 'Toggle Navigation Drawer',
      category: 'System Configuration',
      icon: Monitor,
      shortcut: '⌘B',
      action: () => onTriggerAction('toggle-sidebar')
    },
    {
      id: 'action-calibrate-edge',
      type: 'action' as const,
      label: 'Trigger Regional Edge Calibration',
      category: 'Cloud Topology & Mesh',
      icon: Sparkles,
      shortcut: '⌘E',
      action: () => onTriggerAction('calibrate-edge')
    },
    {
      id: 'action-reset-configs',
      type: 'action' as const,
      label: 'Reset Local Sandbox State',
      category: 'System Configuration',
      icon: Power,
      shortcut: '⌘OptionR',
      action: () => onTriggerAction('reset-state')
    }
  ];

  const allCommands = [...systemActions, ...tabCommands];

  const filteredCommands = allCommands.filter(cmd => {
    const query = search.toLowerCase();
    return (
      cmd.label.toLowerCase().includes(query) ||
      cmd.category.toLowerCase().includes(query)
    );
  });

  // Keep index within bounds
  useEffect(() => {
    if (selectedIndex >= filteredCommands.length) {
      setSelectedIndex(Math.max(0, filteredCommands.length - 1));
    }
  }, [filteredCommands.length, selectedIndex]);

  // Keyboard navigation inside list
  const handleListKeyDown = (e: React.KeyboardEvent) => {
    if (!isOpen) return;

    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedIndex(prev => (prev + 1) % filteredCommands.length);
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedIndex(prev => (prev - 1 + filteredCommands.length) % filteredCommands.length);
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (filteredCommands[selectedIndex]) {
        filteredCommands[selectedIndex].action();
        onClose();
      }
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <div  
          className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-start justify-center pt-24 px-4 select-none"
          id="cmd-palette-overlay"
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.97, y: -10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.97, y: -10 }}
            transition={{ duration: 0.15, ease: 'easeOut' }}
            ref={containerRef}
            className="w-full max-w-2xl bg-[#090909] border border-[#222]/80 shadow-[0_30px_60px_rgba(0,0,0,0.8)] rounded-md overflow-hidden flex flex-col h-[460px]"
            id="cmd-palette-modal"
          >
            {/* Input Box */}
            <div className="flex items-center px-4 py-3.5 border-b border-[#222] gap-3 bg-black/40">
              <Search size={16} className="text-[#555]" />
              <input
                ref={inputRef}
                type="text"
                placeholder="Search commands, navigate tabs, or simulate action queues..."
                value={search}
                onChange={e => {
                  setSearch(e.target.value);
                  setSelectedIndex(0);
                }}
                onKeyDown={handleListKeyDown}
                className="flex-1 bg-transparent text-xs font-mono text-[#E0E0E0] outline-none placeholder:text-[#444] tracking-wide"
                id="cmd-palette-input"
              />
              <div className="flex items-center gap-1.5 px-2 py-0.5 bg-[#151515] border border-[#222] rounded text-[8px] font-mono text-[#444] tracking-tight uppercase">
                <Command size={8} /> K
              </div>
            </div>

            {/* Results body */}
            <div 
              className="flex-1 overflow-y-auto scrollbar-thin p-2 space-y-4"
              id="cmd-palette-results"
            >
              {filteredCommands.length === 0 ? (
                <div className="py-20 flex flex-col items-center justify-center text-center">
                  <AlertTriangle size={24} className="text-[#333] mb-3" />
                  <p className="text-[10px] uppercase tracking-widest text-[#444] font-mono">No matching actions discovered</p>
                  <p className="text-[9px] text-[#222] font-mono mt-1">Refine your diagnostic query identifier</p>
                </div>
              ) : (
                <div>
                  {/* Group items by category to look extremely orderly */}
                  {Array.from(new Set(filteredCommands.map(c => c.category))).map(categoryName => {
                    const categoryCmds = filteredCommands.filter(c => c.category === categoryName);
                    return (
                      <div key={categoryName} className="mb-4">
                        <div className="px-3 py-1 text-[8px] font-bold tracking-[0.2em] text-[#333] uppercase font-mono mb-1.5">
                          {categoryName}
                        </div>
                        <div className="space-y-0.5">
                          {categoryCmds.map(cmd => {
                            // Find flat index overall for highlighted selection
                            const flatIndex = filteredCommands.findIndex(c => c.id === cmd.id);
                            const isSelected = flatIndex === selectedIndex;
                            const CmdIcon = cmd.icon;

                            return (
                              <button
                                key={cmd.id}
                                onClick={() => {
                                  cmd.action();
                                  onClose();
                                }}
                                onMouseEnter={() => setSelectedIndex(flatIndex)}
                                className={cn(
                                  "w-full flex items-center justify-between px-3 py-2.5 rounded transition-all font-mono text-left",
                                  isSelected 
                                    ? "bg-[#111] border-l-2 border-[#00FF9C] text-[#E0E0E0]" 
                                    : "bg-transparent text-[#666] border-l-2 border-transparent"
                                )}
                              >
                                <div className="flex items-center gap-3">
                                  <CmdIcon 
                                    size={13} 
                                    className={cn(
                                      "shrink-0",
                                      isSelected ? "text-[#00FF9C]" : "text-[#333]"
                                    )} 
                                  />
                                  <span className="text-[10px] tracking-tight hover:font-bold">
                                    {cmd.label}
                                  </span>
                                </div>
                                
                                {isSelected ? (
                                  <div className="flex items-center gap-2">
                                    <span className="text-[8px] font-mono text-[#00FF9C]/60 italic font-light uppercase tracking-tighter">
                                      {cmd.type === 'nav' ? 'switch_view' : 'execute_action'}
                                    </span>
                                    <span className="text-[7px] px-1.5 py-0.5 bg-[#1a1a1a] text-[#444] rounded border border-[#222] font-bold">
                                      {cmd.shortcut}
                                    </span>
                                  </div>
                                ) : (
                                  <span className="text-[7px] text-[#222] uppercase tracking-tighter font-light">
                                    {cmd.type}
                                  </span>
                                )}
                              </button>
                            );
                          })}
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

            {/* Micro footer */}
            <div className="px-4 py-2.5 border-t border-[#222] bg-black/60 flex items-center justify-between text-[8px] font-mono text-[#333] uppercase tracking-wider">
              <div className="flex items-center gap-4">
                <span className="flex items-center gap-1"><ArrowRight size={8} /> ↑↓ Navigate</span>
                <span className="flex items-center gap-1"><ArrowRight size={8} /> Enter Execute</span>
                <span className="flex items-center gap-1"><ArrowRight size={8} /> Esc Depart</span>
              </div>
              <div className="opacity-40 flex items-center gap-1">
                <Terminal size={10} className="text-[#00FF9C]" />
                CCAM_CONSOLE_v1.0.3
              </div>
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}
