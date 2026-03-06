import React, { useState, useRef, useEffect } from 'react';
import { Send, Terminal, MessageSquare, ShieldAlert } from 'lucide-react';
import { ScrollArea } from '@/components/ui/scroll-area';

interface Message {
  id: string;
  sender: 'OPERATOR' | 'SYSTEM' | 'AI_STRATEGIST';
  text: string;
  timestamp: string;
}

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
  const [inputValue, setInputValue] = useState('');
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      sender: 'SYSTEM',
      text: 'Secure encrypted link established. Awaiting tactical input.',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
    }
  ]);
  
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSubmit = (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!inputValue.trim() || executing) return;

    const newMessage: Message = {
      id: Date.now().toString(),
      sender: 'OPERATOR',
      text: inputValue.trim(),
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
    };

    setMessages(prev => [...prev, newMessage]);
    onExecute(inputValue.trim());
    setInputValue('');
  };

  useEffect(() => {
    if (lastResult) {
      const systemMessage: Message = {
        id: `res-${Date.now()}`,
        sender: 'SYSTEM',
        text: `COMMAND EXECUTED: ${lastResult.command.toUpperCase()}. SUCCESS PROBABILITY: ${lastResult.success}%.`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
      };
      setMessages(prev => [...prev, systemMessage]);
    }
  }, [lastResult]);

  return (
    <footer className="h-64 bg-[#0F1115] border-t border-[#1F6FEB]/20 flex shrink-0">
      {/* Chat / Comms Panel */}
      <div className="flex-1 flex flex-col p-4 border-r border-[#1F6FEB]/20 bg-[#151A20]">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <MessageSquare className="w-3 h-3 text-[#1F6FEB]" />
            <h2 className="font-headline font-bold text-[10px] uppercase tracking-widest text-[#1F6FEB]">Secure Comms Link</h2>
          </div>
          <span className="text-[9px] font-mono text-[#9CA3AF] animate-pulse">ENCRYPTION_ACTIVE_AES256</span>
        </div>
        
        <div className="flex-1 bg-[#0A0A0A]/50 border border-[#1F6FEB]/10 rounded-sm mb-3 overflow-hidden flex flex-col">
          <ScrollArea className="flex-1 p-3">
            <div className="space-y-3" ref={scrollRef}>
              {messages.map((msg) => (
                <div key={msg.id} className="flex flex-col gap-1">
                  <div className="flex items-center gap-2">
                    <span className={`text-[9px] font-bold px-1 rounded-sm ${
                      msg.sender === 'OPERATOR' ? 'bg-[#1F6FEB]/20 text-[#3A8DFF]' : 
                      msg.sender === 'SYSTEM' ? 'bg-[#F59E0B]/20 text-[#F59E0B]' : 
                      'bg-[#22C55E]/20 text-[#22C55E]'
                    }`}>
                      {msg.sender}
                    </span>
                    <span className="text-[8px] font-mono text-[#4B5563]">{msg.timestamp}</span>
                  </div>
                  <p className={`text-xs leading-relaxed font-mono ${
                    msg.sender === 'OPERATOR' ? 'text-[#E6EDF3]' : 'text-[#9CA3AF]'
                  }`}>
                    {msg.text}
                  </p>
                </div>
              ))}
              {executing && (
                <div className="flex items-center gap-2 animate-pulse">
                  <span className="text-[9px] font-bold px-1 rounded-sm bg-[#F59E0B]/20 text-[#F59E0B]">SYSTEM</span>
                  <div className="flex gap-1">
                    <div className="w-1 h-1 bg-[#F59E0B] rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                    <div className="w-1 h-1 bg-[#F59E0B] rounded-full animate-bounce" style={{ animationDelay: '200ms' }} />
                    <div className="w-1 h-1 bg-[#F59E0B] rounded-full animate-bounce" style={{ animationDelay: '400ms' }} />
                  </div>
                </div>
              )}
            </div>
          </ScrollArea>
        </div>
        
        <form onSubmit={handleSubmit} className="relative flex gap-2">
          <div className="relative flex-1">
            <div className="absolute left-3 top-1/2 -translate-y-1/2">
              <Terminal className="w-4 h-4 text-[#1F6FEB]/50" />
            </div>
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Enter tactical directive or query AI strategist..."
              className="w-full h-11 bg-[#0D223A]/50 border border-[#1F6FEB]/30 rounded-sm pl-10 pr-4 text-xs font-mono text-white placeholder:text-[#4B5563] focus:outline-none focus:border-[#3A8DFF] focus:ring-1 focus:ring-[#3A8DFF]/30 transition-all"
              disabled={executing}
            />
          </div>
          <button
            type="submit"
            disabled={!inputValue.trim() || executing}
            className="w-14 h-11 bg-[#1A3B5D] hover:bg-[#1e456d] disabled:opacity-30 flex items-center justify-center rounded-sm border border-[#1F6FEB]/30 transition-all group"
          >
            <Send className={`w-5 h-5 ${inputValue.trim() ? 'text-[#3A8DFF] group-hover:scale-110' : 'text-[#9CA3AF]'} transition-all`} />
          </button>
        </form>
      </div>

      {/* Result Panel */}
      <div className="w-96 p-4 bg-[#0A0A0A] border-l border-[#1F6FEB]/10 flex flex-col">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <div className="w-1.5 h-1.5 rounded-full bg-[#22C55E]" />
            <h2 className="font-headline font-bold text-[10px] uppercase tracking-widest text-[#9CA3AF]">Operation Update</h2>
          </div>
          <ShieldAlert className="w-3.5 h-3.5 text-[#EF4444]/40" />
        </div>

        {lastResult ? (
          <div className="space-y-4 animate-in fade-in slide-in-from-bottom-2 duration-500 overflow-y-auto pr-2 scrollbar-hide">
            <div className="flex justify-between items-start">
              <div className="max-w-[70%]">
                <span className="text-[9px] text-[#9CA3AF] uppercase font-bold tracking-wider">Directives Path</span>
                <div className="text-[11px] font-bold text-white truncate font-mono">{lastResult.command}</div>
              </div>
              <div className="text-right">
                <span className="text-[9px] text-[#9CA3AF] uppercase font-bold tracking-wider">Status</span>
                <div className="text-[10px] font-bold text-[#22C55E]">ACK_SUCCESS</div>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="bg-[#0D223A]/50 border border-[#1F6FEB]/20 p-2 rounded-sm">
                <div className="text-[8px] text-[#9CA3AF] uppercase font-bold mb-1">Impact Rating</div>
                <div className="text-sm font-headline font-bold text-[#1F6FEB]">{lastResult.success}%</div>
              </div>
              <div className="bg-[#0D223A]/50 border border-[#1F6FEB]/20 p-2 rounded-sm">
                <div className="text-[8px] text-[#9CA3AF] uppercase font-bold mb-1">Threat Level</div>
                <div className="text-sm font-headline font-bold text-[#EF4444]">{lastResult.risk}%</div>
              </div>
            </div>

            <div>
              <div className="text-[8px] text-[#9CA3AF] uppercase font-bold mb-1">Tactical Outcome</div>
              <div className="text-[11px] text-[#E6EDF3] leading-relaxed font-mono bg-[#151A20] p-2 border-l border-[#1F6FEB]/30">
                {lastResult.outcome}
              </div>
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center h-full text-center opacity-20 group">
            <TerminalIcon className="w-12 h-12 text-[#1F6FEB] mb-2 group-hover:scale-110 transition-transform" />
            <p className="text-[9px] uppercase font-bold tracking-[0.3em] text-[#9CA3AF]">
              Awaiting transmission
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
