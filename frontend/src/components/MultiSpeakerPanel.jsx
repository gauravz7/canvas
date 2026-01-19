import React, { useState, useEffect } from 'react';
import { Plus, Trash2 } from 'lucide-react';
import WaveformPlayer from './WaveformPlayer';
import { useConfig } from '../contexts/ConfigContext';

const MOCK_VOICES = ["Kore", "Leda", "Puck", "Charon", "Fenrir", "Aoede"];

const INITIAL_TURNS = [
  { speaker: "Sam", text: "Hi Bob, how are you?" },
  { speaker: "Bob", text: "I am doing well, thanks! And you?" }
];

const INITIAL_SPEAKER_MAP = {
  "Sam": "Kore",
  "Bob": "Charon"
};

const MultiSpeakerPanel = () => {
  const { config } = useConfig();
  const [turns, setTurns] = useState(INITIAL_TURNS);
  const [speakerMap, setSpeakerMap] = useState(INITIAL_SPEAKER_MAP);
  const [model, setModel] = useState(config?.DEFAULT_TTS_MODEL || "gemini-2.5-flash-tts");

  useEffect(() => {
    if (config?.DEFAULT_TTS_MODEL) {
      setModel(config.DEFAULT_TTS_MODEL);
    }
  }, [config]);
  const [prompt, setPrompt] = useState("Say the following as a conversation between friends.");
  const [loading, setLoading] = useState(false);
  const [audioSrc, setAudioSrc] = useState(null);
  const [error, setError] = useState(null);

  const addTurn = () => {
    setTurns([...turns, { speaker: "Sam", text: "" }]);
  };

  const removeTurn = (index) => {
    const newTurns = turns.filter((_, i) => i !== index);
    setTurns(newTurns);
  };

  const updateTurn = (index, field, value) => {
    const newTurns = [...turns];
    newTurns[index][field] = value;
    setTurns(newTurns);

    // Auto-add to speaker map if new speaker
    if (field === "speaker" && value && !speakerMap[value]) {
      setSpeakerMap(prev => ({ ...prev, [value]: "Kore" }));
    }
  };

  const handleSynthesize = async () => {
    setLoading(true);
    setError(null);
    setAudioSrc(null);

    try {
      const response = await fetch('/api/synthesize/multi', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          turns,
          prompt,
          speaker_map: speakerMap,
          model_id: model,
          user_id: localStorage.getItem('gemini_user_id') || 'default_user'
        }),
      });

      if (!response.ok) throw new Error(`Error: ${response.statusText}`);

      const data = await response.json();
      if (data.audioContent) {
        const binaryString = window.atob(data.audioContent);
        const len = binaryString.length;
        const bytes = new Uint8Array(len);
        for (let i = 0; i < len; i++) bytes[i] = binaryString.charCodeAt(i);
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

  const uniqueSpeakers = Array.from(new Set(turns.map(t => t.speaker))).filter(Boolean);

  return (
    <div className="glass-panel">
      <h2 style={{ marginBottom: '1.5rem' }}>Multi-Speaker (Unary)</h2>

      <div style={{ display: 'grid', gap: '1rem', marginBottom: '1.5rem' }}>
        <div>
          <label className="label">Model</label>
          <select value={model} onChange={(e) => setModel(e.target.value)} className="select-field">
            {config?.TTS_MODELS?.map(m => (
              <option key={m} value={m}>{m}</option>
            )) || (
                <>
                  <option value="gemini-2.5-flash-tts">Gemini 2.5 Flash</option>
                  <option value="gemini-2.5-pro-tts">Gemini 2.5 Pro</option>
                </>
              )}
          </select>
        </div>

        <div>
          <label className="label">Style Prompt</label>
          <input
            type="text"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            className="input-field"
          />
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '1rem', marginBottom: '1.5rem', background: 'rgba(0,0,0,0.2)', padding: '1rem', borderRadius: '0.5rem' }}>
          {uniqueSpeakers.map(speaker => (
            <div key={speaker}>
              <label className="label">Voice for {speaker}</label>
              <select
                value={speakerMap[speaker] || "Kore"}
                onChange={(e) => setSpeakerMap(prev => ({ ...prev, [speaker]: e.target.value }))}
                className="select-field"
              >
                {config?.TTS_VOICES?.map(v => <option key={v} value={v}>{v}</option>) || MOCK_VOICES.map(v => <option key={v} value={v}>{v}</option>)}
              </select>
            </div>
          ))}
        </div>

        <div className="config-group" style={{ marginBottom: '1.5rem' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {turns.map((turn, i) => (
              <div key={i} style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
                <input
                  type="text"
                  placeholder="Speaker"
                  value={turn.speaker}
                  onChange={(e) => updateTurn(i, 'speaker', e.target.value)}
                  className="input-field"
                  style={{ width: '150px' }}
                />
                <input
                  type="text"
                  placeholder="Text"
                  value={turn.text}
                  onChange={(e) => updateTurn(i, 'text', e.target.value)}
                  className="input-field"
                  style={{ flex: 1 }}
                />
                <button
                  className="btn-secondary"
                  onClick={() => removeTurn(i)}
                  style={{ padding: '0.75rem', color: '#ef4444', borderColor: 'rgba(239, 68, 68, 0.2)' }}
                  title="Remove Turn"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            ))}
            <button className="btn-secondary" onClick={addTurn} style={{ alignSelf: 'flex-start' }}>
              <Plus size={16} /> Add Turn
            </button>
          </div>
        </div>

        <button className="btn" onClick={handleSynthesize} disabled={loading || turns.length === 0}>
          {loading ? <div className="spinner"></div> : "Synthesize Conversation"}
        </button>

        {error && <div style={{ color: '#ef4444', marginTop: '1rem' }}>{error}</div>}

        <WaveformPlayer src={audioSrc} />
      </div>
    </div>
  );
};

export default MultiSpeakerPanel;
