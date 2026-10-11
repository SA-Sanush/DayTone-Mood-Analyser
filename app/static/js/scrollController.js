/**
 * DayTone 100% Video Recreation Master GSAP Scroll Controller (scrollController.js)
 * Orchestrates:
 * - Act 1: Soft apricot-to-sage dawn gradient + 3D floating frosted cards + liquid glass Torus
 * - Act 2: Camera swoop into dark mineral slate + tablet cockpit dock + fluted spiky torus morph
 * - Act 3: Tone Constellation analytics hub + interactive draggable pebble diamond quadrant + SVG tether
 * - Act 4: Spatial computing sanctuary finale + liquid glass orb on pedestal + micro-droplets + floating panels
 */

import { DaytoneScrollyEngine } from './daytoneScroll3D.js';

const gsap = window.gsap;
const ScrollTrigger = window.ScrollTrigger;
const Lenis = window.Lenis;

if (gsap && ScrollTrigger) {
  gsap.registerPlugin(ScrollTrigger);
}

function initController() {
  const canvas = document.getElementById('scrolly-canvas');
  const track = document.getElementById('scroll-track');

  if (!canvas || !track) return;

  const EngineClass = typeof DaytoneScrollyEngine !== 'undefined' ? DaytoneScrollyEngine : (window.DaytoneScrollyEngine || window.DaytoneScrollEngine);
  if (!EngineClass) {
    console.warn('[DayTone] DaytoneScrollyEngine not loaded.');
    return;
  }

  const engine = new EngineClass(canvas);

  // Initialize smooth inertia scroll (Lenis)
  let lenis = null;
  if (typeof Lenis !== 'undefined') {
    lenis = new Lenis({
      duration: 1.25,
      easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
      smoothWheel: true,
      touchMultiplier: 1.5,
    });
    lenis.on('scroll', ScrollTrigger.update);
    gsap.ticker.add((time) => lenis.raf(time * 1000));
    gsap.ticker.lagSmoothing(0);
    window.lenis = lenis;
  }

  // Navbar elements
  const stageBadge = document.getElementById('stage-badge');
  const navBrandText = document.getElementById('nav-brand-text');
  const navSigninLink = document.getElementById('nav-signin-link');
  const globalNavbar = document.getElementById('global-navbar');
  const scrollPromptText = document.getElementById('scroll-prompt-text');

  // Master GSAP Scrollytelling Timeline
  const tl = gsap.timeline({
    scrollTrigger: {
      trigger: '#scroll-track',
      start: 'top top',
      end: 'bottom bottom',
      scrub: 1.2,
    }
  });

  // =========================================================================
  // ACT 1 -> ACT 2 TRANSITION (Scroll 0% to 35%)
  // =========================================================================
  tl
    // Orbiting Act 1 cards drift and disperse
    .to('#act-1-layer .act-card', {
      scale: 0.85,
      opacity: 0,
      y: (i) => (i % 2 === 0 ? -40 : 40),
      x: (i) => (i < 2 ? -30 : 30),
      stagger: 0.02,
      duration: 0.22,
      ease: 'power2.inOut'
    }, 0.05)

    // Dawn apricot-to-sage gradient shifts to deep mineral slate
    .to(track, {
      background: 'radial-gradient(ellipse at 50% 40%, #0f172a 0%, #020617 100%)',
      duration: 0.35,
      ease: 'power2.inOut'
    }, 0.08)

    // Navbar adapts to dark mode styling
    .to(globalNavbar, {
      backgroundColor: 'rgba(15, 23, 42, 0.65)',
      borderColor: 'rgba(255, 255, 255, 0.15)',
      duration: 0.25
    }, 0.1)
    .to([navBrandText, navSigninLink], {
      color: '#f8fafc',
      duration: 0.25
    }, 0.1)

    // 3D Camera swoops down to low-angle HUD view
    .to(engine.camera.position, {
      y: -0.65,
      z: 5.0,
      duration: 0.35,
      ease: 'power2.out'
    }, 0.12)

    // Torus tilts forward into isometric analytical posture
    .to(engine.torus.rotation, {
      x: Math.PI * 0.52,
      y: -Math.PI * 0.02,
      duration: 0.35,
      ease: 'power2.out'
    }, 0.12)

    // 3D floor perspective grid & glowing cyan coordinate disc illuminate
    .to(engine.grid.material, { opacity: 0.45, duration: 0.25 }, 0.15)
    .to(engine.disc.material, { opacity: 0.68, duration: 0.25 }, 0.18)

    // FLUTED & SPIKY MORPH: uSpikes uniform triggers fluted corrugation + rear-left acute spikes
    .to(engine.material.uniforms.uSpikes, {
      value: 0.48,
      duration: 0.3,
      ease: 'power1.inOut'
    }, 0.16)

    // Act 2 Tablet Cockpit scales in
    .to('#act-2-layer', {
      opacity: 1,
      scale: 1,
      pointerEvents: 'auto',
      duration: 0.3,
      ease: 'power2.out'
    }, 0.2)
    .call(() => {
      if (stageBadge) stageBadge.textContent = 'Act 2: Stress Disruption';
      if (scrollPromptText) scrollPromptText.textContent = 'Keep scrolling for analytics';
    }, null, 0.22);

  // =========================================================================
  // ACT 2 -> ACT 3 TRANSITION (Scroll 35% to 68%)
  // =========================================================================
  tl
    // Tablet cockpit expands slightly and fades out
    .to('#act-2-layer', {
      opacity: 0,
      scale: 1.05,
      pointerEvents: 'none',
      duration: 0.25,
      ease: 'power2.in'
    }, 0.45)

    // Background transitions to dark indigo nebula
    .to(track, {
      background: 'radial-gradient(ellipse at 50% 30%, #111e38 0%, #020617 100%)',
      duration: 0.3
    }, 0.46)

    // Torus calms down: uSpikes returns to 0 (smooth fluid ring)
    .to(engine.material.uniforms.uSpikes, {
      value: 0.0,
      duration: 0.28,
      ease: 'power2.out'
    }, 0.48)

    // Torus rises and recedes behind the Act 3 dashboard
    .to(engine.torus.position, {
      y: 1.15,
      z: -1.8,
      duration: 0.35,
      ease: 'power2.out'
    }, 0.48)
    .to(engine.torus.scale, {
      x: 0.68,
      y: 0.68,
      z: 0.68,
      duration: 0.35
    }, 0.48)

    // Grid and disc soften
    .to(engine.disc.material, { opacity: 0.0, duration: 0.2 }, 0.48)
    .to(engine.grid.material, { opacity: 0.15, duration: 0.25 }, 0.48)

    // Reveal Act 3 Tone Constellation & Analytics Hub
    .fromTo('#act-3-layer', 
      { opacity: 0, y: 35, pointerEvents: 'none' },
      { opacity: 1, y: 0, pointerEvents: 'auto', duration: 0.3, ease: 'power2.out' },
      0.54
    )
    .call(() => {
      if (stageBadge) stageBadge.textContent = 'Act 3: Tone Constellation';
      if (scrollPromptText) scrollPromptText.textContent = 'Explore quadrant & scroll to finale';
    }, null, 0.55);

  // =========================================================================
  // ACT 3 -> ACT 4 FINALE TRANSITION (Scroll 68% to 100%)
  // =========================================================================
  tl
    // Act 3 hub lifts up and fades out
    .to('#act-3-layer', {
      opacity: 0,
      y: -35,
      pointerEvents: 'none',
      duration: 0.25,
      ease: 'power2.in'
    }, 0.74)

    // Background expands into obsidian cosmic sanctuary stage
    .to(track, {
      background: 'radial-gradient(circle at 50% 50%, #0f172a 0%, #000000 100%)',
      duration: 0.3
    }, 0.75)

    // Torus recedes and scales to zero
    .to(engine.torus.scale, {
      x: 0.001,
      y: 0.001,
      z: 0.001,
      duration: 0.25
    }, 0.75)

    // Camera repositions for Grand Sanctuary Orb
    .to(engine.camera.position, {
      x: 0,
      y: 0.15,
      z: 5.6,
      duration: 0.35,
      ease: 'power2.out'
    }, 0.76)

    // FINALE SANCTUARY GROUP SCALES UP: Pedestal + Liquid Crystal Sphere + Orbiting Droplets
    .to(engine.finaleGroup.scale, {
      x: 1.0,
      y: 1.0,
      z: 1.0,
      duration: 0.35,
      ease: 'back.out(1.2)'
    }, 0.76)
    .to(engine.finaleGroup.position, {
      y: -0.2,
      duration: 0.35
    }, 0.76)

    // Reveal Act 4 Spatial Computing Sanctuary HUD
    .fromTo('#act-4-layer',
      { opacity: 0, scale: 0.95, pointerEvents: 'none' },
      { opacity: 1, scale: 1.0, pointerEvents: 'auto', duration: 0.3, ease: 'power2.out' },
      0.82
    )
    .call(() => {
      if (stageBadge) stageBadge.textContent = 'Act 4: Spatial Sanctuary';
      if (scrollPromptText) scrollPromptText.textContent = 'DayTone Rhythm Synchronized';
    }, null, 0.84);

  // Initialize Draggable Pebble in Act 3
  setupInteractivePebble();
}

