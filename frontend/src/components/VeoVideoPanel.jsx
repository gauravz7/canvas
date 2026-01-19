import React, { useRef, useEffect, useState } from 'react';
import { Video, Film, Sparkles, Sliders, Image as ImageIcon } from 'lucide-react';
import { useConfig } from '../contexts/ConfigContext';
import { useVeoGeneration } from '../hooks/useVeoGeneration';
import MediaInput from './common/MediaInput';

const VeoVideoPanel = ({ userId }) => {
  const { config } = useConfig();
  const { state, generateVideo } = useVeoGeneration(userId, config);

  const {
    activeMode, setActiveMode,
    modelId, setModelId,
    prompt, setPrompt,
    negativePrompt, setNegativePrompt,
    duration, setDuration,
    aspectRatio, setAspectRatio,
    resolution, setResolution,
    generateAudio, setGenerateAudio,
    isLoading,
    result,
    error
  } = state;

  // Media Inputs State
  const [firstFrameFile, setFirstFrameFile] = useState(null);
  const [firstFrameUri, setFirstFrameUri] = useState('');
  const [lastFrameFile, setLastFrameFile] = useState(null);
  const [lastFrameUri, setLastFrameUri] = useState('');
  const [videoFile, setVideoFile] = useState(null);
  const [videoUri, setVideoUri] = useState('');
  const [referenceFiles, setReferenceFiles] = useState([]);
  const [referenceUris, setReferenceUris] = useState('');

  const firstFrameRef = useRef(null);
  const lastFrameRef = useRef(null);
  const videoInputRef = useRef(null);
  const refsInputRef = useRef(null);

  useEffect(() => {
    if (config?.DEFAULT_VEO_MODEL) {
      setModelId(config.DEFAULT_VEO_MODEL);
    }
  }, [config, setModelId]);

  const onGenerate = () => {
    generateVideo({
      firstFrameFile, firstFrameUri,
      lastFrameFile, lastFrameUri,
      videoFile, videoUri,
      referenceFiles, referenceUris
    });
  };

  return (
    <div className="panel veo-panel">
      <div className="panel-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div style={{
            background: 'linear-gradient(135deg, #4285F4, #EA4335)',
            padding: '0.75rem',
            borderRadius: '1rem',
            boxShadow: '0 4px 12px rgba(66, 133, 244, 0.3)'
          }}>
            <Video className="icon" size={28} color="white" />
          </div>
          <div>
            <h2>Veo Video Studio</h2>
            <p>Generate cinematic videos with Google's state-of-the-art Veo models.</p>
          </div>
        </div>
      </div>

      <div className="panel-content">
        {/* Left Column: Configuration */}
        <div className="config-column">
          {/* Mode Selection */}
          <div className="modern-tabs">
            {['standard', 'extension', 'subject'].map((mode) => (
              <button
                key={mode}
                className={`modern-tab ${activeMode === mode ? 'active' : ''}`}
                onClick={() => setActiveMode(mode)}
              >
                {mode.charAt(0).toUpperCase() + mode.slice(1)}
              </button>
            ))}
          </div>

          {/* Prompt Section */}
          <div className="modern-input-group">
            <div className="section-title"><Sparkles size={16} /> Describe your video</div>
            <textarea
              className="modern-textarea"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="A cinematic drone shot of a futuristic city..."
              rows={4}
            />
          </div>

          {/* Media Inputs Grid */}
          <div className="config-section">
            <div className="section-title"><Film size={16} /> Input Media</div>

            {activeMode === 'standard' && (
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <MediaInput
                  label="First Frame"
                  file={firstFrameFile} setFile={setFirstFrameFile}
                  uri={firstFrameUri} setUri={setFirstFrameUri}
                  inputRef={firstFrameRef}
                />
                <MediaInput
                  label="Last Frame"
                  file={lastFrameFile} setFile={setLastFrameFile}
                  uri={lastFrameUri} setUri={setLastFrameUri}
                  inputRef={lastFrameRef}
                />
              </div>
            )}

            {activeMode === 'extension' && (
              <MediaInput
                label="Input Video"
                type="video"
                file={videoFile} setFile={setVideoFile}
                uri={videoUri} setUri={setVideoUri}
                inputRef={videoInputRef}
              />
            )}

            {activeMode === 'subject' && (
              <MediaInput
                label="Reference Images (Max 3)"
                maxFiles={3}
                files={referenceFiles} setFiles={setReferenceFiles}
                uri={referenceUris} setUri={setReferenceUris}
                inputRef={refsInputRef}
              />
            )}
          </div>

          {/* Advanced Settings */}
          <div className="config-section">
            <div className="section-title"><Sliders size={16} /> Parameters</div>
            <div style={{ display: 'grid', gridTemplateColumns: 'minmax(140px, 1fr) 1fr', gap: '1.5rem', alignItems: 'center' }}>

              <div className="config-group">
                <label className="label">Model</label>
                <select
                  className="modern-select"
                  value={modelId}
                  onChange={(e) => setModelId(e.target.value)}
                >
                  {(config?.VEO_MODELS || []).map(m => (
                    <option key={m} value={m}>{m}</option>
                  ))}
                </select>
              </div>

              <div className="config-group">
                <label className="label" style={{ display: 'flex', justifyContent: 'space-between' }}>
                  Duration <span>{duration}s</span>
                </label>
                <input
                  type="range"
                  className="modern-range"
                  value={duration}
                  onChange={(e) => setDuration(Number(e.target.value))}
                  min={1} max={60}
                />
              </div>

              <div className="config-group">
                <label className="label">Aspect Ratio</label>
                <select
                  className="modern-select"
                  value={aspectRatio}
                  onChange={(e) => setAspectRatio(e.target.value)}
                >
                  <option value="16:9">16:9 (Landscape)</option>
                  <option value="9:16">9:16 (Portrait)</option>
                  <option value="1:1">1:1 (Square)</option>
                </select>
              </div>

              <div className="config-group">
                <label className="label">Resolution</label>
                <select
                  className="modern-select"
                  value={resolution}
                  onChange={(e) => setResolution(e.target.value)}
                >
                  <option value="720p">720p (HD)</option>
                  <option value="1080p">1080p (FHD)</option>
                </select>
              </div>

            </div>

            <div style={{ display: 'flex', gap: '2rem', marginTop: '1.5rem' }}>
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={generateAudio}
                  onChange={(e) => setGenerateAudio(e.target.checked)}
                />
                <span style={{ fontWeight: 600 }}>Generate Audio</span>
              </label>
            </div>

            <div style={{ marginTop: '1.5rem' }}>
              <label className="label">Negative Prompt</label>
              <input
                type="text"
                className="glass-input"
                placeholder="Blurry, distorted, low quality..."
                value={negativePrompt}
                onChange={(e) => setNegativePrompt(e.target.value)}
              />
            </div>
          </div>

          <button
            className="primary-action-btn"
            onClick={onGenerate}
            disabled={isLoading || !prompt}
          >
            {isLoading ? (
              <>
                <div className="spinner-small"></div>
                Generating Cinematic Video...
              </>
            ) : (
              <>
                <Sparkles size={20} />
                Generate Video
              </>
            )}
          </button>

          {error && (
            <div className="error-message" style={{ marginTop: '1rem' }}>
              {error}
            </div>
          )}
        </div>

        {/* Right Column: Preview/Results */}
        <div className="preview-column">
          <div className="section-title">Output</div>
          {/* Results */}
          {result && result.videos ? (
            <div className="result-feed">
              {result.videos.map((video, idx) => (
                <div key={idx} className="result-card">
                  <video
                    controls
                    autoPlay
                    loop
                    src={video.url}
                    className="video-player"
                    onError={(e) => console.error("Video load error:", e)}
                  />
                  <div className="video-info">
                    <a href={video.url} download={`veo_gen_${idx}.mp4`} className="download-link">Download MP4</a>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div style={{
              height: '300px',
              border: '1px dashed var(--glass-border)',
              borderRadius: '1rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--text-secondary)',
              flexDirection: 'column',
              gap: '1rem',
              background: 'rgba(0,0,0,0.2)'
            }}>
              <Film size={48} style={{ opacity: 0.2 }} />
              <p style={{ opacity: 0.6 }}>Your generated videos will appear here</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default VeoVideoPanel;
