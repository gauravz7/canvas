import React from 'react';
import { Bot, Image as ImageIcon, FileInput, Eye, Play, Save, Upload, Download, ArrowUpCircle, Volume2, Video, Workflow, Trash, Film } from 'lucide-react';

const Toolbar = ({ onDragStart, onAddNode, onRun, onKill, onSave, onImport, onExport, isRunning, useCache, setUseCache, workflowName, setWorkflowName }) => {
  React.useEffect(() => {
    console.log("Toolbar mounted");
  }, []);

  return (
    <div className="canvas-toolbar">
      {/* Node Palette */}
      <div className="toolbar-panel">
        <div className="toolbar-header">Nodes</div>

        {/* INPUT Category */}
        <div className="node-category">
          <div className="category-header">
            <FileInput size={16} color="#4ade80" />
            <span>Inputs</span>
          </div>
          <div className="category-items">
            <div className="node-item sub" onDragStart={(event) => onDragStart(event, 'input', 'text')} onClick={() => onAddNode('input', 'text')} draggable>
              <FileInput size={14} color="#4ade80" />
              <span>Input (Text)</span>
            </div>
            <div className="node-item sub" onDragStart={(event) => onDragStart(event, 'input', 'image')} onClick={() => onAddNode('input', 'image')} draggable>
              <ImageIcon size={14} color="#c084fc" />
              <span>Input (Image)</span>
            </div>
            <div className="node-item sub" onDragStart={(event) => onDragStart(event, 'input', 'video')} onClick={() => onAddNode('input', 'video')} draggable>
              <Bot size={14} color="#60a5fa" />
              <span>Input (Video)</span>
            </div>
            <div className="node-item sub" onDragStart={(event) => onDragStart(event, 'input', 'audio')} onClick={() => onAddNode('input', 'audio')} draggable>
              <Bot size={14} color="#fca5a5" />
              <span>Input (Audio)</span>
            </div>
          </div>
        </div>

        {/* GEMINI Category */}
        <div className="node-category">
          <div className="category-header">
            <Bot size={16} color="#60a5fa" />
            <span>Gemini</span>
          </div>
          <div className="category-items">
            <div className="node-item sub" onDragStart={(event) => onDragStart(event, 'gemini_text')} onClick={() => onAddNode('gemini_text')} draggable>
              <Bot size={14} color="#60a5fa" />
              <span>Gemini Text</span>
            </div>
            <div className="node-item sub" onDragStart={(event) => onDragStart(event, 'gemini_image')} onClick={() => onAddNode('gemini_image')} draggable>
              <ImageIcon size={14} color="#c084fc" />
              <span>Gemini Image</span>
            </div>
          </div>
        </div>

        {/* VOICE & MUSIC Category */}
        <div className="node-category">
          <div className="category-header">
            <Bot size={16} color="#4ade80" />
            <span>Voice & Music</span>
          </div>
          <div className="category-items">
            <div className="node-item sub" onDragStart={(event) => onDragStart(event, 'speech_gen')} onClick={() => onAddNode('speech_gen')} draggable>
              <Bot size={14} color="#4ade80" />
              <span>Speech Gen</span>
            </div>
            <div className="node-item sub" onDragStart={(event) => onDragStart(event, 'lyria_gen')} onClick={() => onAddNode('lyria_gen')} draggable>
              <Bot size={14} color="#60a5fa" />
              <span>Lyria Music</span>
            </div>
          </div>
        </div>

        {/* VIDEO Category */}
        <div className="node-category">
          <div className="category-header">
            <Play size={16} color="#c084fc" />
            <span>Video Gen</span>
          </div>
          <div className="category-items">
            <div className="node-item sub" onDragStart={(event) => onDragStart(event, 'veo_standard')} onClick={() => onAddNode('veo_standard')} draggable>
              <Play size={14} color="#c084fc" />
              <span>Veo Standard</span>
            </div>
            <div className="node-item sub" onDragStart={(event) => onDragStart(event, 'veo_extend')} onClick={() => onAddNode('veo_extend')} draggable>
              <Play size={14} color="#c084fc" />
              <span>Veo Extend</span>
            </div>
            <div className="node-item sub" onDragStart={(event) => onDragStart(event, 'veo_reference')} onClick={() => onAddNode('veo_reference')} draggable>
              <Play size={14} color="#c084fc" />
              <span>Veo Reference</span>
            </div>
          </div>
        </div>

        {/* OUTPUT Category */}
        <div className="node-category">
          <div className="category-header">
            <Eye size={16} color="#fb923c" />
            <span>Outputs</span>
          </div>
          <div className="category-items">
            <div className="node-item sub" onDragStart={(event) => onDragStart(event, 'output', 'text')} onClick={() => onAddNode('output', 'text')} draggable>
              <Eye size={14} color="#fb923c" />
              <span>Output (Text)</span>
            </div>
            <div className="node-item sub" onDragStart={(event) => onDragStart(event, 'output', 'image')} onClick={() => onAddNode('output', 'image')} draggable>
              <ImageIcon size={14} color="#c084fc" />
              <span>Output (Image)</span>
            </div>
            <div className="node-item sub" onDragStart={(event) => onDragStart(event, 'output', 'audio')} onClick={() => onAddNode('output', 'audio')} draggable>
              <Volume2 size={14} color="#4ade80" />
              <span>Output (Audio)</span>
            </div>
            <div className="node-item sub" onDragStart={(event) => onDragStart(event, 'output', 'video')} onClick={() => onAddNode('output', 'video')} draggable>
              <Video size={14} color="#c084fc" />
              <span>Output (Video)</span>
            </div>
          </div>
        </div>

        {/* UTILITY Nodes */}
        <div className="toolbar-panel-section-divider"></div>
        <div
          className="node-item"
          onDragStart={(event) => onDragStart(event, 'imagen_upscale')}
          onClick={() => onAddNode('imagen_upscale')}
          draggable
        >
          <ArrowUpCircle size={16} className="text-purple-400" color="#c084fc" />
          <span className="node-label">Image Upscaler</span>
        </div>

        <div
          className="node-item"
          onDragStart={(event) => onDragStart(event, 'editor')}
          onClick={() => onAddNode('editor')}
          draggable
        >
          <Film size={16} className="text-indigo-400" color="#818cf8" />
          <span className="node-label">Video Editor</span>
        </div>


      </div>

      {/* Actions */}
      <div className="toolbar-panel">
        <div className="toolbar-header">Project</div>

        <div className="px-2 mb-4">
          <label className="block text-[10px] font-bold text-white/30 uppercase tracking-widest mb-1.5 ml-1">
            Canvas Name
          </label>
          <input
            type="text"
            value={workflowName}
            onChange={(e) => setWorkflowName(e.target.value)}
            className="w-full bg-black/60 border border-white/10 rounded-lg px-3 py-2 text-xs text-white placeholder-white/20 focus:outline-none focus:ring-1 focus:ring-blue-500/50 focus:border-blue-500/50 transition-all"
            placeholder="Enter workflow name..."
          />
        </div>

        <div className="toolbar-header">Actions</div>

        {isRunning ? (
          <button
            onClick={() => onKill && onKill()}
            className="toolbar-btn run kill"
          >
            <Trash size={16} color="white" />
            <span className="text-white font-medium">Kill Execution</span>
          </button>
        ) : (
            <button
              onClick={() => onRun()}
              className="toolbar-btn run"
            >
              <Play size={16} color="white" />
              <span className="text-white font-medium">Run</span>
            </button>
        )}



        <button onClick={onSave} className="toolbar-btn secondary">
          <Save size={16} color="#d1d5db" />
          <span className="node-label">Save</span>
        </button>

        <button onClick={() => document.getElementById('import-input').click()} className="toolbar-btn secondary">
          <Upload size={16} color="#d1d5db" />
          <span className="node-label">Import</span>
        </button>
        <input
          type="file"
          id="import-input"
          className="hidden"
          accept=".json"
          onChange={onImport}
          aria-label="Import Workflow"
        />

        <button onClick={onExport} className="toolbar-btn secondary">
          <Download size={16} color="#d1d5db" />
          <span className="node-label">Export</span>
        </button>

      </div>
    </div>
  );
};

export default Toolbar;
