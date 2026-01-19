import React, { useState, useEffect } from 'react';
import WaveformPlayer from './WaveformPlayer';
import { useConfig } from '../contexts/ConfigContext';

const MOCK_VOICES = ["Kore", "Leda", "Puck", "Charon", "Fenrir", "Aoede", "Zephyr"];

const SingleSpeakerPanel = () => {
  const { config } = useConfig();
  const [text, setText] = useState("Gemini-TTS is the latest evolution of our Cloud TTS technology.");
  const [prompt, setPrompt] = useState("");
  const [voice, setVoice] = useState(config?.DEFAULT_TTS_VOICE || "Kore");
  const [model, setModel] = useState(config?.DEFAULT_TTS_MODEL || "gemini-2.5-flash-tts");

  useEffect(() => {
    if (config?.DEFAULT_TTS_MODEL) setModel(config.DEFAULT_TTS_MODEL);
    if (config?.DEFAULT_TTS_VOICE) setVoice(config.DEFAULT_TTS_VOICE);
  }, [config]);
  const [loading, setLoading] = useState(false);
  const [audioSrc, setAudioSrc] = useState(null);
  const [error, setError] = useState(null);

  const handleSynthesize = async () => {
    setLoading(true);
    setError(null);
    setAudioSrc(null);

    try {
      const response = await fetch('/api/synthesize/single', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text,
          prompt: prompt || undefined,
          voice_name: voice,
          model_id: model,
          user_id: localStorage.getItem('gemini_user_id') || 'default_user'
        }),
      });

      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`);
      }

      const data = await response.json();
      if (data.audioContent) {
        const binaryString = window.atob(data.audioContent);
        const len = binaryString.length;
        const bytes = new Uint8Array(len);
        for (let i = 0; i < len; i++) {
          bytes[i] = binaryString.charCodeAt(i);
        }
        const blob = new Blob([bytes], { type: 'audio/wav' });
        setAudioSrc(window.URL.createObjectURL(blob));
      } else {
        throw new Error("No audio content received");
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass-panel">
      <h2 style={{ marginBottom: '1.5rem' }}>Single Speaker (Unary)</h2>

      <div style={{ display: 'grid', gap: '1rem', marginBottom: '1.5rem' }}>
        <div>
          <label className="label">Model</label>
          <select value={model} onChange={(e) => setModel(e.target.value)} className="select-field">
            {config?.TTS_MODELS?.map(m => (
              <option key={m} value={m}>{m}</option>
            )) || (
                <option value="gemini-2.5-flash-tts">Gemini 2.5 Flash</option>
              )}
          </select>
        </div>

        <div>
          <label className="label">Voice</label>
          <select value={voice} onChange={(e) => setVoice(e.target.value)} className="select-field">
            {config?.TTS_VOICES?.map(v => <option key={v} value={v}>{v}</option>) || MOCK_VOICES.map(v => <option key={v} value={v}>{v}</option>)}
          </select>
        </div>

        <div>
          <label className="label">Style Prompt (Optional)</label>
          <input
            type="text"
            placeholder="e.g. Say this in a excited way"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            className="input-field"
          />
        </div>

        <div>
          <label className="label">Text</label>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            rows={5}
            className="textarea-field"
          />
        </div>
      </div>

      <button className="btn" onClick={handleSynthesize} disabled={loading || !text}>
        {loading ? <div className="spinner"></div> : "Synthesize"}
      </button>

      {error && <div style={{ color: '#ef4444', marginTop: '1rem' }}>{error}</div>}

      <WaveformPlayer src={audioSrc} />
    </div>
  );
};

export default SingleSpeakerPanel;
