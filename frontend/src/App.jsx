import React, { useState } from 'react';
import StudioPanel from './components/StudioPanel';
import HistoryPanel from './components/HistoryPanel';
import LogPanel from './components/LogPanel';
import CanvasPage from './components/canvas/CanvasPage';
import ErrorBoundary from './components/ErrorBoundary';
import {
  RefreshCw,
  History,
  LayoutGrid, // Modern icon for Canvas
  AppWindow, // Modern icon for Studio
  Infinity, // Icon for Branding
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
                    <Infinity size={28} strokeWidth={2.5} className="infinity-main" />
                    {/* SVG tracer that follows the path */}
                    <svg width="28" height="28" viewBox="0 0 24 24" className="infinity-tracer-svg">
                      <path
                        d="M18.18 17.77C15.81 19.32 12.18 19.32 9.81 17.77L5.82 15.11C3.45 13.56 3.45 9.92 5.82 8.37C8.19 6.82 11.82 6.82 14.19 8.37L18.18 11.03C20.55 12.58 20.55 16.22 18.18 17.77Z"
                        className="infinity-tracer-path"
                        strokeLinecap="round"
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
            </div>
          </aside>

          {/* Main Content */}
          <main className="flex-1 relative overflow-hidden bg-main-gradient">
            {activeTab === 'canvas' && (
              <div className="absolute inset-0 z-0">
                <CanvasPage />
              </div>
            )}

            {activeTab === 'studio' && (
              <div className="absolute inset-0 z-10">
                <StudioPanel userId={userId} />
              </div>
            )}

            {activeTab === 'history' && (
              <div className="absolute inset-0 z-10 p-8 overflow-y-auto custom-scrollbar">
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
