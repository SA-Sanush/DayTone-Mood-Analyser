import React from 'react';

export const DeviceDashboard: React.FC = () => {
  return (
    <section className="relative w-full h-screen flex flex-col justify-center items-center px-6 py-6 z-10 pointer-events-none">
      
      {/* Tablet / Monitor Frame with thin glowing metallic bezel */}
      <div 
        id="device-frame" 
        className="relative w-full max-w-4xl rounded-[2.5rem] glass-device p-5 md:p-7 pointer-events-auto border border-white/20 shadow-2xl transition-all"
        style={{ transformStyle: 'preserve-3d' }}
      >
        {/* Hardware Top Notch / Camera Sensor */}
        <div className="w-16 h-3 bg-slate-900 rounded-full mx-auto mb-4 border border-white/10 flex items-center justify-center gap-1.5 shadow-inner">
          <div className="w-1.5 h-1.5 rounded-full bg-sky-400/80 animate-ping"></div>
          <div className="w-1.5 h-1.5 rounded-full bg-slate-700"></div>
        </div>

        {/* Interior Device UI Grid */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-5 items-stretch min-h-[380px]">
          
          {/* Left Icon Sidebar (5 Icons) */}
          <div className="hidden md:flex md:col-span-1 flex-col items-center justify-between py-2 border-r border-white/10 pr-3">
            <div className="flex flex-col gap-3.5">
              <button className="w-9 h-9 rounded-xl bg-sky-500/25 border border-sky-400/40 text-sky-300 flex items-center justify-center shadow-sm">
                ⚡
              </button>
              <button className="w-9 h-9 rounded-xl bg-white/5 hover:bg-white/15 text-slate-400 flex items-center justify-center transition-colors">
                📊
              </button>
              <button className="w-9 h-9 rounded-xl bg-white/5 hover:bg-white/15 text-slate-400 flex items-center justify-center transition-colors">
                ▦
              </button>
              <button className="w-9 h-9 rounded-xl bg-white/5 hover:bg-white/15 text-slate-400 flex items-center justify-center transition-colors">
                🔔
              </button>
            </div>
            <button className="w-9 h-9 rounded-xl bg-white/5 hover:bg-white/15 text-slate-400 flex items-center justify-center transition-colors">
              ⚙
            </button>
          </div>

          {/* Main App Display Area */}
          <div className="col-span-1 md:col-span-11 flex flex-col justify-between">
            
            {/* Top Nav Tabs: From / Tidy / Pulse / Meta */}
            <div className="flex items-center justify-between pb-3 border-b border-white/10">
              <div className="flex items-center gap-2">
                <span className="px-3 py-1 rounded-lg bg-sky-500/25 text-sky-300 font-bold text-xs border border-sky-400/35">
                  From
                </span>
                <span className="px-3 py-1 rounded-lg text-slate-400 hover:text-white font-medium text-xs cursor-pointer">
                  Tidy
                </span>
                <span className="px-3 py-1 rounded-lg text-slate-400 hover:text-white font-medium text-xs cursor-pointer">
                  Pulse
                </span>
                <span className="px-3 py-1 rounded-lg text-slate-400 hover:text-white font-medium text-xs cursor-pointer">
                  Meta
                </span>
              </div>
              <div className="text-[10px] font-mono text-slate-400 uppercase tracking-widest">
                CYBERNETIC RESONANCE
              </div>
            </div>

            {/* Content Body: Center is transparent framing area for the 3D Urchin Torus + Notification Stack */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-center my-auto">
              
              {/* Center 3D Framing Area (Open aperture so 3D Urchin Torus sits directly inside) */}
              <div className="lg:col-span-7 flex flex-col items-center justify-center relative min-h-[220px]">
                {/* Ambient glow framing area for the 3D Torus */}
                <div className="w-full h-52 relative flex items-center justify-center pointer-events-none">
                  <div className="w-44 h-44 rounded-full bg-sky-500/10 blur-2xl pointer-events-none" />
                  <div className="absolute bottom-1 text-[10px] font-mono text-sky-400 bg-sky-950/40 px-2.5 py-0.5 rounded-full border border-sky-400/20 backdrop-blur-sm">
                    DIURNAL AXIS: STRESS PEAK MORPH
                  </div>
                </div>
              </div>

              {/* Right Notification Stack */}
              <div className="lg:col-span-5 flex flex-col gap-3.5">
                <div className="p-3.5 rounded-2xl bg-white/10 backdrop-blur-xl border border-white/20 shadow-lg flex items-start gap-3">
                  <span className="w-8 h-8 rounded-xl bg-amber-500/20 text-amber-300 flex items-center justify-center font-bold text-sm shrink-0">
                    ⏰
                  </span>
                  <div>
                    <h5 className="text-xs font-bold text-white">Boundary reminder at 6 PM</h5>
                    <p className="text-[11px] text-slate-300 mt-0.5">Somatic shutdown active to prevent spillover.</p>
                  </div>
                </div>

                <div className="p-3.5 rounded-2xl bg-white/10 backdrop-blur-xl border border-white/20 shadow-lg flex items-start gap-3">
                  <span className="w-8 h-8 rounded-xl bg-indigo-500/20 text-indigo-300 flex items-center justify-center font-bold text-sm shrink-0">
                    ☾
                  </span>
                  <div>
                    <h5 className="text-xs font-bold text-white">Sleep deficit detected</h5>
                    <p className="text-[11px] text-slate-300 mt-0.5">Target wind-down window: 10:15 PM.</p>
                  </div>
                </div>

                <div className="p-2.5 rounded-xl bg-sky-500/10 border border-sky-400/25 flex items-center justify-between text-xs">
                  <span className="text-sky-300 font-semibold">Crystalline Urchin Morph</span>
                  <span className="text-sky-400 font-bold font-mono">LIVE 3D</span>
                </div>
              </div>

            </div>

            {/* Bottom Status Bar */}
            <div className="flex items-center justify-between text-[10px] font-mono text-slate-500 pt-2 border-t border-white/10">
              <span>LATENCY: 14ms</span>
              <span>NEURAL ENGINES ACTIVE</span>
              <span>SECURE HARDWARE ENCLAVE</span>
            </div>

          </div>

        </div>

      </div>

    </section>
  );
};
