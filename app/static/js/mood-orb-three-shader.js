/*
  Slushy "liquid blob" mood orb renderer.
  - Uses a 3D simplex-noise GLSL deformation to prevent sharp spikes.
  - Smoothly interpolates color when switching moods (1..5).

  Integration expectations (matches dashboard.html):
  - <canvas id="moodOrb"></canvas>
  - window.DAYTONE_DASHBOARD contains dashboard.orb.mood and/or primary/secondary.
  - mood pill buttons already exist; we hook into their click events.
*/

(function () {
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

      vec4 j = p - 49.0 * floor(p * ns.z);

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

      // Mood color configuration (as requested)
      this.moodColors = {
        1: new THREE.Color("#ff3b30"), // Raw
        2: new THREE.Color("#ff9500"), // Uneasy
        3: new THREE.Color("#ffcc00"), // Balanced
        4: new THREE.Color("#34c759"), // Lifted
        5: new THREE.Color("#00a86b"), // Radiant
      };

      this.targetColor = this.moodColors[1].clone();
      this.currentColor = this.moodColors[1].clone();
      this.targetColorIndex = 1;

      this.init();
    }

    init() {
      const container = this.canvas.parentElement || document.body;

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

      this.resize();
      window.addEventListener("resize", () => this.resize());

      // Slushy deformed orb
      const geometry = new THREE.IcosahedronGeometry(1.6, 64);

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

          void main() {
            vNormal = normalize(normalMatrix * normal);
            float n = snoise(vec3(position * uNoiseFrequency + uTime * 0.6));
            vec3 displaced = position + normal * n * uNoiseAmplitude;
            gl_Position = projectionMatrix * modelViewMatrix * vec4(displaced, 1.0);
          }
        `,
        fragmentShader: `
          uniform vec3 uColor;
          varying vec3 vNormal;

          void main() {
            vec3 lightDir = normalize(vec3(1.0, 1.0, 1.0));
            vec3 viewDir = normalize(vec3(0.0, 0.0, 1.0));

            float diffuse = max(dot(vNormal, lightDir), 0.0);
            float rim = pow(1.0 - max(dot(vNormal, viewDir), 0.0), 3.0);

            vec3 finalColor = uColor * (diffuse * 0.7 + 0.4) + (vec3(1.0) * rim * 0.3);
            gl_FragColor = vec4(finalColor, 1.0);
          }
        `,
      });

      this.orb = new THREE.Mesh(geometry, this.material);
      this.scene.add(this.orb);

      this.createParticles();

      // Init mood from server state
      const initialMood = Number(dashboard.orb?.mood || 3);
      this.setMood(initialMood);

      // Hook into pill clicks
      this.hookMoodButtons();

      this.clock = new THREE.Clock();
      this.animate();

      // Optional subtle background color
      if (container && container.style) {
        // no-op; dashboard CSS already styles
      }
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
        pill.addEventListener("click", () => {
          const moodId = Number(pill.dataset.mood);
          this.setMood(moodId);
        });
      });
    }

    resize() {
      const w = this.canvas.clientWidth;
      const h = this.canvas.clientHeight;
      this.renderer.setSize(w, h, false);
      this.camera.aspect = w / Math.max(h, 1);
      this.camera.updateProjectionMatrix();
    }

    setMood(moodId) {
      if (!this.moodColors[moodId]) return;
      this.targetColor.copy(this.moodColors[moodId]);
      this.targetColorIndex = moodId;

      // Keep existing UI labels/score in sync (dashboard already does, but this keeps it robust)
      const label = document.getElementById("orbLabel");
      const score = document.getElementById("orbScore");

      const labels = {
        1: "Raw",
        2: "Uneasy",
        3: "Balanced",
        4: "Lifted",
        5: "Radiant",
      };

      if (label && labels[moodId]) label.textContent = labels[moodId];
      if (score) score.textContent = `${moodId}/5`;
    }

    animate() {
      requestAnimationFrame(() => this.animate());

      const elapsedTime = this.clock.getElapsedTime();
      this.material.uniforms.uTime.value = prefersReducedMotion
        ? elapsedTime * 0.15
        : elapsedTime;

      this.currentColor.lerp(this.targetColor, 0.05);
      this.material.uniforms.uColor.value = this.currentColor;

      if (this.orb) {
        this.orb.rotation.y = elapsedTime * 0.05;
        this.orb.rotation.x = elapsedTime * 0.02;
      }

      if (this.particles) {
        this.particles.rotation.y = elapsedTime * -0.01;
      }

      this.renderer.render(this.scene, this.camera);
    }
  }

  // Instantiate on runtime (matches dashboard.html canvas id)
  new SlushyMoodOrb(canvas);
})();
