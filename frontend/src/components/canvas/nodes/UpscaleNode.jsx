import React, { memo } from 'react';
import { Handle, Position, NodeResizer } from '@xyflow/react';
import { ArrowUpCircle, X, Play } from 'lucide-react';

const UpscaleNode = ({ data, isConnectable, selected }) => {
  const upscaleFactor = data.config?.upscale_factor || 'x2';

  const handleFactorChange = (e) => {
    if (data.onUpdate) {
      data.onUpdate({ config: { ...data.config, upscale_factor: e.target.value } });
    }
  };

  return (
    <div className={`node-card ${data.status === 'running' ? 'running' : ''}`}>
      <NodeResizer
        minWidth={250}
        minHeight={150}
        isVisible={selected}
        lineClassName="border-purple-500"
        handleClassName="bg-purple-500 border-2 border-white rounded-full w-3 h-3"
      />
      {data.status && data.status !== 'idle' && (
        <div className={`status-badge ${data.status}`}>
          {data.status}
        </div>
      )}
      <div className="node-header purple">
        <div className="node-title">
          <ArrowUpCircle size={16} color="#c084fc" />
          <span className="node-title-text">{data.label || "Image Upscaler"}</span>
        </div>
        <div className="flex items-center gap-1">
          <button onClick={(e) => { e.stopPropagation(); data.onRunPartial?.(); }} className="delete-btn hover:text-green-400" title="Run Node & Descendants">
            <Play size={14} />
          </button>
          <button onClick={data.onDelete} className="delete-btn">
            <X size={14} />
          </button>
        </div>
      </div>

      <div className="node-content">
        <label className="text-[10px] text-gray-500 font-medium mb-1 block">Upscale Factor</label>
        <select
          className="bg-gray-900 border border-gray-700 text-xs text-gray-300 rounded p-1 w-full focus:outline-none focus:border-purple-500"
          value={upscaleFactor}
          onChange={handleFactorChange}
        >
          <option value="x2">2x</option>
          <option value="x4">4x</option>
        </select>
      </div>

      {/* Inputs */}
      <div className="flex flex-col gap-4 mt-2 border-t border-gray-800 pt-4">
        <div className="node-input-wrapper relative">
          <Handle
            type="target"
            position={Position.Left}
            id="image"
            isConnectable={isConnectable}
            className="node-handle input"
          />
          <span className="node-handle-label left">Image Input</span>
        </div>
      </div>

      {/* Outputs */}
      <div className="node-output-wrapper mt-4">
        <Handle
          type="source"
          position={Position.Right}
          id="image"
          isConnectable={isConnectable}
          className="node-handle output"
        />
        <span className="node-handle-label right">Image Output</span>
      </div>
    </div>
  );
};

export default memo(UpscaleNode);
