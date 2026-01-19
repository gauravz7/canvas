
import React, { useRef, useEffect } from 'react';
import { Play, Pause, Download } from 'lucide-react';

const AudioPlayer = ({ src, mimeType = 'audio/wav' }) => {
  const audioRef = useRef(null);
  const [isPlaying, setIsPlaying] = React.useState(false);

  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.pause();
      setIsPlaying(false);
    }
  }, [src]);

  const togglePlay = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
      } else {
        audioRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const onEnded = () => setIsPlaying(false);

  if (!src) return null;

  return (
    <div className="glass-panel" style={{ marginTop: '1.5rem', display: 'flex', alignItems: 'center', gap: '1rem' }}>
      <audio
        ref={audioRef}
        src={src}
        type={mimeType}
        onEnded={onEnded}
      />

      <button className="btn" onClick={togglePlay} style={{ borderRadius: '50%', padding: '0.75rem' }}>
        {isPlaying ? <Pause size={24} /> : <Play size={24} />}
      </button>

      <div style={{ flex: 1 }}>
        <div style={{ height: '4px', background: 'rgba(255,255,255,0.1)', borderRadius: '2px', overflow: 'hidden' }}>
          {/* Simple visualizer or progress bar could go here */}
          <div style={{ width: isPlaying ? '100%' : '0%', height: '100%', background: 'var(--accent-color)', transition: 'width 0.2s', animation: isPlaying ? 'progress 2s linear infinite' : 'none' }}></div>
        </div>
      </div>

      <a href={src} download="generated_audio.wav" className="btn" style={{ background: 'transparent', border: '1px solid var(--glass-border)' }}>
        <Download size={20} />
      </a>

      <style>{`
        @keyframes progress {
          0% { width: 0%; opacity: 0.5; }
          50% { width: 50%; opacity: 1; }
          100% { width: 100%; opacity: 0.5; }
        }
      `}</style>
    </div>
  );
};

export default AudioPlayer;
