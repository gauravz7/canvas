import React, { useState, useEffect, useMemo, useCallback } from 'react';
import {
  Clock,
  Image as ImageIcon,
  Video,
  FileAudio,
  Download,
  ExternalLink,
  Search,
  LayoutGrid,
  List,
  ChevronDown,
  ChevronUp,
  Filter,
} from 'lucide-react';
import WaveformPlayer from './WaveformPlayer';
import { apiFetch } from '../utils/api';

const FILTER_TABS = [
  { id: 'all', label: 'All', icon: Filter },
  { id: 'image', label: 'Images', icon: ImageIcon },
  { id: 'video', label: 'Videos', icon: Video },
  { id: 'audio', label: 'Audio', icon: FileAudio },
];

const HistoryPanel = ({ userId }) => {
  const [assets, setAssets] = useState([]);
  const [loading, setLoading] = useState(false);
  const [assetFilter, setAssetFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [viewMode, setViewMode] = useState('grid');
  const [expandedPrompts, setExpandedPrompts] = useState(new Set());

  useEffect(() => {
    fetchHistory();
  }, [userId, assetFilter]);

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const url =
        assetFilter === 'all'
          ? '/api/history?limit=100'
          : `/api/history?limit=100&asset_type=${assetFilter}`;
      const res = await apiFetch(url);
      if (res.ok) {
        const data = await res.json();
        setAssets(data);
      }
    } catch (err) {
      console.error('Failed to fetch history', err);
    } finally {
      setLoading(false);
    }
  };

  const filteredAssets = useMemo(() => {
    if (!searchQuery) return assets;
    const q = searchQuery.toLowerCase();
    return assets.filter(
      (a) =>
        (a.prompt && a.prompt.toLowerCase().includes(q)) ||
        (a.model_id && a.model_id.toLowerCase().includes(q)) ||
        (a.filename && a.filename.toLowerCase().includes(q))
    );
  }, [assets, searchQuery]);

  const togglePromptExpand = useCallback((id) => {
    setExpandedPrompts((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  }, []);

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
    return `/api/media/${asset.storage_path}`;
  };

  const getDownloadExt = (asset) => {
    if (asset.mime_type) {
      if (asset.mime_type.includes('png')) return 'png';
      if (asset.mime_type.includes('jpeg') || asset.mime_type.includes('jpg')) return 'jpg';
      if (asset.mime_type.includes('mp4')) return 'mp4';
      if (asset.mime_type.includes('wav')) return 'wav';
      if (asset.mime_type.includes('mp3')) return 'mp3';
    }
    if (asset.asset_type === 'image') return 'png';
    if (asset.asset_type === 'video') return 'mp4';
    if (asset.asset_type === 'audio') return 'wav';
    return 'bin';
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
      return <img src={src} alt={asset.prompt || 'Generated image'} loading="lazy" />;
    } else if (asset.asset_type === 'video') {
      return (
        <video
          src={src}
          className="history-video"
          muted
          onMouseOver={(e) => e.target.play()}
          onMouseOut={(e) => {
            e.target.pause();
            e.target.currentTime = 0;
          }}
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

  const formatTimestamp = (ts) => {
    const date = new Date(ts);
    const now = new Date();
    const diffMs = now - date;
    const diffMin = Math.floor(diffMs / 60000);
    const diffHr = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMin < 1) return 'Just now';
    if (diffMin < 60) return `${diffMin}m ago`;
    if (diffHr < 24) return `${diffHr}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined });
  };

  const renderGridCard = (asset) => {
    const src = getAssetSrc(asset);
    const isExpanded = expandedPrompts.has(asset.id);

    return (
      <div key={asset.id} className="asset-card">
        <div
          className="asset-preview"
          style={{
            aspectRatio: asset.asset_type === 'audio' ? 'auto' : '16/9',
            padding: asset.asset_type === 'audio' ? '0' : undefined,
          }}
        >
          {renderAssetPreview(asset)}
          <div className="asset-badge">
            {getIcon(asset.asset_type)} {asset.asset_type}
          </div>
        </div>

        <div className="asset-info" style={{ padding: '0.75rem' }}>
          <div className="asset-timestamp" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span>{formatTimestamp(asset.created_at)}</span>
            {asset.model_id && (
              <span className="history-model-badge">
                {asset.model_id}
              </span>
            )}
          </div>

          {asset.prompt && (
            <div style={{ position: 'relative' }}>
              <p
                className="asset-prompt"
                style={{
                  fontSize: '0.75rem',
                  marginBottom: '0.25rem',
                  cursor: 'pointer',
                  WebkitLineClamp: isExpanded ? 'unset' : 2,
                  lineClamp: isExpanded ? 'unset' : 2,
                }}
                onClick={() => togglePromptExpand(asset.id)}
                title={isExpanded ? 'Click to collapse' : 'Click to expand'}
              >
                {asset.prompt}
              </p>
              {asset.prompt.length > 80 && (
                <button
                  onClick={() => togglePromptExpand(asset.id)}
                  className="history-expand-btn"
                >
                  {isExpanded ? <ChevronUp size={10} /> : <ChevronDown size={10} />}
                  {isExpanded ? 'Less' : 'More'}
                </button>
              )}
            </div>
          )}

          <div className="asset-footer" style={{ marginTop: '0.5rem', paddingTop: '0.5rem' }}>
            <span
              style={{
                fontSize: '0.65rem',
                color: 'var(--accent-secondary)',
                fontWeight: '600',
                letterSpacing: '0.02em',
                opacity: 0.8,
              }}
            >
              {!asset.model_id && 'System Generated'}
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
                  download={`asset-${asset.id}.${getDownloadExt(asset)}`}
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
  };

  const renderListItem = (asset) => {
    const src = getAssetSrc(asset);
    const isExpanded = expandedPrompts.has(asset.id);

    return (
      <div key={asset.id} className="history-list-item">
        {/* Thumbnail */}
        <div className="history-list-thumb">
          {asset.asset_type === 'image' && src && (
            <img src={src} alt={asset.prompt || 'Generated image'} loading="lazy" />
          )}
          {asset.asset_type === 'video' && src && (
            <video src={src} muted />
          )}
          {asset.asset_type === 'audio' && (
            <div className="history-list-audio-icon">
              <FileAudio size={20} />
            </div>
          )}
          {!src && (
            <div className="history-list-audio-icon">
              {getIcon(asset.asset_type)}
            </div>
          )}
          <span className="history-list-type-dot" data-type={asset.asset_type} />
        </div>

        {/* Content */}
        <div className="history-list-content">
          <div className="history-list-meta">
            <span className="history-list-timestamp">{formatTimestamp(asset.created_at)}</span>
            <span className="history-list-type-label">{asset.asset_type}</span>
            {asset.model_id && (
              <span className="history-model-badge">{asset.model_id}</span>
            )}
          </div>
          {asset.prompt && (
            <p
              className="history-list-prompt"
              style={{
                WebkitLineClamp: isExpanded ? 'unset' : 1,
                lineClamp: isExpanded ? 'unset' : 1,
              }}
              onClick={() => togglePromptExpand(asset.id)}
            >
              {asset.prompt}
            </p>
          )}
        </div>

        {/* Actions */}
        {src && (
          <div className="history-list-actions">
            <a
              href={src}
              target="_blank"
              rel="noopener noreferrer"
              className="btn-secondary"
              style={{ padding: '0.35rem', borderRadius: '0.4rem' }}
              title="Open in new tab"
            >
              <ExternalLink size={13} />
            </a>
            <a
              href={src}
              download={`asset-${asset.id}.${getDownloadExt(asset)}`}
              className="btn-secondary"
              style={{ padding: '0.35rem', borderRadius: '0.4rem' }}
              title="Download"
            >
              <Download size={13} />
            </a>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="studio-container">
      <div className="studio-header">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.75rem' }}>
          <div>
            <h2 style={{ margin: 0 }}>Asset Library</h2>
            <p style={{ marginTop: '0.35rem', opacity: 0.5, fontSize: '0.8rem' }}>
              {filteredAssets.length} asset{filteredAssets.length !== 1 ? 's' : ''}
              {searchQuery && ' matching search'}
            </p>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            {/* View mode toggle */}
            <div className="history-view-toggle">
              <button
                onClick={() => setViewMode('grid')}
                className={viewMode === 'grid' ? 'active' : ''}
                title="Grid view"
              >
                <LayoutGrid size={14} />
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={viewMode === 'list' ? 'active' : ''}
                title="List view"
              >
                <List size={14} />
              </button>
            </div>
            <button
              onClick={fetchHistory}
              className="btn-secondary"
              style={{
                padding: '0.5rem 1rem',
                fontSize: '0.8rem',
                display: 'flex',
                alignItems: 'center',
                gap: '0.4rem',
              }}
            >
              <Clock size={14} /> Refresh
            </button>
          </div>
        </div>

        {/* Filter tabs + Search */}
        <div style={{ marginTop: '0.75rem', display: 'flex', gap: '0.5rem', alignItems: 'center', flexWrap: 'wrap' }}>
          <div className="history-filter-tabs">
            {FILTER_TABS.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setAssetFilter(tab.id)}
                  className={`history-filter-tab ${assetFilter === tab.id ? 'active' : ''}`}
                >
                  <Icon size={12} />
                  {tab.label}
                </button>
              );
            })}
          </div>
          <div className="history-search-bar">
            <Search size={14} style={{ opacity: 0.4, flexShrink: 0 }} />
            <input
              type="text"
              placeholder="Search by prompt, model, or filename..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                className="history-search-clear"
              >
                x
              </button>
            )}
          </div>
        </div>
      </div>

      <div className="studio-content-area">
        <div className="studio-scroll-container">
          {loading && assets.length === 0 && (
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              padding: '4rem 2rem',
              color: 'var(--text-secondary)',
              gap: '0.75rem',
            }}>
              <div className="history-spinner" />
              Loading assets...
            </div>
          )}

          {viewMode === 'grid' ? (
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))',
                gap: '1.25rem',
                paddingRight: '0.5rem',
              }}
            >
              {filteredAssets.map((asset) => renderGridCard(asset))}
            </div>
          ) : (
            <div className="history-list-container">
              {filteredAssets.map((asset) => renderListItem(asset))}
            </div>
          )}

          {filteredAssets.length === 0 && !loading && (
            <div
              style={{
                textAlign: 'center',
                padding: '4rem 2rem',
                background: 'rgba(255,255,255,0.02)',
                borderRadius: '1.5rem',
                border: '1px dashed var(--glass-border)',
                color: 'var(--text-secondary)',
              }}
            >
              <ImageIcon size={48} style={{ opacity: 0.1, marginBottom: '1rem' }} />
              {searchQuery ? (
                <>
                  <p>No assets match "{searchQuery}"</p>
                  <p style={{ fontSize: '0.8rem', opacity: 0.6 }}>
                    Try a different search term or clear the filter
                  </p>
                </>
              ) : (
                <>
                  <p>No assets yet</p>
                  <p style={{ fontSize: '0.8rem', opacity: 0.6 }}>
                    Head to the Canvas tab and run a workflow to generate your first assets.
                  </p>
                  <p style={{ fontSize: '0.75rem', opacity: 0.4, marginTop: '0.5rem' }}>
                    Generated images, videos, and audio will automatically appear here.
                  </p>
                </>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default HistoryPanel;
