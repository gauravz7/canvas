import React, { useState, useCallback, useRef } from 'react';
import { createPortal } from 'react-dom';
import { ReactFlow, Background, useNodesState, useEdgesState, addEdge, useReactFlow } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import './Canvas.css';
import GeminiNode from './nodes/GeminiNode';
import InputNode from './nodes/InputNode';
import OutputNode from './nodes/OutputNode';
import UpscaleNode from './nodes/UpscaleNode';
import SpeechNode from './nodes/SpeechNode';
import VeoNode from './nodes/VeoNode';
import MusicNode from './nodes/MusicNode';
import EditorNode from './nodes/EditorNode';
import Toolbar from './Toolbar';
import { Plus, Minus, Maximize, ZoomIn, ZoomOut } from 'lucide-react';

import { v4 as uuidv4 } from 'uuid';

const CustomControls = () => {
  const { zoomIn, zoomOut, fitView } = useReactFlow();

  return (
    <div className="absolute bottom-4 left-4 flex flex-col gap-1 bg-black/60 backdrop-blur-md border border-white/10 rounded-lg p-1 shadow-xl z-50">
      <button onClick={() => zoomIn()} className="p-2 hover:bg-white/10 rounded transition-colors text-white" title="Zoom In">
        <ZoomIn size={16} />
      </button>
      <button onClick={() => zoomOut()} className="p-2 hover:bg-white/10 rounded transition-colors text-white" title="Zoom Out">
        <ZoomOut size={16} />
      </button>
      <button onClick={() => fitView()} className="p-2 hover:bg-white/10 rounded transition-colors text-white" title="Fit View">
        <Maximize size={16} />
      </button>
    </div>
  );
};

const nodeTypes = {
  gemini_text: GeminiNode,
  gemini_image: GeminiNode,
  input: InputNode,
  output: OutputNode,
  imagen_upscale: UpscaleNode,
  speech_gen: SpeechNode,
  lyria_gen: MusicNode,
  veo_standard: VeoNode,
  veo_extend: VeoNode,
  veo_reference: VeoNode,
  editor: EditorNode,
};

