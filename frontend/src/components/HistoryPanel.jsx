import React, { useState, useEffect } from 'react';
import { Clock, Image as ImageIcon, Video, FileAudio, Download, ExternalLink } from 'lucide-react';
import WaveformPlayer from './WaveformPlayer';

const HistoryPanel = ({ userId }) => {
  const [assets, setAssets] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (userId) {
      fetchHistory();
    }
  }, [userId]);

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const res = await fetch(`/api/history/${userId}?limit=50`);
      if (res.ok) {
        const data = await res.json();
        setAssets(data);
      }
    } catch (err) {
      console.error("Failed to fetch history", err);
    } finally {
      setLoading(false);
    }
  };

  const getIcon = (type) => {
    if (type === 'image') return <ImageIcon size={16} />;
    if (type === 'video') return <Video size={16} />;
    if (type === 'audio') return <FileAudio size={16} />;
    return <Clock size={16} />;
  };

  const getAssetSrc = (asset) => {
    if (asset.signed_url) {
      return asset.signed_url;
    }
    if (asset.storage_path && asset.storage_path?.startsWith?.('gs://')) {
      return null;
    }
    return `/data/assets/${asset.storage_path}`;
  };

  const renderAssetPreview = (asset) => {
    const src = getAssetSrc(asset);

    if (!src) {
      return (
        <div className="asset-placeholder glass">
          <p>GCS Asset</p>
          <code style={{ fontSize: '0.7em' }}>{asset.filename}</code>
        </div>
      );
    }

    if (asset.asset_type === 'image') {
      return <img src={src} alt={asset.prompt} loading="lazy" />;
    } else if (asset.asset_type === 'video') {
      return (
        <video
          src={src}
          className="history-video"
          muted
          onMouseOver={e => e.target.play()}
          onMouseOut={e => { e.target.pause(); e.target.currentTime = 0; }}
          loop
        />
      );
    } else if (asset.asset_type === 'audio') {
      return (
        <div style={{ padding: '0.75rem', width: '100%' }}>
          <WaveformPlayer src={src} mimeType={asset.mime_type} />
        </div>
      );
    } else {
      return <div className="asset-generic">{asset.asset_type}</div>;
    }
  };

  return (
    <div className="studio-container">
      <div className="studio-header">
        <div>
          <h2 style={{ margin: 0 }}>Studio History</h2>
          <p style={{ marginTop: '0.5rem', opacity: 0.7 }}>Browse and manage your creative workspace assets</p>
        </div>
        <button
          onClick={fetchHistory}
          className="btn-secondary"
          style={{ padding: '0.6rem 1.25rem', fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}
        >
          <Clock size={16} /> Refresh Library
        </button>
      </div>

      <div className="studio-content-area">
        <div className="studio-scroll-container">
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
            gap: '1.25rem',
            paddingRight: '0.5rem'
          }}>
            {assets.map((asset) => {
              const src = getAssetSrc(asset);
              return (
                <div key={asset.id} className="asset-card">
                  <div className="asset-preview" style={{
                    aspectRatio: asset.asset_type === 'audio' ? 'auto' : '16/9',
                    padding: asset.asset_type === 'audio' ? '0' : undefined
                  }}>
                    {renderAssetPreview(asset)}
                    <div className="asset-badge">
                      {getIcon(asset.asset_type)} {asset.asset_type}
                    </div>
                  </div>

                  <div className="asset-info" style={{ padding: '0.75rem' }}>
                    <div className="asset-timestamp">
                      {new Date(asset.created_at).toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' })}
                    </div>

                    {asset.prompt && (
                      <p className="asset-prompt" title={asset.prompt} style={{ fontSize: '0.75rem', marginBottom: '0.5rem' }}>
                        {asset.prompt}
                      </p>
                    )}

                    <div className="asset-footer" style={{ marginTop: '0.5rem', paddingTop: '0.5rem' }}>
                      <span style={{ fontSize: '0.65rem', color: 'var(--accent-secondary)', fontWeight: '600', letterSpacing: '0.02em', opacity: 0.8 }}>
                        {asset.model_id || 'System Generated'}
                      </span>

                      {src && (
                        <div style={{ display: 'flex', gap: '0.5rem' }}>
                          <a
                            href={src}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="btn-secondary"
                            style={{ padding: '0.3rem', borderRadius: '0.4rem' }}
                            title="Open in new tab"
                          >
                            <ExternalLink size={12} />
                          </a>
                          <a
                            href={src}
                            download={`asset-${asset.id}.${asset.asset_type === 'image' ? 'png' : 'wav'}`}
                            className="btn-secondary"
                            style={{ padding: '0.3rem', borderRadius: '0.4rem' }}
                            title="Download"
                          >
                            <Download size={12} />
                          </a>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}

            {assets.length === 0 && !loading && (
              <div style={{
                gridColumn: '1/-1',
                textAlign: 'center',
                padding: '4rem 2rem',
                background: 'rgba(255,255,255,0.02)',
                borderRadius: '1.5rem',
                border: '1px dashed var(--glass-border)',
                color: 'var(--text-secondary)'
              }}>
                <ImageIcon size={48} style={{ opacity: 0.1, marginBottom: '1rem' }} />
                <p>Your creative library is empty</p>
                <p style={{ fontSize: '0.8rem', opacity: 0.6 }}>Generated assets will automatically appear here</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};


export default HistoryPanel;
