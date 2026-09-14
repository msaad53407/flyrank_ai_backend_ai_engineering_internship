import React, { memo } from 'react';
import { Handle, Position } from '@xyflow/react';
import { Brain, CheckCircle2, XCircle, Loader2 } from 'lucide-react';

const AIDecisionNode = ({ id, data, isConnectable }) => {
  const execution = data.executionResult || null;
  const isRunning = data.isRunning || false;
  const isTraversed = data.isTraversed || false;
  const isSkipped = data.isSkipped || false;

  const decision = execution ? execution.decision : null;

  // Determine border & glow based on execution state
  let statusBorder = 'border-slate-800 hover:border-slate-700';
  let statusBg = 'bg-slate-900/90';

  if (isRunning) {
    statusBorder = 'border-blue-500 ring-4 ring-blue-500/20 shadow-lg shadow-blue-500/20';
  } else if (isTraversed && decision === 'YES') {
    statusBorder = 'border-emerald-500 ring-2 ring-emerald-500/30 shadow-lg shadow-emerald-500/10';
  } else if (isTraversed && decision === 'NO') {
    statusBorder = 'border-rose-500 ring-2 ring-rose-500/30 shadow-lg shadow-rose-500/10';
  } else if (isSkipped) {
    statusBorder = 'border-slate-800/40 opacity-40';
  }

  const handlePromptChange = (e) => {
    if (data.onUpdateNode) {
      data.onUpdateNode(id, { prompt: e.target.value });
    }
  };

  const handleLabelChange = (e) => {
    if (data.onUpdateNode) {
      data.onUpdateNode(id, { label: e.target.value });
    }
  };

  return (
    <div
      className={`w-72 rounded-xl border ${statusBorder} ${statusBg} p-4 shadow-xl backdrop-blur-md transition-all duration-300`}
    >
      {/* Target Input Handle */}
      <Handle
        type="target"
        position={Position.Top}
        isConnectable={isConnectable}
        className="!h-3 !w-3 !bg-blue-500 !border-2 !border-slate-900"
      />

      {/* Node Header */}
      <div className="flex items-center justify-between gap-2 border-b border-slate-800/80 pb-2.5">
        <div className="flex items-center gap-2">
          <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-blue-500/10 text-blue-400">
            <Brain className="h-4 w-4" />
          </div>
          <input
            type="text"
            value={data.label || 'Decision Node'}
            onChange={handleLabelChange}
            className="w-40 truncate bg-transparent font-medium text-sm text-slate-200 focus:outline-none focus:ring-1 focus:ring-blue-500/50 rounded px-1"
          />
        </div>

        {/* Execution status indicator badge */}
        {isRunning && (
          <span className="flex items-center gap-1 rounded-full bg-blue-500/20 px-2 py-0.5 text-[11px] font-medium text-blue-400 animate-pulse">
            <Loader2 className="h-3 w-3 animate-spin" /> Thinking
          </span>
        )}
        {!isRunning && isTraversed && decision === 'YES' && (
          <span className="flex items-center gap-1 rounded-full bg-emerald-500/20 px-2 py-0.5 text-[11px] font-semibold text-emerald-400">
            <CheckCircle2 className="h-3 w-3" /> YES
          </span>
        )}
        {!isRunning && isTraversed && decision === 'NO' && (
          <span className="flex items-center gap-1 rounded-full bg-rose-500/20 px-2 py-0.5 text-[11px] font-semibold text-rose-400">
            <XCircle className="h-3 w-3" /> NO
          </span>
        )}
      </div>

      {/* Decision Prompt / Rule */}
      <div className="mt-3">
        <label className="text-[11px] font-semibold tracking-wider uppercase text-slate-400">
          AI Evaluation Rule
        </label>
        <textarea
          rows={3}
          value={data.prompt || ''}
          onChange={handlePromptChange}
          placeholder="e.g. Is the customer reporting an urgent double charge?"
          className="mt-1 w-full resize-none rounded-lg border border-slate-800 bg-slate-950/60 p-2 text-xs text-slate-300 placeholder-slate-500 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
        />
      </div>

      {/* Execution reasoning snippet if evaluated */}
      {execution && execution.reasoning && (
        <div className="mt-2 rounded bg-slate-950/40 p-2 text-[11px] text-slate-400 border border-slate-800/60">
          <span className="font-semibold text-slate-300">Reason: </span>
          {execution.reasoning}
          <div className="mt-1 flex gap-3 text-[10px] text-slate-500">
            <span>{execution.latency_ms}ms</span>
            <span>{execution.tokens} tokens</span>
          </div>
        </div>
      )}

      {/* Branching Output Handles */}
      <div className="mt-4 flex items-center justify-between pt-1 text-[11px] font-semibold">
        {/* YES branch */}
        <div className="relative flex items-center">
          <Handle
            type="source"
            position={Position.Bottom}
            id="yes"
            style={{ left: 36 }}
            isConnectable={isConnectable}
            className="!h-3.5 !w-3.5 !bg-emerald-500 !border-2 !border-slate-900"
          />
          <span className="rounded bg-emerald-500/20 px-2 py-0.5 text-emerald-400 border border-emerald-500/30">
            YES ➔
          </span>
        </div>

        {/* NO branch */}
        <div className="relative flex items-center">
          <Handle
            type="source"
            position={Position.Bottom}
            id="no"
            style={{ right: 36 }}
            isConnectable={isConnectable}
            className="!h-3.5 !w-3.5 !bg-rose-500 !border-2 !border-slate-900"
          />
          <span className="rounded bg-rose-500/20 px-2 py-0.5 text-rose-400 border border-rose-500/30">
            NO ➔
          </span>
        </div>
      </div>
    </div>
  );
};

export default memo(AIDecisionNode);
