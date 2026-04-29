import React from 'react';
import { Bot, Image as ImageIcon, FileInput, Eye, Play, Save, Upload, Download, ArrowUpCircle, Volume2, Video, Workflow, Trash, Film } from 'lucide-react';

const Toolbar = ({ onDragStart, onAddNode, onRun, onKill, onSave, onImport, onExport, isRunning, useCache, setUseCache, workflowName, setWorkflowName, visibility, setVisibility, selectedTeamId, setSelectedTeamId, teams }) => {
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
            <div className="node-item sub" onDragStart={(event) => onDragStart(event, 'lyria_clip')} onClick={() => onAddNode('lyria_clip')} draggable>
              <Bot size={14} color="#60a5fa" />
              <span>Lyria Clip</span>
            </div>
            <div className="node-item sub" onDragStart={(event) => onDragStart(event, 'lyria_pro')} onClick={() => onAddNode('lyria_pro')} draggable>
              <Bot size={14} color="#818cf8" />
              <span>Lyria Pro</span>
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
          onDragStart={(event) => onDragStart(event, 'veo_upscale')}
          onClick={() => onAddNode('veo_upscale')}
          draggable
        >
          <ArrowUpCircle size={16} className="text-orange-400" color="#fb923c" />
          <span className="node-label">Video Upscaler</span>
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
            className="w-full rounded-lg px-3 py-2 text-xs transition-all font-medium"
            style={{
              backgroundColor: '#1a1a1a',
              color: '#ffffff',
              border: '1px solid rgba(255,255,255,0.2)',
              outline: 'none'
            }}
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



        {/* Visibility selector */}
        <div style={{ padding: '0 0.5rem', marginBottom: '0.25rem' }}>
          <label style={{ display: 'block', fontSize: '0.6rem', fontWeight: 700, color: 'rgba(255,255,255,0.3)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.25rem', marginLeft: '0.25rem' }}>
            Visibility
          </label>
          <div style={{ display: 'flex', gap: '4px', alignItems: 'center' }}>
            <select
              value={visibility || 'private'}
              onChange={(e) => { setVisibility(e.target.value); if (e.target.value !== 'team') setSelectedTeamId(''); }}
              style={{ background: '#1a1a1a', border: '1px solid rgba(255,255,255,0.15)', color: 'rgba(255,255,255,0.7)', fontSize: '0.65rem', padding: '0.4rem', borderRadius: '0.375rem', cursor: 'pointer', flex: 1 }}
            >
              <option value="private">Private</option>
              <option value="team">Team</option>
              <option value="public">Public</option>
            </select>
            {visibility === 'team' && teams && teams.length > 0 && (
              <select
                value={selectedTeamId || ''}
                onChange={(e) => setSelectedTeamId(e.target.value)}
                style={{ background: '#1a1a1a', border: '1px solid rgba(255,255,255,0.15)', color: 'rgba(255,255,255,0.7)', fontSize: '0.65rem', padding: '0.4rem', borderRadius: '0.375rem', cursor: 'pointer', flex: 1 }}
              >
                <option value="">Select Team</option>
                {teams.map(t => <option key={t.id} value={t.id}>{t.name}</option>)}
              </select>
            )}
          </div>
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

      </div>
    </div>
  );
};

export default Toolbar;
