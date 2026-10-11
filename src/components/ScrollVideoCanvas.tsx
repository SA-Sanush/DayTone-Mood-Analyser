import React, { useEffect, useRef, useState, useCallback } from 'react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import Lenis from 'lenis';

gsap.registerPlugin(ScrollTrigger);

export interface ScrollVideoCanvasProps {
  totalFrames?: number;
  frameFolder?: string;
  containerRef: React.RefObject<HTMLDivElement>;
}

export const ScrollVideoCanvas: React.FC<ScrollVideoCanvasProps> = ({
  totalFrames = 300,
  frameFolder = '/anime_frames',
  containerRef,
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const imagesRef = useRef<HTMLImageElement[]>([]);
  const currentFrameRef = useRef<number>(0);
  const [loadProgress, setLoadProgress] = useState<number>(0);

  // Helper to format frame path: /anime_frames/frame_001.jpg ... /anime_frames/frame_300.jpg
  const getFramePath = useCallback((index: number) => {
    const num = String(index + 1).padStart(3, '0');
    return `${frameFolder}/frame_${num}.jpg`;
  }, [frameFolder]);

  // Find closest loaded frame if requested frame is still decoding
  const findClosestFrame = useCallback((idx: number): HTMLImageElement | null => {
    const list = imagesRef.current;
    const direct = list[idx];
    if (direct && direct.complete && direct.naturalWidth > 0) return direct;

    // Search nearest loaded neighbor
    for (let offset = 1; offset < 30; offset++) {
      const prev = list[idx - offset];
      if (prev && prev.complete && prev.naturalWidth > 0) return prev;
      const next = list[idx + offset];
      if (next && next.complete && next.naturalWidth > 0) return next;
    }
    return null;
  }, []);

  // Apple-grade sub-frame optical cross-fade renderer
  const drawFrame = useCallback((frameFloat: number) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d', { alpha: false });
    if (!ctx) return;

    const baseIdx = Math.max(0, Math.min(totalFrames - 1, Math.floor(frameFloat)));
    const nextIdx = Math.min(totalFrames - 1, baseIdx + 1);
    const fraction = frameFloat - baseIdx;

    const img1 = findClosestFrame(baseIdx);
    if (!img1) return;

    const cw = canvas.width;
    const ch = canvas.height;
    const nw = img1.naturalWidth || 1920;
    const nh = img1.naturalHeight || 1080;
    const imgRatio = nw / nh;
    const canvasRatio = cw / ch;

    let drawW: number;
    let drawH: number;
    let drawX: number;
    let drawY: number;

    if (canvasRatio > imgRatio) {
      drawW = cw;
      drawH = cw / imgRatio;
      drawX = 0;
      drawY = (ch - drawH) / 2;
    } else {
      drawH = ch;
      drawW = ch * imgRatio;
      drawX = (cw - drawW) / 2;
      drawY = 0;
    }

    ctx.imageSmoothingEnabled = true;
    ctx.imageSmoothingQuality = 'high';

    // 1. Draw base frame
    ctx.drawImage(
      img1,
      Math.round(drawX),
      Math.round(drawY),
      Math.round(drawW),
      Math.round(drawH)
    );

    // 2. Continuous sub-frame optical cross-fade (the Apple smoothness secret)
    // Eliminates discrete stepped jumps when scrolling slowly
    if (fraction > 0.02 && baseIdx !== nextIdx) {
      const img2 = findClosestFrame(nextIdx);
      if (img2 && img2 !== img1) {
        ctx.globalAlpha = fraction;
        ctx.drawImage(
          img2,
          Math.round(drawX),
          Math.round(drawY),
          Math.round(drawW),
          Math.round(drawH)
        );
        ctx.globalAlpha = 1.0;
      }
    }
  }, [totalFrames, findClosestFrame]);

  // Resize canvas to match display size with HiDPI ratio
  const handleResize = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const width = window.innerWidth;
    const height = window.innerHeight;

    canvas.width = Math.round(width * dpr);
    canvas.height = Math.round(height * dpr);
    canvas.style.width = `${width}px`;
    canvas.style.height = `${height}px`;

    drawFrame(currentFrameRef.current);
  }, [drawFrame]);

  // Two-phase prioritized streaming:
  // Phase 1: Keyframes (every 5th frame) load immediately for instant scrubbable preview
  // Phase 2: In-between frames stream off-thread with async decode
  useEffect(() => {
    const images: HTMLImageElement[] = new Array(totalFrames);
    imagesRef.current = images;

    let loadedCount = 0;

    const loadSingleFrame = (idx: number, isPriority: boolean = false) => {
      const img = new Image();
      if (isPriority) {
        (img as any).fetchPriority = 'high';
      }
      const onReady = () => {
        if (!images[idx]) {
          images[idx] = img;
          loadedCount++;
          const pct = Math.round((loadedCount / totalFrames) * 100);
          setLoadProgress(pct);

          if (idx === 0) {
            handleResize();
            drawFrame(0);
          } else if (Math.abs(idx - currentFrameRef.current) < 2) {
            drawFrame(currentFrameRef.current);
          }
        }
      };

      img.onload = onReady;
      img.onerror = onReady;
      img.src = getFramePath(idx);
      if (typeof img.decode === 'function') {
        img.decode().then(onReady).catch(() => {});
      }
    };

    // 1. Immediate keyframe pass (0, 5, 10, 15, ..., 295, 299)
    loadSingleFrame(0, true);
    for (let i = 5; i < totalFrames; i += 5) {
      loadSingleFrame(i, true);
    }
    loadSingleFrame(totalFrames - 1, true);

    // 2. Stream all remaining intermediate frames in background
    for (let i = 1; i < totalFrames; i++) {
      if (i % 5 !== 0 && i !== totalFrames - 1) {
        loadSingleFrame(i, false);
      }
    }

    window.addEventListener('resize', handleResize);
    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, [totalFrames, getFramePath, handleResize, drawFrame]);

  // Apple-grade luxury scroll physics (Lenis + GSAP ScrollTrigger)
  useEffect(() => {
    if (!containerRef.current) return;

    // Apple physics curve: exponential damping with natural inertia
    const lenis = new Lenis({
      duration: 1.3,
      easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
      orientation: 'vertical',
      gestureOrientation: 'vertical',
      smoothWheel: true,
      wheelMultiplier: 0.82, // buttery smooth, weighted feel
      touchMultiplier: 1.2,
      infinite: false,
    });

    lenis.on('scroll', ScrollTrigger.update);
    (window as any).__lenis = lenis;
    (window as any).ScrollTrigger = ScrollTrigger;
    (window as any).gsap = gsap;

    // Direct tie to GSAP ticker for 60/120 FPS synchronization
    const raf = (time: number) => {
      lenis.raf(time * 1000);
    };
    gsap.ticker.add(raf);
    gsap.ticker.lagSmoothing(0);

    // Continuous floating-point playhead scrub
    const playhead = { frame: 0 };
    const tween = gsap.to(playhead, {
      frame: totalFrames - 1,
      ease: 'none',
      scrollTrigger: {
        trigger: containerRef.current,
        start: 'top top',
        end: 'bottom bottom',
        scrub: true, // Instant 1:1 lock with Lenis inertia curve (zero double-lag)
      },
      onUpdate: () => {
        const frame = Math.min(
          totalFrames - 1,
          Math.max(0, playhead.frame)
        );

        // Draw on every sub-frame tick (optical cross-fade handles intermediate values)
        drawFrame(frame);

        const intFrame = Math.round(frame);
        if (intFrame !== currentFrameRef.current) {
          currentFrameRef.current = intFrame;
        }
      },
    });

    return () => {
      tween.kill();
      gsap.ticker.remove(raf);
      lenis.destroy();
    };
  }, [containerRef, totalFrames, drawFrame]);

  return (
    <div className="fixed inset-0 w-screen h-screen pointer-events-none z-0 overflow-hidden bg-slate-950">
      <canvas
        ref={canvasRef}
        className="w-full h-full block will-change-transform"
      />

      {/* Subtle top progress bar while streaming remaining frames */}
      {loadProgress < 100 && (
        <div className="absolute top-0 left-0 right-0 h-0.5 bg-white/5 z-50 pointer-events-none">
          <div
            className="h-full bg-gradient-to-r from-sky-400 to-indigo-500 transition-all duration-300"
            style={{ width: `${loadProgress}%` }}
          />
        </div>
      )}
    </div>
  );
};
