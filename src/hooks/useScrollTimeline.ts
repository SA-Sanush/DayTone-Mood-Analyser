import { useEffect, useRef } from 'react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import Lenis from 'lenis';

gsap.registerPlugin(ScrollTrigger);

export interface TimelineState {
  morph: number;
  ridges: number;
  flutes: number;
  spikes: number;
  scale: number;
  posX: number;
  posY: number;
  posZ: number;
  rotX: number;
  rotY: number;
  rotZ: number;
  pedestalScale: number;
  bubblesOpacity: number;
  visible: boolean;
}

// Global mutable timeline state read directly by Three.js useFrame without React setState
export const timelineState: TimelineState = {
  morph: 0,
  ridges: 1,
  flutes: 0,
  spikes: 0,
  scale: 0.68,
  posX: 0,
  posY: 0.62,    // Hero: cleanly between navbar and badge with >24px clearance
  posZ: 0,
  rotX: 0,
  rotY: 0,
  rotZ: 0,
  pedestalScale: 0,
  bubblesOpacity: 0,
  visible: true,
};

export function useScrollTimeline(containerRef: React.RefObject<HTMLDivElement>) {
  const lenisRef = useRef<Lenis | null>(null);

  useEffect(() => {
    // 1. Single Smoothing Layer: Lenis with lerp 0.1
    const lenis = new Lenis({
      lerp: 0.1,
      smoothWheel: true,
      touchMultiplier: 1.5,
    });
    lenisRef.current = lenis;
    (window as any).__lenis = lenis;
    (window as any).__ScrollTrigger = ScrollTrigger;

    // Drive Lenis from GSAP ticker
    lenis.on('scroll', ScrollTrigger.update);
    const tickHandler = (time: number) => lenis.raf(time * 1000);
    gsap.ticker.add(tickHandler);
    gsap.ticker.lagSmoothing(0);

    // 2. Master Scrubbed GSAP Timeline (scrub: true, no lag on top of Lenis)
    const tl = gsap.timeline({
      scrollTrigger: {
        trigger: containerRef.current,
        start: 'top top',
        end: 'bottom bottom',
        scrub: true,
      },
    });

    // Reset initial state
    timelineState.morph = 0;
    timelineState.ridges = 1;
    timelineState.flutes = 0;
    timelineState.spikes = 0;
    timelineState.scale = 0.68;
    timelineState.posX = 0;
    timelineState.posY = 0.62;
    timelineState.rotX = 0;
    timelineState.rotY = 0;
    timelineState.rotZ = 0;
    timelineState.pedestalScale = 0;
    timelineState.bubblesOpacity = 0;
    timelineState.visible = true;

    // -------------------------------------------------------------
    // TRANSITION 1 -> 2 (0.08 to 0.18): Hero -> Feature Cards
    // -------------------------------------------------------------
    tl
      // Hero DOM exits
      .to('#scene-hero', { opacity: 0, y: -40, duration: 0.10 }, 0.08)
      // Background crossfade: Hero -> Features
      .to('#bg-hero', { opacity: 0, duration: 0.10 }, 0.08)
      .to('#bg-features', { opacity: 1, duration: 0.12 }, 0.12)
      // Sphere flies upward and morphs into smooth Torus
      .to(timelineState, {
        posY: 1.6,
        scale: 0.60,
        duration: 0.08,
        ease: 'power2.in',
      }, 0.08)
      .to(timelineState, {
        morph: 1.0,         // Donut Ring (major R=1.0, tube r=0.38)
        ridges: 0.0,
        flutes: 0.0,
        spikes: 0.0,
        rotX: Math.PI * 0.32, // Forward tilt matching video
        rotY: 0,
        rotZ: 0,
        posY: 0.0,
        posX: 0.0,
        scale: 0.74,        // 45% viewport height, clear of step cards
        duration: 0.10,
        ease: 'power2.out',
      }, 0.14)
      // Feature cards DOM enters
      .fromTo('#scene-features',
        { opacity: 0, scale: 0.95 },
        { opacity: 1, scale: 1.0, duration: 0.10 },
        0.16
      )
      .fromTo('.feature-card',
        { y: 35, opacity: 0 },
        { y: 0, opacity: 1, stagger: 0.02, duration: 0.10 },
        0.18
      );

    // -------------------------------------------------------------
    // SCENE 2 PLATEAU (0.18 to 0.36): Hold Clean Donut Steady
    // -------------------------------------------------------------
    // (Timeline maintains morph: 1.0, flutes: 0.0, scale: 0.74)

    // -------------------------------------------------------------
    // TRANSITION 2 -> 3 (0.36 to 0.54): Feature Cards -> Act 2 Ruffled Donut
    // -------------------------------------------------------------
    tl
      // Feature cards DOM exits
      .to('#scene-features', { opacity: 0, y: -30, duration: 0.08 }, 0.36)
      // Background crossfade: Features -> Act 2
      .to('#bg-features', { opacity: 0, duration: 0.10 }, 0.36)
      .to('#bg-act2', { opacity: 1, duration: 0.10 }, 0.38)
      // Act 2 DOM enters
      .fromTo('#scene-act2',
        { opacity: 0, y: 30 },
        { opacity: 1, y: 0, duration: 0.10 },
        0.40
      )
      // Torus deforms to radial ruffled donut & moves center-right, lower
      .to(timelineState, {
        morph: 1.0,
        flutes: 1.0,        // Radial ruffle along tube normal
        spikes: 0.0,
        rotX: Math.PI * 0.34,
        rotY: 0,
        rotZ: 0,
        posX: 0.50,         // Center-right and lower, avoiding notification chips
        posY: -0.15,
        scale: 0.74,
        duration: 0.14,
        ease: 'power2.inOut',
      }, 0.38)
      .to('#circadian-chart-path', {
        strokeDashoffset: 0,
        duration: 0.12,
        ease: 'none',
      }, 0.42);

    // -------------------------------------------------------------
    // TRANSITION 3 -> 4 (0.54 to 0.76): Act 2 -> Dark Tablet & Urchin
    // -------------------------------------------------------------
    tl
      // Act 2 DOM exits
      .to('#scene-act2', { opacity: 0, y: -30, duration: 0.08 }, 0.54)
      // Background crossfade: Act 2 -> Device
      .to('#bg-act2', { opacity: 0, duration: 0.10 }, 0.54)
      .to('#bg-device', { opacity: 1, duration: 0.10 }, 0.56)
      // Device DOM enters
      .fromTo('#scene-device',
        { opacity: 0, scale: 0.90, rotateX: 15 },
        { opacity: 1, scale: 1.0, rotateX: 0, duration: 0.10, ease: 'power2.out' },
        0.58
      )
      // Torus morphs to crystalline spiky urchin cleanly inside left orbit aperture
      .to(timelineState, {
        morph: 1.0,
        flutes: 0.0,
        spikes: 1.0,        // Sharper crystalline urchin spikes
        posX: -0.74,        // Exactly centered on the left orbit aperture
        posY: 0.0,
        rotX: Math.PI * 0.36,
        rotY: 0,
        rotZ: 0,
        scale: 0.42,        // Uniform scale fitting entirely inside the frame
        duration: 0.14,
        ease: 'power2.inOut',
      }, 0.56)
      // Device exits at end of Act 4
      .to('#scene-device', {
        opacity: 0,
        scale: 0.94,
        y: -35,
        duration: 0.08,
      }, 0.74);

    // -------------------------------------------------------------
    // TRANSITION 4 -> 5 (0.74 to 1.00): Urchin -> Sanctuary Orb & Dashboard
    // -------------------------------------------------------------
    tl
      // Background crossfade: Device -> Sanctuary
      .to('#bg-device', { opacity: 0, duration: 0.10 }, 0.74)
      .to('#bg-sanctuary', { opacity: 1, duration: 0.10 }, 0.76)
      // Mesh morphs back to smooth clear sphere on pedestal
      .to(timelineState, {
        morph: 0.0,
        spikes: 0.0,
        flutes: 0.0,
        ridges: 0.0,
        scale: 0.76,        // Clear sphere centered below action buttons
        posX: 0.0,
        posY: 0.08,
        rotX: 0,
        rotY: 0,
        rotZ: 0,
        pedestalScale: 0.82,
        bubblesOpacity: 1.0,
        duration: 0.16,
        ease: 'power2.out',
      }, 0.76)
      // Sanctuary DOM enters
      .fromTo('#scene-sanctuary',
        { opacity: 0, y: 30 },
        { opacity: 1, y: 0, duration: 0.12, ease: 'power2.out' },
        0.78
      )
      .fromTo('#scene5-dashboard',
        { y: 35, opacity: 0 },
        { y: 0, opacity: 1, duration: 0.14, ease: 'power2.out' },
        0.82
      );

    return () => {
      tl.kill();
      ScrollTrigger.getAll().forEach((st) => st.kill());
      gsap.ticker.remove(tickHandler);
      lenis.destroy();
    };
  }, [containerRef]);

  return { lenis: lenisRef.current };
}
