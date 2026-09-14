import React, { memo } from 'react';
import { Handle, Position } from '@xyflow/react';
import { Zap, CheckCircle } from 'lucide-react';

const ActionNode = ({ id, data, isConnectable }) => {
  const isTraversed = data.isTraversed || false;
  const isSkipped = data.isSkipped || false;

  let statusBorder = 'border-amber-500/40 hover:border-amber-500/80';
  let statusBg = 'bg-slate-900/90';

  if (isTraversed) {
    statusBorder = 'border-amber-400 ring-4 ring-amber-400/20 shadow-xl shadow-amber-400/20';
  } else if (isSkipped) {
    statusBorder = 'border-slate-800/40 opacity-40';
  }

  const handleActionChange = (e) => {
    if (data.onUpdateNode) {
      data.onUpdateNode(id, { action: e.target.value });
    }
  };

  const handleLabelChange = (e) => {
    if (data.onUpdateNode) {
      data.onUpdateNode(id, { label: e.target.value });
    }
  };

  return (
    <div
      className={`w-64 rounded-xl border ${statusBorder} ${statusBg} p-4 shadow-xl backdrop-blur-md transition-all duration-300`}
    >
      {/* Target Handle */}
      <Handle
        type="target"
        position={Position.Top}
        isConnectable={isConnectable}
        className="!h-3 !w-3 !bg-amber-500 !border-2 !border-slate-900"
      />

      <div className="flex items-center justify-between border-b border-slate-800 pb-2">
        <div className="flex items-center gap-2">
          <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-amber-500/10 text-amber-400">
            <Zap className="h-4 w-4" />
          </div>
          <input
            type="text"
            value={data.label || 'Action Node'}
            onChange={handleLabelChange}
            className="w-36 truncate bg-transparent font-medium text-xs text-amber-200 focus:outline-none focus:ring-1 focus:ring-amber-500/50 rounded px-1"
          />
        </div>
        {isTraversed && (
          <span className="flex items-center gap-1 rounded-full bg-amber-500/20 px-2 py-0.5 text-[10px] font-bold text-amber-300">
            <CheckCircle className="h-3 w-3" /> Reached
          </span>
        )}
      </div>

      <div className="mt-3">
        <label className="text-[10px] font-semibold tracking-wider uppercase text-slate-400">
          Terminal Action Payload
        </label>
        <textarea
          rows={2}
          value={data.action || ''}
          onChange={handleActionChange}
          placeholder="e.g. Route to VIP Support Team"
          className="mt-1 w-full resize-none rounded-lg border border-slate-800 bg-slate-950/60 p-2 text-xs text-slate-300 placeholder-slate-500 focus:border-amber-500 focus:outline-none"
        />
      </div>
    </div>
  );
};

export default memo(ActionNode);
