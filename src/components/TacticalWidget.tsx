import React from 'react';
import { LucideIcon } from 'lucide-react';
import { cn } from '@/lib/utils';

interface TacticalWidgetProps {
  title: string;
  icon: LucideIcon;
  children: React.ReactNode;
  className?: string;
  headerAction?: React.ReactNode;
}

export function TacticalWidget({ title, icon: Icon, children, className, headerAction }: TacticalWidgetProps) {
  return (
    <div className={cn(
      "bg-[#151A20] border border-[#1F6FEB]/20 rounded-sm shadow-[inset_0_0_15px_rgba(31,111,235,0.05)] flex flex-col overflow-hidden group hover:border-[#1F6FEB]/40 transition-colors",
      className
    )}>
      <div className="px-3 py-2 border-b border-[#1F6FEB]/10 bg-[#0F1115]/50 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-2">
          <Icon className="w-3.5 h-3.5 text-[#1F6FEB]" />
          <h3 className="text-[10.5px] font-bold uppercase tracking-[0.2em] text-[#1F6FEB]">{title}</h3>
        </div>
        {headerAction}
      </div>
      <div className="p-3 flex-1 flex flex-col min-h-0">
        {children}
      </div>
    </div>
  );
}