const CanvasPage = () => {
  React.useEffect(() => {
    console.log("CanvasPage mounted - nodeTypes:", Object.keys(nodeTypes));
  }, []);
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [isRunning, setIsRunning] = useState(false);
  const [useCache, setUseCache] = useState(false);
  const [currentExecutionId, setCurrentExecutionId] = useState(null);
  const [reactFlowInstance, setReactFlowInstance] = useState(null);
  const reactFlowWrapper = useRef(null);
  const fileInputRef = useRef(null);

  // Refs to hold latest state for callbacks stored in node data
  const edgesRef = useRef(edges);
  const nodesRef = useRef(nodes);

  // Update refs on render
  edgesRef.current = edges;
  nodesRef.current = nodes;

  // Load Sample Workflow on Mount if empty or check for pending load
  React.useEffect(() => {
    const pendingLoad = localStorage.getItem('pending_workflow_load');
    if (pendingLoad) {
      try {
        const flow = JSON.parse(pendingLoad);
        if (flow.nodes && flow.edges) {
          setNodes(flow.nodes);
          setEdges(flow.edges);
          // Auto-trigger fitView after a short delay
          setTimeout(() => {
            if (reactFlowInstance) reactFlowInstance.fitView();
          }, 100);
        }
        localStorage.removeItem('pending_workflow_load');
        return; // Don't load sample if we loaded a pending one
      } catch (e) {
        console.error("Failed to load pending workflow", e);
        localStorage.removeItem('pending_workflow_load');
      }
    }

    if (nodes.length === 0) {
      // Sample Workflow
      const sampleNodes = [
        { id: '1', type: 'gemini_text', position: { x: 100, y: 100 }, data: { label: 'Start Idea', value: 'Explain quantum computing in 5 words' } },
        { id: '2', type: 'speech_gen', position: { x: 500, y: 100 }, data: { label: 'Narrate' } },
        { id: '3', type: 'output', position: { x: 900, y: 100 }, data: { label: 'Audio Output', outputType: 'audio' } }
      ];
      const sampleEdges = [
        { id: 'e1-2', source: '1', target: '2' },
        { id: 'e2-3', source: '2', target: '3' }
      ];
      setNodes(sampleNodes);
      setEdges(sampleEdges);
    }
  }, [reactFlowInstance]);

  const controlStyles = `
  #canvas-controls-wrapper .react-flow__controls {
    background: #1e1e1e !important;
    background-color: #1e1e1e !important;
    box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.1) !important;
    border-radius: 8px !important;
    overflow: hidden !important;
    z-index: 9999 !important;
  }
  #canvas-controls-wrapper .react-flow__controls button {
    background: transparent !important;
    border: none !important;
    border-bottom: 1px solid #333 !important;
    border-radius: 0 !important;
    width: 30px !important;
    height: 30px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
  }
  #canvas-controls-wrapper .react-flow__controls button:hover {
    background: rgba(255, 255, 255, 0.1) !important;
  }
  #canvas-controls-wrapper .react-flow__controls button svg {
    fill: #ffffff !important;
    stroke: #ffffff !important;
    color: #ffffff !important;
    width: 16px !important;
    height: 16px !important;
  }
  #canvas-controls-wrapper .react-flow__controls button svg path {
    fill: #ffffff !important;
    stroke: #ffffff !important;
  }
  `;


  const onConnect = useCallback(
    (params) => setEdges((eds) => addEdge(params, eds)),
    [setEdges],
  );

  const onDragOver = useCallback((event) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  const onDrop = useCallback(
    (event) => {
      event.preventDefault();

      const type = event.dataTransfer.getData('application/reactflow');
      const subtype = event.dataTransfer.getData('application/reactflow-subtype') || 'text';
      if (typeof type === 'undefined' || !type) {
        return;
      }

      const position = reactFlowWrapper.current.getBoundingClientRect();
      const clientX = event.clientX - position.left;
      const clientY = event.clientY - position.top;

      const id = uuidv4();
      let label = '';
      if (type === 'gemini_text') label = 'Gemini Text';
      else if (type === 'gemini_image') label = 'Gemini Image';
      else if (type === 'input') label = subtype === 'image' ? 'Image Input' : subtype === 'video' ? 'Video Input' : subtype === 'audio' ? 'Audio Input' : 'Text Input';
      else if (type === 'output') {
        if (subtype === 'image') label = 'Image Output';
        else if (subtype === 'video') label = 'Video Output';
        else if (subtype === 'audio') label = 'Audio Output';
        else label = 'Text Output';
      }
      else if (type === 'imagen_upscale') label = 'Image Upscaler';
      else if (type === 'speech_gen') label = 'Speech Gen';
      else if (type === 'lyria_gen') label = 'Lyria Music';
      else if (type === 'veo_standard') label = 'Veo Standard';
      else if (type === 'veo_extend') label = 'Veo Extend';
      else if (type === 'veo_reference') label = 'Veo Reference';
      else if (type === 'editor') label = 'Video Editor';
      else label = 'Node';

      const newNode = {
        id,
        type,
        position: { x: clientX, y: clientY },
        data: {
          label,
          type,
          inputType: type === 'input' ? subtype : undefined,
          outputType: type === 'output' ? subtype : undefined,
          value: '',
          model: '',
          onUpdate: (updates) => {
            setNodes((nds) => nds.map((node) => {
              if (node.id === id) {
                return { ...node, data: { ...node.data, ...updates } };
              }
              return node;
            }));
          },
          onDelete: () => handleDeleteNode(id),
          onRunPartial: () => handlePartialRun(id),
          onChange: (val) => {
            setNodes((nds) => nds.map((node) => {
              if (node.id === id) {
                return { ...node, data: { ...node.data, value: val } };
              }
              return node;
            }));
          }
        },
      };

      setNodes((nds) => nds.concat(newNode));
    },
    [setNodes, edges], // Added edges dependency for partial run calculation
  );

  const onDragStart = (event, nodeType, subtype = 'text') => {
    event.dataTransfer.setData('application/reactflow', nodeType);
    event.dataTransfer.setData('application/reactflow-subtype', subtype);
    event.dataTransfer.effectAllowed = 'move';
  };

  const handleAddNode = (type, subtype = 'text') => {
    const id = uuidv4();
    const position = {
      x: Math.random() * 400 + 100,
      y: Math.random() * 200 + 100,
    };

    // Default label based on type/subtype
    let label = '';
    if (type === 'gemini_text') label = 'Gemini Text';
    else if (type === 'gemini_image') label = 'Gemini Image';
    else if (type === 'input') label = subtype === 'image' ? 'Image Input' : subtype === 'video' ? 'Video Input' : subtype === 'audio' ? 'Audio Input' : 'Text Input';
    else if (type === 'output') {
      if (subtype === 'image') label = 'Image Output';
      else if (subtype === 'video') label = 'Video Output';
      else if (subtype === 'audio') label = 'Audio Output';
      else label = 'Text Output';
    }
    else if (type === 'imagen_upscale') label = 'Image Upscaler';
    else if (type === 'speech_gen') label = 'Speech Gen';
    else if (type === 'lyria_gen') label = 'Lyria Music';
    else if (type === 'veo_standard') label = 'Veo Standard';
    else if (type === 'veo_extend') label = 'Veo Extend';
    else if (type === 'veo_reference') label = 'Veo Reference';
    else if (type === 'editor') label = 'Video Editor';
    else label = 'Node';

    const newNode = {
      id,
      type,
      position,
      data: {
        label,
        type,
        inputType: type === 'input' ? subtype : undefined,
        outputType: type === 'output' ? subtype : undefined,
        value: '',
        model: '', // For Gemini nodes
        // Generic update handler
        onUpdate: (updates) => {
          setNodes((nds) => nds.map((node) => {
            if (node.id === id) {
              return { ...node, data: { ...node.data, ...updates } };
            }
            return node;
          }));
        },
        onDelete: () => handleDeleteNode(id),
        onRunPartial: () => handlePartialRun(id),
        onChange: (val) => {
          setNodes((nds) => nds.map((node) => {
            if (node.id === id) {
              return { ...node, data: { ...node.data, value: val } };
            }
            return node;
          }));
        }
      },
    };

    setNodes((nds) => nds.concat(newNode));
  };

  const handleDeleteNode = (id) => {
    setNodes((nds) => nds.filter((node) => node.id !== id));
    setEdges((eds) => eds.filter((edge) => edge.source !== id && edge.target !== id));
  };

  const handlePartialRun = useCallback((startNodeId) => {
    // BFS to find all downstream nodes
    const downstreamIds = new Set([startNodeId]);
    const queue = [startNodeId];
    const currentEdges = edgesRef.current;

    while (queue.length > 0) {
      const currentId = queue.shift();
      // Find edges where source is currentId
      const childEdges = currentEdges.filter(e => e.source === currentId);
      childEdges.forEach(edge => {
        if (!downstreamIds.has(edge.target)) {
          downstreamIds.add(edge.target);
          queue.push(edge.target);
        }
      });
    }

    handleRun(Array.from(downstreamIds));
  }, []); // Empty deps as we use refs for state access

  const handleRun = async (nodeIds = null) => {
    if (isRunning) {
      console.warn("Already running, skipping run request");
      return;
    }

    // Normalize nodeIds: if it's not an array (e.g. MouseEvent), treat as null (run all)
    const runNodeIds = Array.isArray(nodeIds) ? nodeIds : null;
    const currentNodes = nodesRef.current;
    const currentEdges = edgesRef.current;

    setIsRunning(true);
    const executionId = uuidv4();
    setCurrentExecutionId(executionId);

    // Reset status and results for nodes being run
    setNodes((nds) =>
      nds.map((node) => {
        const shouldRun = !runNodeIds || (Array.isArray(runNodeIds) && runNodeIds.includes(node.id));
        if (shouldRun) {
          return {
            ...node,
            data: { ...node.data, status: 'idle', executionResult: null },
          };
        }
        return node;
      })
    );

    try {
      // Use proxy or full URL
      const response = await fetch('/api/workflow/execute/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          workflow: {
            id: "workflow-" + uuidv4(),
            name: "Untitled Workflow",
            nodes: currentNodes.map(n => {
              const { onUpdate, onDelete, onRunPartial, onChange, ...cleanData } = n.data;
              return {
                id: n.id,
                type: n.type,
                position: n.position,
                data: cleanData
              };
            }),
            edges: currentEdges.map(e => ({
              id: e.id,
              source: e.source,
              target: e.target,
              sourceHandle: e.sourceHandle,
              targetHandle: e.targetHandle
            }))
          },
          node_ids: runNodeIds,
          use_cache: useCache,
          execution_id: executionId
        }),
      });

      if (!response.ok) throw new Error(`Execution failed: ${response.statusText} `);

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n\n');
        buffer = lines.pop();

        for (const line of lines) {
          const trimmedLine = line.trim();
          if (!trimmedLine || typeof trimmedLine !== 'string' || !trimmedLine?.startsWith?.('data: ')) continue;

          try {
            const dataStr = trimmedLine.slice(6);
            if (dataStr === '[DONE]') break;

            const data = JSON.parse(dataStr);

            if (data.type === 'node_started') {
              setNodes((nds) =>
                nds.map((n) =>
                  n.id === data.node_id
                    ? { ...n, data: { ...n.data, status: 'running' } }
                    : n
                )
              );
            } else if (data.type === 'node_completed' || data.type === 'node_completed_cache' || data.type === 'node_failed') {
              const isCache = data.type === 'node_completed_cache';
              setNodes((nds) =>
                nds.map((n) =>
                  n.id === data.node_id
                    ? {
                      ...n,
                      data: {
                        ...n.data,
                        status: data.type === 'node_failed' ? 'failed' : 'completed',
                        executionResult: data.result,
                        // If it was cached, we might want to indicate it, but 'completed' is fine
                      },
                    }
                    : n
                )
              );
              if (isCache) console.log(`Node ${data.node_id} used cache`);
            } else if (data.type === 'workflow_completed' || data.type === 'execution_cancelled') {
              setIsRunning(false);
              setCurrentExecutionId(null);
            }
          } catch (e) {
            console.error("Failed to parse SSE event:", trimmedLine, e);
          }
        }
      }
    } catch (error) {
      console.error('Execution Error:', error);
      setIsRunning(false);
      setCurrentExecutionId(null);
      alert('Execution error: ' + error.message);
    }
  };

  const handleKill = async () => {
    if (!currentExecutionId) return;
    try {
      const response = await fetch(`/api/workflow/execute/cancel/${currentExecutionId}`, {
        method: 'POST'
      });
      if (!response.ok) {
        throw new Error('Kill request failed');
      }
      console.log('Kill signal sent for:', currentExecutionId);
    } catch (error) {
      console.error('Kill Error:', error);
    }
  };

  const handleSave = async () => {
    try {
      const flow = reactFlowInstance.toObject();
      const response = await fetch('/api/workflow/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(flow)
      });
      if (response.ok) {
        alert('Workflow saved!');
      } else {
        alert('Save failed');
      }
    } catch (error) {
      alert('Save error: ' + error);
    }
  };

  const handleExport = () => {
    const includeMedia = window.confirm("Include media (images, videos, voice) in the export? \n\nChoose 'Cancel' for a lightweight JSON (no images/videos/voice) for sharing.");

    // Create a deep-ish clone that strips functions
    const cleanNodes = nodes.map(node => {
      const cleanData = { ...node.data };

      // Strip functions and internal non-serializable refs
      delete cleanData.onUpdate;
      delete cleanData.onDelete;
      delete cleanData.onRunPartial;
      delete cleanData.onChange;

      if (!includeMedia) {
        // Strip execution results and large values
        delete cleanData.executionResult;
        delete cleanData.status;

        if (typeof cleanData.value === 'string' && (cleanData.value.startsWith('data:') || cleanData.value.length > 500)) {
          cleanData.value = "";
        }

        if (node.type === 'input') {
          delete cleanData.fileName;
          delete cleanData.lastRun;
        }
      }

      return {
        ...node,
        data: cleanData
      };
    });

    const exportData = {
      nodes: cleanNodes,
      edges: edges.map(e => ({
        id: e.id,
        source: e.source,
        target: e.target,
        sourceHandle: e.sourceHandle,
        targetHandle: e.targetHandle
      }))
    };

    try {
      const jsonString = JSON.stringify(exportData, null, 2);
      const blob = new Blob([jsonString], { type: 'application/json' });
      const url = URL.createObjectURL(blob);

      const downloadAnchorNode = document.createElement('a');
      const fileName = includeMedia ? "workflow_full.json" : "workflow_light.json";

      downloadAnchorNode.setAttribute("href", url);
      downloadAnchorNode.setAttribute("download", fileName);
      document.body.appendChild(downloadAnchorNode);
      downloadAnchorNode.click();
      downloadAnchorNode.remove();

      // Revoke the object URL after a delay to free memory
      setTimeout(() => URL.revokeObjectURL(url), 100);
    } catch (err) {
      console.error("Export failed:", err);
      alert("Export failed: " + err.message);
    }
  };

  const handleImport = (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const flow = JSON.parse(e.target.result);
        if (flow.nodes && flow.edges) {
          setNodes(flow.nodes || []);
          setEdges(flow.edges || []);
          alert('Workflow imported!');
        } else {
          alert('Invalid workflow JSON');
        }
      } catch (err) {
        alert('Import failed: ' + err);
      }
    };
    reader.readAsText(file);
  };

  return (
    <div className="canvas-page">
      <style>{controlStyles}</style>
      <div className="canvas-container" ref={reactFlowWrapper}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onDragOver={onDragOver}
          onDrop={onDrop}
          onInit={setReactFlowInstance}
          nodeTypes={nodeTypes}
          fitView
          className="bg-black"
          style={{ backgroundColor: 'black' }}
        >
          <Background color="#333" gap={16} />
          <CustomControls />
        </ReactFlow>

        <Toolbar
          onDragStart={onDragStart}
          onAddNode={handleAddNode}
          onRun={handleRun}
          onKill={handleKill}
          onSave={handleSave}
          onImport={handleImport}
          onExport={handleExport}
          isRunning={isRunning}
          useCache={useCache}
          setUseCache={setUseCache}
        />
      </div>

    </div>
  );
};

export default CanvasPage;
