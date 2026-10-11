import React from 'react';

export const Hero: React.FC = () => {
  return (
    <section className="relative w-full h-screen flex flex-col justify-between items-center px-6 py-10 z-10 pointer-events-none">
      {/* Top Floating Pill Header */}
      <header className="pointer-events-auto flex items-center justify-between w-full max-w-4xl mx-auto px-6 py-2.5 rounded-full glass-dark border border-white/10 shadow-2xl">
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-full bg-gradient-to-tr from-amber-400 via-rose-400 to-indigo-500 p-0.5 shadow-md">
            <div className="w-full h-full rounded-full bg-slate-900 flex items-center justify-center font-extrabold text-[10px] text-white">DT</div>
          </div>
          <span className="font-extrabold tracking-tight text-sm text-white">Daytone</span>
        </div>

        <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-xs font-semibold text-slate-300">
          <span className="w-1.5 h-1.5 rounded-full bg-sky-400 animate-ping"></span>
          <span>Circadian Resonance Engine</span>
        </div>

        <button className="px-4 py-1.5 rounded-full bg-white/10 hover:bg-white/20 border border-white/20 text-xs font-bold text-white transition-all">
          Sign In
        </button>
      </header>

      {/* Middle Spacer: The 3D frosted glass sphere is rendered in the upper-middle canvas area here */}
      <div className="w-full h-48 md:h-56 pointer-events-none" aria-hidden="true" />

      {/* Lower Content (Cleanly positioned below the 3D sphere) */}
      <div className="text-center max-w-2xl mx-auto pointer-events-auto flex flex-col items-center pb-6">
        <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-sky-500/10 border border-sky-400/25 text-sky-300 text-xs font-bold tracking-wide mb-3 backdrop-blur-md">
          <span className="w-2 h-2 rounded-full bg-sky-400 animate-pulse"></span>
          <span>Predictive Burnout Intelligence</span>
        </div>

        <h1 className="text-3xl md:text-5xl font-extrabold tracking-tight text-white leading-tight">
          Listen to the <span className="bg-gradient-to-r from-sky-400 via-indigo-300 to-rose-300 bg-clip-text text-transparent">rhythm</span> of your day.
        </h1>

        <p className="mt-3 text-xs md:text-sm text-slate-300 leading-relaxed max-w-lg font-medium">
          A mindful cognitive sanctuary. Track emotional tone, energy frequencies, and burnout signals through daily micro-reflections.
        </p>

        <div className="mt-5 flex items-center gap-4">
          <button className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-sky-500 via-indigo-500 to-indigo-600 text-white font-bold text-xs shadow-xl shadow-sky-500/30 hover:scale-105 active:scale-95 transition-all">
            Begin First Check-in
          </button>
          <button className="px-5 py-2.5 rounded-xl glass-dark hover:bg-white/15 text-slate-200 font-bold text-xs transition-all border border-white/15">
            Explore Engine ↓
          </button>
        </div>
      </div>

      {/* Bottom Scroll Indicator */}
      <div className="flex items-center gap-2 text-[10px] font-bold tracking-widest uppercase text-slate-400 pb-1">
        <span className="w-1.5 h-1.5 rounded-full bg-sky-400 animate-bounce"></span>
        <span>Scroll to morph</span>
      </div>
    </section>
  );
};
