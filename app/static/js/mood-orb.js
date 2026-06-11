(function () {
  // Disabled to prevent conflicts with the slushy three-shader orb
  return;
  const canvas = document.getElementById('moodOrb');
  const dashboard = window.DAYTONE_DASHBOARD;
  if (!canvas || !dashboard || !dashboard.orb || !window.THREE) return;

  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const moodStates = {
    1: { label: 'Sick', primary: '#ef4444', secondary: '#f97316', sharpness: 1, calm: 0.2 },
    2: { label: 'Sad', primary: '#f97316', secondary: '#facc15', sharpness: 0.8, calm: 0.4 },
    3: { label: 'Anxious', primary: '#14b8a6', secondary: '#60a5fa', sharpness: 0.6, calm: 0.6 },
    4: { label: 'Calm', primary: '#3b82f6', secondary: '#8b5cf6', sharpness: 0.4, calm: 0.8 },
    5: { label: 'Happy', primary: '#8b5cf6', secondary: '#ec4899', sharpness: 0.2, calm: 1 }
  };

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(45, 1, 0.1, 100);
  camera.position.set(0, 0, 5.8);

  const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));

  const group = new THREE.Group();
  scene.add(group);

  const uniforms = {
    uTime: { value: 0 },
    uSharpness: { value: dashboard.orb.sharpness || 0.5 },
    uCalm: { value: dashboard.orb.calm || 0.5 },
    uColorA: { value: new THREE.Color(dashboard.orb.primary || moodStates[3].primary) },
    uColorB: { value: new THREE.Color(dashboard.orb.secondary || moodStates[3].secondary) }
  };

  const orb = new THREE.Mesh(
    new THREE.IcosahedronGeometry(1.55, 5),
    new THREE.ShaderMaterial({
      uniforms,
      transparent: true,
      vertexShader: `
        uniform float uTime;
        uniform float uSharpness;
        uniform float uCalm;
        varying vec3 vNormal;
        varying float vPulse;

        void main() {
          vNormal = normalize(normalMatrix * normal);
          vec3 p = position;
          float ridges =
            sin(p.x * 7.0 + uTime * 1.2) *
            sin(p.y * 8.0 - uTime * 0.8) *
            sin(p.z * 6.0 + uTime * 0.9);
          float breath = sin(uTime * 1.4) * 0.055 * uCalm;
          float spike = ridges * mix(0.28, 0.04, uCalm) * uSharpness;
          vPulse = ridges * 0.5 + 0.5;
          vec3 displaced = p + normal * (breath + spike);
          gl_Position = projectionMatrix * modelViewMatrix * vec4(displaced, 1.0);
        }
      `,
      fragmentShader: `
        uniform vec3 uColorA;
        uniform vec3 uColorB;
        varying vec3 vNormal;
        varying float vPulse;

        void main() {
          float fresnel = pow(1.0 - max(dot(vNormal, vec3(0.0, 0.0, 1.0)), 0.0), 2.0);
          vec3 color = mix(uColorA, uColorB, smoothstep(0.1, 0.95, vPulse + fresnel * 0.4));
          gl_FragColor = vec4(color + fresnel * 0.18, 0.94);
        }
      `
    })
  );
  group.add(orb);

  const ringMaterial = new THREE.MeshBasicMaterial({
    color: new THREE.Color(dashboard.orb.secondary || moodStates[3].secondary),
    transparent: true,
    opacity: 0.22,
    side: THREE.DoubleSide
  });

  for (let i = 0; i < 3; i += 1) {
    const ring = new THREE.Mesh(new THREE.TorusGeometry(2.0 + i * 0.32, 0.01, 12, 180), ringMaterial);
    ring.rotation.x = Math.PI / 2.5 + i * 0.38;
    ring.rotation.y = i * 0.55;
    group.add(ring);
  }

  const particleGeometry = new THREE.BufferGeometry();
  const positions = [];
  for (let i = 0; i < 620; i += 1) {
    const radius = 2.2 + Math.random() * 2.2;
    const theta = Math.random() * Math.PI * 2;
    const phi = Math.acos(2 * Math.random() - 1);
    positions.push(
      radius * Math.sin(phi) * Math.cos(theta),
      radius * Math.sin(phi) * Math.sin(theta),
      radius * Math.cos(phi)
    );
  }
  particleGeometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
  const particleMaterial = new THREE.PointsMaterial({
    color: new THREE.Color(dashboard.orb.primary || moodStates[3].primary),
    size: 0.024,
    transparent: true,
    opacity: 0.48
  });
  const particles = new THREE.Points(particleGeometry, particleMaterial);
  group.add(particles);

  scene.add(new THREE.AmbientLight(0xffffff, 1.4));
  const keyLight = new THREE.PointLight(0xffffff, 8, 12);
  keyLight.position.set(3, 2, 5);
  scene.add(keyLight);

  const label = document.getElementById('orbLabel');
  const score = document.getElementById('orbScore');
  const cockpit = document.querySelector('.orb-cockpit');
  const pills = Array.from(document.querySelectorAll('.mood-pill'));

  const target = {
    sharpness: uniforms.uSharpness.value,
    calm: uniforms.uCalm.value,
    colorA: uniforms.uColorA.value.clone(),
    colorB: uniforms.uColorB.value.clone()
  };

  function setMood(mood) {
    const state = moodStates[mood] || moodStates[3];
    target.sharpness = state.sharpness;
    target.calm = state.calm;
    target.colorA = new THREE.Color(state.primary);
    target.colorB = new THREE.Color(state.secondary);
    if (cockpit) {
      cockpit.style.setProperty('--orb-primary', state.primary);
      cockpit.style.setProperty('--orb-secondary', state.secondary);
    }
    if (label) label.textContent = state.label;
    if (score) score.textContent = `${mood}/5`;
    pills.forEach((pill) => pill.classList.toggle('active', Number(pill.dataset.mood) === mood));
  }

  pills.forEach((pill) => {
    pill.addEventListener('click', () => setMood(Number(pill.dataset.mood)));
  });

  function resize() {
    const rect = canvas.getBoundingClientRect();
    renderer.setSize(rect.width, rect.height, false);
    camera.aspect = rect.width / Math.max(rect.height, 1);
    camera.updateProjectionMatrix();
  }

  function render(time) {
    const t = time * 0.001;
    uniforms.uTime.value = prefersReducedMotion ? 0.6 : t;
    uniforms.uSharpness.value += (target.sharpness - uniforms.uSharpness.value) * 0.08;
    uniforms.uCalm.value += (target.calm - uniforms.uCalm.value) * 0.08;
    uniforms.uColorA.value.lerp(target.colorA, 0.08);
    uniforms.uColorB.value.lerp(target.colorB, 0.08);
    ringMaterial.color.lerp(target.colorB, 0.08);
    particleMaterial.color.lerp(target.colorA, 0.08);

    if (!prefersReducedMotion) {
      group.rotation.y = t * 0.16;
      orb.rotation.x = t * 0.07;
      particles.rotation.y = -t * 0.035;
      particles.rotation.x = Math.sin(t * 0.3) * 0.05;
    }

    renderer.render(scene, camera);
    requestAnimationFrame(render);
  }

  setMood(Number(dashboard.orb.mood || 3));
  resize();
  window.addEventListener('resize', resize);
  requestAnimationFrame(render);
})();
