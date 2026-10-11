import React from 'react';

export const FeatureCards: React.FC = () => {
  return (
    <section className="relative w-full h-screen flex flex-col justify-between items-center px-6 py-8 z-10 pointer-events-none overflow-hidden">
      {/* 3D Perspective Grid floor */}
      <div className="absolute inset-0 perspective-grid opacity-30 pointer-events-none -z-10" />

      {/* Moving Blurred Rectangular Shadows on background for depth */}
      <div className="absolute top-1/4 left-1/4 w-96 h-64 bg-slate-900/10 rounded-3xl blur-3xl -z-10 animate-pulse"></div>
      <div className="absolute bottom-1/4 right-1/4 w-80 h-60 bg-sky-500/10 rounded-3xl blur-3xl -z-10"></div>

      {/* Floating Glassmorphism Pill Navbar */}
      <header className="pointer-events-auto flex items-center justify-between w-full max-w-4xl mx-auto px-6 py-2.5 rounded-full glass-panel shadow-md">
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-full bg-gradient-to-tr from-amber-400 via-rose-400 to-indigo-500 p-0.5 shadow-sm">
            <div className="w-full h-full rounded-full bg-white flex items-center justify-center font-extrabold text-[10px] text-slate-800">DT</div>
          </div>
          <span className="font-extrabold tracking-tight text-sm text-slate-800">Daytone</span>
        </div>

        {/* Center Pill */}
        <div className="hidden sm:flex items-center gap-2 px-3 py-1 rounded-full bg-black/5 text-xs font-semibold text-slate-700">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
          <span>Features &amp; Micro-Reflections</span>
        </div>

        {/* Right Sign In Dropdown + Avatar */}
        <div className="flex items-center gap-3">
          <div className="relative group cursor-pointer">
            <button className="flex items-center gap-1.5 text-xs font-bold text-slate-700 hover:text-slate-900">
              <span>Sign In</span>
              <span className="text-[10px]">▼</span>
            </button>
          </div>
          <div className="w-7 h-7 rounded-full bg-slate-800/10 border border-white/80 flex items-center justify-center text-xs font-bold text-slate-700 shadow-sm">
            SA
          </div>
        </div>
      </header>

      {/* 4 Frosted Glass Cards orbiting the central Torus */}
      <div className="relative w-full max-w-5xl mx-auto h-[68vh] flex items-center justify-center pointer-events-none">
        
        {/* Card 1: Top-Left */}
        <div className="feature-card absolute top-2 left-4 md:left-12 w-64 p-4 rounded-2xl glass-panel shadow-xl pointer-events-auto transform transition-transform hover:-translate-y-1">
          <div className="flex items-center gap-2 mb-1.5">
            <span className="w-6 h-6 rounded-lg bg-sky-500/15 text-sky-600 flex items-center justify-center text-xs font-bold">✓</span>
            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">Step 01</span>
          </div>
          <h4 className="text-sm font-bold text-slate-800">Log your first check-in</h4>
          <p className="text-[11px] text-slate-600 mt-1 leading-snug">
            Takes 60 seconds. Capture real-time energy and mood frequencies.
          </p>
        </div>

        {/* Card 2: Top-Right */}
        <div className="feature-card absolute top-2 right-4 md:right-12 w-64 p-4 rounded-2xl glass-panel shadow-xl pointer-events-auto transform transition-transform hover:-translate-y-1">
          <div className="flex items-center gap-2 mb-1.5">
            <span className="w-6 h-6 rounded-lg bg-indigo-500/15 text-indigo-600 flex items-center justify-center text-xs">📝</span>
            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">Step 02</span>
          </div>
          <h4 className="text-sm font-bold text-slate-800">Drop a note</h4>
          <p className="text-[11px] text-slate-600 mt-1 leading-snug">
            Reflect on micro-moments without journaling guilt or pressure.
          </p>
        </div>

        {/* Card 3: Bottom-Left */}
        <div className="feature-card absolute bottom-4 left-4 md:left-12 w-64 p-4 rounded-2xl glass-panel shadow-xl pointer-events-auto transform transition-transform hover:-translate-y-1">
          <div className="flex items-center gap-2 mb-1.5">
            <span className="w-6 h-6 rounded-lg bg-emerald-500/15 text-emerald-600 flex items-center justify-center text-xs">🛡️</span>
            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">Step 03</span>
          </div>
          <h4 className="text-sm font-bold text-slate-800">Get your AI burnout risk score</h4>
          <p className="text-[11px] text-slate-600 mt-1 leading-snug">
            Predictive ML classifies acute cognitive fatigue signals.
          </p>
        </div>

        {/* Card 4: Bottom-Right */}
        <div className="feature-card absolute bottom-4 right-4 md:right-12 w-64 p-4 rounded-2xl glass-panel shadow-xl pointer-events-auto transform transition-transform hover:-translate-y-1">
          <div className="flex items-center gap-2 mb-1.5">
            <span className="w-6 h-6 rounded-lg bg-amber-500/15 text-amber-600 flex items-center justify-center text-xs">⚡</span>
            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">Step 04</span>
          </div>
          <h4 className="text-sm font-bold text-slate-800">Circadian Sync</h4>
          <p className="text-[11px] text-slate-600 mt-1 leading-snug">
            Harmonize daily habits with your internal biological rhythm.
          </p>
        </div>

      </div>

      {/* Tiny Progress Indicator (3 Dashes) at bottom center */}
      <div className="flex items-center gap-1.5 pb-2">
        <span className="w-5 h-1 rounded-full bg-slate-800"></span>
        <span className="w-3 h-1 rounded-full bg-slate-400/50"></span>
        <span className="w-3 h-1 rounded-full bg-slate-400/50"></span>
      </div>
    </section>
  );
};
