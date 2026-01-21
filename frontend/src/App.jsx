import React, { useState } from 'react';
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

function App() {
  const [activeTab, setActiveTab] = useState('canvas'); // Canvas moves up, default
  const [userId, setUserId] = useState(() => localStorage.getItem('gemini_user_id') || 'user_' + Math.floor(Math.random() * 10000));
  const [tempUserId, setTempUserId] = useState(userId);

  const handleSetUser = () => {
    setUserId(tempUserId);
    localStorage.setItem('gemini_user_id', tempUserId);
  };

  const navItems = [
    { id: 'canvas', label: 'Canvas', icon: <LayoutGrid size={20} /> },
    { id: 'templates', label: 'Saved Canvas', icon: <Library size={20} /> },
    { id: 'studio', label: 'Studio', icon: <AppWindow size={20} /> },
    { id: 'history', label: 'History', icon: <History size={20} /> },
  ];

  return (
    <ConfigProvider>
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

            {/* User Identity / Bottom Section */}
            <div className="p-4 mt-auto border-t-glass bg-white-5 backdrop-blur-sm">
              <div className="flex items-center gap-3">
                <div className="flex-1 min-w-0">
                  <div className="text-[10px] text-white-50 font-medium uppercase tracking-wider mb-1">Signed in as</div>
                  <input
                    type="text"
                    value={tempUserId}
                    onChange={(e) => setTempUserId(e.target.value)}
                    onBlur={handleSetUser}
                    onKeyDown={(e) => e.key === 'Enter' && handleSetUser()}
                    className="w-full bg-transparent text-xs font-bold text-white-90 border-none p-0 focus-ring-0 focus-outline-none placeholder-white-20"
                    placeholder="Enter Username"
                  />
                </div>
                <button
                  onClick={handleSetUser}
                  className="p-2 rounded-lg bg-white-5 text-white-40 hover-text-white hover-bg-white-10 transition-colors border-glass"
                  title="Refresh Session"
                >
                  <RefreshCw size={14} />
                </button>
              </div>
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
          </aside>

          {/* Main Content */}
          <main className="flex-1 relative overflow-hidden bg-main-gradient">
            {activeTab === 'canvas' && (
              <div className="absolute inset-0 z-0">
                <CanvasPage userId={userId} />
              </div>
            )}

            {activeTab === 'studio' && (
              <div className="absolute inset-0 z-10 overflow-y-auto custom-scrollbar">
                <StudioPanel userId={userId} />
              </div>
            )}

            {activeTab === 'templates' && (
              <div className="absolute inset-0 z-10 overflow-y-auto custom-scrollbar">
                <SavedCanvasPanel userId={userId} onSwitchToCanvas={() => setActiveTab('canvas')} />
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
    </ConfigProvider>
  );
}

export default App;
