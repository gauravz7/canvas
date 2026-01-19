import React, { memo } from 'react';
import { Handle, Position, NodeResizer } from '@xyflow/react';
import { Eye, Image as ImageIcon, X, Play } from 'lucide-react';

const OutputNode = ({ data, isConnectable, selected }) => {
  const renderContent = () => {
    try {
      if (!data.executionResult) {
        return (
          <div className="node-text-small italic text-gray-500">
            Waiting for execution...
          </div>
        );
      }

      const executionResult = data.executionResult;
      // Unwrap the ExecutionResult model if present
      const res = (executionResult && executionResult.output !== undefined)
        ? executionResult.output
        : executionResult;

      if (!res) {
        return <div className="node-text-small text-gray-600 italic">No output received</div>;
      }

      console.log("OutputNode Raw Data:", res); // DEBUG

      let processedRes = res;
      if (typeof res === 'string') {
        try {
          const parsed = JSON.parse(res);
          if (parsed && typeof parsed === 'object') {
            processedRes = parsed;
            console.log("OutputNode Parsed Data:", processedRes);
          }
        } catch (e) {
          // Not JSON, treat as string
        }
      }



      // 1. Audio Component Detection
      const hasStandardAudio = processedRes.audio && (processedRes.audio.data || processedRes.audio.url);
      const hasDirectAudio = (processedRes.data || processedRes.url) && processedRes.mime_type && typeof processedRes.mime_type === 'string' && processedRes.mime_type.toLowerCase().includes('audio');

      const showAudio = hasStandardAudio || hasDirectAudio;

      // 2. Video Component Detection
      const hasVideos = processedRes.videos && Array.isArray(processedRes.videos) && processedRes.videos.length > 0;

      // 3. Image Component Detection
      const hasImages = processedRes.images && Array.isArray(processedRes.images) && processedRes.images.length > 0;
      const isDirectImage = (typeof processedRes === 'string' && processedRes?.startsWith?.('data:image/'));

      // 4. Text Content (Only if NOT exclusively media)
      let textContent = "";
      if (typeof processedRes === 'string' && !isDirectImage) {
        textContent = processedRes;
      } else if (typeof processedRes === 'object' && processedRes !== null) {
        // Explicit text fields
        if (processedRes.text || processedRes.thoughts) {
          textContent = processedRes.text || processedRes.thoughts;
        }
        // If NO media found, dump JSON
        else if (!showAudio && !hasVideos && !hasImages && !isDirectImage) {
          textContent = JSON.stringify(processedRes, null, 2);
        }
      }

      return (
        <div className="flex flex-col gap-3">
          {/* Audio Section - Display FIRST if present */}
          {showAudio && (
            <div className="flex flex-col gap-2 bg-gray-900/50 p-2 rounded border border-gray-800">
              <span className="text-[10px] text-gray-500 font-medium">Audio Result:</span>
              <audio
                controls
                className="w-full h-8"
                src={
                  hasStandardAudio
                    ? (processedRes.audio.url || (processedRes.audio.data?.startsWith?.('data:') ? processedRes.audio.data : `data:${processedRes.audio.mime_type};base64,${processedRes.audio.data}`))
                    : (processedRes.url || (processedRes.data?.startsWith?.('data:') ? processedRes.data : `data:${processedRes.mime_type};base64,${processedRes.data}`))
                }
              />
            </div>
          )}

          {/* Image Section */}
          {hasImages && (
            <div className="flex flex-col gap-2">
              {processedRes.images.map((img, idx) => (
                <img
                  key={idx}
                  src={(typeof img.data === 'string' && img.data?.startsWith?.('data:')) ? img.data : (img.data ? `data:${img.mime_type};base64,${img.data}` : '')}
                  alt={`Generated ${idx}`}
                  className="node-file-preview"
                />
              ))}
            </div>
          )}
          {isDirectImage && (
            <img src={processedRes} alt="Direct Output" className="node-file-preview" />
          )}


          {/* Video Section */}
          {hasVideos && (
            <div className="flex flex-col gap-2">
              {processedRes.videos.map((vid, idx) => (
                <div key={idx} className="flex flex-col gap-1 bg-gray-900/50 p-2 rounded border border-gray-800">
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-[10px] text-gray-500 font-medium">Video Result {idx + 1}:</span>
                    {vid.url && (
                      <a
                        href={vid.url}
                        download={`video_${idx + 1}.mp4`}
                        className="text-[10px] text-blue-400 hover:text-blue-300 underline"
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        Download / External Link
                      </a>
                    )}
                  </div>
                  <video
                    controls
                    playsInline
                    autoPlay={false}
                    preload="metadata"
                    crossOrigin="anonymous"
                    className="w-full rounded bg-black aspect-video shadow-lg border border-orange-500/30"
                    src={vid.url ? vid.url : ((typeof vid.data === 'string' && vid.data?.startsWith?.('data:')) ? vid.data : (vid.data ? `data:${vid.mime_type};base64,${vid.data}` : ''))}
                    onError={(e) => {
                      console.error("Video load error:", e);
                      const msg = vid.url ? `Failed to load video. This might be a missing file or CORS issue. URL: ${vid.url}` : "Failed to load video data.";
                      e.target.insertAdjacentHTML('afterend', `<div class="text-[10px] text-red-500 mt-2 font-bold p-2 bg-red-900/10 rounded">${msg}</div>`);
                    }}
                  />
                  <div className="flex justify-center mt-2">
                    <span className="text-[10px] text-orange-400 animate-pulse">Click the play button to view</span>
                  </div>
                  {vid.uri && (
                    <div className="text-[8px] text-gray-600 truncate mt-1" title={vid.uri}>
                      URI: {vid.uri}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Text Section */}
          {textContent && (
            <div className="node-value-box whitespace-pre-wrap font-mono text-[10px]">
              {textContent}
            </div>
          )}

          {!hasImages && !isDirectImage && !textContent && !showAudio && !hasVideos && (
            <div className="node-text-small text-gray-600 italic">Empty output</div>
          )}
        </div>
      );
    } catch (err) {
      console.error("OutputNode render error:", err);
      return (
        <div className="text-red-500 text-[10px] p-2 bg-red-900/20 rounded">
          Render Error: {err.message}
        </div>
      );
    }
  };

  return (
    <div className={`node-card ${data.status === 'running' ? 'running' : ''}`}>
      <NodeResizer
        minWidth={280}
        minHeight={250}
        isVisible={selected}
        lineClassName="border-orange-500"
        handleClassName="bg-orange-500 border-2 border-white rounded-full w-3 h-3"
      />
      {data.status && data.status !== 'idle' && (
        <div className={`status-badge ${data.status}`}>
          {data.status}
        </div>
      )}
      <div className="node-header orange">
        <div className="node-title">
          <Eye size={16} color="#fb923c" />
          <span className="node-title-text">{data.label || "Output"}</span>
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

      <div className="node-input-wrapper" style={{ marginTop: '0.5rem', marginBottom: '0.5rem' }}>
        <Handle
          type="target"
          position={Position.Left}
          id="input"
          isConnectable={isConnectable}
          className="node-handle input"
        />
        <span className="node-handle-label left">Input</span>
      </div>

      <div className="node-content overflow-y-auto flex-1">
        <div className="node-text-small" style={{ marginBottom: '0.5rem' }}>Result:</div>
        {renderContent()}
      </div>
    </div>
  );
};

export default memo(OutputNode);
