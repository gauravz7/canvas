import React, { memo } from 'react';
import { Handle, Position, NodeResizer } from '@xyflow/react';
import { Bot, Image as ImageIcon, FileText, Code, X, Play } from 'lucide-react';
import { useConfig } from '../../../contexts/ConfigContext';

const GeminiNode = ({ data, isConnectable, selected }) => {
  const isImageModel = data.type === 'gemini_image';
  const { config } = useConfig();

  const models = isImageModel
    ? (config?.GEMINI_IMAGE_MODELS || [])
    : (config?.GEMINI_TEXT_MODELS || []);

  const handleModelChange = (e) => {
    const newModel = e?.target?.value;
    data?.onUpdate?.({ model: newModel });
  };

  return (
    <div className={`node-card ${data.status === 'running' ? 'running' : ''}`}>
      <NodeResizer
        minWidth={280}
        minHeight={300}
        isVisible={selected}
        lineClassName={isImageModel ? "border-purple-500" : "border-blue-500"}
        handleClassName={`${isImageModel ? "bg-purple-500" : "bg-blue-500"} border-2 border-white rounded-full w-3 h-3`}
      />
      {data.status && data.status !== 'idle' && (
        <div className={`status-badge ${data.status}`}>
          {data.status}
        </div>
      )}
      {/* Header */}
      <div className={`node-header ${isImageModel ? 'purple' : 'blue'}`}>
        <div className="node-title">
          {isImageModel ? <ImageIcon size={16} color="#c084fc" /> : <Bot size={16} color="#60a5fa" />}
          <span className="node-title-text">{data.label}</span>
        </div>
        <div className="flex items-center gap-1">
          <button onClick={(e) => {
            e.stopPropagation();
            data.onRunPartial?.();
          }} className="delete-btn hover:text-green-400" title="Run Node & Descendants">
            <Play size={14} />
          </button>
          <button onClick={data.onDelete} className="delete-btn">
            <X size={14} />
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="node-content">
        {/* Model Selector */}
        <select
          className="bg-gray-900 border border-gray-700 text-xs text-gray-300 rounded p-1 w-full focus:outline-none focus:border-blue-500 mb-2"
          value={data.model || ""}
          onChange={handleModelChange}
        >
          <option value="" disabled>Select Model</option>
          {models.map(m => (
            <option key={m} value={m}>{m}</option>
          ))}
        </select>

        {/* Configuration Controls */}
        <div className="flex flex-col gap-2 mt-1 border-t border-gray-800 pt-2">
          {isImageModel ? (
            <div className="flex flex-col gap-1">
              <label className="text-[10px] text-gray-500 font-medium">Aspect Ratio</label>
              <select
                className="bg-gray-900 border border-gray-700 text-[10px] text-gray-300 rounded p-1 w-full focus:outline-none focus:border-purple-500"
                value={data.config?.aspect_ratio || "1:1"}
                onChange={(e) => data.onUpdate({ config: { ...data.config, aspect_ratio: e.target.value } })}
              >
                <option value="1:1">1:1 (Square)</option>
                <option value="16:9">16:9 (Landscape)</option>
                <option value="9:16">9:16 (Portrait)</option>
                <option value="4:3">4:3 (Standard)</option>
                <option value="3:4">3:4 (Portrait Standard)</option>
              </select>
            </div>
          ) : (
            <div className="flex flex-col gap-2">
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id={`grounding-${data.id}`}
                  className="rounded border-gray-700 bg-gray-900 text-blue-500 focus:ring-offset-0 focus:ring-0 w-3 h-3"
                  checked={data.config?.use_google_search || false}
                  onChange={(e) => data.onUpdate({ config: { ...data.config, use_google_search: e.target.checked } })}
                />
                <label htmlFor={`grounding-${data.id}`} className="text-[10px] text-gray-400 cursor-pointer select-none">
                  Google Search Grounding
                </label>
              </div>
              {(typeof data.model === 'string' && data.model?.includes?.('thinking')) && (
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id={`thinking-${data.id}`}
                    className="rounded border-gray-700 bg-gray-900 text-purple-500 focus:ring-offset-0 focus:ring-0 w-3 h-3"
                    checked={data.config?.include_thoughts !== false}
                    onChange={(e) => data.onUpdate({ config: { ...data.config, include_thoughts: e.target.checked } })}
                  />
                  <label htmlFor={`thinking-${data.id}`} className="text-[10px] text-gray-400 cursor-pointer select-none">
                    Show Thoughts
                  </label>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Dynamic content if we want to show preview or inputs */}
        {data.value && (
          <div className="node-value-box">
            {data.value}
          </div>
        )}
      </div>

      {/* Inputs */}
      <div className="flex flex-col gap-4 mt-2 border-t border-gray-800 pt-4">
        <div className="node-input-wrapper relative">
          <Handle
            type="target"
            position={Position.Left}
            id="text"
            isConnectable={isConnectable}
            className="node-handle input"
          />
          <span className="node-handle-label left">Text Input</span>
        </div>

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

        <div className="node-input-wrapper relative">
          <Handle
            type="target"
            position={Position.Left}
            id="other"
            isConnectable={isConnectable}
            className="node-handle input"
          />
          <span className="node-handle-label left">Other (Video/Audio)</span>
        </div>
      </div>

      {/* Outputs */}
      <div className="node-output-wrapper mt-4">
        <Handle
          type="source"
          position={Position.Right}
          id={isImageModel ? "image" : "text"}
          isConnectable={isConnectable}
          className="node-handle output"
        />
        <span className="node-handle-label right">
          {isImageModel ? "Image Output" : "Text Output"}
        </span>
      </div>
    </div>
  );
};

export default memo(GeminiNode);
