import React, { useEffect, useRef, useState } from 'react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { TiltCard } from './TiltCard';
import { 
  Sun, 
  Leaf, 
  Clock, 
  Activity, 
  Radio, 
  BarChart2, 
  Moon, 
  Volume2, 
  ShieldCheck, 
  Compass, 
  Check, 
  X,
  Eye,
  EyeOff
} from 'lucide-react';

gsap.registerPlugin(ScrollTrigger);

export interface ScrollOverlaysProps {
  containerRef: React.RefObject<HTMLDivElement>;
}

export const ScrollOverlays: React.FC<ScrollOverlaysProps> = ({ containerRef }) => {
  const heroRef = useRef<HTMLDivElement>(null);
  const navRef = useRef<HTMLElement>(null);
  const feat1Ref = useRef<HTMLDivElement>(null);
  const feat2Ref = useRef<HTMLDivElement>(null);
  const feat3Ref = useRef<HTMLDivElement>(null);
  const feat4Ref = useRef<HTMLDivElement>(null);

  // Audio state
  const [isPlayingTone, setIsPlayingTone] = useState(false);

  // Active navigation section state
  const [activeSection, setActiveSection] = useState<'overview' | 'baseline' | 'resonance' | 'harmonics' | 'sanctuary'>('overview');
  const [circadianInfo, setCircadianInfo] = useState({ time: '', phase: 'Golden Hour Calm' });

  // Update live real-time circadian status
  useEffect(() => {
    const updateCircadian = () => {
      const now = new Date();
      const h = now.getHours();
      const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      let phase = 'Circadian Flow';
      if (h >= 5 && h < 11) phase = 'Dawn Baseline';
      else if (h >= 11 && h < 16) phase = 'Daylight Resonance';
      else if (h >= 16 && h < 20) phase = 'Golden Hour Calm';
      else phase = 'Twilight Stillness';
      setCircadianInfo({ time: timeStr, phase });
    };
    updateCircadian();
    const interval = setInterval(updateCircadian, 30000);
    return () => clearInterval(interval);
  }, []);

  // Heatmap modal preview state
  const [showHeatmapModal, setShowHeatmapModal] = useState(false);

  // Auth form state for Scene 5 (after scrolling animation)
  const [authTab, setAuthTab] = useState<'login' | 'register'>('login');
  const [authName, setAuthName] = useState('');
  const [authEmail, setAuthEmail] = useState('');
  const [authPassword, setAuthPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(true);
  const [authLoading, setAuthLoading] = useState(false);
  const [authError, setAuthError] = useState<string | null>(null);
  const [authSuccess, setAuthSuccess] = useState<string | null>(null);

  // Smooth scroll helper using Lenis or window fallback
  const scrollToProgress = (progress: number) => {
    const maxScroll = document.documentElement.scrollHeight - window.innerHeight;
    const target = Math.round(progress * maxScroll);
    const lenis = (window as any).__lenis;
    if (lenis && typeof lenis.scrollTo === 'function') {
      lenis.scrollTo(target, { duration: 1.4 });
    } else {
      window.scrollTo({ top: target, behavior: 'smooth' });
    }
  };

  // Detect direct URL entry to /login, /register, or hash anchors on initial mount
  useEffect(() => {
    const handleUrlRoute = () => {
      const path = (window.location.pathname || '').toLowerCase();
      const hash = (window.location.hash || '').toLowerCase();
      if (path.includes('register') || hash.includes('register')) {
        setAuthTab('register');
        setTimeout(() => scrollToProgress(0.95), 350);
      } else if (path.includes('login') || hash.includes('login')) {
        setAuthTab('login');
        setTimeout(() => scrollToProgress(0.95), 350);
      }
    };
    handleUrlRoute();
    window.addEventListener('popstate', handleUrlRoute);
    return () => window.removeEventListener('popstate', handleUrlRoute);
  }, []);

  // 432 Hz Solfeggio harmonic tone using native Web Audio API
  const playHarmonicTone = () => {
    try {
      const AudioContextClass = window.AudioContext || (window as any).webkitAudioContext;
      if (!AudioContextClass) return;
      const ctx = new AudioContextClass();
      if (ctx.state === 'suspended') {
        ctx.resume();
      }

      const osc = ctx.createOscillator();
      const gain = ctx.createGain();

      // 432 Hz Solfeggio frequency
      osc.type = 'sine';
      osc.frequency.setValueAtTime(432, ctx.currentTime);

      // Smooth gentle envelope
      gain.gain.setValueAtTime(0.0001, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.18, ctx.currentTime + 0.3);
      gain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 2.2);

      osc.connect(gain);
      gain.connect(ctx.destination);

      osc.start();
      osc.stop(ctx.currentTime + 2.2);

      setIsPlayingTone(true);
      setTimeout(() => setIsPlayingTone(false), 2200);
    } catch (err) {
      console.warn('Audio tone could not play', err);
    }
  };

  // Handle in-page login / register submission
  const handleAuthSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthLoading(true);
    setAuthError(null);
    setAuthSuccess(null);

    const endpoint = authTab === 'login' ? '/api/login' : '/api/register';
    const payload = authTab === 'login' 
      ? { email: authEmail, password: authPassword, remember_me: rememberMe }
      : { name: authName, email: authEmail, password: authPassword };

    try {
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(payload),
      });

      const data = await response.json().catch(() => ({}));

      if (response.ok && data.success) {
        setAuthSuccess(authTab === 'login' ? 'Signed in! Redirecting to sanctuary...' : 'Account created! Welcome to DayTone...');
        setTimeout(() => {
          window.location.href = data.redirect || '/dashboard';
        }, 800);
      } else {
        setAuthError(data.message || (authTab === 'login' ? 'Invalid email or password.' : 'Could not create account. Please check details.'));
      }
    } catch {
      // Fallback: standard form submit if fetch fails
      const form = document.createElement('form');
      form.method = 'POST';
      form.action = authTab === 'login' ? '/login' : '/register';
      
      const emailInput = document.createElement('input');
      emailInput.type = 'hidden';
      emailInput.name = 'email';
      emailInput.value = authEmail;
      form.appendChild(emailInput);

      const passInput = document.createElement('input');
      passInput.type = 'hidden';
      passInput.name = 'password';
      passInput.value = authPassword;
      form.appendChild(passInput);

      if (authTab === 'register') {
        const nameInput = document.createElement('input');
        nameInput.type = 'hidden';
        nameInput.name = 'name';
        nameInput.value = authName;
        form.appendChild(nameInput);
      }

      document.body.appendChild(form);
      form.submit();
    } finally {
      setAuthLoading(false);
    }
  };

  useEffect(() => {
    if (!containerRef.current) return;

    const ctx = gsap.context(() => {
      // Synchronized scrub timeline with autoAlpha & pointer-events safety
      const master = gsap.timeline({
        scrollTrigger: {
          trigger: containerRef.current,
          start: 'top top',
          end: 'bottom bottom',
          scrub: true, // 1:1 direct sync with Lenis smooth momentum
          onUpdate: (self) => {
            const p = self.progress;
            if (p < 0.20) {
              setActiveSection('overview');
            } else if (p < 0.42) {
              setActiveSection('baseline');
            } else if (p < 0.64) {
              setActiveSection('resonance');
            } else if (p < 0.85) {
              setActiveSection('harmonics');
            } else {
              setActiveSection('sanctuary');
            }
          },
        },
      });

      // 1. HERO CONTENT (0.00 to 0.16) - Top Navbar remains persistent across all scenes
      master
        .to(heroRef.current, { autoAlpha: 0, y: -45, scale: 0.98, pointerEvents: 'none', ease: 'power2.inOut', duration: 0.09 }, 0.07);

      // 2. FEATURE 01: Ambient Glass Display & Morning Baseline (0.17 to 0.41)
      master
        .fromTo(
          feat1Ref.current,
          { autoAlpha: 0, y: 35, scale: 0.97, pointerEvents: 'none' },
          { autoAlpha: 1, y: 0, scale: 1, pointerEvents: 'auto', ease: 'power2.out', duration: 0.06 },
          0.17
        )
        .to(
          feat1Ref.current,
          { autoAlpha: 0, y: -25, scale: 0.98, pointerEvents: 'none', ease: 'power2.in', duration: 0.06 },
          0.35
        );

      // 3. FEATURE 02: Physical Haptic Dial & Frequency Tuning (0.42 to 0.63)
      master
        .fromTo(
          feat2Ref.current,
          { autoAlpha: 0, y: 35, scale: 0.97, pointerEvents: 'none' },
          { autoAlpha: 1, y: 0, scale: 1, pointerEvents: 'auto', ease: 'power2.out', duration: 0.06 },
          0.42
        )
        .to(
          feat2Ref.current,
          { autoAlpha: 0, y: -25, scale: 0.98, pointerEvents: 'none', ease: 'power2.in', duration: 0.06 },
          0.58
        );

      // 4. FEATURE 03: Binaural Tone Stabilization & Waves (0.64 to 0.84)
      master
        .fromTo(
          feat3Ref.current,
          { autoAlpha: 0, y: 35, scale: 0.97, pointerEvents: 'none' },
          { autoAlpha: 1, y: 0, scale: 1, pointerEvents: 'auto', ease: 'power2.out', duration: 0.06 },
          0.64
        )
        .to(
          feat3Ref.current,
          { autoAlpha: 0, y: -25, scale: 0.98, pointerEvents: 'none', ease: 'power2.in', duration: 0.06 },
          0.79
        );

      // 5. FEATURE 04 / FINAL SECTION: Login & Register Sanctuary Gateway (0.85 to 1.00)
      master
        .fromTo(
          feat4Ref.current,
          { autoAlpha: 0, y: 35, scale: 0.97, pointerEvents: 'none' },
          { autoAlpha: 1, y: 0, scale: 1, pointerEvents: 'auto', ease: 'power2.out', duration: 0.07 },
          0.85
        );

      master.set({}, {}, 1.0);
    }, containerRef);

    return () => ctx.revert();
  }, [containerRef]);

  return (
    <div className="fixed inset-0 w-screen h-screen pointer-events-none z-10 overflow-hidden select-none">
      
      {/* ============================================================== */}
      {/* GLOBAL TOP NAVBAR (Frosted Glass Floating Capsule) */}
      {/* ============================================================== */}
      <header 
        ref={navRef}
        className="fixed top-4 left-1/2 -translate-x-1/2 z-50 flex items-center justify-between gap-4 sm:gap-7 w-max max-w-[95vw] pointer-events-auto will-change-transform glass-nav px-4 sm:px-6 py-2 rounded-full shadow-2xl transition-all"
      >
        {/* Brand & Live Real-Time Circadian Feed */}
        <button 
          onClick={() => scrollToProgress(0)}
          className="flex items-center gap-2 sm:gap-2.5 cursor-pointer text-left bg-transparent border-none p-0 group shrink-0"
          title="Return to top"
        >
          <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-sky-400 via-teal-300 to-indigo-500 p-[1.5px] shadow-md shadow-sky-500/25 group-hover:scale-105 transition-transform">
            <div className="w-full h-full bg-slate-950/70 rounded-[10px] flex items-center justify-center backdrop-blur-md">
              <span className="font-extrabold text-xs text-transparent bg-clip-text bg-gradient-to-r from-sky-300 to-teal-200">
                DT
              </span>
            </div>
          </div>
          <span className="text-base font-bold tracking-tight text-white drop-shadow-sm group-hover:text-sky-300 transition-colors">
            DayTone
          </span>
          <span className="hidden sm:inline-flex items-center gap-1.5 glass-pill px-2.5 py-0.5 rounded-full text-emerald-300 text-[11px] font-medium">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            <span>{circadianInfo.time ? `${circadianInfo.time} · ${circadianInfo.phase}` : 'Live Circadian Feed'}</span>
          </span>
        </button>

        {/* Center navigation links: Current active section tracking + DayTone core tools */}
        <nav className="hidden md:flex items-center gap-1 text-xs font-medium text-slate-200">
          <button 
            onClick={() => scrollToProgress(0)} 
            className={`px-2.5 py-1.5 rounded-xl transition-all cursor-pointer ${
              activeSection === 'overview'
                ? 'bg-white/20 text-white font-bold shadow-sm'
                : 'text-slate-300 hover:text-white hover:bg-white/10'
            }`}
          >
            Overview
          </button>
          <button 
            onClick={() => scrollToProgress(0.28)} 
            className={`px-2.5 py-1.5 rounded-xl transition-all cursor-pointer ${
              activeSection === 'baseline'
                ? 'bg-emerald-500/30 text-emerald-200 border border-emerald-400/30 font-bold shadow-sm'
                : 'text-slate-300 hover:text-white hover:bg-white/10'
            }`}
          >
            Baseline
          </button>
          <button 
            onClick={() => scrollToProgress(0.52)} 
            className={`px-2.5 py-1.5 rounded-xl transition-all cursor-pointer ${
              activeSection === 'resonance'
                ? 'bg-amber-500/30 text-amber-200 border border-amber-400/30 font-bold shadow-sm'
                : 'text-slate-300 hover:text-white hover:bg-white/10'
            }`}
          >
            Resonance
          </button>
          <button 
            onClick={() => scrollToProgress(0.72)} 
            className={`px-2.5 py-1.5 rounded-xl transition-all cursor-pointer ${
              activeSection === 'harmonics'
                ? 'bg-sky-500/30 text-sky-200 border border-sky-400/30 font-bold shadow-sm'
                : 'text-slate-300 hover:text-white hover:bg-white/10'
            }`}
          >
            Harmonics
          </button>
          <button 
            onClick={() => {
              setAuthTab('login');
              window.history.pushState(null, '', '/login');
              scrollToProgress(0.95);
            }} 
            className={`px-2.5 py-1.5 rounded-xl transition-all cursor-pointer ${
              activeSection === 'sanctuary'
                ? 'bg-indigo-500/30 text-indigo-200 border border-indigo-400/30 font-bold shadow-sm'
                : 'text-slate-300 hover:text-white hover:bg-white/10'
            }`}
          >
            Sanctuary
          </button>

        </nav>

        {/* Right CTAs: Smoothly glide to Register or Sign In at the end of the scroll */}
        <div className="flex items-center gap-2 sm:gap-2.5 shrink-0">
          <button
            onClick={() => {
              setAuthTab('register');
              window.history.pushState(null, '', '/register');
              scrollToProgress(0.95);
            }}
            className="glass-btn-secondary px-3.5 py-1.5 rounded-xl text-white text-xs font-semibold hover:-translate-y-0.5 active:translate-y-0 transition-all shadow-sm cursor-pointer"
          >
            Register
          </button>
          <button 
            onClick={() => {
              setAuthTab('login');
              window.history.pushState(null, '', '/login');
              scrollToProgress(0.95);
            }}
            className="glass-btn-primary px-4 py-1.5 rounded-xl text-white text-xs font-bold hover:-translate-y-0.5 active:translate-y-0 transition-all shadow-md cursor-pointer"
          >
            Sign In
          </button>
        </div>
      </header>

      {/* ============================================================== */}
      {/* 1. HERO SECTION (Mindful Morning Sanctuary) */}
      {/* ============================================================== */}
      <div 
        ref={heroRef}
        className="absolute inset-0 flex flex-col justify-center items-center px-6 pt-20 pb-8 pointer-events-none will-change-transform"
      >
        {/* Central Hero Typography & Glass Controls */}
        <div className="text-center max-w-3xl mx-auto flex flex-col items-center pointer-events-auto my-auto">
          {/* Pill badge */}
          <div className="glass-pill inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-sky-200 text-xs font-semibold mb-4 shadow-xl">
            <span className="w-1.5 h-1.5 rounded-full bg-sky-400 animate-pulse" />
            <span>DayTone · Circadian Mindfulness & Rhythm</span>
          </div>

          {/* Title */}
          <h1 className="text-4xl sm:text-5xl md:text-6xl font-extrabold tracking-tight text-white leading-[1.12] drop-shadow-lg">
            Listen to the{' '}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-sky-400 via-teal-300 to-indigo-400">
              rhythm
            </span>{' '}
            of your day.
          </h1>

          {/* Subtitle */}
          <p className="mt-4 text-sm sm:text-base text-slate-100 max-w-xl mx-auto leading-relaxed drop-shadow-md font-normal">
            A mindful cognitive sanctuary. Track emotional tone, energy frequencies, and circadian harmony through daily tactile micro-reflections.
          </p>

          {/* Action buttons */}
          <div className="mt-7 flex flex-wrap items-center justify-center gap-4">
            <button 
              onClick={() => {
                setAuthTab('register');
                window.history.pushState(null, '', '/register');
                scrollToProgress(0.95);
              }}
              className="glass-btn-primary px-7 py-3 rounded-2xl text-white text-sm font-bold shadow-xl hover:-translate-y-0.5 active:translate-y-0 transition-all flex items-center gap-2 cursor-pointer"
            >
              <span>Begin Daily Check-In</span>
              <span>→</span>
            </button>
            <button 
              onClick={() => scrollToProgress(0.28)}
              className="glass-btn-secondary px-6 py-3 rounded-2xl text-white text-sm font-semibold hover:-translate-y-0.5 active:translate-y-0 transition-all shadow-md flex items-center gap-2 cursor-pointer"
            >
              <span>Explore Morning Baseline</span>
              <span>↓</span>
            </button>
          </div>
        </div>
      </div>

      {/* ============================================================== */}
      {/* 2. FEATURE 01: AMBIENT GLASS DISPLAY & MORNING BASELINE */}
      {/* ============================================================== */}
      <div 
        ref={feat1Ref}
        className="absolute inset-0 flex items-end md:items-center justify-start px-6 md:px-16 pb-12 md:pb-0 pointer-events-none will-change-transform"
      >
        <TiltCard 
          maxTilt={9} 
          scale={1.02} 
          perspective={1000}
          glare={true}
          className="glass-card flex flex-col gap-4 sm:gap-4.5 p-7 sm:p-8 md:p-9 rounded-3xl pointer-events-auto w-full max-w-xl md:max-w-[620px] lg:max-w-[640px]"
        >
          <div className="tilt-depth flex items-center justify-between gap-3">
            <div className="glass-pill inline-flex items-center gap-2 px-3.5 py-1 rounded-full text-emerald-300 text-[11px] font-mono font-bold tracking-wider w-fit">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
              01 · DAWN EQUILIBRIUM
            </div>
            <span className="text-[11px] sm:text-xs font-medium text-emerald-200/90 flex items-center gap-1.5">
              <Leaf className="w-3.5 h-3.5 text-emerald-300" />
              <span>Morning Sanctuary</span>
            </span>
          </div>

          <h3 className="tilt-depth text-2xl sm:text-3xl font-extrabold text-white tracking-tight drop-shadow-sm">
            Awaken Without Urgency
          </h3>

          <p className="tilt-depth text-xs sm:text-[13px] text-slate-200/90 leading-relaxed font-normal">
            Before notifications invade your headspace, calibrate your inner tone. DayTone's ambient glass hardware invites a tranquil 30-second ritual to anchor circadian clarity.
          </p>

          {/* Inspiring Circadian Quote with Botanical Card */}
          <div className="tilt-depth glass-card-sm p-4 sm:p-4.5 rounded-2xl border border-white/20 relative overflow-hidden bg-gradient-to-br from-emerald-500/10 via-teal-500/5 to-transparent">
            <div className="absolute -top-10 -right-10 w-24 h-24 bg-emerald-400/20 rounded-full blur-xl pointer-events-none" />
            <div className="flex items-start gap-3 relative z-10">
              <span className="text-2xl text-emerald-300 font-serif leading-none select-none">“</span>
              <div className="flex flex-col gap-1">
                <p className="text-xs sm:text-[13px] text-emerald-50 font-medium italic leading-relaxed">
                  Smile, breathe, and go slowly. There is nowhere to rush; morning is an offering.
                </p>
                <span className="text-[10px] text-emerald-300/80 font-mono tracking-wider">
                  — Thich Nhat Hanh
                </span>
              </div>
            </div>
          </div>

          {/* Luminous Circadian Micro-Visual & Badges */}
          <div className="tilt-depth flex flex-wrap items-center gap-2 sm:gap-2.5 pt-0.5">
            <span className="glass-pill flex items-center gap-1.5 px-3 py-1 rounded-xl text-[11px] text-slate-200 font-medium">
              <Sun className="w-3 h-3 text-amber-300" />
              <span>Dawn Calibration</span>
            </span>
            <span className="glass-pill flex items-center gap-1.5 px-3 py-1 rounded-xl text-[11px] text-slate-200 font-medium">
              <Leaf className="w-3 h-3 text-emerald-300" />
              <span>Grounded Presence</span>
            </span>
            <span className="glass-pill flex items-center gap-1.5 px-3 py-1 rounded-xl text-[11px] text-slate-200 font-medium">
              <Clock className="w-3 h-3 text-teal-300" />
              <span>Unrushed Space</span>
            </span>
          </div>

          {/* Interactive Actions for Feature 01 */}
          <div className="tilt-depth flex flex-wrap items-center gap-3 pt-3 mt-1 border-t border-white/15">
            <button 
              onClick={() => scrollToProgress(0.52)}
              className="glass-btn-primary px-5 py-2.5 rounded-xl text-white text-xs font-bold shadow-md hover:-translate-y-0.5 active:translate-y-0 transition-all flex items-center gap-2 cursor-pointer"
            >
              <span>Explore Emotional Tone</span>
              <span>→</span>
            </button>
            <button 
              onClick={() => {
                setAuthTab('register');
                scrollToProgress(0.95);
              }}
              className="glass-btn-secondary px-4 py-2.5 rounded-xl text-white text-xs font-semibold hover:-translate-y-0.5 active:translate-y-0 transition-all shadow-sm cursor-pointer"
            >
              Begin Calibration
            </button>
          </div>
        </TiltCard>
      </div>

      {/* ============================================================== */}
      {/* 3. FEATURE 02: PHYSICAL HAPTIC FREQUENCY TUNING */}
      {/* ============================================================== */}
      <div 
        ref={feat2Ref}
        className="absolute inset-0 flex items-start md:items-center justify-start px-6 md:px-16 pt-16 md:pt-0 pointer-events-none will-change-transform"
      >
        <TiltCard 
          maxTilt={9} 
          scale={1.02} 
          perspective={1000}
          glare={true}
          className="glass-card flex flex-col gap-4 sm:gap-4.5 p-7 sm:p-8 md:p-9 rounded-3xl pointer-events-auto w-full max-w-xl md:max-w-[620px] lg:max-w-[640px]"
        >
          <div className="tilt-depth flex items-center justify-between gap-3">
            <div className="glass-pill inline-flex items-center gap-2 px-3.5 py-1 rounded-full text-amber-300 text-[11px] font-mono font-bold tracking-wider w-fit">
              <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse" />
              02 · HARMONIC RESONANCE
            </div>
            <span className="text-[11px] sm:text-xs font-medium text-amber-200/90 flex items-center gap-1.5">
              <Radio className="w-3.5 h-3.5 text-amber-300" />
              <span>Solfeggio 432 Hz</span>
            </span>
          </div>

          <h3 className="tilt-depth text-2xl sm:text-3xl font-extrabold text-white tracking-tight drop-shadow-sm">
            Dial In Your Emotional Frequency
          </h3>

          <p className="tilt-depth text-xs sm:text-[13px] text-slate-200/90 leading-relaxed font-normal">
            Bypass digital fatigue with tactile intuition. Tune your inner baseline like a warm acoustic instrument, learning to feel your emotional cadence without self-judgment.
          </p>

          {/* Inspiring Harmonic Quote */}
          <div className="tilt-depth glass-card-sm p-4 sm:p-4.5 rounded-2xl border border-white/20 relative overflow-hidden bg-gradient-to-br from-amber-500/10 via-rose-500/5 to-transparent">
            <div className="absolute -top-10 -right-10 w-24 h-24 bg-amber-400/20 rounded-full blur-xl pointer-events-none" />
            <div className="flex items-start gap-3 relative z-10">
              <span className="text-2xl text-amber-300 font-serif leading-none select-none">“</span>
              <div className="flex flex-col gap-1">
                <p className="text-xs sm:text-[13px] text-amber-50 font-medium italic leading-relaxed">
                  The quieter you become, the more you are able to hear the subtle pulse of your own life.
                </p>
                <span className="text-[10px] text-amber-300/80 font-mono tracking-wider">
                  — Ram Dass
                </span>
              </div>
            </div>
          </div>

          {/* Luminous Visualizer: Solfeggio Soundwave Harmonic Bars */}
          <div className="tilt-depth glass-card-sm p-3.5 sm:p-4 rounded-2xl flex items-center justify-between gap-4 border border-white/15">
            <div className="flex items-center gap-3">
              <div className="flex items-end gap-1 h-7">
                <span className="w-1 bg-amber-400/90 rounded-full animate-pulse h-4" />
                <span className="w-1 bg-amber-300 rounded-full animate-bounce h-7" style={{ animationDelay: '0.15s' }} />
                <span className="w-1 bg-teal-300 rounded-full animate-bounce h-5" style={{ animationDelay: '0.3s' }} />
                <span className="w-1 bg-sky-400 rounded-full animate-bounce h-6" style={{ animationDelay: '0.45s' }} />
                <span className="w-1 bg-amber-400/80 rounded-full animate-pulse h-3" />
              </div>
              <div>
                <span className="text-xs font-bold text-white block">432 Hz Solfeggio Tuning</span>
                <span className="text-[10px] text-amber-200/90 font-mono">Resonant Natural Harmony</span>
              </div>
            </div>
            <span className="glass-pill text-[10px] text-emerald-300 font-mono font-bold px-2.5 py-1 rounded-lg">
              ● Coherent Tone
            </span>
          </div>

          {/* Interactive Actions for Feature 02 */}
          <div className="tilt-depth flex flex-wrap items-center gap-3 pt-3 mt-1 border-t border-white/15">
            <button 
              onClick={() => scrollToProgress(0.72)}
              className="glass-btn-primary px-5 py-2.5 rounded-xl text-white text-xs font-bold shadow-md hover:-translate-y-0.5 active:translate-y-0 transition-all flex items-center gap-2 cursor-pointer"
            >
              <span>Experience Harmonics</span>
              <span>→</span>
            </button>
            <button 
              onClick={() => setShowHeatmapModal(true)}
              className="glass-btn-secondary px-4 py-2.5 rounded-xl text-white text-xs font-semibold hover:-translate-y-0.5 active:translate-y-0 transition-all shadow-sm cursor-pointer flex items-center gap-2"
            >
              <BarChart2 className="w-3.5 h-3.5 text-amber-200" />
              <span>Preview 30-Day Flow</span>
            </button>
          </div>
        </TiltCard>
      </div>

      {/* ============================================================== */}
      {/* 4. FEATURE 03: BINAURAL TONE STABILIZATION */}
      {/* ============================================================== */}
      <div 
        ref={feat3Ref}
        className="absolute inset-0 flex items-end md:items-center justify-end px-6 md:px-16 pb-12 md:pb-0 pointer-events-none will-change-transform"
      >
        <TiltCard 
          maxTilt={9} 
          scale={1.02} 
          perspective={1000}
          glare={true}
          className="glass-card flex flex-col gap-4 sm:gap-4.5 p-7 sm:p-8 md:p-9 rounded-3xl pointer-events-auto w-full max-w-xl md:max-w-[620px] lg:max-w-[640px]"
        >
          <div className="tilt-depth flex items-center justify-between gap-3">
            <div className="glass-pill inline-flex items-center gap-2 px-3.5 py-1 rounded-full text-sky-300 text-[11px] font-mono font-bold tracking-wider w-fit">
              <span className="w-1.5 h-1.5 rounded-full bg-sky-400 animate-ping" />
              03 · TWILIGHT SANCTUARY
            </div>
            <span className="text-[11px] sm:text-xs font-medium text-sky-200/90 flex items-center gap-1.5">
              <Moon className="w-3.5 h-3.5 text-sky-300" />
              <span>Restorative Waves</span>
            </span>
          </div>

          <h3 className="tilt-depth text-2xl sm:text-3xl font-extrabold text-white tracking-tight drop-shadow-sm">
            Binaural Harmonic Diffusion
          </h3>

          <p className="tilt-depth text-xs sm:text-[13px] text-slate-200/90 leading-relaxed font-normal">
            As twilight softens the room, DayTone releases soothing acoustic waves and warm amber diffusion designed to gently down-regulate your nervous system before rest.
          </p>

          {/* Inspiring Twilight Rest Quote */}
          <div className="tilt-depth glass-card-sm p-4 sm:p-4.5 rounded-2xl border border-white/20 relative overflow-hidden bg-gradient-to-br from-indigo-500/10 via-sky-500/5 to-transparent">
            <div className="absolute -top-10 -right-10 w-24 h-24 bg-sky-400/20 rounded-full blur-xl pointer-events-none" />
            <div className="flex items-start gap-3 relative z-10">
              <span className="text-2xl text-sky-300 font-serif leading-none select-none">“</span>
              <div className="flex flex-col gap-1">
                <p className="text-xs sm:text-[13px] text-sky-50 font-medium italic leading-relaxed">
                  Rest is not a reward for surviving the day; it is the sacred soil from which your tomorrow blooms.
                </p>
                <span className="text-[10px] text-sky-300/80 font-mono tracking-wider">
                  — Circadian Wisdom
                </span>
              </div>
            </div>
          </div>

          {/* Serene Twilight Micro-Visual & Badges */}
          <div className="tilt-depth flex flex-wrap items-center gap-2 sm:gap-2.5 pt-0.5">
            <span className="glass-pill flex items-center gap-1.5 px-3 py-1 rounded-xl text-[11px] text-slate-200 font-medium">
              <Moon className="w-3 h-3 text-indigo-300" />
              <span>Twilight Wind-Down</span>
            </span>
            <span className="glass-pill flex items-center gap-1.5 px-3 py-1 rounded-xl text-[11px] text-slate-200 font-medium">
              <Activity className="w-3 h-3 text-sky-300" />
              <span>Vagal Stillness</span>
            </span>
            <span className="glass-pill flex items-center gap-1.5 px-3 py-1 rounded-xl text-[11px] text-slate-200 font-medium">
              <ShieldCheck className="w-3 h-3 text-teal-300" />
              <span>Restorative Sleep</span>
            </span>
          </div>

          {/* Interactive Actions for Feature 03 */}
          <div className="tilt-depth flex flex-wrap items-center gap-3 pt-3 mt-1 border-t border-white/15">
            <button 
              onClick={playHarmonicTone}
              className={`px-5 py-2.5 rounded-xl text-xs font-bold transition-all shadow-md flex items-center gap-2 cursor-pointer ${
                isPlayingTone 
                  ? 'bg-emerald-500 text-white ring-2 ring-emerald-300 animate-pulse' 
                  : 'glass-btn-primary text-white hover:-translate-y-0.5'
              }`}
            >
              <Volume2 className="w-3.5 h-3.5" />
              <span>{isPlayingTone ? 'Harmonic Wave Active...' : 'Play 432 Hz Solfeggio'}</span>
            </button>
            <button 
              onClick={() => {
                setAuthTab('login');
                scrollToProgress(0.95);
              }}
              className="glass-btn-secondary px-4 py-2.5 rounded-xl text-white text-xs font-semibold hover:-translate-y-0.5 active:translate-y-0 transition-all shadow-sm cursor-pointer"
            >
              <span>Enter Sanctuary</span>
              <span>→</span>
            </button>
          </div>
        </TiltCard>
      </div>

      {/* ============================================================== */}
      {/* 5. FINAL SECTION: LOGIN / REGISTER SANCTUARY GATEWAY */}
      {/* (Visible directly after scrolling through the entire animation) */}
      {/* ============================================================== */}
      <div 
        ref={feat4Ref}
        className="absolute inset-0 flex flex-col justify-between items-center px-4 sm:px-6 pt-16 sm:pt-20 pb-6 pointer-events-none will-change-transform"
      >
        <div className="h-2" />

        {/* Central Luminous Authentication Card with 3D Tilt */}
        <div className="w-full max-w-md mx-auto pointer-events-auto my-auto">
          <TiltCard
            maxTilt={7}
            scale={1.01}
            perspective={1000}
            glare={true}
            className="glass-card p-7 sm:p-8 rounded-3xl flex flex-col gap-4.5 shadow-2xl relative border border-white/30 backdrop-blur-3xl"
          >
            {/* Header branding */}
            <div className="tilt-depth flex flex-col items-center text-center gap-1.5">
              <div className="glass-pill inline-flex items-center gap-2 px-3 py-0.5 rounded-full text-emerald-300 text-[10px] sm:text-[11px] font-mono font-bold">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                <span>DAYTONE COGNITIVE SANCTUARY</span>
              </div>
              <h2 className="text-xl sm:text-2xl font-extrabold text-white tracking-tight drop-shadow-sm mt-1">
                Awaken to Inner Equilibrium
              </h2>
              <p className="text-xs text-slate-200 max-w-xs leading-relaxed font-normal">
                {authTab === 'login' 
                  ? 'Enter your private sanctuary to calibrate your daily tone with quiet clarity.' 
                  : 'Create your private on-device space with zero streak pressure and zero noise.'}
              </p>
            </div>

            {/* Tab Switcher: Sign In vs Create Account */}
            <div className="tilt-depth flex rounded-2xl p-1 bg-white/10 border border-white/20 text-xs">
              <button
                type="button"
                onClick={() => {
                  setAuthTab('login');
                  window.history.replaceState(null, '', '/login');
                  setAuthError(null);
                  setAuthSuccess(null);
                }}
                className={`flex-1 py-2 rounded-xl font-bold transition-all cursor-pointer ${
                  authTab === 'login'
                    ? 'glass-btn-primary text-white shadow-md'
                    : 'text-slate-300 hover:text-white'
                }`}
              >
                Sign In
              </button>
              <button
                type="button"
                onClick={() => {
                  setAuthTab('register');
                  window.history.replaceState(null, '', '/register');
                  setAuthError(null);
                  setAuthSuccess(null);
                }}
                className={`flex-1 py-2 rounded-xl font-bold transition-all cursor-pointer ${
                  authTab === 'register'
                    ? 'glass-btn-primary text-white shadow-md'
                    : 'text-slate-300 hover:text-white'
                }`}
              >
                Create Account
              </button>
            </div>

            {/* Error or Success feedback alerts */}
            {authError && (
              <div className="tilt-depth px-3.5 py-2.5 rounded-xl bg-rose-500/20 border border-rose-400/40 text-rose-200 text-xs font-medium text-center flex flex-col items-center gap-1.5">
                <span>{authError}</span>
                {authError.toLowerCase().includes('already exists') && (
                  <button
                    type="button"
                    onClick={() => {
                      setAuthTab('login');
                      window.history.replaceState(null, '', '/login');
                      setAuthError(null);
                    }}
                    className="text-sky-300 font-bold hover:underline cursor-pointer text-[11px]"
                  >
                    Switch to Sign In →
                  </button>
                )}
              </div>
            )}
            {authSuccess && (
              <div className="tilt-depth px-3 py-2 rounded-xl bg-emerald-500/20 border border-emerald-400/40 text-emerald-200 text-xs font-medium text-center animate-pulse flex items-center justify-center gap-1.5">
                <Check className="w-3.5 h-3.5 text-emerald-300 shrink-0" />
                <span>{authSuccess}</span>
              </div>
            )}

            {/* Form */}
            <form onSubmit={handleAuthSubmit} className="tilt-depth flex flex-col gap-3">
              {authTab === 'register' && (
                <div className="flex flex-col gap-1">
                  <label className="text-[11px] font-bold uppercase tracking-wider text-slate-300">
                    Full Name
                  </label>
                  <input
                    type="text"
                    required
                    value={authName}
                    onChange={(e) => setAuthName(e.target.value)}
                    placeholder="e.g. Maya Chen"
                    className="glass-input px-3.5 py-2.5 rounded-xl text-xs w-full placeholder-slate-400"
                  />
                </div>
              )}

              <div className="flex flex-col gap-1">
                <label className="text-[11px] font-bold uppercase tracking-wider text-slate-300">
                  Email Address
                </label>
                <input
                  type="email"
                  required
                  value={authEmail}
                  onChange={(e) => setAuthEmail(e.target.value)}
                  placeholder="you@domain.com"
                  className="glass-input px-3.5 py-2.5 rounded-xl text-xs w-full placeholder-slate-400"
                />
              </div>

              <div className="flex flex-col gap-1">
                <label className="text-[11px] font-bold uppercase tracking-wider text-slate-300">
                  Password
                </label>
                <div className="relative flex items-center">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    required
                    minLength={6}
                    value={authPassword}
                    onChange={(e) => setAuthPassword(e.target.value)}
                    placeholder="••••••••"
                    className="glass-input pl-3.5 pr-10 py-2.5 rounded-xl text-xs w-full placeholder-slate-400"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword((prev) => !prev)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-sky-300 transition-colors cursor-pointer p-1 rounded-lg focus:outline-none"
                    aria-label={showPassword ? 'Hide password' : 'Show password'}
                    title={showPassword ? 'Hide password' : 'Show password'}
                  >
                    {showPassword ? (
                      <EyeOff className="w-4 h-4 text-sky-300" />
                    ) : (
                      <Eye className="w-4 h-4 text-slate-400 hover:text-sky-300" />
                    )}
                  </button>
                </div>
              </div>

              {authTab === 'login' && (
                <div className="flex items-center justify-between text-xs text-slate-300 pt-0.5">
                  <label className="flex items-center gap-1.5 cursor-pointer select-none">
                    <input
                      type="checkbox"
                      checked={rememberMe}
                      onChange={(e) => setRememberMe(e.target.checked)}
                      className="rounded accent-sky-400 cursor-pointer"
                    />
                    <span className="text-[11px]">Remember session</span>
                  </label>
                  <a href="/login" className="text-sky-300 hover:text-sky-200 text-[11px] hover:underline">
                    Forgot?
                  </a>
                </div>
              )}

              <button
                type="submit"
                disabled={authLoading}
                className="glass-btn-primary w-full py-3 rounded-xl text-white text-xs font-bold shadow-lg hover:-translate-y-0.5 active:translate-y-0 transition-all cursor-pointer mt-1 flex items-center justify-center gap-2"
              >
                {authLoading ? (
                  <span className="animate-pulse">Authenticating...</span>
                ) : authTab === 'login' ? (
                  <>
                    <span>Sign In to Sanctuary</span>
                    <span>→</span>
                  </>
                ) : (
                  <>
                    <span>Create DayTone Account</span>
                    <span>→</span>
                  </>
                )}
              </button>
            </form>

            {/* Toggle prompt at bottom of card */}
            <div className="tilt-depth text-center text-xs text-slate-300 pt-2 border-t border-white/10">
              {authTab === 'login' ? (
                <span>
                  New to DayTone?{' '}
                  <button
                    type="button"
                    onClick={() => {
                      setAuthTab('register');
                      window.history.replaceState(null, '', '/register');
                      setAuthError(null);
                    }}
                    className="text-sky-300 font-bold hover:underline cursor-pointer"
                  >
                    Create an account
                  </button>
                </span>
              ) : (
                <span>
                  Already registered?{' '}
                  <button
                    type="button"
                    onClick={() => {
                      setAuthTab('login');
                      window.history.replaceState(null, '', '/login');
                      setAuthError(null);
                    }}
                    className="text-sky-300 font-bold hover:underline cursor-pointer"
                  >
                    Sign in here
                  </button>
                </span>
              )}
            </div>
          </TiltCard>
        </div>

        {/* Bottom Mindful Sanctuary Wisdom Card with 3D Tilt */}
        <div className="w-full max-w-3xl pointer-events-auto">
          <TiltCard
            maxTilt={6}
            scale={1.01}
            perspective={1000}
            glare={true}
            className="glass-card p-3.5 sm:p-4 rounded-2xl border border-white/25"
          >
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3.5 sm:gap-4 w-full">
              <div className="tilt-depth flex items-center gap-3 sm:gap-4 text-xs text-slate-200 flex-1 min-w-0">
                <div className="w-8 h-8 rounded-xl bg-emerald-500/15 border border-emerald-400/30 flex items-center justify-center shrink-0">
                  <Compass className="w-4 h-4 text-emerald-300" />
                </div>
                <div className="flex flex-col gap-0.5 min-w-0">
                  <p className="text-[11px] sm:text-xs text-emerald-100 font-medium italic leading-snug">
                    “Your rhythm is a compass, not a race. Return to yourself without pressure.”
                  </p>
                  <div className="flex items-center gap-3 text-[10px] text-slate-300 font-mono pt-0.5 flex-wrap">
                    <span className="flex items-center gap-1 whitespace-nowrap">
                      <span className="text-emerald-300 font-bold">●</span> Zero Streak Guilt
                    </span>
                    <span className="flex items-center gap-1 whitespace-nowrap">
                      <span className="text-sky-300 font-bold">●</span> Private On-Device Enclave
                    </span>
                    <span className="flex items-center gap-1 whitespace-nowrap hidden sm:inline-flex">
                      <span className="text-teal-300 font-bold">●</span> Circadian Harmony
                    </span>
                  </div>
                </div>
              </div>

              <button 
                onClick={() => scrollToProgress(0)}
                className="tilt-depth glass-btn-secondary px-3.5 py-2 rounded-xl text-white text-xs font-semibold hover:-translate-y-0.5 active:translate-y-0 transition-all shadow-sm cursor-pointer flex items-center gap-1.5 shrink-0 whitespace-nowrap self-end sm:self-auto"
              >
                <span>Back to Top</span>
                <span>↑</span>
              </button>
            </div>
          </TiltCard>
        </div>
      </div>


      {/* ============================================================== */}
      {/* 30-DAY MOOD HEATMAP PREVIEW MODAL */}
      {/* ============================================================== */}
      {showHeatmapModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/65 backdrop-blur-md pointer-events-auto animate-fadeIn">
          <div className="glass-card w-full max-w-xl p-6 sm:p-7 rounded-3xl flex flex-col gap-4 shadow-2xl relative border border-white/30">
            <button 
              onClick={() => setShowHeatmapModal(false)}
              className="absolute top-5 right-5 text-slate-300 hover:text-white w-8 h-8 rounded-full glass-card-sm flex items-center justify-center transition-all cursor-pointer"
            >
              <X className="w-4 h-4" />
            </button>

            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-sky-400 to-indigo-500 p-[1.5px]">
                <div className="w-full h-full bg-slate-900 rounded-[10px] flex items-center justify-center text-xs font-bold text-white">
                  <BarChart2 className="w-4 h-4 text-sky-300" />
                </div>
              </div>
              <div>
                <h3 className="text-lg font-bold text-white tracking-tight">30-Day Circadian Mood Heatmap</h3>
                <span className="text-[11px] text-sky-300 font-mono">Continuous Restorative Flow Trajectory</span>
              </div>
            </div>

            {/* 30-Day Heatmap Grid */}
            <div className="glass-card-sm p-4 rounded-2xl flex flex-col gap-3">
              <div className="flex justify-between items-center text-xs text-slate-200">
                <span className="font-semibold">Last 30 Calendar Days</span>
                <span className="text-emerald-300 font-mono text-[11px]">94% Restorative Coherence</span>
              </div>

              <div className="grid grid-cols-6 gap-2 pt-1">
                {Array.from({ length: 30 }).map((_, idx) => {
                  const tones = [
                    'bg-emerald-400/90 text-emerald-950',
                    'bg-teal-400/85 text-teal-950',
                    'bg-sky-400/90 text-sky-950',
                    'bg-indigo-400/80 text-white',
                    'bg-emerald-300/90 text-emerald-950'
                  ];
                  const color = tones[idx % tones.length];
                  const day = idx + 1;
                  return (
                    <div 
                      key={idx}
                      className={`${color} h-9 rounded-xl flex flex-col items-center justify-center text-[10px] font-bold shadow-sm transition-transform hover:scale-110 cursor-pointer`}
                      title={`Day ${day}: Optimal Circadian Harmony (Mood: 8.5/10)`}
                    >
                      <span>{day}</span>
                    </div>
                  );
                })}
              </div>

              <div className="flex items-center justify-between text-[10px] text-slate-300 pt-1 border-t border-white/10">
                <span className="flex items-center gap-1.5">
                  <span className="w-2.5 h-2.5 rounded bg-emerald-400 inline-block" /> High Flow
                </span>
                <span className="flex items-center gap-1.5">
                  <span className="w-2.5 h-2.5 rounded bg-sky-400 inline-block" /> Restorative
                </span>
                <span className="flex items-center gap-1.5">
                  <span className="w-2.5 h-2.5 rounded bg-indigo-400 inline-block" /> Balanced
                </span>
              </div>
            </div>

            <div className="flex items-center justify-between gap-3 pt-1">
              <button 
                onClick={() => {
                  setShowHeatmapModal(false);
                  setAuthTab('register');
                  scrollToProgress(0.95);
                }}
                className="glass-btn-primary px-4 py-2 rounded-xl text-white text-xs font-bold shadow-md hover:-translate-y-0.5 transition-all cursor-pointer"
              >
                Log Today's Square →
              </button>
              <a 
                href="/heatmap"
                className="glass-btn-secondary px-4 py-2 rounded-xl text-white text-xs font-semibold hover:-translate-y-0.5 transition-all shadow-sm flex items-center gap-1"
              >
                <span>Open Full Heatmap</span>
                <span className="text-[10px] opacity-70">↗</span>
              </a>
            </div>
          </div>
        </div>
      )}

    </div>
  );
};
