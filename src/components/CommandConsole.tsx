import React, { useState } from 'react';
import { Send, Crosshair, ShieldCheck, Zap, Radar, Navigation } from 'lucide-react';

interface CommandConsoleProps {
  onExecute: (command: string) => void;
  executing: boolean;
  lastResult: {
    command: string;
    success: number;
    risk: number;
    outcome: string;
  } | null;
}

export function CommandConsole({ onExecute, executing, lastResult }: CommandConsoleProps) {
  const [selectedCommand, setSelectedCommand] = useState<string | null>(null);

  const commands = [
    { id: 'recon', label: 'Deploy Reconnaissance Units', icon: Radar },
    { id: 'defend', label: 'Reinforce Defensive Positions', icon: ShieldCheck },
    { id: 'attack', label: 'Launch Counteroffensive', icon: Crosshair },
    { id: 'strike', label: 'Conduct Precision Strike', icon: Zap },
    { id: 'logistics', label: 'Secure Supply Routes', icon: Navigation },
  ];

  return (
    <footer className="h-56 bg-[#0F1115] border-t border-[#1F6FEB]/20 flex shrink-0">
      {/* Selection Panel */}
      <div className="flex-1 p-4 border-r border-[#1F6FEB]/20 bg-[#151A20]">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-headline font-bold text-xs uppercase tracking-widest text-[#1F6FEB]">Directives Console</h2>
          <span className="text-[10px] font-mono text-[#9CA3AF]">SECURE_AUTH_LVL_4</span>
        </div>
        
        <div className="grid grid-cols-2 gap-3 h-28">
          {commands.map((cmd) => (
            <button
              key={cmd.id}
              onClick={() => setSelectedCommand(cmd.id)}
              className={`flex items-center gap-3 px-4 py-3 border transition-all rounded-sm text-left ${
                selectedCommand === cmd.id 
                ? 'bg-[#1A3B5D] border-[#3A8DFF] text-white shadow-[0_0_15px_rgba(58,141,255,0.2)]' 
                : 'bg-[#0D223A]/50 border-[#1F6FEB]/20 text-[#9CA3AF] hover:border-[#1F6FEB]/50'
              }`}
            >
              <cmd.icon className={`w-4 h-4 ${selectedCommand === cmd.id ? 'text-[#3A8DFF]' : 'text-[#9CA3AF]'}`} />
              <span className="text-[11px] font-bold uppercase tracking-tight">{cmd.label}</span>
            </button>
          ))}
        </div>
        
        <div className="mt-4 flex items-center gap-4">
          <button
            onClick={() => selectedCommand && onExecute(selectedCommand)}
            disabled={!selectedCommand || executing}
            className="flex-1 h-12 bg-[#1A3B5D] hover:bg-[#1e456d] hover:shadow-[0_0_20px_rgba(58,141,255,0.3)] disabled:opacity-50 disabled:bg-[#0D223A] text-white font-headline font-bold uppercase tracking-[0.2em] flex items-center justify-center gap-3 rounded-sm transition-all border border-[#1F6FEB]/30"
          >
            {executing ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Processing Transmission
              </>
            ) : (
              <>
                <Send className="w-5 h-5" />
                Execute Command
              </>
            )}
          </button>
        </div>
      </div>

      {/* Result Panel */}
      <div className="w-96 p-4 bg-[#0A0A0A] border-l border-[#1F6FEB]/10">
        <div className="flex items-center gap-2 mb-4">
          <div className="w-1.5 h-1.5 rounded-full bg-[#22C55E]" />
          <h2 className="font-headline font-bold text-[10px] uppercase tracking-widest text-[#9CA3AF]">Operation Update</h2>
        </div>

        {lastResult ? (
          <div className="space-y-4 animate-in fade-in slide-in-from-bottom-2 duration-500">
            <div className="flex justify-between items-start">
              <div>
                <span className="text-[10px] text-[#9CA3AF] uppercase font-bold tracking-wider">Command</span>
                <div className="text-sm font-bold text-white uppercase">{lastResult.command.replace(/_/g, ' ')}</div>
              </div>
              <div className="text-right">
                <span className="text-[10px] text-[#9CA3AF] uppercase font-bold tracking-wider">Status</span>
                <div className="text-xs font-bold text-[#22C55E]">SUCCESS_NOMINAL</div>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="bg-[#0D223A]/50 border border-[#1F6FEB]/20 p-2 rounded">
                <div className="text-[9px] text-[#9CA3AF] uppercase font-bold mb-1">Success Prob.</div>
                <div className="text-lg font-headline font-bold text-[#1F6FEB]">{lastResult.success}%</div>
              </div>
              <div className="bg-[#0D223A]/50 border border-[#1F6FEB]/20 p-2 rounded">
                <div className="text-[9px] text-[#9CA3AF] uppercase font-bold mb-1">Op Risk</div>
                <div className="text-lg font-headline font-bold text-[#EF4444]">{lastResult.risk}%</div>
              </div>
            </div>

            <div>
              <div className="text-[9px] text-[#9CA3AF] uppercase font-bold mb-1">Immediate Outcome</div>
              <div className="text-xs text-[#E6EDF3] leading-tight font-mono">
                {lastResult.outcome}
              </div>
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center h-full text-center opacity-30">
            <TerminalIcon className="w-12 h-12 text-[#1F6FEB] mb-2" />
            <p className="text-[10px] uppercase font-bold tracking-[0.2em] text-[#9CA3AF]">
              Standby for mission results
            </p>
          </div>
        )}
      </div>
    </footer>
  );
}

const TerminalIcon = ({ className }: { className?: string }) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <polyline points="4 17 10 11 4 5" />
    <line x1="12" y1="19" x2="20" y2="19" />
  </svg>
);