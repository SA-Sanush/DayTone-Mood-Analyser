import React, { useRef } from 'react';
import { ScrollVideoCanvas } from './components/ScrollVideoCanvas.tsx';
import { ScrollOverlays } from './components/ScrollOverlays.tsx';

export const App: React.FC = () => {
  const containerRef = useRef<HTMLDivElement>(null);

  return (
    <div
      ref={containerRef}
      className="relative w-full font-sans bg-slate-950 text-white select-none"
      style={{
        height: '500vh',
      }}
    >
      {/* 1. ULTRA-SMOOTH CANVAS SEQUENCE SCRUBBER (z: 0) */}
      <ScrollVideoCanvas
        totalFrames={300}
        frameFolder="/anime_frames"
        containerRef={containerRef}
      />

      {/* 2. RICH SCROLL-SYNCHRONIZED TEXT & FEATURE OVERLAYS (z: 10) */}
      <ScrollOverlays
        containerRef={containerRef}
      />
    </div>
  );
};

export default App;
