import React, { useState, useEffect, useRef } from 'react';
import { Terminal, X } from 'lucide-react';

const LogPanel = () => {
  const [logs, setLogs] = useState([]);
  const [isOpen, setIsOpen] = useState(false);
  const scrollRef = useRef(null);

  useEffect(() => {
    if (!isOpen) return;

    // Fetch initial logs
    const fetchInitial = async () => {
      try {
        const res = await fetch('/api/logs?limit=50');
        if (res.ok) {
          const data = await res.json();
          setLogs(data);
        }
      } catch (e) {
        console.error("Initial log fetch failed", e);
      }
    };
    fetchInitial();

    // Setup real-time stream
    let eventSource = null;
    let retryTimeout = null;

    const connect = () => {
      eventSource = new EventSource('/api/logs/stream');

      eventSource.onopen = () => {
        console.log("Log stream connected");
      };

      eventSource.onmessage = (event) => {
        try {
          const newLog = JSON.parse(event.data);
          setLogs(prev => [...prev.slice(-49), newLog]);
        } catch (e) {
          console.error("Failed to parse log entry", e);
        }
      };

      eventSource.onerror = (err) => {
        console.warn("EventSource failed, retrying in 5s...", err);
        eventSource.close();
        // Simple retry logic
        retryTimeout = setTimeout(connect, 5000);
      };
    };

    connect();

    return () => {
      if (eventSource) eventSource.close();
      if (retryTimeout) clearTimeout(retryTimeout);
    };
  }, [isOpen]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs]);

  if (!isOpen) {
    return (
      <button
        className="btn"
        style={{
          position: 'fixed',
          bottom: '2rem',
          right: '2rem',
          zIndex: 100,
          borderRadius: '1.25rem',
          width: '3.75rem',
          height: '3.75rem',
          padding: 0,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 20px 40px -12px rgba(0, 0, 0, 0.5), 0 0 30px var(--glow-color)',
          border: '1px solid var(--accent-primary)',
          background: 'rgba(16, 185, 129, 0.15)',
          backdropFilter: 'blur(16px)',
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
        }}
        onClick={() => setIsOpen(true)}
        title="Open System Logs"
      >
        <Terminal size={24} className="spinner" style={{ animationDuration: '4s' }} />
      </button>
    );
  }

  return (
    <div className="log-panel-container" style={{
      position: 'fixed',
      bottom: '2rem',
      right: '2rem',
      width: '480px',
      height: '400px',
      zIndex: 100,
      display: 'flex',
      flexDirection: 'column',
      backdropFilter: 'blur(32px)',
    }}>
      <div style={{
        padding: '1.25rem 1.5rem',
        borderBottom: '1px solid var(--glass-border)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        background: 'rgba(255,255,255,0.02)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <Terminal size={18} color="var(--accent-primary)" />
          <span style={{ fontWeight: '800', fontSize: '0.75rem', letterSpacing: '0.1em', color: 'var(--text-primary)' }}>TELEMETRY STREAM</span>
        </div>
        <button
          onClick={() => setIsOpen(false)}
          className="bare-input"
          style={{ cursor: 'pointer', opacity: 0.6, display: 'flex', transition: 'opacity 0.2s' }}
          onMouseEnter={(e) => e.currentTarget.style.opacity = '1'}
          onMouseLeave={(e) => e.currentTarget.style.opacity = '0.6'}
        >
          <X size={20} />
        </button>
      </div>
      <div className="log-content" ref={scrollRef} style={{
        flex: 1,
        overflowY: 'auto',
        padding: '1.25rem',
        fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
        fontSize: '0.75rem',
        display: 'flex',
        flexDirection: 'column',
        gap: '0.5rem'
      }}>
        {logs.map((log, i) => (
          <div key={i} className="log-entry" style={{
            background: log.level === 'ERROR' ? 'rgba(239, 68, 68, 0.08)' : 'transparent',
            borderLeft: log.level === 'ERROR' ? '2px solid #ef4444' : 'none'
          }}>
            <span style={{ color: 'var(--text-secondary)', opacity: 0.5, minWidth: '4.5rem' }}>
              {new Date(log.timestamp).toLocaleTimeString([], { hour12: false })}
            </span>
            <span style={{
              color: log.level === 'ERROR' ? '#ef4444' : log.level === 'WARNING' ? '#eab308' : 'var(--accent-primary)',
              fontWeight: '800',
              minWidth: '3.5rem',
              textAlign: 'center',
              fontSize: '0.7rem'
            }}>{log.level}</span>
            <span style={{ color: 'var(--accent-secondary)', opacity: 0.8, fontWeight: '600' }}>
              {log.source.toLowerCase()}
            </span>
            <span style={{ color: '#f1f5f9', flex: 1, wordBreak: 'break-word', opacity: 0.9 }}>{log.message}</span>
          </div>
        ))}
        {logs.length === 0 && (
          <div style={{ color: 'var(--text-secondary)', textAlign: 'center', marginTop: '4rem', opacity: 0.5 }}>
            <Terminal size={24} style={{ marginBottom: '0.5rem', opacity: 0.2 }} />
            <p>Awaiting system telemetry...</p>
          </div>
        )}
      </div>
    </div>
  );
};


export default LogPanel;
