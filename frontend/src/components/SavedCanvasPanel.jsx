import React, { useState, useEffect } from 'react';
import { 
  Library, 
  Play, 
  Settings2, 
  Image as ImageIcon, 
  Type, 
  Video, 
  Music, 
  ChevronRight,
  Loader2,
  Trash2,
  ExternalLink,
  Save
} from 'lucide-react';

const SavedCanvasPanel = ({ userId, onSwitchToCanvas }) => {
  const [examples, setExamples] = useState([]);
  const [savedWorkflows, setSavedWorkflows] = useState([]);
  const [selectedWorkflow, setSelectedWorkflow] = useState(null);
  const [loading, setLoading] = useState(false);
  const [isRunning, setIsRunning] = useState(false);
  const [inputs, setInputs] = useState({});
  const [results, setResults] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      // Fetch examples
      const exRes = await fetch('/api/workflow/templates/examples');
      if (exRes.ok) {
        const data = await exRes.json();
        setExamples(data.workflows);
      }

      // Fetch saved
      const savedRes = await fetch(`/api/workflow/list?user_id=${userId}`);
      if (savedRes.ok) {
        const data = await savedRes.json();
        setSavedWorkflows(data.workflows);
      }
    } catch (err) {
      console.error("Failed to fetch workflows", err);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectWorkflow = async (wfSummary, isExample = false) => {
    setLoading(true);
    setResults(null);
    try {
      let workflowData;
      if (isExample) {
        workflowData = examples.find(e => e.id === wfSummary.id);
      } else {
        const res = await fetch(`/api/workflow/${wfSummary.id}`);
        if (res.ok) {
          workflowData = await res.json();
        }
      }

      if (workflowData) {
        setSelectedWorkflow(workflowData);
        // Initialize inputs from input nodes
        const initialInputs = {};
        workflowData.nodes.forEach(node => {
          if (node.type === 'input') {
            initialInputs[node.id] = node.data.value || '';
          }
        });
        setInputs(initialInputs);
      }
    } catch (err) {
      console.error("Failed to load workflow detail", err);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (nodeId, value) => {
    setInputs(prev => ({ ...prev, [nodeId]: value }));
  };

  const handleFileUpload = (nodeId, file) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      handleInputChange(nodeId, e.target.result);
    };
    reader.readAsDataURL(file);
  };

  const handleRun = async () => {
    if (!selectedWorkflow) return;
    setIsRunning(true);
    setResults(null);

    try {
      // Prepare workflow for execution with current inputs
      const workflowToRun = {
        ...selectedWorkflow,
        nodes: selectedWorkflow.nodes.map(node => {
          if (node.type === 'input' && inputs[node.id] !== undefined) {
             return {
               ...node,
               data: { ...node.data, value: inputs[node.id] }
             };
          }
          return node;
        })
      };

      const response = await fetch('/api/workflow/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          workflow: workflowToRun,
          use_cache: true
        })
      });

      if (response.ok) {
        const data = await response.json();
        setResults(data.results);
      } else {
        alert("Execution failed");
      }
    } catch (err) {
      console.error("Run error", err);
      alert("Error: " + err.message);
    } finally {
      setIsRunning(false);
    }
  };

  const renderInputFields = () => {
    if (!selectedWorkflow) return null;

    const inputNodes = selectedWorkflow.nodes.filter(n => n.type === 'input');
    
    return (
      <div className="space-y-6">
        <h3 className="text-lg font-semibold flex items-center gap-2 text-white-90">
          <Settings2 size={20} className="text-blue-400" />
          Configure Inputs
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {inputNodes.map(node => (
            <div key={node.id} className="p-4 rounded-xl bg-white-5 border border-white-10 hover:border-white-20 transition-all">
              <label className="block text-xs font-bold text-white-40 uppercase tracking-wider mb-2">
                {node.data.label}
              </label>
              
              {node.data.inputType === 'text' ? (
                <textarea
                  value={inputs[node.id] || ''}
                  onChange={(e) => handleInputChange(node.id, e.target.value)}
                  className="w-full bg-black-20 border border-white-10 rounded-lg p-3 text-sm text-white-90 focus:ring-1 focus:ring-blue-500/50 outline-none transition-all h-24 resize-none"
                  placeholder="Enter text..."
                />
              ) : (
                <div className="space-y-3">
                  <div className="flex items-center gap-3">
                    <input
                      type="file"
                      id={`file-${node.id}`}
                      className="hidden"
                      onChange={(e) => handleFileUpload(node.id, e.target.files[0])}
                      accept={node.data.inputType === 'image' ? 'image/*' : node.data.inputType === 'video' ? 'video/*' : '*'}
                    />
                    <label
                      htmlFor={`file-${node.id}`}
                      className="flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-lg bg-blue-500/10 hover:bg-blue-500/20 text-blue-400 text-sm font-semibold border border-blue-500/20 cursor-pointer transition-all"
                    >
                      <ImageIcon size={18} />
                      Upload {node.data.inputType}
                    </label>
                  </div>
                  {inputs[node.id] && inputs[node.id].startsWith('data:') && (
                    <div className="relative aspect-video rounded-lg overflow-hidden border border-white-10">
                      <img src={inputs[node.id]} className="w-full h-full object-contain" alt="Preview" />
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>

        <div className="flex gap-4 pt-4">
          <button
            onClick={handleRun}
            disabled={isRunning}
            className="flex-1 flex items-center justify-center gap-2 py-4 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold shadow-lg shadow-blue-900/20 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isRunning ? (
              <>
                <Loader2 size={20} className="animate-spin" />
                Executing Template...
              </>
            ) : (
              <>
                <Play size={20} fill="currentColor" />
                Run with New Inputs
              </>
            )}
          </button>
          
          <button
             onClick={() => {
                // We'll need a way to pass the workflow to CanvasPage
                // For now, let's use localStorage as a bridge
                localStorage.setItem('pending_workflow_load', JSON.stringify({
                    ...selectedWorkflow,
                    nodes: selectedWorkflow.nodes.map(node => {
                        if (node.type === 'input' && inputs[node.id] !== undefined) {
                            return { ...node, data: { ...node.data, value: inputs[node.id] } };
                        }
                        return node;
                    })
                }));
                onSwitchToCanvas();
             }}
             className="px-6 py-4 rounded-xl bg-white-5 hover:bg-white-10 text-white font-semibold border border-white-10 transition-all"
          >
            Open in Canvas
          </button>
        </div>
      </div>
    );
  };

  const renderResults = () => {
    if (!results) return null;

    // Filter output nodes
    const outputResults = Object.entries(results).filter(([id, res]) => {
        const node = selectedWorkflow.nodes.find(n => n.id === id);
        return node && node.type === 'output';
    });

    return (
      <div className="mt-8 space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
        <div className="flex items-center justify-between border-b border-white-10 pb-4">
          <h3 className="text-lg font-semibold text-white-90 uppercase tracking-widest text-xs opacity-50">
            Execution Results
          </h3>
          <span className="px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-400 text-[10px] font-bold uppercase tracking-tighter border border-emerald-500/20">
            Success
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {outputResults.map(([id, res]) => {
            const node = selectedWorkflow.nodes.find(n => n.id === id);
            return (
              <div key={id} className="group relative rounded-2xl bg-white-5 border border-white-10 overflow-hidden hover:border-white-20 transition-all shadow-lg hover:shadow-2xl">
                <div className="p-3 border-b border-white-5 bg-white-2 flex items-center justify-between">
                  <span className="text-[10px] font-bold text-white-40 uppercase tracking-widest">
                    {node.data.label}
                  </span>
                  {res.output && res.output.startsWith('http') && (
                    <a href={res.output} target="_blank" rel="noreferrer" className="text-blue-400 hover:text-blue-300">
                      <ExternalLink size={12} />
                    </a>
                  )}
                </div>
                
                <div className="aspect-square bg-black-40 flex items-center justify-center p-2">
                  {node.data.outputType === 'image' && (
                    <img src={res.output} className="w-full h-full object-contain rounded-lg" alt="Result" />
                  )}
                  {node.data.outputType === 'video' && (
                    <video src={res.output} className="w-full h-full object-contain rounded-lg" controls />
                  )}
                  {node.data.outputType === 'audio' && (
                    <audio src={res.output} className="w-full" controls />
                  )}
                  {node.data.outputType === 'text' && (
                    <div className="p-4 text-sm text-white-80 font-mono overflow-y-auto max-h-full w-full">
                      {res.output}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  return (
    <div className="studio-container p-8">
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-white tracking-tighter flex items-center gap-3">
              <Library size={32} className="text-blue-400" />
              Saved Canvas
            </h1>
            <p className="text-white-40 mt-1">Select a template or saved workflow to start creating</p>
          </div>
          
          <button 
            onClick={fetchData}
            className="p-2 rounded-xl bg-white-5 hover:bg-white-10 text-white-60 transition-all border border-white-10"
            title="Refresh Library"
          >
            <Loader2 size={18} className={loading ? 'animate-spin' : ''} />
          </button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Sidebar - List of Workflows */}
          <div className="lg:col-span-1 space-y-6">
            <section>
              <h2 className="text-[10px] font-bold text-white-40 uppercase tracking-[0.2em] mb-4 px-2">Templates</h2>
              <div className="space-y-1">
                {examples.map(wf => (
                  <button
                    key={wf.id}
                    onClick={() => handleSelectWorkflow(wf, true)}
                    className={`w-full text-left p-3 rounded-xl transition-all group flex items-center justify-between ${
                      selectedWorkflow?.id === wf.id ? 'bg-blue-600/20 text-blue-400 border border-blue-500/20' : 'text-white-60 hover:bg-white-5 hover:text-white'
                    }`}
                  >
                    <span className="text-sm font-medium truncate">{wf.name}</span>
                    <ChevronRight size={14} className={`transition-transform duration-300 ${selectedWorkflow?.id === wf.id ? 'translate-x-1' : 'opacity-0'}`} />
                  </button>
                ))}
              </div>
            </section>

            <section>
              <h2 className="text-[10px] font-bold text-white-40 uppercase tracking-[0.2em] mb-4 px-2">Your Saved</h2>
              <div className="space-y-1">
                {savedWorkflows.map(wf => (
                  <button
                    key={wf.id}
                    onClick={() => handleSelectWorkflow(wf)}
                    className={`w-full text-left p-3 rounded-xl transition-all group flex items-center justify-between ${
                      selectedWorkflow?.id === wf.id ? 'bg-indigo-600/20 text-indigo-400 border border-indigo-500/20' : 'text-white-60 hover:bg-white-5 hover:text-white'
                    }`}
                  >
                    <span className="text-sm font-medium truncate">{wf.name}</span>
                    <ChevronRight size={14} className={`transition-transform duration-300 ${selectedWorkflow?.id === wf.id ? 'translate-x-1' : 'opacity-0'}`} />
                  </button>
                ))}
                {savedWorkflows.length === 0 && !loading && (
                    <div className="p-4 text-center border border-dashed border-white-10 rounded-xl">
                        <p className="text-[10px] text-white-20 leading-relaxed font-medium">No saved workflows yet</p>
                    </div>
                )}
              </div>
            </section>
          </div>

          {/* Main Area - Configuration & Run */}
          <div className="lg:col-span-3">
             {selectedWorkflow ? (
                 <div className="glass-card rounded-3xl p-8 border border-white-10 overflow-hidden relative min-h-[500px]">
                    {loading && (
                        <div className="absolute inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center">
                            <Loader2 size={40} className="animate-spin text-blue-400" />
                        </div>
                    )}
                    
                    <div className="mb-8">
                        <div className="flex items-center gap-3 mb-2">
                             <div className="w-8 h-8 rounded-lg bg-blue-600/20 flex items-center justify-center text-blue-400">
                                <Library size={18} />
                             </div>
                             <h2 className="text-2xl font-bold text-white tracking-tight">{selectedWorkflow.name}</h2>
                        </div>
                        <p className="text-white-40 text-sm">Fill in the fields below to run this automated workflow.</p>
                    </div>

                    {renderInputFields()}
                    {renderResults()}
                 </div>
             ) : (
                 <div className="h-full min-h-[500px] flex flex-col items-center justify-center border-2 border-dashed border-white-10 rounded-3xl p-12 text-center text-white-20 bg-white-[0.02]">
                    <div className="w-16 h-16 rounded-2xl bg-white-5 flex items-center justify-center mb-6">
                        <Library size={32} />
                    </div>
                    <h3 className="text-xl font-semibold mb-2 text-white-40">Load a Workflow</h3>
                    <p className="max-w-xs text-sm">Select one of the pre-designed templates on the left or an existing saved canvas to start.</p>
                 </div>
             )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SavedCanvasPanel;
