import React, { memo } from 'react';
import { getBezierPath, EdgeLabelRenderer, BaseEdge } from '@xyflow/react';

const DecisionEdge = ({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  sourceHandleId,
  label,
  data,
  markerEnd,
}) => {
  const [edgePath, labelX, labelY] = getBezierPath({
    sourceX,
    sourceY,
    sourcePosition,
    targetX,
    targetY,
    targetPosition,
  });

  const branchType = (sourceHandleId || label || (data && data.branch) || 'yes').toUpperCase();
  const isYes = branchType.includes('YES');
  const isActive = data && data.isActive;

  let activeClass = '';
  if (isActive) {
    activeClass = isYes ? 'edge-active-yes' : 'edge-active-no';
  }

  return (
    <>
      <BaseEdge
        id={id}
        path={edgePath}
        markerEnd={markerEnd}
        className={`${activeClass}`}
        style={{
          stroke: isActive ? (isYes ? '#10b981' : '#f43f5e') : isYes ? '#065f46' : '#881337',
          strokeWidth: isActive ? 3 : 2,
        }}
      />
      <EdgeLabelRenderer>
        <div
          style={{
            position: 'absolute',
            transform: `translate(-50%, -50%) translate(${labelX}px,${labelY}px)`,
            pointerEvents: 'all',
          }}
          className="nodrag nopan"
        >
          <span
            className={`rounded-full px-2 py-0.5 text-[10px] font-bold tracking-wider shadow-md transition-all ${
              isYes
                ? isActive
                  ? 'bg-emerald-500 text-slate-950 ring-2 ring-emerald-400'
                  : 'bg-emerald-950/80 text-emerald-400 border border-emerald-800/80'
                : isActive
                ? 'bg-rose-500 text-white ring-2 ring-rose-400'
                : 'bg-rose-950/80 text-rose-400 border border-rose-800/80'
            }`}
          >
            {isYes ? 'YES' : 'NO'}
          </span>
        </div>
      </EdgeLabelRenderer>
    </>
  );
};

export default memo(DecisionEdge);
