/*
  DayTone Executive Cognitive 3D Orb Shader Engine
  - Full-sphere physical geometry with micro-surface harmonic fluid ripples.
  - Multi-tone studio lighting with Blinn-Phong specular gloss and velvet Fresnel rim aura.
  - Anti-clip viewport projection guaranteeing complete 360-degree spherical contour.
  - Interactive mouse kinetic steering and click ripple surge.
*/

(function () {
  if (window.__DAYTONE_MOOD_ORB_INITIALIZED__) return;
  window.__DAYTONE_MOOD_ORB_INITIALIZED__ = true;

  const canvas = document.getElementById("moodOrb");
  const dashboard = window.DAYTONE_DASHBOARD;
  if (!canvas || !dashboard || !window.THREE) return;

  const THREE = window.THREE;

  const prefersReducedMotion = window.matchMedia(
    "(prefers-reduced-motion: reduce)",
  ).matches;

  class ExecutiveMoodOrb {
    constructor(canvasEl) {
      this.canvas = canvasEl;

      this.moodColors = {
        1: { primary: "#ff2222", secondary: "#ff5555" }, // Sick: Bright Red
        2: { primary: "#ff7700", secondary: "#ffa333" }, // Sad: Vibrant Orange
        3: { primary: "#eab308", secondary: "#fde047" }, // Anxious: Golden Yellow
        4: { primary: "#22c55e", secondary: "#86efac" }, // Calm: Fresh Light Green
        5: { primary: "#059669", secondary: "#34d399" }, // Happy: Radiant Emerald Green
      };

      const initialMood = Number(dashboard.orb?.mood || 4);
      const palette = this.moodColors[initialMood] || this.moodColors[4];

      this.targetColor = new THREE.Color(palette.primary);
      this.currentColor = this.targetColor.clone();
      this.targetSecondaryColor = new THREE.Color(palette.secondary);
      this.currentSecondaryColor = this.targetSecondaryColor.clone();

      this.targetColorIndex = initialMood;
      this.activeMoodId = initialMood;

      this.mouse = new THREE.Vector2(0, 0);
      this.targetMouse = new THREE.Vector2(0, 0);
      this.clickSurge = 0;

      this.init();
    }

    init() {
      this.scene = new THREE.Scene();

      // Camera positioned with generous breathing room ensuring zero edge clipping
      this.camera = new THREE.PerspectiveCamera(45, 1.0, 0.1, 100);
      this.camera.position.set(0, 0, 5.0);

      this.renderer = new THREE.WebGLRenderer({
        antialias: true,
        alpha: true,
        canvas: this.canvas,
        powerPreference: "high-performance",
      });
      this.renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));

      // Pristine, ultra-dense SphereGeometry (Radius 1.38)
      const geometry = new THREE.SphereGeometry(1.38, 128, 128);

      this.material = new THREE.ShaderMaterial({
        uniforms: {
          uTime: { value: 0 },
          uColor: { value: this.currentColor },
          uSecondaryColor: { value: this.currentSecondaryColor },
          uNoiseAmplitude: { value: 0.038 },
          uClickSurge: { value: 0.0 },
        },
        vertexShader: `
          uniform float uTime;
          uniform float uNoiseAmplitude;
          uniform float uClickSurge;
          varying vec3 vNormal;
          varying vec3 vPosition;
          varying vec3 vViewPosition;

          void main() {
            vNormal = normalize(normalMatrix * normal);
            
            // Subtle, organic fluid surface breathing preserving true full spherical contour
            float wave = sin(position.x * 2.8 + uTime * 1.5) * 
                         cos(position.y * 2.6 + uTime * 1.3) * 
                         sin(position.z * 2.4 + uTime * 1.4) * uNoiseAmplitude;

            // Concentric interactive click wobble
            float ripple = sin(length(position.xy) * 7.5 - uTime * 8.0) * uClickSurge * 0.06;

            vec3 newPosition = position + normal * (wave + ripple);
            vPosition = newPosition;

            vec4 mvPosition = modelViewMatrix * vec4(newPosition, 1.0);
            vViewPosition = -mvPosition.xyz;

            gl_Position = projectionMatrix * mvPosition;
          }
        `,
        fragmentShader: `
          precision highp float;
          uniform vec3 uColor;
          uniform vec3 uSecondaryColor;
          varying vec3 vNormal;
          varying vec3 vPosition;
          varying vec3 vViewPosition;

          void main() {
            vec3 normal = normalize(vNormal);
            vec3 viewDir = normalize(vViewPosition);

            // Studio Key Light (Top-Right Frontal)
            vec3 keyLight = normalize(vec3(0.7, 0.9, 1.1));
            float NdotL = max(dot(normal, keyLight), 0.0);

            // Soft Wrap Fill Light (Bottom-Left Counter)
            vec3 fillLight = normalize(vec3(-0.7, -0.6, 0.4));
            float NdotFill = max(dot(normal, fillLight), 0.0) * 0.38;

            // Physical Blinn-Phong Specular Gloss Highlight (Polished Glass / Pearl sheen)
            vec3 halfVector = normalize(keyLight + viewDir);
            float specSharp = pow(max(dot(normal, halfVector), 0.0), 38.0) * 0.90;
            float specSoft = pow(max(dot(normal, halfVector), 0.0), 10.0) * 0.25;

            // Velvet Fresnel Rim Glow around the outer curvature
            float fresnel = pow(1.0 - max(dot(normal, viewDir), 0.0), 2.6);

            // Ambient spherical light
            float ambient = 0.46;

            // Two-tone inner-to-outer depth blend
            vec3 coreTone = mix(uColor, uSecondaryColor, fresnel * 0.45);
            vec3 diffuse = coreTone * (ambient + NdotL * 0.68 + NdotFill);

            // Luminous rim aura
            vec3 finalColor = diffuse + vec3(1.0) * (specSharp + specSoft) + uSecondaryColor * fresnel * 0.88;

            gl_FragColor = vec4(finalColor, 1.0);
          }
        `,
      });

      this.orb = new THREE.Mesh(geometry, this.material);
      this.scene.add(this.orb);

      this.createParticles();
      this.setMood(this.targetColorIndex);
      this.hookMoodButtons();

      this.clock = new THREE.Clock();
      this.animate();
    }

    createParticles() {
      const particleCount = 75;
      const g = new THREE.BufferGeometry();
      const positions = new Float32Array(particleCount * 3);

      for (let i = 0; i < particleCount * 3; i += 3) {
        positions[i] = (Math.random() - 0.5) * 8.5;
        positions[i + 1] = (Math.random() - 0.5) * 6.5;
        positions[i + 2] = (Math.random() - 0.5) * 4.5;
      }

      g.setAttribute("position", new THREE.BufferAttribute(positions, 3));

      const m = new THREE.PointsMaterial({
        color: 0xffffff,
        size: 0.032,
        transparent: true,
        opacity: 0.35,
      });

      this.particles = new THREE.Points(g, m);
      this.scene.add(this.particles);
    }

    hookMoodButtons() {
      const pills = Array.from(document.querySelectorAll(".mood-pill"));
      if (!pills.length) return;

      pills.forEach((pill) => {
        pill.addEventListener("click", () => {
          const moodId = Number(pill.dataset.mood);
          this.setMood(moodId);
          this.activeMoodId = moodId;
        });

        pill.addEventListener("mouseenter", () => {
          const moodId = Number(pill.dataset.mood);
          this.previewMood(moodId);
        });

        pill.addEventListener("mouseleave", () => {
          this.previewMood(this.activeMoodId);
        });
      });

      window.addEventListener("mousemove", (event) => {
        const rect = this.canvas.getBoundingClientRect();
        const x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
        const y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

        if (
          event.clientX >= rect.left - 200 &&
          event.clientX <= rect.right + 200 &&
          event.clientY >= rect.top - 200 &&
          event.clientY <= rect.bottom + 200
        ) {
          this.targetMouse.set(x * 0.7, y * 0.7);
        } else {
          this.targetMouse.set(0, 0);
        }
      });

      this.canvas.addEventListener("click", () => {
        this.clickSurge = 1.0;
      });
    }

    previewMood(moodId) {
      if (!this.moodColors[moodId]) return;
      const palette = this.moodColors[moodId];
      this.targetColor.copy(new THREE.Color(palette.primary));
      this.targetSecondaryColor.copy(new THREE.Color(palette.secondary));
    }

    setMood(moodId) {
      if (!this.moodColors[moodId]) return;
      const palette = this.moodColors[moodId];
      this.targetColor.copy(new THREE.Color(palette.primary));
      this.targetSecondaryColor.copy(new THREE.Color(palette.secondary));
      this.targetColorIndex = moodId;

      const label = document.getElementById("orbLabel");
      const score = document.getElementById("orbScore");
      const cockpit = document.querySelector(".orb-cockpit");
      const pills = Array.from(document.querySelectorAll(".mood-pill"));

      const labels = {
        1: "Sick",
        2: "Sad",
        3: "Anxious",
        4: "Calm",
        5: "Happy",
      };

      if (cockpit) {
        cockpit.style.setProperty("--orb-primary", palette.primary);
        cockpit.style.setProperty("--orb-secondary", palette.secondary);
      }

      pills.forEach((pill) => {
        pill.classList.toggle("active", Number(pill.dataset.mood) === moodId);
      });

      if (label && labels[moodId]) {
        label.textContent = labels[moodId];
      }
      if (score) {
        score.textContent = `${moodId}/5`;
        score.style.color = palette.primary;
      }

      const descriptors = {
        1: "Acute Fatigue • Immediate Rest",
        2: "Low Vitality • Gentle Pacing",
        3: "Elevated Tension • Grounding Flow",
        4: "Restorative Flow • Balanced Harmony",
        5: "Peak Resonance • Radiant Vitality",
      };
      const desc = document.getElementById("orbDesc");
      if (desc && descriptors[moodId]) {
        desc.textContent = `• ${descriptors[moodId]}`;
      }

      const dots = Array.from(document.querySelectorAll(".orb-pulse-dot"));
      dots.forEach((dot) => {
        dot.style.background = palette.primary;
        dot.style.boxShadow = `0 0 10px ${palette.primary}`;
      });

      if (prefersReducedMotion && this.renderer && this.scene && this.camera) {
        this.currentColor.copy(this.targetColor);
        this.currentSecondaryColor.copy(this.targetSecondaryColor);
        this.material.uniforms.uColor.value = this.currentColor;
        this.material.uniforms.uSecondaryColor.value = this.currentSecondaryColor;
        this.renderer.render(this.scene, this.camera);
      }
    }

    animate() {
      if (prefersReducedMotion) {
        this.currentColor.copy(this.targetColor);
        this.currentSecondaryColor.copy(this.targetSecondaryColor);
        this.material.uniforms.uColor.value = this.currentColor;
        this.material.uniforms.uSecondaryColor.value = this.currentSecondaryColor;
        this.material.uniforms.uTime.value = 0.0;
        if (this.orb) {
          this.orb.rotation.y = 0;
          this.orb.rotation.x = 0;
        }
        if (this.particles) {
          this.particles.rotation.y = 0;
        }
        this.renderer.render(this.scene, this.camera);
        return;
      }

      requestAnimationFrame(() => this.animate());

      const w = this.canvas.clientWidth || 260;
      const h = this.canvas.clientHeight || 260;
      if (w > 0 && h > 0 && (this.canvas.width !== w || this.canvas.height !== h)) {
        this.renderer.setSize(w, h, false);
        this.camera.aspect = w / h;
        this.camera.updateProjectionMatrix();
      }

      const elapsedTime = this.clock.getElapsedTime();
      this.material.uniforms.uTime.value = elapsedTime;

      // Click wobble decay
      this.clickSurge *= 0.92;
      this.material.uniforms.uClickSurge.value = this.clickSurge;

      // Smooth mouse steering
      this.mouse.lerp(this.targetMouse, 0.08);

      // Smooth color transitions
      this.currentColor.lerp(this.targetColor, 0.18);
      this.currentSecondaryColor.lerp(this.targetSecondaryColor, 0.18);
      this.material.uniforms.uColor.value = this.currentColor;
      this.material.uniforms.uSecondaryColor.value = this.currentSecondaryColor;

      if (this.orb) {
        this.orb.rotation.y = elapsedTime * 0.08 + this.mouse.x * 0.5;
        this.orb.rotation.x = elapsedTime * 0.03 - this.mouse.y * 0.5;
      }

      if (this.particles) {
        this.particles.rotation.y = elapsedTime * -0.015 - this.mouse.x * 0.1;
        this.particles.rotation.x = this.mouse.y * 0.1;
      }

      this.renderer.render(this.scene, this.camera);
    }
  }

  try {
    new ExecutiveMoodOrb(canvas);
  } catch (err) {
    console.error("Executive 3D Orb initialization failed:", err);
  }
})();
