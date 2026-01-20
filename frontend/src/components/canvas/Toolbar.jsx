import React from 'react';
import { Bot, Image as ImageIcon, FileInput, Eye, Play, Save, Upload, Download, ArrowUpCircle, Volume2, Video, Workflow, Trash, Film } from 'lucide-react';

const Toolbar = ({ onDragStart, onAddNode, onRun, onSave, onImport, onExport, isRunning, useCache, setUseCache }) => {
  React.useEffect(() => {
    console.log("Toolbar mounted - v2 (with Clear Cache)");
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
        <div className="toolbar-header">Actions</div>

        <button
          onClick={() => onRun()}
          disabled={isRunning}
          className="toolbar-btn run"
        >
          <Play size={16} color="white" />
          <span className="text-white font-medium">
            {isRunning ? 'Running...' : 'Run'}
          </span>
        </button>

        {/* Cache Toggle */}
        <div className="flex items-center justify-between px-3 py-2 bg-white/5 rounded-xl border border-white/5">
          <span className="text-xs font-medium text-gray-400">Cache</span>
          <button
            onClick={() => setUseCache && setUseCache(!useCache)}
            className={`w-8 h-4 rounded-full transition-colors relative ${useCache ? 'bg-green-500' : 'bg-gray-600'}`}
            title={useCache ? "Cache Enabled" : "Cache Disabled"}
          >
            <div className={`absolute top-0.5 w-3 h-3 bg-white rounded-full transition-transform ${useCache ? 'left-4.5' : 'left-0.5'}`} style={{ left: useCache ? '18px' : '2px' }} />
          </button>
        </div>


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

        <button
          onClick={async () => {
            if (confirm("Clear execution cache?")) {
              try {
                await fetch('/api/workflow/cache/clear', { method: 'POST' });
                alert("Cache cleared!");
              } catch (e) {
                console.error(e);
                alert("Failed to clear cache: " + e);
              }
            }
          }}
          className="toolbar-btn secondary"
        >
          <Trash size={16} color="#d1d5db" />
          <span className="node-label">Clear Cache</span>
        </button>
      </div>
    </div>
  );
};

export default Toolbar;
