import React, { memo } from 'react';
import { Handle, Position, NodeResizer } from '@xyflow/react';
import { Music, X, Play } from 'lucide-react';
import { useConfig } from '../../../contexts/ConfigContext';

const MusicNode = ({ data, type, isConnectable, selected }) => {
  const isPro = type === 'lyria_pro';
  const { config } = useConfig();
  const musicModels = config?.MUSIC_MODELS || ['lyria-3-clip-preview', 'lyria-3-pro-preview', 'lyria-002'];

  const relevantModels = isPro
    ? musicModels.filter(m => m.includes('pro') || m === 'lyria-002')
    : musicModels.filter(m => m.includes('clip') || m === 'lyria-002');

  const handleConfigChange = (key, value) => {
    if (data.onUpdate) {
      data.onUpdate({ config: { ...data.config, [key]: value } });
    }
  };

  return (
    <div className={`node-card ${data.status === 'running' ? 'running' : ''}`}>
      <NodeResizer
        minWidth={250}
        minHeight={180}
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
          <span className="node-title-text">{data.label || (isPro ? 'Lyria Pro' : 'Lyria Clip')}</span>
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
          {isPro ? 'Text + image input to generate a full song with lyrics.' : 'Text prompt to generate a 30s audio clip.'}
        </div>

        <div className="flex flex-col gap-2">
          <div className="flex flex-col gap-1">
            <label className="text-[10px] text-gray-500 font-medium">Model</label>
            <select
              className="bg-gray-900 border border-gray-700 text-[10px] text-gray-300 rounded p-1 w-full focus:outline-none focus:border-blue-500"
              value={data.config?.model_id || (isPro ? 'lyria-3-pro-preview' : 'lyria-3-clip-preview')}
              onChange={(e) => handleConfigChange('model_id', e.target.value)}
            >
              {relevantModels.map(m => (
                <option key={m} value={m}>{m}</option>
              ))}
            </select>
          </div>
        </div>

        {data.value && (
          <div className="node-value-box mt-2">
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

      {isPro && (
        <div className="node-input-wrapper mt-2">
          <Handle
            type="target"
            position={Position.Left}
            id="image"
            isConnectable={isConnectable}
            className="node-handle input"
            style={{ top: '75%' }}
          />
          <span className="node-handle-label left">Image</span>
        </div>
      )}

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
