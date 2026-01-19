import React, { memo, useState } from 'react';
import { Handle, Position, NodeResizer } from '@xyflow/react';
import { FileText, Image as ImageIcon, X, Play } from 'lucide-react';

const InputNode = ({ data, isConnectable, selected }) => {
  const [value, setValue] = useState(data.value || '');
  const [inputType, setInputType] = useState(data.inputType || 'text');

  const isImage = inputType === 'image';
  const isVideo = inputType === 'video';
  const isAudio = inputType === 'audio';
  const isText = inputType === 'text';

  const renderPreview = () => {
    if (!value) return null;
    if (isImage) return <img src={value} alt="Preview" className="node-file-preview" />;
    if (isVideo) return <video src={value} controls className="node-file-preview h-32" />;
    if (isAudio) return <audio src={value} controls className="w-full mt-2" />;
    return null;
  };

  const handleChange = (evt) => {
    const val = evt.target.value;
    setValue(val);
    if (data.onUpdate) data.onUpdate({ value: val });
  };

  const handleTypeChange = (e) => {
    const newType = e.target.value;
    setInputType(newType);
    // Persist new type and potentially update label if it was default
    const label = newType.charAt(0).toUpperCase() + newType.slice(1) + " Input";
    if (data.onUpdate) {
      data.onUpdate({ inputType: newType, label: label });
    }
  };

  const handleFileChange = (evt) => {
    const file = evt.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const val = e.target.result;
        setValue(val);
        if (data.onUpdate) data.onUpdate({ value: val, fileName: file.name, mimeType: file.type });
      };
      reader.readAsDataURL(file);
    }
  };

  const getHeaderColor = () => {
    if (isText) return 'green';
    return 'purple';
  };

  return (
    <div className={`node-card ${data.status === 'running' ? 'running' : ''}`}>
      <NodeResizer
        minWidth={250}
        minHeight={200}
        isVisible={selected}
        lineClassName="border-green-500"
        handleClassName="bg-green-500 border-2 border-white rounded-full w-3 h-3"
      />
      {data.status && data.status !== 'idle' && (
        <div className={`status-badge ${data.status}`}>
          {data.status}
        </div>
      )}
      <div className={`node-header ${getHeaderColor()}`}>
        <div className="node-title">
          {isText ? <FileText size={16} color="#4ade80" /> : <ImageIcon size={16} color="#c084fc" />}
          <span className="node-title-text">{data.label || `${inputType.charAt(0).toUpperCase() + inputType.slice(1)} Input`}</span>
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
        {/* Modality Selector */}
        <select
          className="bg-gray-900 border border-gray-700 text-[10px] text-gray-300 rounded p-1 w-full focus:outline-none focus:border-green-500 mb-2"
          value={inputType}
          onChange={handleTypeChange}
        >
          <option value="text">Text / Prompt</option>
          <option value="image">Image File</option>
          <option value="video">Video File</option>
          <option value="audio">Audio File</option>
        </select>

        {isText ? (
          <textarea
            className="node-input-field"
            value={value}
            onChange={handleChange}
            placeholder="Enter prompt..."
            rows={3}
          />
        ) : (
          <div className="flex flex-col gap-2">
            <input
              type="file"
              accept={isImage ? "image/*" : isVideo ? "video/*" : isAudio ? "audio/*" : "*/*"}
              onChange={handleFileChange}
              className="text-[10px] text-gray-400 file:mr-2 file:py-1 file:px-2 file:rounded file:border-0 file:text-[10px] file:bg-gray-800 file:text-gray-300 hover:file:bg-gray-700"
            />
            {renderPreview()}
          </div>
        )}
      </div>

      <div className="node-output-wrapper">
        <Handle
          type="source"
          position={Position.Right}
          id="output"
          isConnectable={isConnectable}
          className="node-handle output"
        />
        <span className="node-handle-label right">Output</span>
      </div>
    </div>
  );
};

export default memo(InputNode);
