import React, { memo, useState } from 'react';
import { Handle, Position, NodeResizer } from '@xyflow/react';
import { Mic, X, Play, ChevronDown, ChevronUp } from 'lucide-react';
import { useConfig } from '../../../contexts/ConfigContext';

const SpeechNode = ({ data, isConnectable, selected }) => {
  const { config } = useConfig();
  const [showAdvanced, setShowAdvanced] = useState(false);

  const voices = config?.TTS_VOICES || ["Kore", "Leda", "Puck", "Charon", "Fenrir", "Aoede"];
  const models = config?.TTS_MODELS || ["gemini-3.1-flash-tts-preview"];
  const languages = config?.TTS_LANGUAGES || [{ code: "en", name: "English" }];

  const handleConfigChange = (key, value) => {
    if (data.onUpdate) {
      data.onUpdate({ config: { ...data.config, [key]: value } });
    }
  };

  return (
    <div className={`node-card ${data.status === 'running' ? 'running' : ''}`}>
      <NodeResizer
        minWidth={250}
        minHeight={250}
        isVisible={selected}
        lineClassName="border-green-500"
        handleClassName="bg-green-500 border-2 border-white rounded-full w-3 h-3"
      />
      {data.status && data.status !== 'idle' && (
        <div className={`status-badge ${data.status}`}>
          {data.status}
        </div>
      )}
      <div className="node-header green">
        <div className="node-title">
          <Mic size={16} color="#4ade80" />
          <span className="node-title-text">{data.label || 'Speech Gen'}</span>
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
          <div className="flex flex-col gap-1">
            <label className="text-[10px] text-gray-500 font-medium">Model</label>
            <select
              className="bg-gray-900 border border-gray-700 text-[10px] text-gray-300 rounded p-1 w-full focus:outline-none focus:border-green-500"
              value={data.config?.model_id || config?.DEFAULT_TTS_MODEL || 'gemini-3.1-flash-tts-preview'}
              onChange={(e) => handleConfigChange('model_id', e.target.value)}
            >
              {models.map(m => (
                <option key={m} value={m}>{m}</option>
              ))}
            </select>
          </div>

          <div className="flex flex-col gap-1">
            <label className="text-[10px] text-gray-500 font-medium">Voice</label>
            <select
              className="bg-gray-900 border border-gray-700 text-[10px] text-gray-300 rounded p-1 w-full focus:outline-none focus:border-green-500"
              value={data.config?.voice_name || config?.DEFAULT_TTS_VOICE || 'Kore'}
              onChange={(e) => handleConfigChange('voice_name', e.target.value)}
            >
              {voices.map(v => (
                <option key={v} value={v}>{v}</option>
              ))}
            </select>
          </div>

          <div className="flex flex-col gap-1">
            <label className="text-[10px] text-gray-500 font-medium">Language</label>
            <select
              className="bg-gray-900 border border-gray-700 text-[10px] text-gray-300 rounded p-1 w-full focus:outline-none focus:border-green-500"
              value={data.config?.language || config?.DEFAULT_TTS_LANGUAGE || 'en'}
              onChange={(e) => handleConfigChange('language', e.target.value)}
            >
              {languages.map(l => (
                <option key={l.code} value={l.code}>{l.name}</option>
              ))}
            </select>
          </div>

          <div>
            <button
              onClick={() => setShowAdvanced(!showAdvanced)}
              className="flex items-center gap-1 text-[10px] text-gray-500 hover:text-gray-300 transition-colors"
            >
              {showAdvanced ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
              System Instruction
            </button>
            {showAdvanced && (
              <textarea
                className="w-full mt-1 bg-gray-900 border border-gray-700 text-[10px] text-gray-300 rounded p-1.5 resize-none focus:outline-none focus:border-green-500"
                rows={3}
                placeholder="e.g. Speak cheerfully and with enthusiasm..."
                value={data.config?.system_instruction || ''}
                onChange={(e) => handleConfigChange('system_instruction', e.target.value)}
              />
            )}
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
        <span className="node-handle-label left">Text Input</span>
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

export default memo(SpeechNode);
