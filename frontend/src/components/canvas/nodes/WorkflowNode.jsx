import React, { memo, useState, useEffect, useCallback } from 'react';
import { Handle, Position, NodeResizer } from '@xyflow/react';
import { Workflow, X, RefreshCw, AlertCircle, Play } from 'lucide-react';

const WorkflowNode = ({ data, isConnectable, selected }) => {
  const [workflows, setWorkflows] = useState([]);
  const [selectedWorkflowId, setSelectedWorkflowId] = useState(data.workflow_id || '');
  const [workflowDetails, setWorkflowDetails] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchWorkflows = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch('/api/workflow/list');
      if (!response.ok) throw new Error('Failed to fetch workflows');
      const json = await response.json();
      setWorkflows(json.workflows || []);
    } catch (err) {
      console.error("Fetch error", err);
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchWorkflowDetails = useCallback(async (id) => {
    if (!id) {
      setWorkflowDetails(null);
      return;
    }
    try {
      const response = await fetch(`/api/workflow/${id}`);
      if (!response.ok) throw new Error('Failed to fetch workflow details');
      const json = await response.json();
      setWorkflowDetails(json);
    } catch (err) {
      console.error("Details fetch error", err);
      // Don't separate error state for details vs list for now, just log it
    }
  }, []);

  useEffect(() => {
    fetchWorkflows();
    if (data.workflow_id) {
      fetchWorkflowDetails(data.workflow_id);
    }
  }, [data.workflow_id, fetchWorkflowDetails]);

  const handleChange = (evt) => {
    const val = evt.target.value;
    setSelectedWorkflowId(val);
    fetchWorkflowDetails(val);

    const wf = workflows.find(w => w.id === val);
    const label = wf ? `Workflow: ${wf.name}` : 'Saved Workflow';

    if (data.onUpdate) {
      data.onUpdate({
        workflow_id: val,
        label: label
      });
    }
  };

  // Extract Input and Output nodes from the loaded workflow
  // Sort by Y position to maintain visual order from the original canvas
  const inputNodes = workflowDetails
    ? workflowDetails.nodes.filter(n => n.type === 'input').sort((a, b) => a.position.y - b.position.y)
    : [];
  const outputNodes = workflowDetails
    ? workflowDetails.nodes.filter(n => n.type === 'output').sort((a, b) => a.position.y - b.position.y)
    : [];

  return (
    <div className={`node-card ${data.status === 'running' ? 'running' : ''} border-orange-500 min-w-[280px]`}>
      <NodeResizer
        minWidth={280}
        minHeight={150}
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
          <Workflow size={16} className="text-orange-400" />
          <span className="node-title-text">{data.label || 'Saved Workflow'}</span>
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

      <div className="node-content p-3 flex flex-col gap-3">
        {/* Selector Section */}
        <div className="flex flex-col gap-2">
          <div className="flex items-center justify-between">
            <span className="text-[10px] text-gray-400 uppercase font-bold tracking-wider">Select Workflow</span>
            <button onClick={fetchWorkflows} className="p-1 hover:bg-gray-800 rounded text-gray-400 transition-colors" title="Refresh List">
              <RefreshCw size={10} className={isLoading ? "animate-spin" : ""} />
            </button>
          </div>

          {error ? (
            <div className="text-red-400 text-xs flex items-center gap-1 bg-red-900/20 p-2 rounded border border-red-900/50">
              <AlertCircle size={12} /> {error}
            </div>
          ) : (
            <select
              className="bg-gray-900 border border-gray-700 text-xs text-gray-300 rounded p-2 w-full focus:outline-none focus:border-orange-500 transition-colors"
              value={selectedWorkflowId}
              onChange={handleChange}
              disabled={isLoading}
            >
              <option value="">-- Select a Workflow --</option>
              {workflows.map(wf => (
                <option key={wf.id} value={wf.id}>
                  {wf.name} ({(new Date(wf.updated_at || Date.now())).toLocaleDateString()})
                </option>
              ))}
            </select>
          )}

          {selectedWorkflowId && (
            <div className="text-[9px] text-gray-600 font-mono">
              ID: {selectedWorkflowId.slice(0, 8)}...
            </div>
          )}
        </div>

        {/* Dynamic Handles Layout */}
        {(inputNodes.length > 0 || outputNodes.length > 0) ? (
          <div className="flex justify-between gap-4 mt-2 border-t border-gray-800 pt-3">
            {/* Inputs Column */}
            <div className="flex flex-col gap-3 w-1/2">
              <span className="text-[9px] text-gray-500 font-bold uppercase mb-1">Inputs</span>
              {inputNodes.map((node) => (
                <div key={node.id} className="relative flex items-center h-5 group">
                  {/* Handle is absolutely positioned relative to this row, but effectively aligned */}
                  <Handle
                    type="target"
                    position={Position.Left}
                    id={node.id}
                    isConnectable={isConnectable}
                    className="!w-3 !h-3 !bg-blue-500 !-left-[18px] border border-gray-900"
                  />
                  <span className="text-[10px] text-gray-300 truncate" title={node.data.label || 'Input'}>
                    {node.data.label || 'Input'}
                  </span>
                </div>
              ))}
            </div>

            {/* Outputs Column */}
            <div className="flex flex-col gap-3 w-1/2 items-end">
              <span className="text-[9px] text-gray-500 font-bold uppercase mb-1 text-right">Outputs</span>
              {outputNodes.map((node) => (
                <div key={node.id} className="relative flex items-center justify-end h-5 group w-full">
                  <span className="text-[10px] text-gray-300 truncate text-right" title={node.data.label || 'Output'}>
                    {node.data.label || 'Output'}
                  </span>
                  <Handle
                    type="source"
                    position={Position.Right}
                    id={node.id}
                    isConnectable={isConnectable}
                    className="!w-3 !h-3 !bg-green-500 !-right-[18px] border border-gray-900"
                  />
                </div>
              ))}
            </div>
          </div>
        ) : (
          /* Fallback / Default Handles if no detailed workflow loaded or empty */
          <div className="flex justify-between mt-2 pt-2 border-t border-gray-800">
            <div className="relative flex items-center h-5">
              <Handle type="target" position={Position.Left} id="input" isConnectable={isConnectable} className="!w-3 !h-3 !bg-gray-500 !-left-[18px]" />
              <span className="text-[10px] text-gray-500 italic ml-1">Default Input</span>
            </div>
            <div className="relative flex items-center h-5">
              <span className="text-[10px] text-gray-500 italic mr-1">Default Output</span>
              <Handle type="source" position={Position.Right} id="output" isConnectable={isConnectable} className="!w-3 !h-3 !bg-gray-500 !-right-[18px]" />
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default memo(WorkflowNode);
