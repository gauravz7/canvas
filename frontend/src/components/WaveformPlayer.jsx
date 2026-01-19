import React, { useRef, useEffect, useState } from 'react';
import { Play, Pause, Download, Volume2, VolumeX } from 'lucide-react';

const WaveformPlayer = ({ src, mimeType = 'audio/wav' }) => {
  const audioRef = useRef(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [isMuted, setIsMuted] = useState(false);
  const [bars, setBars] = useState([]);

  // Generate random bars for visualization
  useEffect(() => {
    setBars(Array.from({ length: 40 }, () => Math.random() * 0.5 + 0.3));
  }, [src]);

  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.pause();
      setIsPlaying(false);
      setCurrentTime(0);
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

  const toggleMute = () => {
    if (audioRef.current) {
      audioRef.current.muted = !isMuted;
      setIsMuted(!isMuted);
    }
  };

  const handleTimeUpdate = () => {
    if (audioRef.current) {
      setCurrentTime(audioRef.current.currentTime);
    }
  };

  const handleLoadedMetadata = () => {
    if (audioRef.current) {
      setDuration(audioRef.current.duration);
    }
  };

  const onEnded = () => setIsPlaying(false);

  const formatTime = (time) => {
    const min = Math.floor(time / 60);
    const sec = Math.floor(time % 60);
    return `${min}:${sec.toString().padStart(2, '0')}`;
  };

  if (!src) return null;

  return (
    <div className="glass-panel" style={{
      marginTop: '1.5rem',
      padding: '1.25rem',
      background: 'rgba(255, 255, 255, 0.03)',
      border: '1px solid var(--glass-border)',
      borderRadius: '1.25rem'
    }}>
      <audio
        ref={audioRef}
        src={src}
        type={mimeType}
        onTimeUpdate={handleTimeUpdate}
        onLoadedMetadata={handleLoadedMetadata}
        onEnded={onEnded}
      />

      <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
        <button
          className="btn"
          onClick={togglePlay}
          style={{
            borderRadius: '50%',
            width: '3.5rem',
            height: '3.5rem',
            padding: 0,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: 'linear-gradient(135deg, var(--accent-primary), var(--accent-secondary))',
            boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
            border: 'none'
          }}
        >
          {isPlaying ? <Pause fill="white" size={20} /> : <Play fill="white" size={20} style={{ marginLeft: '2px' }} />}
        </button>

        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          {/* Waveform Visualizer */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '3px',
            height: '2rem',
            maskImage: 'linear-gradient(to right, transparent, black 10%, black 90%, transparent)'
          }}>
            {bars.map((height, i) => (
              <div
                key={i}
                style={{
                  flex: 1,
                  background: isPlaying ? 'var(--accent-primary)' : 'var(--text-secondary)',
                  height: isPlaying
                    ? `${Math.max(20, height * 100 * (Math.sin(Date.now() / 200 + i) + 1.5) / 2)}%`
                    : '20%',
                  borderRadius: '999px',
                  opacity: 0.8,
                  transition: 'all 0.2s ease',
                  animation: isPlaying ? `bounce 0.8s ease-in-out infinite alternate` : 'none',
                  animationDelay: `${i * 0.05}s`
                }}
              />
            ))}
          </div>

          {/* Progress Bar & Time */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', fontSize: '0.75rem', color: 'var(--text-secondary)', fontWeight: 500 }}>
            <span>{formatTime(currentTime)}</span>
            <div style={{
              flex: 1,
              height: '4px',
              background: 'rgba(255,255,255,0.1)',
              borderRadius: '2px',
              position: 'relative',
              overflow: 'hidden'
            }}>
              <div style={{
                width: `${(currentTime / duration) * 100}%`,
                height: '100%',
                background: 'var(--accent-primary)',
                borderRadius: '2px'
              }} />
            </div>
            <span>{formatTime(duration)}</span>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button
            className="btn-secondary"
            onClick={toggleMute}
            style={{ padding: '0.6rem', background: 'rgba(255,255,255,0.05)', border: 'none' }}
          >
            {isMuted ? <VolumeX size={18} /> : <Volume2 size={18} />}
          </button>

          <a
            href={src}
            download="generated_audio.wav"
            className="btn-secondary"
            style={{ padding: '0.6rem', background: 'rgba(255,255,255,0.05)', border: 'none', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
          >
            <Download size={18} />
          </a>
        </div>
      </div>

      <style>{`
        @keyframes bounce {
          0% { transform: scaleY(0.5); }
          100% { transform: scaleY(1.5); }
        }
      `}</style>
    </div>
  );
};

export default WaveformPlayer;
