
import React, { useState, useEffect } from 'react';
import { Upload, X, Send, Cpu, Layers } from 'lucide-react';
import { useConfig } from '../contexts/ConfigContext';

const GeminiThreePanel = () => {
  const { config } = useConfig();
  const [prompt, setPrompt] = useState("");
  const [model, setModel] = useState(config?.DEFAULT_GEMINI_TEXT_MODEL || "gemini-3-pro-preview");

  useEffect(() => {
    if (config?.DEFAULT_GEMINI_TEXT_MODEL) {
      setModel(config.DEFAULT_GEMINI_TEXT_MODEL);
    }
  }, [config]);

  const [thinkingLevel, setThinkingLevel] = useState("HIGH");
  const [mediaResolution, setMediaResolution] = useState("");
  const [files, setFiles] = useState([]);
  const [result, setResult] = useState("");
  const [groundingMetadata, setGroundingMetadata] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [useGrounding, setUseGrounding] = useState(false);

  const handleFileChange = (e) => {
    const selectedFiles = Array.from(e.target.files);
    setFiles([...files, ...selectedFiles]);
  };

  const removeFile = (index) => {
    setFiles(files.filter((_, i) => i !== index));
  };

  const handleSubmit = async () => {
    if (!prompt && files.length === 0) return;

    setLoading(true);
    setError(null);
    setResult("");

    try {
      const formData = new FormData();
      formData.append("prompt", prompt);
      formData.append("model_id", model);
      formData.append("thinking_level", thinkingLevel);
      if (mediaResolution) formData.append("media_resolution", mediaResolution);
      formData.append("use_grounding", useGrounding);

      files.forEach(file => {
        formData.append("files", file);
      });

      const response = await fetch('/api/generate/content', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || "Generation failed");
      }

      const data = await response.json();
      setResult(data.text);
      setGroundingMetadata(data.grounding_metadata);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass-panel">
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '2rem' }}>
        <Cpu size={32} color="#8b5cf6" />
        <h2 style={{ margin: 0 }}>Gemini 3 Reasoning</h2>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1.5rem' }}>
        <div>
          <label className="label">Model</label>
          <select value={model} onChange={(e) => setModel(e.target.value)} className="select-field">
            {config?.GEMINI_TEXT_MODELS?.map(m => (
              <option key={m} value={m}>{m}</option>
            )) || (
                <>
                  <option value="gemini-3-pro-preview">Gemini 3 Pro Preview</option>
                  <option value="gemini-3-flash-preview">Gemini 3 Flash Preview</option>
                </>
              )}
          </select>
        </div>
        <div>
          <label className="label">Thinking Level</label>
          <select value={thinkingLevel} onChange={(e) => setThinkingLevel(e.target.value)} className="select-field">
            <option value="MINIMAL">Minimal (Flash Only)</option>
            <option value="LOW">Low</option>
            <option value="MEDIUM">Medium (Flash Only)</option>
            <option value="HIGH">High (Default)</option>
          </select>
        </div>
      </div>

      <div style={{ marginBottom: '1.5rem' }}>
        <label className="label">Media Resolution</label>
        <select value={mediaResolution} onChange={(e) => setMediaResolution(e.target.value)} className="select-field">
          <option value="">Default (Optimal)</option>
          <option value="MEDIA_RESOLUTION_LOW">Low</option>
          <option value="MEDIA_RESOLUTION_MEDIUM">Medium</option>
          <option value="MEDIA_RESOLUTION_HIGH">High</option>
          <option value="MEDIA_RESOLUTION_ULTRA_HIGH">Ultra High (Image Only)</option>
        </select>
      </div>

      <div style={{ marginBottom: '1.5rem' }}>
        <label className="label">Prompt</label>
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="What's on your mind? Gemini 3 will reason it out..."
          className="input-field"
          style={{ minHeight: '120px', resize: 'vertical' }}
        />
      </div>

      <div style={{ marginBottom: '1.5rem' }}>
        <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer', color: '#8b5cf6', fontWeight: 500 }}>
          <input
            type="checkbox"
            checked={useGrounding}
            onChange={(e) => setUseGrounding(e.target.checked)}
            style={{ width: '18px', height: '18px' }}
          />
          Enable Google Search Grounding
        </label>
        <p style={{ margin: '0.5rem 0 0 1.8rem', fontSize: '0.85rem', opacity: 0.7 }}>
          Gemini will use real-world info from Google Search to reason and verify facts.
        </p>
      </div>

      <div style={{ marginBottom: '1.5rem' }}>
        <label className="label">Multimodal Input (Images, PDFs, Videos)</label>
        <div
          className="upload-zone"
          onDragOver={(e) => e.preventDefault()}
          onClick={() => document.getElementById('file-upload').click()}
        >
          <Upload size={32} />
          <p>Click or drag files here to reason with media</p>
          <input
            id="file-upload"
            type="file"
            multiple
            hidden
            onChange={handleFileChange}
          />
        </div>

        {files.length > 0 && (
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginTop: '1rem' }}>
            {files.map((file, i) => (
              <div key={i} style={{
                background: 'rgba(255,255,255,0.1)',
                padding: '0.25rem 0.75rem',
                borderRadius: '1rem',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                fontSize: '0.9rem'
              }}>
                <span style={{ maxWidth: '150px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {file.name}
                </span>
                <X
                  size={14}
                  style={{ cursor: 'pointer', opacity: 0.7 }}
                  onClick={(e) => { e.stopPropagation(); removeFile(i); }}
                />
              </div>
            ))}
          </div>
        )}
      </div>

      <button className="btn" onClick={handleSubmit} disabled={loading} style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '0.75rem',
        padding: '1rem'
      }}>
        {loading ? <div className="spinner"></div> : <><Send size={20} /> Generate with Thinking</>}
      </button>

      {error && (
        <div style={{
          background: 'rgba(239, 68, 68, 0.1)',
          color: '#ef4444',
          padding: '1rem',
          borderRadius: '0.5rem',
          marginTop: '1.5rem',
          border: '1px solid rgba(239, 68, 68, 0.2)'
        }}>
          {error}
        </div>
      )}

      {result && (
        <div style={{ marginTop: '2rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem', opacity: 0.7 }}>
            <Layers size={18} />
            <h3 style={{ margin: 0, fontSize: '1.1rem' }}>Response</h3>
          </div>
          <div className="glass-panel" style={{
            background: 'rgba(0,0,0,0.3)',
            whiteSpace: 'pre-wrap',
            fontSize: '1rem',
            lineHeight: '1.6',
            maxHeight: '400px',
            overflowY: 'auto'
          }}>
            {result}
          </div>

          {groundingMetadata && groundingMetadata.groundingChunks && (
            <div style={{ marginTop: '1.5rem' }}>
              <h4 style={{ fontSize: '0.9rem', opacity: 0.7, marginBottom: '0.75rem' }}>Sources (Grounded)</h4>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.75rem' }}>
                {groundingMetadata.groundingChunks.map((chunk, idx) => (
                  chunk.web && (
                    <a
                      key={idx}
                      href={chunk.web.uri}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="glass-card"
                      style={{
                        padding: '0.5rem 1rem',
                        fontSize: '0.85rem',
                        textDecoration: 'none',
                        color: '#60a5fa',
                        display: 'flex',
                        flexDirection: 'column',
                        gap: '0.25rem',
                        background: 'rgba(255,255,255,0.05)',
                        border: '1px solid rgba(255,255,255,0.1)'
                      }}
                    >
                      <span style={{ fontWeight: 600, maxWidth: '200px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {chunk.web.title}
                      </span>
                      <span style={{ fontSize: '0.75rem', opacity: 0.6 }}>
                        {new URL(chunk.web.uri).hostname}
                      </span>
                    </a>
                  )
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default GeminiThreePanel;