/**
 * Interactive Draggable Pebble with Live SVG Vector Tether in Act 3
 */
function setupInteractivePebble() {
  const pebble = document.getElementById('drag-pebble');
  const box = document.getElementById('quadrant-box');
  const tetherLine = document.getElementById('pebble-tether-line');
  const coordVal = document.getElementById('pebble-coord-val');

  if (!pebble || !box || !tetherLine) return;

  let isDragging = false;
  const originX = 140; // SVG viewBox center (280 / 2)
  const originY = 140;

  function updatePebblePosition(clientX, clientY) {
    const rect = box.getBoundingClientRect();
    const relX = clientX - rect.left;
    const relY = clientY - rect.top;

    // Constrain within quadrant box
    const padding = 20;
    const clampedX = Math.max(padding, Math.min(rect.width - padding, relX));
    const clampedY = Math.max(padding, Math.min(rect.height - padding, relY));

    // Update pebble DOM position
    pebble.style.left = `${clampedX - 16}px`;
    pebble.style.top = `${clampedY - 16}px`;

    // Map to SVG coordinates (0 - 280)
    const svgX = (clampedX / rect.width) * 280;
    const svgY = (clampedY / rect.height) * 280;

    // Update SVG tether line
    tetherLine.setAttribute('x2', svgX);
    tetherLine.setAttribute('y2', svgY);

    // Calculate normalized valence & arousal (-1.0 to +1.0)
    const normX = ((svgX - originX) / (originX - padding)).toFixed(2);
    const normY = (-(svgY - originY) / (originY - padding)).toFixed(2);

    const signX = normX >= 0 ? '+' : '';
    const signY = normY >= 0 ? '+' : '';

    if (coordVal) {
      coordVal.textContent = `Arousal: ${signY}${normY} · Valence: ${signX}${normX}`;
    }
  }

  // Mouse / Pointer Events
  pebble.addEventListener('pointerdown', (e) => {
    isDragging = true;
    pebble.setPointerCapture(e.pointerId);
    pebble.classList.add('scale-110');
    e.preventDefault();
  });

  window.addEventListener('pointermove', (e) => {
    if (!isDragging) return;
    updatePebblePosition(e.clientX, e.clientY);
  });

  window.addEventListener('pointerup', (e) => {
    if (isDragging) {
      isDragging = false;
      pebble.classList.remove('scale-110');
    }
  });

  // Touch fallback
  box.addEventListener('touchmove', (e) => {
    if (e.touches && e.touches[0] && isDragging) {
      updatePebblePosition(e.touches[0].clientX, e.touches[0].clientY);
    }
  }, { passive: true });
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initController);
} else {
  initController();
}
