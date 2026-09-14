import React from 'react';
import {
  CheckCircle2,
  XCircle,
  Clock,
  Coins,
  ArrowRight,
  Zap,
  ChevronDown,
  ChevronUp,
  X,
} from 'lucide-react';

const ExecutionLogPanel = ({ executionResult, isCollapsed, onToggleCollapse, onClear }) => {
  if (!executionResult) return null;

  const {
    run_id,
    status,
    input_context,
    path_taken,
    node_results,
    final_action,
    total_tokens,
    total_latency_ms,
    created_at,
  } = executionResult;

  return (
    <div
      className={`fixed bottom-4 right-4 z-40 w-96 rounded-2xl border border-slate-800 bg-slate-950/95 shadow-2xl backdrop-blur-md transition-all duration-300 ${
        isCollapsed ? 'h-14 overflow-hidden' : 'max-h-[32rem] flex flex-col'
      }`}
    >
      {/* Header */}
      <div className="flex h-14 items-center justify-between border-b border-slate-800 px-4">
        <div className="flex items-center gap-2">
          <div className="flex h-6 w-6 items-center justify-center rounded-md bg-emerald-500/10 text-emerald-400">
            <CheckCircle2 className="h-3.5 w-3.5" />
          </div>
          <div>
            <h3 className="text-xs font-semibold text-white flex items-center gap-1.5">
              Execution Trace
              <span className="font-mono text-[10px] text-slate-500">({run_id})</span>
            </h3>
          </div>
        </div>

        <div className="flex items-center gap-1">
          <button
            onClick={onToggleCollapse}
            className="rounded p-1 text-slate-400 hover:bg-slate-800 hover:text-white"
          >
            {isCollapsed ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
          </button>
          <button
            onClick={onClear}
            className="rounded p-1 text-slate-400 hover:bg-slate-800 hover:text-white"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Content */}
      {!isCollapsed && (
        <div className="flex-1 overflow-y-auto p-4 space-y-4 text-xs">
          {/* Summary KPIs */}
          <div className="grid grid-cols-3 gap-2 rounded-xl bg-slate-900/80 p-2.5 border border-slate-800/80 text-center">
            <div>
              <div className="text-[10px] text-slate-400 flex items-center justify-center gap-1">
                <Clock className="h-3 w-3" /> Latency
              </div>
              <div className="mt-0.5 font-mono text-xs font-bold text-slate-200">
                {total_latency_ms} ms
              </div>
            </div>
            <div>
              <div className="text-[10px] text-slate-400 flex items-center justify-center gap-1">
                <Coins className="h-3 w-3" /> Tokens
              </div>
              <div className="mt-0.5 font-mono text-xs font-bold text-slate-200">
                {total_tokens}
              </div>
            </div>
            <div>
              <div className="text-[10px] text-slate-400">Path Depth</div>
              <div className="mt-0.5 font-mono text-xs font-bold text-blue-400">
                {path_taken.length} steps
              </div>
            </div>
          </div>

          {/* Terminal Action */}
          {final_action && (
            <div className="rounded-xl border border-amber-500/30 bg-amber-500/10 p-3 text-amber-200">
              <div className="flex items-center gap-1.5 font-semibold text-[11px] uppercase tracking-wider text-amber-400">
                <Zap className="h-3.5 w-3.5" /> Terminal Action Dispatched
              </div>
              <div className="mt-1 font-medium text-xs">{final_action}</div>
            </div>
          )}

          {/* Step By Step Traversal */}
          <div>
            <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-2">
              Decision Steps ({path_taken.length})
            </div>
            <div className="space-y-2.5">
              {path_taken.map((nodeId, idx) => {
                const step = node_results[nodeId];
                if (!step) return null;
                const isDecision = step.node_type === 'decision';

                return (
                  <div
                    key={nodeId}
                    className="relative rounded-xl border border-slate-800 bg-slate-900/60 p-3 space-y-1.5"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-slate-200 flex items-center gap-1.5 text-xs">
                        <span className="flex h-4 w-4 items-center justify-center rounded-full bg-slate-800 text-[10px] font-mono text-slate-400">
                          {idx + 1}
                        </span>
                        {step.label}
                      </span>

                      {isDecision && step.decision === 'YES' && (
                        <span className="rounded bg-emerald-500/20 px-2 py-0.5 text-[10px] font-bold text-emerald-400 border border-emerald-500/30">
                          YES
                        </span>
                      )}
                      {isDecision && step.decision === 'NO' && (
                        <span className="rounded bg-rose-500/20 px-2 py-0.5 text-[10px] font-bold text-rose-400 border border-rose-500/30">
                          NO
                        </span>
                      )}
                    </div>

                    {step.reasoning && (
                      <p className="text-[11px] text-slate-400 leading-relaxed italic">
                        "{step.reasoning}"
                      </p>
                    )}

                    <div className="flex items-center justify-between text-[10px] text-slate-500 pt-1 border-t border-slate-800/40">
                      <span>{step.latency_ms} ms</span>
                      <span>{step.tokens} tokens</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ExecutionLogPanel;
