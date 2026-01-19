import React, { useState } from 'react';
import {
  Mic2,
  Users2,
  BrainCircuit,
  ImagePlus,
  Maximize,
  Clapperboard,
  Music4
} from 'lucide-react';
import SingleSpeakerPanel from './SingleSpeakerPanel';
import MultiSpeakerPanel from './MultiSpeakerPanel';
import GeminiThreePanel from './GeminiThreePanel';
import GeminiImagePanel from './GeminiImagePanel';
import ImageUpscalePanel from './ImageUpscalePanel';
import VeoVideoPanel from './VeoVideoPanel';
import MusicPanel from './MusicPanel';

import './StudioPanel.css';

const StudioPanel = ({ userId }) => {
  const [activeTool, setActiveTool] = useState('single');

  const tools = [
    { id: 'single', label: 'Single Voice', icon: <Mic2 size={20} />, gradient: 'gradient-single', color: 'text-blue-400' },
    { id: 'multi', label: 'Multi Voice', icon: <Users2 size={20} />, gradient: 'gradient-multi', color: 'text-indigo-400' },
    { id: 'reasoning', label: 'Reasoning', icon: <BrainCircuit size={20} />, gradient: 'gradient-reasoning', color: 'text-fuchsia-400' },
    { id: 'image', label: 'Image Studio', icon: <ImagePlus size={20} />, gradient: 'gradient-image', color: 'text-rose-400' },
    { id: 'upscale', label: 'Upscale', icon: <Maximize size={20} />, gradient: 'gradient-upscale', color: 'text-amber-400' },
    { id: 'video', label: 'Video Studio', icon: <Clapperboard size={20} />, gradient: 'gradient-video', color: 'text-red-400' },
    { id: 'music', label: 'Music Studio', icon: <Music4 size={20} />, gradient: 'gradient-music', color: 'text-emerald-400' },
  ];

  return (
    <div className="studio-container">
      {/* Studio Header / Navigation */}
      <div className="studio-header">
        <div className="flex items-center gap-1 overflow-x-auto pb-2 scrollbar-hide mask-fade-x">
          {tools.map((tool) => {
            const isActive = activeTool === tool.id;
            return (
              <button
                key={tool.id}
                onClick={() => setActiveTool(tool.id)}
                className={`
                  relative group flex items-center gap-2 px-4 py-2-5 rounded-xl transition-all duration-300 ease-out
                  ${isActive
                    ? 'nav-item-active'
                    : 'nav-item-inactive hover-lift'
                  }
                `}
              >
                {/* Active Indicator Background */}
                {isActive && (
                  <div className={`absolute inset-0 rounded-xl ${tool.gradient} opacity-10 blur-md`} />
                )}

                {/* Icon */}
                <span className={`relative transition-colors duration-300 ${isActive ? 'text-white' : 'group-hover-text-white'}`}>
                  {React.cloneElement(tool.icon, {
                    size: isActive ? 18 : 18,
                    strokeWidth: isActive ? 2.5 : 2
                  })}
                </span>

                {/* Label */}
                <span className="relative text-sm font-medium whitespace-nowrap">
                  {tool.label}
                </span>

                {/* Active Dot & Label */}
                {isActive && (
                  <div className="flex items-center gap-1.5 ml-2 pl-2 border-l-white-20">
                    <span className="w-1-5 h-1-5 rounded-full bg-white animate-pulse shadow-[0_0_8px_rgba(255,255,255,0.8)]" />
                  </div>
                )}
              </button>
            );
          })}
        </div>
      </div>

      {/* Content Area */}
      <div className="studio-content-area">
        <div className="studio-scroll-container">
          <div className="max-w-7xl mx-auto space-y-6">
            {activeTool === 'single' && <SingleSpeakerPanel />}
            {activeTool === 'multi' && <MultiSpeakerPanel />}
            {activeTool === 'reasoning' && <GeminiThreePanel />}
            {activeTool === 'image' && <GeminiImagePanel userId={userId} />}
            {activeTool === 'upscale' && <ImageUpscalePanel userId={userId} />}
            {activeTool === 'video' && <VeoVideoPanel userId={userId} />}
            {activeTool === 'music' && <MusicPanel userId={userId} />}
          </div>
        </div>
      </div>
    </div>
  );
};

export default StudioPanel;
