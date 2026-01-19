import React, { useState, useRef, useEffect } from 'react';
import { Upload, Maximize2, Download, AlertCircle } from 'lucide-react';
import { useConfig } from '../contexts/ConfigContext';

const ImageUpscalePanel = ({ userId }) => {
  const { config } = useConfig();
  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [upscaleFactor, setUpscaleFactor] = useState('x2');
  const [modelId, setModelId] = useState(config?.DEFAULT_UPSCALE_MODEL || 'imagen-4.0-upscale-preview');

  useEffect(() => {
    if (config?.DEFAULT_UPSCALE_MODEL) setModelId(config.DEFAULT_UPSCALE_MODEL);
  }, [config]);

  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setPreviewUrl(URL.createObjectURL(selectedFile));
      setResult(null);
      setError(null);
    }
  };

  const handleUpscale = async () => {
    if (!file) return;

    setIsLoading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('upscale_factor', upscaleFactor);
    formData.append('model_id', modelId);
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
      setResult(data.image);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="glass-panel">
      <div className="panel-header">
        <h2 style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <Maximize2 className="text-primary" size={24} />
          Image Upscale Studio
        </h2>
        <p>Imagen 4.0 High-Fidelity Upscaling with intelligent detail reconstruction</p>
      </div>

      <div className="panel-content">
        <div className="grid-2">
          <div className="upload-section">
            <label className="label">Source Image</label>
            <div
              className={`upload-zone ${file ? 'has-file' : ''}`}
              onClick={() => fileInputRef.current?.click()}
              style={{ height: '320px' }}
            >
              {previewUrl ? (
                <img src={previewUrl} alt="Preview" style={{ maxWidth: '100%', maxHeight: '100%', objectFit: 'contain', borderRadius: '0.75rem' }} />
              ) : (
                <>
                  <Upload size={48} style={{ opacity: 0.3, marginBottom: '1rem' }} />
                  <p style={{ fontSize: '0.95rem' }}>Drop or click to select source image</p>
                </>
              )}
              <input
                type="file"
                hidden
                ref={fileInputRef}
                onChange={handleFileChange}
                accept="image/*"
              />
            </div>
          </div>

          <div className="controls-section">
            <div className="config-group">
              <label className="label">Model</label>
              <select
                className="select-field"
                value={modelId}
                onChange={(e) => setModelId(e.target.value)}
              >
                {config?.IMAGEN_UPSCALE_MODELS?.map(m => (
                  <option key={m} value={m}>{m}</option>
                )) || <option value="imagen-4.0-upscale-preview">Imagen 4.0 Upscale</option>}
              </select>
            </div>

            <div className="config-group">
              <label className="label">Upscale Factor</label>
              <select
                className="select-field"
                value={upscaleFactor}
                onChange={(e) => setUpscaleFactor(e.target.value)}
              >
                <option value="x2">2x Resolution</option>
                <option value="x3">3x Resolution</option>
                <option value="x4">4x Resolution</option>
              </select>
              <p style={{ fontSize: '0.8rem', opacity: 0.6, marginTop: '0.5rem' }}>
                <AlertCircle size={12} style={{ verticalAlign: 'middle', marginRight: '4px' }} />
                Final resolution must not exceed 17 megapixels.
              </p>
            </div>

            <button
              className="btn"
              onClick={handleUpscale}
              disabled={isLoading || !file}
              style={{ marginTop: '2rem' }}
            >
              {isLoading ? (
                <>
                  <div className="spinner" style={{ marginRight: '10px' }}></div>
                  Upscaling...
                </>
              ) : 'Start High-Fidelity Upscale'}
            </button>

            {error && (
              <div className="error-box" style={{ marginTop: '1.5rem' }}>
                {error}
              </div>
            )}
          </div>
        </div>

        {result && (
          <div style={{ marginTop: '3.5rem', animation: 'fadeInUp 0.6s ease-out forwards' }}>
            <div className="flex-between" style={{ marginBottom: '1.5rem' }}>
              <h3 style={{ margin: 0, display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <Maximize2 size={20} className="text-secondary" />
                Upscaled Result
              </h3>
            </div>
            <div className="image-container" style={{ position: 'relative' }}>
              <img
                src={`data:${result.mime_type};base64,${result.data}`}
                alt="Upscaled"
                style={{ width: '100%', display: 'block' }}
              />
              <div style={{
                position: 'absolute',
                bottom: '1.5rem',
                right: '1.5rem',
                display: 'flex',
                gap: '0.75rem'
              }}>
                <a
                  href={`data:${result.mime_type};base64,${result.data}`}
                  download={`upscaled-${upscaleFactor}.png`}
                  className="btn-secondary"
                  style={{
                    padding: '0.6rem 1.25rem',
                    background: 'rgba(15, 23, 42, 0.85)',
                    backdropFilter: 'blur(12px)',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                    fontSize: '0.9rem',
                    border: '1px solid var(--glass-border)'
                  }}
                >
                  <Download size={16} /> Download
                </a>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ImageUpscalePanel;
