import React, { memo, useState, useEffect } from 'react';
import { Handle, Position, NodeResizer, useEdges, useNodes } from '@xyflow/react';
import { Film, Mic, Music, X, ChevronUp, ChevronDown, Volume2, Play } from 'lucide-react';

const EditorNode = ({ id, data, isConnectable, selected }) => {
  const edges = useEdges();
  const nodes = useNodes();

  // Helper to get connected nodes for a specific target handle
  const getConnectedInfo = (handleId) => {
    return edges
      .filter(edge => edge.target === id && edge.targetHandle === handleId)
      .map(edge => {
        const sourceNode = nodes.find(n => n.id === edge.source);
        return {
          id: edge.source,
          label: sourceNode?.data?.label || sourceNode?.id || 'Unknown',
          type: sourceNode?.type
        };
      });
  };

  const videoNodes = getConnectedInfo('videos');
  const speechNodes = getConnectedInfo('speech');
  const bgNodes = getConnectedInfo('background');

  const config = data.config || {};
  const sequence = config.sequence || { videos: [], speech: [], background: [] };

  // Sync sequence with actual connections
  useEffect(() => {
    const syncSequence = (currentConnections, type) => {
      let newSeq = [...(sequence[type] || [])];
      
      // Remove nodes no longer connected
      newSeq = newSeq.filter(s => currentConnections.some(c => c.id === s.nodeId));
      
      // Add new connections
      currentConnections.forEach(c => {
        if (!newSeq.some(s => s.nodeId === c.id)) {
          newSeq.push({ nodeId: c.id, volume: type === 'background' ? 20 : 100, label: c.label });
        }
      });

      // Update labels if they changed
      newSeq = newSeq.map(s => {
        const conn = currentConnections.find(c => c.id === s.nodeId);
        return { ...s, label: conn?.label || s.label };
      });

      return newSeq;
    };

    const newVideoSeq = syncSequence(videoNodes, 'videos');
    const newSpeechSeq = syncSequence(speechNodes, 'speech');
    const newBgSeq = syncSequence(bgNodes, 'background');

    // Check if anything actually changed to avoid infinite loop
    const changed = 
      JSON.stringify(newVideoSeq) !== JSON.stringify(sequence.videos) ||
      JSON.stringify(newSpeechSeq) !== JSON.stringify(sequence.speech) ||
      JSON.stringify(newBgSeq) !== JSON.stringify(sequence.background);

    if (changed && data.onUpdate) {
      data.onUpdate({
        config: {
          ...config,
          sequence: {
              videos: newVideoSeq,
              speech: newSpeechSeq,
              background: newBgSeq
          }
        }
      });
    }
  }, [videoNodes.length, speechNodes.length, bgNodes.length, nodes]); // Watch nodes for label updates

  const updateSequence = (type, newItems) => {
    if (data.onUpdate) {
      data.onUpdate({
        config: {
          ...config,
          sequence: {
            ...sequence,
            [type]: newItems
          }
        }
      });
    }
  };

  const moveElement = (type, index, direction) => {
    const items = [...sequence[type]];
    const newIndex = index + direction;
    if (newIndex < 0 || newIndex >= items.length) return;
    
    const [movedItem] = items.splice(index, 1);
    items.splice(newIndex, 0, movedItem);
    updateSequence(type, items);
  };

  const updateVolume = (type, index, volume) => {
    const items = [...sequence[type]];
    items[index].volume = parseInt(volume);
    updateSequence(type, items);
  };

  const renderSequencer = (type, title, icon, colorClass) => {
    const items = sequence[type] || [];
    return (
      <div className="flex flex-col gap-2 mb-4">
        <div className="flex items-center gap-2 mb-1">
          {icon}
          <span className="text-[10px] font-bold uppercase text-gray-400 tracking-wider font-mono">{title}</span>
          <span className="ml-auto text-[9px] text-gray-600">{items.length} clips</span>
        </div>
        <div className="flex flex-col gap-1.5 min-h-[40px] bg-black/40 rounded-lg p-2 border border-white/5">
          {items.map((item, idx) => (
            <div key={`${type}-${item.nodeId}`} className="flex flex-col gap-1.5 p-2 bg-white/5 rounded-md border border-white/5 group hover:border-white/10 transition-colors">
              <div className="flex items-center gap-2">
                <span className="text-[10px] text-gray-300 font-medium truncate flex-1" title={item.label}>{item.label}</span>
                <div className="flex items-center gap-0.5 opacity-40 group-hover:opacity-100 transition-opacity">
                  <button 
                    onClick={() => moveElement(type, idx, -1)} 
                    disabled={idx === 0}
                    className="p-1 hover:bg-white/10 rounded disabled:opacity-20"
                  >
                    <ChevronUp size={12} />
                  </button>
                  <button 
                    onClick={() => moveElement(type, idx, 1)} 
                    disabled={idx === items.length - 1}
                    className="p-1 hover:bg-white/10 rounded disabled:opacity-20"
                  >
                    <ChevronDown size={12} />
                  </button>
                </div>
              </div>
              <div className="flex items-center gap-3 px-1">
                <Volume2 size={10} className="text-gray-500" />
                <input 
                  type="range"
                  min="0"
                  max="100"
                  value={item.volume}
                  onChange={(e) => updateVolume(type, idx, e.target.value)}
                  className="flex-1 h-1 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-indigo-500"
                />
                <span className="text-[9px] text-gray-500 w-6 text-right font-mono">{item.volume}%</span>
              </div>
            </div>
          ))}
          {items.length === 0 && (
            <div className="flex-1 flex items-center justify-center text-[9px] text-gray-600 italic py-2">
              Connect nodes to start sequencing
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className={`node-card ${data.status === 'running' ? 'running' : ''} border-indigo-500/50`}>
      <NodeResizer
        minWidth={320}
        minHeight={400}
        isVisible={selected}
        lineClassName="border-indigo-500"
        handleClassName="bg-indigo-500 border-2 border-white rounded-full w-3 h-3"
      />
      
      {data.status && data.status !== 'idle' && (
        <div className={`status-badge ${data.status}`}>
          {data.status}
        </div>
      )}

      <div className="node-header indigo" style={{ backgroundColor: 'rgba(99, 102, 241, 0.15)' }}>
        <div className="node-title">
          <Film size={16} className="text-indigo-400" />
          <span className="node-title-text">{data.label || 'Video Editor'}</span>
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

      <div className="node-content overflow-y-auto flex-1 p-3">
        {renderSequencer('videos', 'Video Sequence', <Film size={12} className="text-indigo-400" />, 'indigo')}
        {renderSequencer('speech', 'Speech Track', <Mic size={12} className="text-rose-400" />, 'rose')}
        {renderSequencer('background', 'Background Score', <Music size={12} className="text-emerald-400" />, 'emerald')}

        {/* Dynamic Handles */}
        <div className="flex flex-col gap-6 mt-4 border-t border-gray-800/50 pt-4 pb-2">
          <div className="node-input-wrapper relative">
            <Handle type="target" position={Position.Left} id="videos" isConnectable={isConnectable} className="!bg-indigo-500" />
            <span className="node-handle-label left">Videos</span>
          </div>
          <div className="node-input-wrapper relative">
            <Handle type="target" position={Position.Left} id="speech" isConnectable={isConnectable} className="!bg-rose-500" />
            <span className="node-handle-label left">Speech</span>
          </div>
          <div className="node-input-wrapper relative">
            <Handle type="target" position={Position.Left} id="background" isConnectable={isConnectable} className="!bg-emerald-500" />
            <span className="node-handle-label left">Score</span>
          </div>
        </div>

        <div className="node-output-wrapper mt-4">
          <Handle
            type="source"
            position={Position.Right}
            id="video"
            isConnectable={isConnectable}
            className="!bg-green-500"
          />
          <span className="node-handle-label right">Mixed Output</span>
        </div>
      </div>
    </div>
  );
};

export default memo(EditorNode);
