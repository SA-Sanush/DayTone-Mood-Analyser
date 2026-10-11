import React from 'react';

export const SanctuaryOrb: React.FC = () => {
  return (
    <section className="relative w-full h-screen flex flex-col justify-between items-center px-6 py-6 z-10 pointer-events-none">
      
      {/* Top Header: Centered Heading + Subtitle + Action Buttons */}
      <div id="scene5-heading" className="text-center max-w-xl mx-auto pointer-events-auto transition-all pt-2">
        <div className="inline-flex items-center gap-2 px-3 py-0.5 rounded-full bg-amber-400/15 border border-amber-400/30 text-amber-200 text-[11px] font-bold tracking-wider mb-2">
          <span>Act 5 / Harmonic Sanctuary</span>
        </div>

        <h2 className="text-2xl md:text-4xl font-extrabold text-white tracking-tight leading-tight">
          Comprehensive Cognitive Telemetry
        </h2>

        <p className="mt-2 text-xs md:text-sm text-slate-200 leading-relaxed font-medium max-w-md mx-auto">
          Circadian synchrony visualized in high fidelity. Discover how daily reflections stabilize mental entropy.
        </p>

        <div className="mt-3 flex items-center justify-center gap-3">
          <button className="px-4 py-1.5 rounded-xl bg-white/15 hover:bg-white/25 border border-white/25 text-xs font-bold text-white transition-all shadow-sm">
            Learn More →
          </button>
          <button className="px-4 py-1.5 rounded-xl bg-gradient-to-r from-sky-400 to-indigo-500 text-white text-xs font-bold shadow-lg shadow-sky-500/25">
            Sign In to Daytone
          </button>
        </div>
      </div>

      {/* Main Center Area: Flanked 3-column layout */}
      <div id="scene5-dashboard" className="w-full max-w-6xl mx-auto flex-1 grid grid-cols-1 md:grid-cols-12 items-center gap-5 my-auto pointer-events-auto">
        
        {/* Left Flank (Columns 1-4): Tone Constellation Scatter Chart & Affective Diamond */}
        <div className="md:col-span-4 flex flex-col gap-3.5">
          {/* Panel 1: Tone Constellation Scatter Chart */}
          <div className="p-4 rounded-2xl glass-dark border border-white/15 shadow-xl flex flex-col justify-between">
            <div className="flex items-center justify-between mb-1.5">
              <div>
                <h4 className="text-xs font-bold text-white uppercase tracking-wider">Tone Constellation</h4>
                <span className="text-[10px] text-slate-300 font-mono">0 – 190 Hz Diurnal</span>
              </div>
              <div className="flex gap-1 bg-white/10 p-0.5 rounded-lg border border-white/15 text-[10px] font-bold">
                <span className="px-2 py-0.5 rounded bg-sky-500/30 text-sky-200">All</span>
                <span className="px-2 py-0.5 rounded text-slate-300 hover:text-white cursor-pointer">Tres</span>
                <span className="px-2 py-0.5 rounded text-slate-300 hover:text-white cursor-pointer">Sell</span>
              </div>
            </div>

            {/* Scatter Chart SVG */}
            <div className="w-full h-24 relative bg-slate-950/50 rounded-xl border border-white/10 p-1.5 overflow-hidden my-1">
              <svg className="w-full h-full overflow-visible" viewBox="0 0 320 80">
                <path d="M 10 65 Q 80 35, 160 48 T 260 20 T 310 12" fill="none" stroke="rgba(251, 191, 36, 0.55)" strokeWidth="2.5" />
                <circle cx="35" cy="55" r="3.5" fill="#38bdf8" />
                <circle cx="75" cy="45" r="3" fill="#fbbf24" />
                <circle cx="120" cy="50" r="4" fill="#38bdf8" />
                <circle cx="160" cy="48" r="4" fill="#fbbf24" />
                <circle cx="210" cy="35" r="3" fill="#818cf8" />
                <circle cx="260" cy="20" r="3.5" fill="#fbbf24" />
                <circle cx="295" cy="14" r="4" fill="#38bdf8" />
              </svg>
            </div>

            <div className="flex justify-between text-[10px] font-mono text-slate-300">
              <span>PEAK: 16.4 Hz</span>
              <span className="text-emerald-300 font-bold">UPWARD RESONANCE ↑</span>
            </div>
          </div>

          {/* Panel 2: Radar / Affective Diamond Card */}
          <div className="p-3.5 rounded-2xl glass-dark border border-white/15 shadow-xl flex items-center justify-between">
            <div className="flex flex-col text-left">
              <span className="text-[10px] font-bold text-slate-300 uppercase tracking-wider">Affective Diamond</span>
              <span className="text-xs font-bold text-white mt-1">Autonomic Equilibrium: 92%</span>
              <span className="text-[10px] text-sky-300 font-mono">Synchrony Stable</span>
            </div>

            <div className="w-16 h-16 relative flex items-center justify-center shrink-0">
              <svg className="w-full h-full" viewBox="0 0 100 100">
                <polygon points="50,10 90,50 50,90 10,50" fill="none" stroke="rgba(255,255,255,0.2)" strokeWidth="1.5" strokeDasharray="3 3" />
                <polygon points="50,22 80,50 50,78 20,50" fill="rgba(56, 189, 248, 0.25)" stroke="#38bdf8" strokeWidth="1.5" />
                <circle cx="50" cy="22" r="3.5" fill="#fbbf24" />
                <circle cx="80" cy="50" r="3.5" fill="#38bdf8" />
                <circle cx="50" cy="78" r="3" fill="#fbbf24" />
                <circle cx="20" cy="50" r="3.5" fill="#818cf8" />
              </svg>
            </div>
          </div>
        </div>

        {/* Center Stage (Columns 5-8): Open Aperture for Clear Glass Sphere on Pedestal */}
        <div className="md:col-span-4 flex flex-col items-center justify-end h-80 relative pointer-events-none pb-2">
          {/* Label positioned strictly under the architectural pedestal */}
          <div className="text-center pointer-events-auto mt-auto">
            <h3 className="text-sm font-black text-white tracking-widest uppercase">Daytone</h3>
            <p className="text-[10px] text-slate-300 font-mono tracking-wider">HARMONIC BASELINE</p>
          </div>
        </div>

        {/* Right Flank (Columns 9-12): Weekly Recaps Heatmap & Monthly Chart */}
        <div className="md:col-span-4 flex flex-col gap-3.5">
          <div className="p-4 rounded-2xl glass-dark border border-white/15 shadow-xl flex flex-col justify-between">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold text-white uppercase tracking-wider">Weekly Recaps</span>
              <span className="text-[10px] font-mono text-rose-300 font-bold">BURNOUT DELTA: -22%</span>
            </div>

            {/* Red/Pink Contribution Heatmap Grid */}
            <div className="my-1">
              <div className="grid grid-cols-7 gap-1.5 p-2 rounded-xl bg-slate-950/50 border border-white/10">
                {[
                  'bg-rose-500/30', 'bg-rose-500/50', 'bg-rose-500/80', 'bg-rose-500',
                  'bg-rose-500/90', 'bg-rose-500/40', 'bg-rose-500', 'bg-rose-500/60',
                  'bg-rose-500', 'bg-rose-500/90', 'bg-rose-500/70', 'bg-rose-500',
                  'bg-rose-500/90', 'bg-rose-500/50'
                ].map((c, i) => (
                  <div key={i} className={`w-3.5 h-3.5 rounded-sm ${c}`}></div>
                ))}
              </div>
            </div>

            {/* Monthly Mini Bar Chart */}
            <div className="w-full h-8 flex items-end gap-1.5 pt-2">
              <div className="w-1/6 bg-rose-400/50 rounded-t h-3"></div>
              <div className="w-1/6 bg-rose-400/70 rounded-t h-5"></div>
              <div className="w-1/6 bg-rose-400/80 rounded-t h-4"></div>
              <div className="w-1/6 bg-rose-500 rounded-t h-6"></div>
              <div className="w-1/6 bg-rose-400/90 rounded-t h-5"></div>
              <div className="w-1/6 bg-rose-500 rounded-t h-7"></div>
            </div>
          </div>
        </div>

      </div>

    </section>
  );
};
export default SanctuaryOrb;
