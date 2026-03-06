import React from 'react';
import { BrainCircuit, AlertTriangle, TrendingUp, Target, Loader2 } from 'lucide-react';
import { ReceiveStrategicAnalysisOutput } from '@/ai/flows/receive-strategic-analysis';

interface StrategicAnalysisPanelProps {
  analysis: ReceiveStrategicAnalysisOutput | null;
  loading: boolean;
}

export function StrategicAnalysisPanel({ analysis, loading }: StrategicAnalysisPanelProps) {
  return (
    <aside className="w-80 bg-[#151A20] border-l border-[#1F6FEB]/20 flex flex-col p-4 shrink-0 overflow-hidden">
      <div className="flex items-center gap-2 mb-6">
        <BrainCircuit className="w-4 h-4 text-[#F59E0B]" />
        <h2 className="font-headline font-bold text-xs uppercase tracking-[0.2em] text-[#F59E0B]">Strategic Analysis</h2>
      </div>

      {loading ? (
        <div className="flex-1 flex flex-col items-center justify-center text-[#9CA3AF]">
          <Loader2 className="w-8 h-8 animate-spin mb-4 text-[#1F6FEB]" />
          <span className="text-xs uppercase font-bold tracking-widest animate-pulse">Consulting AI Strategist...</span>
        </div>
      ) : analysis ? (
        <div className="flex-1 overflow-y-auto pr-2 space-y-6 scrollbar-hide">
          {/* Overview */}
          <section className="space-y-2">
            <div className="flex items-center gap-2">
              <Target className="w-3.5 h-3.5 text-[#1F6FEB]" />
              <h3 className="text-[10px] font-bold text-[#9CA3AF] uppercase tracking-widest">Operational Overview</h3>
            </div>
            <p className="text-xs text-[#E6EDF3] leading-relaxed border-l-2 border-[#1F6FEB]/30 pl-3 italic">
              "{analysis.strategicOverview}"
            </p>
          </section>

          {/* Risk */}
          <section className="space-y-2">
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-3.5 h-3.5 text-[#EF4444]" />
              <h3 className="text-[10px] font-bold text-[#9CA3AF] uppercase tracking-widest">Risk Assessment</h3>
            </div>
            <div className="bg-[#EF4444]/5 border border-[#EF4444]/20 p-3 rounded-sm">
              <p className="text-xs text-[#EF4444] font-medium leading-relaxed">
                {analysis.riskAssessment}
              </p>
            </div>
          </section>

          {/* Enemy Behavior */}
          <section className="space-y-2">
            <div className="flex items-center gap-2">
              <TrendingUp className="w-3.5 h-3.5 text-[#F59E0B]" />
              <h3 className="text-[10px] font-bold text-[#9CA3AF] uppercase tracking-widest">Enemy Forecast</h3>
            </div>
            <p className="text-xs text-[#9CA3AF] leading-relaxed">
              {analysis.predictedEnemyBehavior}
            </p>
          </section>

          {/* Recommended Actions */}
          <section className="space-y-3 pt-4 border-t border-[#1F6FEB]/10">
            <h3 className="text-[10px] font-bold text-white uppercase tracking-widest">Directive Recommendations</h3>
            <div className="space-y-2">
              {analysis.recommendedActions.map((action, idx) => (
                <div key={idx} className="flex gap-3 group">
                  <span className="text-[10px] font-mono text-[#1F6FEB] font-bold">0{idx + 1}</span>
                  <p className="text-xs text-[#E6EDF3] group-hover:text-[#1F6FEB] transition-colors leading-snug">
                    {action}
                  </p>
                </div>
              ))}
            </div>
          </section>
        </div>
      ) : (
        <div className="flex-1 flex items-center justify-center text-center px-4">
          <p className="text-[10px] uppercase font-bold tracking-widest text-[#9CA3AF]">
            Awaiting Battlefield Summary to generate analysis
          </p>
        </div>
      )}

      <div className="mt-auto pt-4 bg-[#151A20] z-10">
        <div className="bg-[#0D223A] p-2 rounded border border-[#1F6FEB]/20 flex items-center gap-3">
          <div className="w-2 h-2 rounded-full bg-[#22C55E] animate-pulse shadow-[0_0_5px_#22C55E]" />
          <span className="text-[10px] font-mono text-[#9CA3AF]">AI STRATEGIST ONLINE</span>
        </div>
      </div>
    </aside>
  );
}