import React, { memo } from 'react';
import { Handle, Position, NodeResizer } from '@xyflow/react';
import { ArrowUpCircle, X, Play } from 'lucide-react';

const VideoUpscaleNode = ({ data, isConnectable, selected }) => {
  const handleConfigChange = (key, value) => {
    if (data.onUpdate) {
      data.onUpdate({ config: { ...data.config, [key]: value } });
    }
  };

  return (
    <div className={`node-card ${data.status === 'running' ? 'running' : ''}`}>
      <NodeResizer
        minWidth={250}
        minHeight={200}
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
          <span className="node-title-text">{data.label || 'Video Upscale'}</span>
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
          Upscale video to 4K using Veo 3.1
        </div>
        <div className="flex flex-col gap-2">
          <div className="flex flex-col gap-1">
            <label className="text-[10px] text-gray-500 font-medium">Resolution</label>
            <select
              className="bg-gray-900 border border-gray-700 text-[10px] text-gray-300 rounded p-1 w-full focus:outline-none focus:border-purple-500"
              value={data.config?.resolution || '4k'}
              onChange={(e) => handleConfigChange('resolution', e.target.value)}
            >
              <option value="4k">4K</option>
              <option value="1080p">1080p</option>
            </select>
          </div>

          <div className="flex flex-col gap-1">
            <label className="text-[10px] text-gray-500 font-medium">Aspect Ratio</label>
            <select
              className="bg-gray-900 border border-gray-700 text-[10px] text-gray-300 rounded p-1 w-full focus:outline-none focus:border-purple-500"
              value={data.config?.aspect_ratio || '16:9'}
              onChange={(e) => handleConfigChange('aspect_ratio', e.target.value)}
            >
              <option value="16:9">16:9 (Landscape)</option>
              <option value="9:16">9:16 (Portrait)</option>
            </select>
          </div>

          <div className="flex flex-col gap-1">
            <label className="text-[10px] text-gray-500 font-medium">Sharpness (0-4)</label>
            <input
              type="range"
              min="0"
              max="4"
              step="1"
              className="w-full"
              value={data.config?.sharpness ?? 1}
              onChange={(e) => handleConfigChange('sharpness', parseInt(e.target.value))}
            />
            <span className="text-[9px] text-gray-500 text-right">{data.config?.sharpness ?? 1}</span>
          </div>

          <div className="flex flex-col gap-1">
            <label className="text-[10px] text-gray-500 font-medium">Quality</label>
            <select
              className="bg-gray-900 border border-gray-700 text-[10px] text-gray-300 rounded p-1 w-full focus:outline-none focus:border-purple-500"
              value={data.config?.compression_quality || 'optimized'}
              onChange={(e) => handleConfigChange('compression_quality', e.target.value)}
            >
              <option value="optimized">Optimized</option>
              <option value="lossless_16bit_png">Lossless 16-bit PNG</option>
            </select>
          </div>
        </div>
      </div>

      <div className="node-input-wrapper mt-2">
        <Handle
          type="target"
          position={Position.Left}
          id="video"
          isConnectable={isConnectable}
          className="node-handle input"
        />
        <span className="node-handle-label left">Video Input</span>
      </div>

      <div className="node-output-wrapper mt-4">
        <Handle
          type="source"
          position={Position.Right}
          id="video"
          isConnectable={isConnectable}
          className="node-handle output"
        />
        <span className="node-handle-label right">Upscaled Video</span>
      </div>
    </div>
  );
};

export default memo(VideoUpscaleNode);
