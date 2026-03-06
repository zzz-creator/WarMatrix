'use client';

import React from 'react';
import { CloudRain, Wind, Activity, Radio, Boxes } from 'lucide-react';
import { ScrollArea } from '@/components/ui/scroll-area';

export function IntelligencePanel() {
  const intelItems = [
    { label: 'Terrain Type', value: 'Highland / Rugged', icon: Boxes },
    { label: 'Weather', value: 'Partly Cloudy / 18°C', icon: CloudRain },
    { label: 'Wind Speed', value: '12 knots NE', icon: Wind },
    { label: 'Visibility', value: '8.5 km', icon: Activity },
    { label: 'Comm Status', value: 'Encrypted / Stable', icon: Radio },
  ];

  return (
    <aside className="w-72 bg-[#151A20] border-r border-[#1F6FEB]/20 flex flex-col shrink-0 overflow-hidden">
      {/* Panel Header - Always Visible */}
      <div className="p-4 border-b border-[#1F6FEB]/10 bg-[#0F1115]/50 flex items-center gap-2">
        <Activity className="w-4 h-4 text-[#1F6FEB]" />
        <h2 className="font-headline font-bold text-xs uppercase tracking-[0.2em] text-[#1F6FEB]">Battlefield Intel</h2>
      </div>

      {/* Scrollable Content Area */}
      <ScrollArea className="flex-1">
        <div className="p-4 space-y-6">
          {/* Tactical Intel Cards */}
          <div className="space-y-3">
            {intelItems.map((item, idx) => (
              <div 
                key={idx} 
                className="bg-[#0D223A]/30 border border-[#1F6FEB]/10 p-3 rounded-sm group hover:border-[#1F6FEB]/50 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <item.icon className="w-4 h-4 text-[#9CA3AF] group-hover:text-[#1F6FEB] transition-colors" />
                  <div className="flex flex-col">
                    <span className="text-[10px] text-[#9CA3AF] uppercase font-bold tracking-wider">{item.label}</span>
                    <span className="text-xs text-[#E6EDF3] font-medium">{item.value}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Live Signal Feed Section */}
          <div className="pt-2">
            <div className="flex items-center gap-2 mb-3">
              <Radio className="w-4 h-4 text-[#22C55E]" />
              <h2 className="font-headline font-bold text-[10px] uppercase tracking-widest text-[#22C55E]">Live Signal Feed</h2>
            </div>
            
            <div className="space-y-2 font-mono">
              {[
                '[08:22:15] SIGINT: Traffic detected',
                '[08:22:42] SAT: Optical pass complete',
                '[08:23:05] LOG: Convoy reached Obj B',
                '[08:24:12] SENSOR: Seismic activity detected',
                '[08:25:30] COMMS: Alpha team standby',
                '[08:26:01] SYS: Refreshing tactical grid...',
              ].map((log, i) => (
                <div 
                  key={i} 
                  className="text-[10px] text-[#9CA3AF] border-l border-[#1F6FEB]/10 pl-2 py-1 hover:bg-[#1F6FEB]/5 transition-colors cursor-default"
                >
                  {log}
                </div>
              ))}
            </div>
          </div>
        </div>
      </ScrollArea>

      {/* Global Readiness - Always Visible at Bottom */}
      <div className="p-4 border-t border-[#1F6FEB]/10 bg-[#0F1115]/50">
        <div className="flex justify-between items-center text-[10px] text-[#9CA3AF] uppercase font-bold tracking-widest mb-2">
          <span>Global Readiness</span>
          <span className="text-[#22C55E]">88%</span>
        </div>
        <div className="h-1 bg-[#0D223A] rounded-full overflow-hidden">
          <div className="h-full bg-[#22C55E] w-[88%] shadow-[0_0_8px_rgba(34,197,94,0.4)]" />
        </div>
      </div>
    </aside>
  );
}
