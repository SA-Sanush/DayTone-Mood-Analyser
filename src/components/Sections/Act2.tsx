import React from 'react';

interface Act2Props {
  chartProgress?: number; // 0 to 1
}

export const Act2: React.FC<Act2Props> = ({ chartProgress = 1 }) => {
  // SVG stroke-dashoffset calculation for line drawing animation
  const pathLength = 650;
  const strokeDashoffset = pathLength * (1 - Math.min(1, Math.max(0, chartProgress)));

  return (
    <section className="relative w-full h-screen flex flex-col justify-between items-center px-6 py-12 z-10 pointer-events-none">
      
      {/* Top Header & Content Split */}
      <div className="w-full max-w-5xl mx-auto flex flex-col md:flex-row items-start justify-between gap-8 mt-12 pointer-events-auto">
        
        {/* Left Column: Act 2 Headline & Outline Button */}
        <div className="max-w-md">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/15 border border-emerald-500/30 text-emerald-700 text-xs font-bold tracking-wider mb-4">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <span>Act 2</span>
          </div>

          <h2 className="text-3xl md:text-5xl font-extrabold text-slate-900 tracking-tight leading-tight">
            Stress time tracking
          </h2>

          <p className="mt-3 text-sm text-slate-600 leading-relaxed font-medium">
            Forecasting burnout signals through continuous circadian telemetry. Subtle corrugations in focus indicate elevated strain hours before fatigue is felt.
          </p>

          <button className="mt-6 px-5 py-2.5 rounded-xl border border-slate-800 text-slate-900 hover:bg-slate-900 hover:text-white text-xs font-bold tracking-wide transition-all">
            Explore Protocol →
          </button>
        </div>

        {/* Right Column: Two Glass Notification Chips */}
        <div className="flex flex-col gap-3.5 w-full max-w-xs self-center md:self-auto">
          <div className="p-4 rounded-2xl bg-white/70 backdrop-blur-xl border border-white/90 shadow-xl flex items-start gap-3 transform hover:scale-102 transition-all">
            <span className="w-8 h-8 rounded-xl bg-amber-500/15 text-amber-600 flex items-center justify-center text-sm font-bold shrink-0">
              ⏰
            </span>
            <div>
              <h5 className="text-xs font-bold text-slate-900">Boundary reminder</h5>
              <p className="text-[11px] text-slate-600 mt-0.5">Step away at 6:00 PM to reset cortisol baseline.</p>
            </div>
          </div>

          <div className="p-4 rounded-2xl bg-white/70 backdrop-blur-xl border border-white/90 shadow-xl flex items-start gap-3 transform hover:scale-102 transition-all">
            <span className="w-8 h-8 rounded-xl bg-indigo-500/15 text-indigo-600 flex items-center justify-center text-sm font-bold shrink-0">
              ☾
            </span>
            <div>
              <h5 className="text-xs font-bold text-slate-900">Sleep deficit detected</h5>
              <p className="text-[11px] text-slate-600 mt-0.5">Lower evening cognitive tone recommended.</p>
            </div>
          </div>
        </div>

      </div>

      {/* Bottom: Smooth Green Line-Chart Curve that draws itself */}
      <div className="w-full max-w-5xl mx-auto h-32 relative pointer-events-auto">
        <svg className="w-full h-full overflow-visible" viewBox="0 0 650 100" preserveAspectRatio="none">
          <defs>
            <linearGradient id="chartGlow" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0%" stopColor="#10b981" stopOpacity="0.8" />
              <stop offset="50%" stopColor="#34d399" stopOpacity="1" />
              <stop offset="100%" stopColor="#059669" stopOpacity="0.6" />
            </linearGradient>
            <linearGradient id="chartFill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#10b981" stopOpacity="0.25" />
              <stop offset="100%" stopColor="#10b981" stopOpacity="0" />
            </linearGradient>
          </defs>

          {/* Background Dotted Guideline */}
          <line x1="0" y1="70" x2="650" y2="70" stroke="rgba(16, 185, 129, 0.2)" strokeDasharray="4 4" />

          {/* Area Fill */}
          <path
            d="M 10 70 Q 150 15, 300 65 T 500 25 T 640 50 L 640 100 L 10 100 Z"
            fill="url(#chartFill)"
          />

          {/* Animated Smooth Line */}
          <path
            id="circadian-chart-path"
            d="M 10 70 Q 150 15, 300 65 T 500 25 T 640 50"
            fill="none"
            stroke="url(#chartGlow)"
            strokeWidth="3.5"
            strokeLinecap="round"
            style={{
              strokeDasharray: pathLength,
              strokeDashoffset: 0,
            }}
          />

          {/* Beacon Points */}
          <circle cx="300" cy="65" r="4.5" fill="#10b981" />
          <circle cx="500" cy="25" r="6" fill="#059669" />
          <circle cx="500" cy="25" r="10" fill="none" stroke="#059669" strokeWidth="1.5" className="animate-ping" />
        </svg>

        <div className="flex justify-between text-[10px] font-mono font-bold text-slate-500 mt-1 px-2">
          <span>08:00 AM (Awakening)</span>
          <span>12:30 PM (Midday Load)</span>
          <span className="text-emerald-700">03:45 PM (Resonance Peak)</span>
          <span>09:00 PM (Wind Down)</span>
        </div>
      </div>

    </section>
  );
};
