import React, { useState, useCallback } from 'react';
import { v4 as uuidv4 } from 'uuid';
import StudioPanel from './components/StudioPanel';
import HistoryPanel from './components/HistoryPanel';
import LogPanel from './components/LogPanel';
import SavedCanvasPanel from './components/SavedCanvasPanel';
import CanvasPage from './components/canvas/CanvasPage';
import ErrorBoundary from './components/ErrorBoundary';
import {
  RefreshCw,
  History,
  LayoutGrid, // Modern icon for Canvas
  AppWindow, // Modern icon for Studio
  Infinity, // Icon for Branding
  Library, // Icon for Saved Canvas
} from 'lucide-react';

import { ConfigProvider } from './contexts/ConfigContext';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { apiFetch } from './utils/api';

function AppContent() {
  const [activeTab, setActiveTab] = useState('canvas'); // Canvas moves up, default
  const { user, loading, login, logout, authError } = useAuth();
  const userId = user?.uid || 'anonymous';

  // Workflow tabs state
  const [workflowTabs, setWorkflowTabs] = useState([
    { id: uuidv4(), name: 'Untitled Workflow', nodes: [], edges: [] }
  ]);
  const [activeWorkflowIdx, setActiveWorkflowIdx] = useState(0);
  const [renamingTabIdx, setRenamingTabIdx] = useState(null);
  const [renameValue, setRenameValue] = useState('');

  // Team state
  const [userTeams, setUserTeams] = useState([]);
  const [showTeamDialog, setShowTeamDialog] = useState(null); // null, 'create', 'join'
  const [teamInput, setTeamInput] = useState('');
  const [teamError, setTeamError] = useState('');

  const addNewTab = () => {
    const newTab = { id: uuidv4(), name: 'Untitled Workflow', nodes: [], edges: [] };
    setWorkflowTabs(prev => [...prev, newTab]);
    setActiveWorkflowIdx(workflowTabs.length);
  };

  const openWorkflowInNewTab = (workflowData) => {
    const newTab = {
      id: workflowData.id || uuidv4(),
      name: workflowData.name || 'Loaded Workflow',
      nodes: workflowData.nodes || [],
      edges: workflowData.edges || []
    };
    setWorkflowTabs(prev => [...prev, newTab]);
    setActiveWorkflowIdx(workflowTabs.length);
    setActiveTab('canvas');
  };

  const closeTab = (idx) => {
    if (workflowTabs.length <= 1) return;
    setWorkflowTabs(prev => prev.filter((_, i) => i !== idx));
    if (activeWorkflowIdx >= idx && activeWorkflowIdx > 0) {
      setActiveWorkflowIdx(prev => prev - 1);
    }
  };

  const switchToTab = (idx) => {
    setActiveWorkflowIdx(idx);
  };

  const startRenameTab = (idx, currentName) => {
    setRenamingTabIdx(idx);
    setRenameValue(currentName || 'Untitled Workflow');
  };

  const finishRenameTab = () => {
    if (renamingTabIdx !== null && renameValue.trim()) {
      setWorkflowTabs(prev => prev.map((tab, i) =>
        i === renamingTabIdx ? { ...tab, name: renameValue.trim() } : tab
      ));
    }
    setRenamingTabIdx(null);
  };

  const updateTabState = useCallback((idx, state) => {
    setWorkflowTabs(prev => prev.map((tab, i) => i === idx ? { ...tab, ...state } : tab));
  }, []);

  // Fetch teams when user is logged in
  React.useEffect(() => {
    if (user) {
      apiFetch('/api/teams/mine').then(r => r.ok ? r.json() : []).then(setUserTeams).catch(() => {});
    } else {
      setUserTeams([]);
    }
  }, [user]);

  const refreshTeams = () => {
    apiFetch('/api/teams/mine').then(r => r.ok ? r.json() : []).then(setUserTeams).catch(() => {});
  };

  const handleCreateTeam = async () => {
    if (!teamInput.trim()) return;
    setTeamError('');
    try {
      const res = await apiFetch('/api/teams/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: teamInput.trim() }),
      });
      if (res.ok) {
        setTeamInput('');
        setShowTeamDialog(null);
        refreshTeams();
      } else {
        const data = await res.json().catch(() => ({}));
        setTeamError(data.detail || 'Failed to create team');
      }
    } catch {
      setTeamError('Network error');
    }
  };

  const handleJoinTeam = async () => {
    if (!teamInput.trim()) return;
    setTeamError('');
    try {
      const res = await apiFetch('/api/teams/join', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ join_code: teamInput.trim() }),
      });
      if (res.ok) {
        setTeamInput('');
        setShowTeamDialog(null);
        refreshTeams();
      } else {
        const data = await res.json().catch(() => ({}));
        setTeamError(data.detail || 'Failed to join team');
      }
    } catch {
      setTeamError('Network error');
    }
  };

  const handleLeaveTeam = async (teamId) => {
    try {
      const res = await apiFetch(`/api/teams/${teamId}/leave`, { method: 'POST' });
      if (res.ok) {
        refreshTeams();
      }
    } catch {
      // ignore
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text).catch(() => {});
  };

  const navItems = [
    { id: 'canvas', label: 'Canvas', icon: <LayoutGrid size={20} /> },
    { id: 'templates', label: 'Saved Canvas', icon: <Library size={20} /> },
    { id: 'studio', label: 'Studio', icon: <AppWindow size={20} /> },
    { id: 'history', label: 'History', icon: <History size={20} /> },
  ];

  if (loading) {
    return (
      <div className="h-screen flex items-center justify-center bg-black text-white">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-400 mx-auto mb-4"></div>
          <p className="text-white/50 text-sm">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <ErrorBoundary>
      <div className="app-layout h-screen flex bg-black text-white font-sans overflow-hidden">
        {/* Sidebar */}
        <aside className="w-64 flex flex-col sidebar-border bg-black-60 backdrop-blur-2xl">
          {/* Header / Branding */}
          <div className="p-6">
            <h1 className="text-2xl font-bold flex items-center gap-2 tracking-tighter">
              <span className="text-gradient-brand flex items-center gap-2">
                <div className="infinity-container">
                  <Infinity size={32} strokeWidth={2.5} className="infinity-main" />
                  {/* SVG tracer that follows the path perfectly */}
                  <svg width="32" height="32" viewBox="0 0 24 24" className="infinity-tracer-svg">
                    <defs>
                      <linearGradient id="silver-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                        <stop offset="0%" stopColor="rgba(255,255,255,0)" />
                        <stop offset="50%" stopColor="rgba(255,255,255,0.8)" />
                        <stop offset="100%" stopColor="rgba(255,255,255,1)" />
                      </linearGradient>
                    </defs>
                    <path
                      d="M6 16c5 0 7-8 12-8a4 4 0 0 1 0 8c-5 0-7-8-12-8a4 4 0 1 0 0 8"
                      className="infinity-tracer-path"
                      stroke="url(#silver-gradient)"
                      strokeLinecap="round"
                      pathLength="1"
                    />
                  </svg>
                </div>
                <span>Canvas</span>
              </span>
            </h1>
            <p className="text-xs font-medium text-white-40 mt-1 tracking-wide uppercase">
              Multimodal Orchestrator
            </p>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-3 space-y-1">
            {navItems.map(item => (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`
                  w-full flex items-center gap-3 px-3 py-2-5 rounded-lg text-sm font-medium transition-all duration-200
                  ${activeTab === item.id
                    ? 'nav-item-active'
                    : 'nav-item-inactive'
                  }
                `}
              >
                <span className={`transition-colors duration-200 ${activeTab === item.id ? 'text-blue-400' : ''}`}>
                  {React.cloneElement(item.icon, { size: 18 })}
                </span>
                {item.label}
              </button>
            ))}
          </nav>

          {/* Teams Section */}
          {user && (
            <div style={{ padding: '0 0.75rem', marginTop: 'auto' }}>
              <div style={{ borderTop: '1px solid rgba(255,255,255,0.1)', paddingTop: '0.75rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                  <span style={{ fontSize: '0.65rem', fontWeight: 700, color: 'rgba(255,255,255,0.3)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Teams</span>
                  <button onClick={() => { setShowTeamDialog(showTeamDialog === 'create' ? null : 'create'); setTeamInput(''); setTeamError(''); }} style={{ background: 'none', border: 'none', color: 'rgba(255,255,255,0.4)', cursor: 'pointer', fontSize: '1rem', lineHeight: 1 }}>+</button>
                </div>

                {/* Team dialog */}
                {showTeamDialog && (
                  <div style={{ marginBottom: '0.5rem', padding: '0.5rem', background: 'rgba(255,255,255,0.05)', borderRadius: '0.5rem', border: '1px solid rgba(255,255,255,0.1)' }}>
                    <div style={{ fontSize: '0.7rem', fontWeight: 600, color: 'rgba(255,255,255,0.7)', marginBottom: '0.4rem' }}>
                      {showTeamDialog === 'create' ? 'Create Team' : 'Join Team'}
                    </div>
                    <input
                      type="text"
                      value={teamInput}
                      onChange={(e) => setTeamInput(e.target.value)}
                      onKeyDown={(e) => { if (e.key === 'Enter') { showTeamDialog === 'create' ? handleCreateTeam() : handleJoinTeam(); } if (e.key === 'Escape') { setShowTeamDialog(null); setTeamError(''); } }}
                      placeholder={showTeamDialog === 'create' ? 'Team name...' : 'Paste join code...'}
                      autoFocus
                      style={{ width: '100%', padding: '0.35rem 0.5rem', fontSize: '0.7rem', background: '#1a1a1a', border: '1px solid rgba(255,255,255,0.15)', borderRadius: '0.375rem', color: 'white', outline: 'none', marginBottom: '0.35rem', boxSizing: 'border-box' }}
                    />
                    {teamError && (
                      <div style={{ fontSize: '0.65rem', color: '#f87171', marginBottom: '0.35rem' }}>{teamError}</div>
                    )}
                    <div style={{ display: 'flex', gap: '0.35rem' }}>
                      <button
                        onClick={showTeamDialog === 'create' ? handleCreateTeam : handleJoinTeam}
                        style={{ flex: 1, padding: '0.35rem', fontSize: '0.65rem', background: 'rgba(96,165,250,0.2)', border: '1px solid rgba(96,165,250,0.3)', borderRadius: '0.375rem', color: '#93c5fd', cursor: 'pointer', fontWeight: 600 }}
                      >
                        {showTeamDialog === 'create' ? 'Create' : 'Join'}
                      </button>
                      <button
                        onClick={() => { setShowTeamDialog(null); setTeamError(''); }}
                        style={{ padding: '0.35rem 0.5rem', fontSize: '0.65rem', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '0.375rem', color: 'rgba(255,255,255,0.5)', cursor: 'pointer' }}
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                )}

                {/* Team list */}
                {userTeams.map(team => (
                  <div key={team.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.4rem 0.5rem', fontSize: '0.7rem', color: 'rgba(255,255,255,0.6)', borderRadius: '0.375rem', marginBottom: '2px', background: 'rgba(255,255,255,0.03)' }}>
                    <span style={{ flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{team.name}</span>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', flexShrink: 0 }}>
                      <span style={{ fontSize: '0.6rem', color: 'rgba(255,255,255,0.3)' }}>{team.member_count} {team.member_count === 1 ? 'member' : 'members'}</span>
                      {team.join_code && (
                        <button
                          onClick={() => copyToClipboard(team.join_code)}
                          title={`Copy join code: ${team.join_code}`}
                          style={{ background: 'none', border: 'none', color: 'rgba(255,255,255,0.3)', cursor: 'pointer', fontSize: '0.65rem', padding: '0 2px', lineHeight: 1 }}
                        >
                          {'[code]'}
                        </button>
                      )}
                    </div>
                  </div>
                ))}

                {/* Join team button */}
                <button
                  onClick={() => { setShowTeamDialog(showTeamDialog === 'join' ? null : 'join'); setTeamInput(''); setTeamError(''); }}
                  style={{ width: '100%', marginTop: '0.25rem', padding: '0.4rem', fontSize: '0.65rem', background: 'rgba(255,255,255,0.03)', border: '1px dashed rgba(255,255,255,0.1)', borderRadius: '0.375rem', color: 'rgba(255,255,255,0.4)', cursor: 'pointer' }}
                >
                  Join a Team
                </button>
              </div>
            </div>
          )}

          {/* User Identity / Bottom Section */}
          {user ? (
            <div className="p-4 mt-auto border-t-glass bg-white-5 backdrop-blur-sm">
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem' }}>
                {user.photoURL && (
                  <img src={user.photoURL} alt="" style={{ width: 32, height: 32, borderRadius: '50%' }} referrerPolicy="no-referrer" />
                )}
                <div>
                  <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'rgba(255,255,255,0.9)' }}>{user.displayName}</div>
                  <div style={{ fontSize: '0.65rem', color: 'rgba(255,255,255,0.5)' }}>{user.email}</div>
                </div>
              </div>
              <button onClick={logout} style={{ width: '100%', padding: '0.5rem', fontSize: '0.75rem', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '0.5rem', color: 'rgba(255,255,255,0.7)', cursor: 'pointer' }}>
                Sign Out
              </button>
              <div className="mt-4 pt-4 border-t border-white/5">
                <a
                  href="mailto:gauravz@google.com"
                  className="text-[8px] text-white-40 hover:text-white-60 transition-colors flex items-center gap-4 no-underline"
                >
                  <span className="opacity-50">Created by:</span>
                  <span className="font-semibold text-white-50">gauravz</span>
                </a>
              </div>
            </div>
          ) : (
            <div className="p-4 mt-auto border-t-glass bg-white-5 backdrop-blur-sm">
              <button onClick={login} style={{ width: '100%', padding: '0.75rem', fontSize: '0.8rem', background: 'linear-gradient(135deg, #4285f4, #357ae8)', border: 'none', borderRadius: '0.5rem', color: 'white', cursor: 'pointer', fontWeight: 600 }}>
                Sign in with Google
              </button>
              {authError && (
                <div style={{ marginTop: '0.5rem', padding: '0.5rem', fontSize: '0.7rem', color: '#f87171', background: 'rgba(239,68,68,0.1)', borderRadius: '0.375rem', wordBreak: 'break-word' }}>
                  {authError}
                </div>
              )}
              <div className="mt-4 pt-4 border-t border-white/5">
                <a
                  href="mailto:gauravz@google.com"
                  className="text-[8px] text-white-40 hover:text-white-60 transition-colors flex items-center gap-4 no-underline"
                >
                  <span className="opacity-50">Created by:</span>
                  <span className="font-semibold text-white-50">gauravz</span>
                </a>
              </div>
            </div>
          )}
        </aside>

        {/* Main Content */}
        <main className="flex-1 flex flex-col overflow-hidden bg-main-gradient" style={{ position: 'relative' }}>
          {/* Canvas - always mounted, hidden when other tabs active to preserve state */}
          <div style={{
            display: activeTab === 'canvas' ? 'flex' : 'none',
            flexDirection: 'column',
            flex: 1,
            overflow: 'hidden',
          }}>
            <>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                background: 'rgba(10,10,20,0.95)',
                borderBottom: '1px solid rgba(255,255,255,0.15)',
                padding: '0 0.75rem',
                height: '42px',
                flexShrink: 0,
                gap: '4px',
                overflowX: 'auto',
                backdropFilter: 'blur(12px)',
                zIndex: 100,
              }}>
                {workflowTabs.map((tab, idx) => (
                  <div
                    key={tab.id}
                    onClick={() => switchToTab(idx)}
                    onDoubleClick={() => startRenameTab(idx, tab.name)}
                    style={{
                      display: 'flex', alignItems: 'center', gap: '0.5rem',
                      padding: '0.5rem 1rem',
                      fontSize: '0.75rem', fontWeight: 600,
                      cursor: 'pointer',
                      borderRadius: '0.5rem 0.5rem 0 0',
                      background: idx === activeWorkflowIdx ? 'rgba(96,165,250,0.15)' : 'rgba(255,255,255,0.03)',
                      color: idx === activeWorkflowIdx ? '#93c5fd' : 'rgba(255,255,255,0.45)',
                      borderBottom: idx === activeWorkflowIdx ? '2px solid #60a5fa' : '2px solid transparent',
                      borderTop: idx === activeWorkflowIdx ? '1px solid rgba(96,165,250,0.3)' : '1px solid transparent',
                      borderLeft: idx === activeWorkflowIdx ? '1px solid rgba(96,165,250,0.15)' : '1px solid transparent',
                      borderRight: idx === activeWorkflowIdx ? '1px solid rgba(96,165,250,0.15)' : '1px solid transparent',
                      whiteSpace: 'nowrap',
                      maxWidth: '220px',
                      transition: 'all 0.15s ease',
                    }}
                    title="Double-click to rename"
                  >
                    {renamingTabIdx === idx ? (
                      <input
                        autoFocus
                        value={renameValue}
                        onChange={(e) => setRenameValue(e.target.value)}
                        onBlur={finishRenameTab}
                        onKeyDown={(e) => { if (e.key === 'Enter') finishRenameTab(); if (e.key === 'Escape') setRenamingTabIdx(null); }}
                        onClick={(e) => e.stopPropagation()}
                        style={{
                          background: 'rgba(0,0,0,0.5)', border: '1px solid #60a5fa',
                          color: 'white', fontSize: '0.75rem', fontWeight: 600,
                          padding: '2px 6px', borderRadius: '3px', outline: 'none',
                          width: '140px',
                        }}
                      />
                    ) : (
                      <span style={{ overflow: 'hidden', textOverflow: 'ellipsis' }}>{tab.name || 'Untitled Workflow'}</span>
                    )}
                    {workflowTabs.length > 1 && renamingTabIdx !== idx && (
                      <span
                        onClick={(e) => { e.stopPropagation(); closeTab(idx); }}
                        style={{
                          opacity: 0.4, cursor: 'pointer', fontSize: '1rem', lineHeight: 1,
                          padding: '0 2px', borderRadius: '3px',
                          transition: 'opacity 0.15s',
                        }}
                        onMouseEnter={(e) => e.target.style.opacity = '1'}
                        onMouseLeave={(e) => e.target.style.opacity = '0.4'}
                      >{'×'}</span>
                    )}
                  </div>
                ))}
                <button
                  onClick={addNewTab}
                  style={{
                    padding: '0.4rem 0.75rem', fontSize: '0.85rem', fontWeight: 600,
                    background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)',
                    borderRadius: '0.375rem',
                    color: 'rgba(255,255,255,0.5)', cursor: 'pointer',
                    marginLeft: '4px',
                    transition: 'all 0.15s ease',
                  }}
                  onMouseEnter={(e) => { e.target.style.background = 'rgba(96,165,250,0.15)'; e.target.style.color = '#93c5fd'; }}
                  onMouseLeave={(e) => { e.target.style.background = 'rgba(255,255,255,0.05)'; e.target.style.color = 'rgba(255,255,255,0.5)'; }}
                  title="New Workflow"
                >+ New</button>
              </div>
              {/* Canvas - render ALL tabs simultaneously, hide inactive (preserves state) */}
              <div style={{ flex: 1, position: 'relative' }}>
                {workflowTabs.map((tab, idx) => (
                  <div
                    key={tab.id}
                    style={{
                      position: 'absolute',
                      inset: 0,
                      visibility: idx === activeWorkflowIdx ? 'visible' : 'hidden',
                      pointerEvents: idx === activeWorkflowIdx ? 'auto' : 'none',
                    }}
                  >
                    <CanvasPage
                      userId={userId}
                      initialData={tab}
                      onStateChange={(state) => updateTabState(idx, state)}
                    />
                  </div>
                ))}
              </div>
            </>
          </div>

          {activeTab === 'studio' && (
            <div className="absolute inset-0 z-10 overflow-y-auto custom-scrollbar">
              <StudioPanel userId={userId} />
            </div>
          )}

          {activeTab === 'templates' && (
            <div className="absolute inset-0 z-10 overflow-y-auto custom-scrollbar">
              <SavedCanvasPanel
                userId={userId}
                onSwitchToCanvas={() => setActiveTab('canvas')}
                onOpenInNewTab={openWorkflowInNewTab}
              />
            </div>
          )}

          {activeTab === 'history' && (
            <div className="absolute inset-0 z-10 overflow-y-auto custom-scrollbar">
              <HistoryPanel userId={userId} />
            </div>
          )}

          {/* Log Panel Overlay or Persistent? Keeping it as overlay or bottom bar if designed */}
          <LogPanel />
        </main>
      </div>
    </ErrorBoundary>
  );
}

function App() {
  return (
    <AuthProvider>
      <ConfigProvider>
        <AppContent />
      </ConfigProvider>
    </AuthProvider>
  );
}

export default App;
