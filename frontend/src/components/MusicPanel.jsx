
import React, { useState } from 'react';
import { Music, Send, Download, RefreshCw, Sparkles, Zap } from 'lucide-react';
import WaveformPlayer from './WaveformPlayer';

const MusicPanel = ({ userId }) => {
  const [prompt, setPrompt] = useState('An uplifting and hopeful orchestral piece with a soaring string melody and triumphant brass.');
  const [negativePrompt, setNegativePrompt] = useState('dissonant, minor key');
  const [seed, setSeed] = useState(12345);
  const [isLoading, setIsLoading] = useState(false);
  const [audioSrc, setAudioSrc] = useState(null);
  const [error, setError] = useState(null);

  const handleGenerate = async () => {
    setIsLoading(true);
    setError(null);
    setAudioSrc(null);

    const formData = new FormData();
    formData.append('prompt', prompt);
    formData.append('negative_prompt', negativePrompt);
    formData.append('seed', seed);
    formData.append('user_id', userId);

    try {
      const response = await fetch('/api/generate/music', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Music generation failed');
      }

      const data = await response.json();
      if (data.audio && data.audio.data) {
        const binaryString = window.atob(data.audio.data);
        const len = binaryString.length;
        const bytes = new Uint8Array(len);
        for (let i = 0; i < len; i++) {
          bytes[i] = binaryString.charCodeAt(i);
        }
        const blob = new Blob([bytes], { type: data.audio.mime_type || 'audio/wav' });
        setAudioSrc(window.URL.createObjectURL(blob));
      } else {
        throw new Error('No audio data received');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const randomizeSeed = () => {
    setSeed(Math.floor(Math.random() * 1000000));
  };

  return (
    <div className="glass-panel">
      <div className="panel-header">
        <h2 style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <Music className="text-secondary" size={24} />
          Music Studio
        </h2>
        <p>High-fidelity music generation with Lyria-002</p>
      </div>

      <div className="panel-content">
        <div style={{ display: 'grid', gap: '1.5rem' }}>
          <div className="config-group">
            <label className="label">Prompt</label>
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Describe the music you want to generate..."
              rows={4}
              className="textarea-field"
            />
          </div>

          <div className="config-group">
            <label className="label">Negative Prompt (Optional)</label>
            <input
              type="text"
              value={negativePrompt}
              onChange={(e) => setNegativePrompt(e.target.value)}
              placeholder="What to exclude (e.g. vocals, high tempo)"
              className="input-field"
            />
          </div>

          <div className="config-group">
            <label className="label">Seed</label>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <input
                type="number"
                value={seed}
                onChange={(e) => setSeed(parseInt(e.target.value))}
                className="input-field"
                style={{ flex: 1 }}
              />
              <button onClick={randomizeSeed} className="btn-secondary" style={{ padding: '0.75rem' }} title="Randomize Seed">
                <RefreshCw size={18} />
              </button>
            </div>
          </div>

          <button
            className="btn"
            onClick={handleGenerate}
            disabled={isLoading || !prompt}
            style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.75rem' }}
          >
            {isLoading ? (
              <>
                <div className="spinner"></div>
                Generating Harmony...
              </>
            ) : (
              <>
                <Send size={18} />
                Generate 32s Clip
              </>
            )}
          </button>

          {error && (
            <div className="error-box" style={{ marginTop: '1rem' }}>
              {error}
            </div>
          )}

          {audioSrc && (
            <div style={{ marginTop: '2rem', animation: 'fadeInUp 0.6s ease-out' }}>
              <div style={{
                marginBottom: '1.5rem',
                display: 'flex',
                alignItems: 'center',
                gap: '0.75rem',
                justifyContent: 'center'
              }}>
                <Sparkles size={24} className="text-primary" style={{ animation: 'pulse 2s infinite' }} />
                <h3 style={{
                  fontSize: '1.5rem',
                  margin: 0,
                  background: 'linear-gradient(to right, #4285F4, #EA4335, #FBBC05)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  fontWeight: 800,
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em',
                  textShadow: '0 0 30px rgba(66, 133, 244, 0.3)'
                }}>
                  Generated Masterpiece
                </h3>
                <Sparkles size={24} className="text-secondary" style={{ animation: 'pulse 2s infinite', animationDelay: '1s' }} />
              </div>
              <WaveformPlayer src={audioSrc} />

              <style>{`
                @keyframes pulse {
                  0% { transform: scale(1); opacity: 1; }
                  50% { transform: scale(1.2); opacity: 0.7; }
                  100% { transform: scale(1); opacity: 1; }
                }
              `}</style>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MusicPanel;
