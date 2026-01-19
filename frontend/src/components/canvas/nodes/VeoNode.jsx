import React, { memo } from 'react';
import { Handle, Position, NodeResizer } from '@xyflow/react';
import { Video, X, Layout, Maximize2, Image as ImageIcon, Play } from 'lucide-react';
import { useConfig } from '../../../contexts/ConfigContext';

const VeoNode = ({ data, isConnectable, selected }) => {
  const { config } = useConfig();
  const isStandard = data.type === 'veo_standard';
  const isExtend = data.type === 'veo_extend';
  const isReference = data.type === 'veo_reference';

  const models = config?.VEO_MODELS || [];

  const handleConfigChange = (key, value) => {
    if (data.onUpdate) {
      data.onUpdate({ config: { ...data.config, [key]: value } });
    }
  };

  const handleModelChange = (e) => {
    if (data.onUpdate) {
      data.onUpdate({ model: e.target.value });
    }
  };

  return (
    <div className={`node-card ${data.status === 'running' ? 'running' : ''}`} style={{ width: '100%', height: '100%' }}>
      <NodeResizer
        minWidth={250}
        minHeight={300}
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
          <Video size={16} color="#c084fc" />
          <span className="node-title-text">{data.label}</span>
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
        <div className="flex flex-col gap-2">
          {/* Model Selector */}
          <div className="flex flex-col gap-1 mb-1">
            <label className="text-[10px] text-gray-500 font-medium">Model</label>
            <select
              className="bg-gray-900 border border-gray-700 text-[10px] text-gray-300 rounded p-1 w-full focus:outline-none focus:border-purple-500"
              value={data.model || ""}
              onChange={handleModelChange}
            >
              <option value="" disabled>Select Model</option>
              {models.map(m => (
                <option key={m} value={m}>{m}</option>
              ))}
            </select>
          </div>

          <div className="flex flex-col gap-2">
            {/* Common Configs */}
            <div className="flex flex-col gap-1">
              <label className="text-[10px] text-gray-500 font-medium">Aspect Ratio</label>
              <select
                className="bg-gray-900 border border-gray-700 text-[10px] text-gray-300 rounded p-1"
                value={data.config?.aspect_ratio || "16:9"}
                onChange={(e) => handleConfigChange('aspect_ratio', e.target.value)}
              >
                <option value="16:9">16:9 (Landscape)</option>
                <option value="9:16">9:16 (Portrait)</option>
                <option value="1:1">1:1 (Square)</option>
              </select>
            </div>

            {isStandard && (
              <div className="flex flex-col gap-1">
                <label className="text-[10px] text-gray-500 font-medium">Resolution</label>
                <select
                  className="bg-gray-900 border border-gray-700 text-[10px] text-gray-300 rounded p-1"
                  value={data.config?.resolution || "720p"}
                  onChange={(e) => handleConfigChange('resolution', e.target.value)}
                >
                  <option value="720p">720p</option>
                  <option value="1080p">1080p</option>
                  <option value="4k">4k</option>
                </select>
              </div>
            )}

            <div className="flex flex-col gap-1">
              <label className="text-[10px] text-gray-500 font-medium">Duration (Seconds)</label>
              <input
                type="number"
                className="bg-gray-900 border border-gray-700 text-[10px] text-gray-300 rounded p-1 node-input-no-stepper"
                value={data.config?.duration_seconds || 8}
                min={1}
                max={15}
                onChange={(e) => handleConfigChange('duration_seconds', parseInt(e.target.value))}
              />
            </div>

            <div className="flex items-center gap-2 mt-1">
              <input
                type="checkbox"
                id={`audio-${data.id}`}
                className="w-3 h-3"
                checked={data.config?.generate_audio || false}
                onChange={(e) => handleConfigChange('generate_audio', e.target.checked)}
              />
              <label htmlFor={`audio-${data.id}`} className="text-[10px] text-gray-400">Generate Audio</label>
            </div>
          </div>
        </div>

        {/* Inputs handle based on type */}
        <div className="flex flex-col gap-3 mt-2 border-t border-gray-800 pt-3">
          <div className="node-input-wrapper relative">
            <Handle type="target" position={Position.Left} id="text" isConnectable={isConnectable} className="node-handle input" />
            <span className="node-handle-label left">Prompt</span>
          </div>

          {isStandard && (
            <>
              <div className="node-input-wrapper relative">
                <Handle type="target" position={Position.Left} id="first_frame" isConnectable={isConnectable} className="node-handle input" />
                <span className="node-handle-label left">First Frame</span>
              </div>
              <div className="node-input-wrapper relative">
                <Handle type="target" position={Position.Left} id="last_frame" isConnectable={isConnectable} className="node-handle input" />
                <span className="node-handle-label left">Last Frame</span>
              </div>
            </>
          )}

          {isExtend && (
            <>
              <div className="node-input-wrapper relative">
                <Handle type="target" position={Position.Left} id="video" isConnectable={isConnectable} className="node-handle input" />
                <span className="node-handle-label left">Input Video</span>
              </div>
              <div className="node-input-wrapper relative">
                <Handle type="target" position={Position.Left} id="next_video" isConnectable={isConnectable} className="node-handle input" />
                <span className="node-handle-label left">Next Video (Optional)</span>
              </div>
            </>
          )}

          {isReference && (
            <div className="node-input-wrapper relative">
              <Handle type="target" position={Position.Left} id="image" isConnectable={isConnectable} className="node-handle input" />
              <span className="node-handle-label left">Ref Images (max 3)</span>
            </div>
          )}
        </div>

        <div className="node-output-wrapper mt-4">
          <Handle
            type="source"
            position={Position.Right}
            id="video"
            isConnectable={isConnectable}
            className="node-handle output"
          />
          <span className="node-handle-label right">Video Output</span>
        </div>
      </div>
    </div>
  );
};

export default memo(VeoNode);
