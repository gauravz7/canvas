import React, { memo } from 'react';
import { Handle, Position, NodeResizer } from '@xyflow/react';
import { Music, X, Play } from 'lucide-react';

const MusicNode = ({ data, isConnectable, selected }) => {
  return (
    <div className={`node-card ${data.status === 'running' ? 'running' : ''}`}>
      <NodeResizer
        minWidth={250}
        minHeight={150}
        isVisible={selected}
        lineClassName="border-blue-500"
        handleClassName="bg-blue-500 border-2 border-white rounded-full w-3 h-3"
      />
      {data.status && data.status !== 'idle' && (
        <div className={`status-badge ${data.status}`}>
          {data.status}
        </div>
      )}
      <div className="node-header blue">
        <div className="node-title">
          <Music size={16} color="#60a5fa" />
          <span className="node-title-text">{data.label || 'Lyria Music'}</span>
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

      <div className="node-content overflow-y-auto flex-1">
        <div className="node-text-small text-gray-400 mb-2">
          Input a prompt to generate music.
        </div>
        {data.value && (
          <div className="node-value-box">
            {data.value}
          </div>
        )}
      </div>

      <div className="node-input-wrapper mt-2">
        <Handle
          type="target"
          position={Position.Left}
          id="text"
          isConnectable={isConnectable}
          className="node-handle input"
        />
        <span className="node-handle-label left">Prompt</span>
      </div>

      <div className="node-output-wrapper mt-4">
        <Handle
          type="source"
          position={Position.Right}
          id="audio"
          isConnectable={isConnectable}
          className="node-handle output"
        />
        <span className="node-handle-label right">Audio Output</span>
      </div>
    </div>
  );
};

export default memo(MusicNode);
