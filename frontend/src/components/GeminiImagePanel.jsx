import React, { useState, useRef, useEffect } from 'react';
import { Upload, Maximize2, Image as ImageIcon } from 'lucide-react';
import { useConfig } from '../contexts/ConfigContext';

const GeminiImagePanel = ({ userId }) => {
  const { config } = useConfig();
  const [activeMode, setActiveMode] = useState('generate'); // 'generate' or 'upscale'

  // Generation State
  const [prompt, setPrompt] = useState('');
  const [modelId, setModelId] = useState(config?.DEFAULT_GEMINI_IMAGE_MODEL || 'gemini-3-pro-image-preview');

  useEffect(() => {
    if (config?.DEFAULT_GEMINI_IMAGE_MODEL) {
      setModelId(config.DEFAULT_GEMINI_IMAGE_MODEL);
    }
  }, [config]);

  const [aspectRatio, setAspectRatio] = useState('1:1');
  const [imageSize, setImageSize] = useState('1K');
  const [candidateCount, setCandidateCount] = useState(1);
  const [gcsUris, setGcsUris] = useState('');
  const [files, setFiles] = useState([]);

  // Upscaling State
  const [upscaleFactor, setUpscaleFactor] = useState('x2');
  const [upscaleFile, setUpscaleFile] = useState(null);

  // Shared State
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const fileInputRef = useRef(null);
  const upscaleInputRef = useRef(null);

  const handleFileChange = (e) => {
    setFiles(Array.from(e.target.files));
  };

  const handleUpscaleFileChange = (e) => {
    if (e.target.files[0]) {
      setUpscaleFile(e.target.files[0]);
    }
  };

  const handleGenerate = async () => {
    setIsLoading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append('prompt', prompt);
    formData.append('model_id', modelId);
    formData.append('aspect_ratio', aspectRatio);
    formData.append('image_size', imageSize);
    formData.append('candidate_count', candidateCount);
    formData.append('gcs_uris', gcsUris);
    formData.append('response_modalities', 'TEXT,IMAGE');
    formData.append('user_id', userId);

    files.forEach((file) => {
      formData.append('files', file);
    });

    try {
      const response = await fetch('/api/generate/content', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Generation failed');
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleUpscale = async () => {
    if (!upscaleFile) {
      setError("Please upload an image to upscale");
      return;
    }

    setIsLoading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append('file', upscaleFile);
    formData.append('upscale_factor', upscaleFactor);
    formData.append('user_id', userId);

    try {
      const response = await fetch('/api/generate/upscale', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Upscaling failed');
      }

      const data = await response.json();
      // Normalize result structure to match generation so we can reuse the display logic
      setResult({
        images: [data.image],
        text: `Successfully upscaled by ${upscaleFactor}`
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="glass-panel">
      <div className="panel-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2>Gemini Image Studio</h2>
          <p>Generate, edit, and upscale images with Gemini & Imagen</p>
        </div>

        <div className="toggle-pill-container" style={{ display: 'flex', background: 'rgba(255,255,255,0.05)', padding: '0.25rem', borderRadius: '999px', border: '1px solid var(--glass-border)' }}>
          <button
            className={`toggle-pill ${activeMode === 'generate' ? 'active' : ''}`}
            onClick={() => { setActiveMode('generate'); setResult(null); setError(null); }}
            style={{
              padding: '0.4rem 1rem',
              borderRadius: '999px',
              border: 'none',
              background: activeMode === 'generate' ? 'var(--accent-primary)' : 'transparent',
              color: activeMode === 'generate' ? 'white' : 'var(--text-secondary)',
              fontSize: '0.8rem',
              fontWeight: '600',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              transition: 'all 0.2s ease'
            }}
          >
            <ImageIcon size={14} />
            Generate
          </button>
          <button
            className={`toggle-pill ${activeMode === 'upscale' ? 'active' : ''}`}
            onClick={() => { setActiveMode('upscale'); setResult(null); setError(null); }}
            style={{
              padding: '0.4rem 1rem',
              borderRadius: '999px',
              border: 'none',
              background: activeMode === 'upscale' ? 'var(--accent-primary)' : 'transparent',
              color: activeMode === 'upscale' ? 'white' : 'var(--text-secondary)',
              fontSize: '0.8rem',
              fontWeight: '600',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              transition: 'all 0.2s ease'
            }}
          >
            <Maximize2 size={14} />
            Upscale
          </button>
        </div>
      </div>

      <div className="panel-content">
        {activeMode === 'generate' ? (
          <>
            <div className="config-grid">


              <div className="config-group">
                <label className="label">Model</label>
                <select className="select-field" value={modelId} onChange={(e) => setModelId(e.target.value)}>
                  {config?.GEMINI_IMAGE_MODELS?.map(model => (
                    <option key={model} value={model}>{model}</option>
                  )) || <option value="gemini-3-pro-image-preview">Gemini 3 Pro Image</option>}
                </select>
              </div>

              <div className="config-group">
                <label className="label">Aspect Ratio</label>
                <select className="select-field" value={aspectRatio} onChange={(e) => setAspectRatio(e.target.value)}>
                  <option value="1:1">1:1 (Square)</option>
                  <option value="16:9">16:9 (Widescreen)</option>
                  <option value="9:16">9:16 (Portrait)</option>
                  <option value="3:2">3:2</option>
                  <option value="2:3">2:3</option>
                  <option value="4:3">4:3</option>
                  <option value="3:4">3:4</option>
                </select>
              </div>

              <div className="config-group">
                <label className="label">Image Size</label>
                <select className="select-field" value={imageSize} onChange={(e) => setImageSize(e.target.value)}>
                  <option value="1K">1K</option>
                  <option value="2K">2K</option>
                  <option value="4K">4K</option>
                </select>
              </div>

              <div className="config-group">
                <label className="label">Wait Count</label>
                <select className="select-field" value={candidateCount} onChange={(e) => setCandidateCount(parseInt(e.target.value))}>
                  <option value={1}>1 Model Output</option>
                  <option value={2}>2 Model Outputs</option>
                  <option value={3}>3 Model Outputs</option>
                </select>
              </div>
            </div>

            <div className="config-group" style={{ marginTop: '1.5rem' }}>
              <label className="label">GCS URIs (Optional)</label>
              <input
                type="text"
                placeholder="gs://bucket/image.png, gs://bucket/ref.jpg"
                value={gcsUris}
                onChange={(e) => setGcsUris(e.target.value)}
                className="input-field"
              />
            </div>

            <div className="config-group" style={{ marginTop: '1.5rem' }}>
              <label className="label">Upload Reference Images (Optional)</label>
              <div
                className={`upload-zone ${files.length > 0 ? 'has-file' : ''}`}
                onClick={() => fileInputRef.current?.click()}
              >
                {files.length > 0 ? (
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.75rem' }}>
                    {files.map((f, i) => (
                      <div key={i} className="glass-panel" style={{ padding: '0.5rem 1rem', borderRadius: '0.75rem', fontSize: '0.85rem' }}>
                        {f.name}
                      </div>
                    ))}
                  </div>
                ) : (
                  <>
                    <Upload size={32} />
                    <p style={{ marginTop: '0.5rem', fontSize: '0.9rem' }}>Click or drag images for editing/reference</p>
                  </>
                )}
                <input
                  type="file"
                  multiple
                  hidden
                  ref={fileInputRef}
                  onChange={handleFileChange}
                  accept="image/*"
                />
              </div>
            </div>

            <div className="config-group" style={{ marginTop: '1.5rem' }}>
              <label className="label">Prompt</label>
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Describe the image you want to generate or how to edit the uploaded one..."
                rows={4}
                className="textarea-field"
              />
            </div>

            <button
              className="btn"
              onClick={handleGenerate}
              disabled={isLoading || !prompt}
            >
              {isLoading ? <div className="spinner"></div> : 'Generate / Edit Image'}
            </button>
          </>
        ) : (
          /* Upscaling Mode */
          <>
            <div className="config-grid">
              <div className="config-group">
                <label className="label">Upscale Factor</label>
                <select className="select-field" value={upscaleFactor} onChange={(e) => setUpscaleFactor(e.target.value)}>
                  <option value="x2">x2 (Double Resolution)</option>
                  <option value="x4">x4 (Quadruple Resolution)</option>
                </select>
              </div>
            </div>

            <div className="config-group" style={{ marginTop: '1.5rem' }}>
              <label className="label">Upload Image to Upscale</label>
              <div
                className={`upload-zone ${upscaleFile ? 'has-file' : ''}`}
                onClick={() => upscaleInputRef.current?.click()}
              >
                {upscaleFile ? (
                  <div className="glass-panel" style={{ padding: '0.5rem 1rem', borderRadius: '0.75rem', fontSize: '0.85rem' }}>
                    {upscaleFile.name}
                  </div>
                ) : (
                  <>
                    <Upload size={32} />
                    <p style={{ marginTop: '0.5rem', fontSize: '0.9rem' }}>Click to upload image for upscaling</p>
                  </>
                )}
                <input
                  type="file"
                  hidden
                  ref={upscaleInputRef}
                  onChange={handleUpscaleFileChange}
                  accept="image/*"
                />
              </div>
            </div>

            <button
              className="btn"
              onClick={handleUpscale}
              disabled={isLoading || !upscaleFile}
              style={{ marginTop: '1.5rem' }}
            >
              {isLoading ? <div className="spinner"></div> : 'Upscale Image'}
            </button>
          </>
        )}

        {error && (
          <div style={{ background: 'rgba(239, 68, 68, 0.1)', color: '#ef4444', padding: '1rem', borderRadius: '0.75rem', marginTop: '1.5rem', border: '1px solid rgba(239, 68, 68, 0.2)', fontSize: '0.9rem' }}>
            {error}
          </div>
        )}

        {result && (
          <div style={{ marginTop: '2.5rem' }}>
            {(Array.isArray(result) ? result : [result]).map((res, resIdx) => (
              <div key={resIdx} style={{ marginBottom: '2.5rem' }}>
                {res.thoughts && (
                  <details className="thoughts-container" style={{ marginBottom: '1.5rem' }}>
                    <summary style={{ cursor: 'pointer', fontWeight: '600', color: 'var(--text-secondary)' }}>View Generation Logic (Candidate {resIdx + 1})</summary>
                    <pre style={{ marginTop: '1rem', whiteSpace: 'pre-wrap', fontSize: '0.85rem', opacity: 0.8 }}>{res.thoughts}</pre>
                  </details>
                )}
                {res.text && <div className="response-text" style={{ marginBottom: '1.5rem' }}>{res.text}</div>}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.5rem' }}>
                  {res.images?.map((img, idx) => (
                    <div key={idx} className="image-container" style={{ position: 'relative' }}>
                      <img
                        src={`data:${img.mime_type};base64,${img.data}`}
                        alt={`Generated ${resIdx}-${idx}`}
                        style={{ width: '100%', display: 'block' }}
                      />
                      <a
                        href={`data:${img.mime_type};base64,${img.data}`}
                        download={`generated-${resIdx}-${idx}.png`}
                        className="btn-secondary"
                        style={{
                          position: 'absolute',
                          bottom: '1rem',
                          right: '1rem',
                          padding: '0.5rem 1rem',
                          fontSize: '0.8rem',
                          background: 'rgba(15, 23, 42, 0.8)',
                          backdropFilter: 'blur(10px)'
                        }}
                      >
                        Download
                      </a>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default GeminiImagePanel;

