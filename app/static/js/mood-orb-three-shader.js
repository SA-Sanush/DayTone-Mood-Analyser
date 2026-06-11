/*
  Slushy "liquid blob" mood orb renderer.
  - Uses a custom vertex shader with a 3D simplex noise to warp a high-density sphere smoothly over time.
  - Smooth color interpolation system for moods (1..5).
  - Single-color representation per mood (representing exact mood color with organic lighting).
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

  // GLSL 3D Noise (simplex) for smooth organic deformation.
  const noiseGLSL = `
    vec3 mod289(vec3 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
    vec4 mod289(vec4 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
    vec4 permute(vec4 x) { return mod289(((x*34.0)+1.0)*x); }
    vec4 taylorInvSqrt(vec4 r) { return 1.79284291400159 - 0.85373472095314 * r; }

    float snoise(vec3 v) {
      const vec2  C = vec2(1.0/6.0, 1.0/3.0);
      const vec4  D = vec4(0.0, 0.5, 1.0, 2.0);

      vec3 i  = floor(v + dot(v, C.yyy) );
      vec3 x0 = v - i + dot(i, C.xxx);

      vec3 g = step(x0.yzx, x0.xyz);
      vec3 l = 1.0 - g;
      vec3 i1 = min( g.xyz, l.zxy );
      vec3 i2 = max( g.xyz, l.zxy );

      vec3 x1 = x0 - i1 + C.xxx;
      vec3 x2 = x0 - i2 + C.yyy;
      vec3 x3 = x0 - D.yyy;

      i = mod289(i);
      vec4 p = permute( permute( permute(
                 i.z + vec4(0.0, i1.z, i2.z, 1.0 ))
               + i.y + vec4(0.0, i1.y, i2.y, 1.0 ))
               + i.x + vec4(0.0, i1.x, i2.x, 1.0 ));

      float n_ = 0.142857142857;
      vec3 ns = n_ * D.wyz - D.xzx;

      vec4 j = p - 49.0 * floor(p * ns.z * ns.z);

      vec4 x_ = floor(j * ns.z);
      vec4 y_ = floor(j - 7.0 * x_ );

      vec4 x = x_ *ns.x + ns.yyyy;
      vec4 y = y_ *ns.x + ns.yyyy;
      vec4 h = 1.0 - abs(x) - abs(y);

      vec4 b0 = vec4( x.xy, y.xy );
      vec4 b1 = vec4( x.zw, y.zw );

      vec4 s0 = floor(b0)*2.0 + 1.0;
      vec4 s1 = floor(b1)*2.0 + 1.0;
      vec4 sh = -step(h, vec4(0.0));

      vec4 a0 = b0.xzyw + s0.xzyw*sh.xxyy ;
      vec4 a1 = b1.xzyw + s1.xzyw*sh.zzww ;

      vec3 p0 = vec3(a0.xy,h.x);
      vec3 p1 = vec3(a0.zw,h.y);
      vec3 p2 = vec3(a1.xy,h.z);
      vec3 p3 = vec3(a1.zw,h.w);

      vec4 norm = taylorInvSqrt(vec4(dot(p0,p0), dot(p1,p1), dot(p2,p2), dot(p3,p3)));
      p0 *= norm.x; p1 *= norm.y; p2 *= norm.z; p3 *= norm.w;

      vec4 m = max(0.6 - vec4(dot(x0,x0), dot(x1,x1), dot(x2,x2), dot(x3,x3)), 0.0);
      m = m*m;
      return 42.0 * dot( m*m, vec4( dot(p0,x0), dot(p1,x1), dot(p2,x2), dot(p3,x3) ) );
    }
  `;

  class SlushyMoodOrb {
    constructor(canvasEl) {
      this.canvas = canvasEl;

      this.moodColors = {
        1: { primary: "#ef4444", secondary: "#ea580c" }, // Sick (Red)
        2: { primary: "#f97316", secondary: "#d97706" }, // Sad (Orange)
        3: { primary: "#eab308", secondary: "#ca8a04" }, // Anxious (Yellow)
        4: { primary: "#10b981", secondary: "#34d399" }, // Calm (Light Green)
        5: { primary: "#22c55e", secondary: "#16a34a" }, // Happy (Green)
      };

      const initialMood = Number(dashboard.orb?.mood || 3);
      const palette = this.moodColors[initialMood] || this.moodColors[3];
      this.targetColor = new THREE.Color(palette.primary);
      this.currentColor = this.targetColor.clone();
      this.targetColorIndex = initialMood;
      this.activeMoodId = initialMood;

      this.mouse = new THREE.Vector2(0, 0);
      this.targetMouse = new THREE.Vector2(0, 0);
      this.clickSurge = 0;

      this.init();
    }

    init() {
      this.scene = new THREE.Scene();
      this.camera = new THREE.PerspectiveCamera(
        45,
        this.canvas.clientWidth / Math.max(this.canvas.clientHeight, 1),
        0.1,
        100,
      );
      this.camera.position.z = 5.5;

      this.renderer = new THREE.WebGLRenderer({
        antialias: true,
        alpha: true,
        canvas: this.canvas,
      });
      this.renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));

      // Safe, high-density SphereGeometry for smooth, liquid-like surface
      const geometry = new THREE.SphereGeometry(1.6, 64, 64);

      this.material = new THREE.ShaderMaterial({
        uniforms: {
          uTime: { value: 0 },
          uColor: { value: this.currentColor },
          uNoiseFrequency: { value: 0.45 },
          uNoiseAmplitude: { value: 0.25 },
        },
        vertexShader:
          noiseGLSL +
          `
          uniform float uTime;
          uniform float uNoiseFrequency;
          uniform float uNoiseAmplitude;
          varying vec3 vNormal;
          varying vec3 vPosition;

          void main() {
            vNormal = normalize(normalMatrix * normal);
            
            // Generate organic, liquid-like displacement mapping
            float noise = snoise(position * uNoiseFrequency + vec3(uTime * 0.6));
            vec3 newPosition = position + normal * noise * uNoiseAmplitude;
            
            vPosition = newPosition;
            gl_Position = projectionMatrix * modelViewMatrix * vec4(newPosition, 1.0);
          }
        `,
        fragmentShader: `
          precision highp float;
          uniform vec3 uColor;
          varying vec3 vNormal;
          varying vec3 vPosition;

          void main() {
            // Fake studio lighting configuration for 3D depth
            vec3 lightDir = normalize(vec3(1.0, 1.0, 1.0));
            vec3 viewDir = normalize(vec3(0.0, 0.0, 1.0));
            
            // Diffuse shading component
            vec3 normal = normalize(vNormal);
            float diffuse = max(dot(normal, lightDir), 0.0);
            
            // Smooth rim/fresnel lighting to give it that soft velvet/slush look
            float rim = pow(1.0 - max(dot(normal, viewDir), 0.0), 3.0);
            
            vec3 finalColor = uColor * (diffuse * 0.7 + 0.4) + (vec3(1.0) * rim * 0.3);
            gl_FragColor = vec4(finalColor, 1.0);
          }
        `,
      });

      this.orb = new THREE.Mesh(geometry, this.material);
      this.scene.add(this.orb);

      this.createParticles();

      // Set initial mood and trigger cockpit styling
      this.setMood(this.targetColorIndex);

      this.hookMoodButtons();

      this.clock = new THREE.Clock();
      this.animate();
    }

    createParticles() {
      const particleCount = 60;
      const g = new THREE.BufferGeometry();
      const positions = new Float32Array(particleCount * 3);

      for (let i = 0; i < particleCount * 3; i += 3) {
        positions[i] = (Math.random() - 0.5) * 8;
        positions[i + 1] = (Math.random() - 0.5) * 6;
        positions[i + 2] = (Math.random() - 0.5) * 4;
      }

      g.setAttribute("position", new THREE.BufferAttribute(positions, 3));

      const m = new THREE.PointsMaterial({
        color: 0xffffff,
        size: 0.03,
        transparent: true,
        opacity: 0.25,
      });

      this.particles = new THREE.Points(g, m);
      this.scene.add(this.particles);
    }

    hookMoodButtons() {
      const pills = Array.from(document.querySelectorAll(".mood-pill"));
      if (!pills.length) return;

      pills.forEach((pill) => {
        // Click sets mood permanently
        pill.addEventListener("click", () => {
          const moodId = Number(pill.dataset.mood);
          this.setMood(moodId);
          this.activeMoodId = moodId;
        });

        // Hover enters preview color
        pill.addEventListener("mouseenter", () => {
          const moodId = Number(pill.dataset.mood);
          this.previewMood(moodId);
        });

        // Hover leaves restores active log color
        pill.addEventListener("mouseleave", () => {
          this.previewMood(this.activeMoodId);
        });
      });

      // Pointer tracking listener for steering
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
          this.targetMouse.set(x * 0.75, y * 0.75);
        } else {
          this.targetMouse.set(0, 0);
        }
      });

      // Click wobble listener
      this.canvas.addEventListener("click", () => {
        this.clickSurge = 0.65;
      });
    }

    previewMood(moodId) {
      if (!this.moodColors[moodId]) return;
      const palette = this.moodColors[moodId];
      this.targetColor.copy(new THREE.Color(palette.primary));
    }

    setMood(moodId) {
      if (!this.moodColors[moodId]) return;
      const palette = this.moodColors[moodId];
      this.targetColor.copy(new THREE.Color(palette.primary));
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

      if (label && labels[moodId]) label.textContent = labels[moodId];
      if (score) score.textContent = `${moodId}/5`;

      if (prefersReducedMotion && this.renderer && this.scene && this.camera) {
        this.currentColor.copy(this.targetColor);
        this.material.uniforms.uColor.value = this.currentColor;
        this.renderer.render(this.scene, this.camera);
      }
    }

    animate() {
      if (prefersReducedMotion) {
        this.currentColor.copy(this.targetColor);
        this.material.uniforms.uColor.value = this.currentColor;
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

      const w = this.canvas.clientWidth;
      const h = this.canvas.clientHeight;
      if (w > 0 && h > 0 && (this.canvas.width !== w || this.canvas.height !== h)) {
        this.renderer.setSize(w, h, false);
        this.camera.aspect = w / h;
        this.camera.updateProjectionMatrix();
      }

      const elapsedTime = this.clock.getElapsedTime();
      this.material.uniforms.uTime.value = elapsedTime;

      // Click wobble surge calculation
      this.clickSurge *= 0.93;
      const amplitudeSurge = this.clickSurge * Math.sin(elapsedTime * 22.0);
      this.material.uniforms.uNoiseAmplitude.value = 0.25 + amplitudeSurge;
      this.material.uniforms.uNoiseFrequency.value = 0.45 + this.clickSurge * 0.15;

      // Mouse steering interpolation
      this.mouse.lerp(this.targetMouse, 0.08);

      this.currentColor.lerp(this.targetColor, 0.05);
      this.material.uniforms.uColor.value = this.currentColor;

      if (this.orb) {
        this.orb.rotation.y = elapsedTime * 0.05 + this.mouse.x * 0.55;
        this.orb.rotation.x = elapsedTime * 0.02 - this.mouse.y * 0.55;
      }

      if (this.particles) {
        this.particles.rotation.y = elapsedTime * -0.01 - this.mouse.x * 0.12;
        this.particles.rotation.x = this.mouse.y * 0.12;
      }

      this.renderer.render(this.scene, this.camera);
    }
  }

  try {
    new SlushyMoodOrb(canvas);
  } catch (err) {
    console.error("Three.js Orb initialization failed:", err);
    const orbContainer = document.querySelector(".orb-stage-wrap");
    if (orbContainer) {
      orbContainer.classList.add("orb-error-state");
      const fallbackDiv = document.createElement("div");
      fallbackDiv.className = "orb-fallback-text";
      fallbackDiv.textContent = "Interactive 3D orb could not load.";
      orbContainer.appendChild(fallbackDiv);
    }
  }
})();
