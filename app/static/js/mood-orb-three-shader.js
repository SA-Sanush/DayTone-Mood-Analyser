// Optional alternate mood orb renderer using a simpler gradient/glow shader.
// This file is not auto-loaded; mood-orb.js is the active implementation.

(function () {
  const canvas = document.getElementById("moodOrb");
  const dashboard = window.DAYTONE_DASHBOARD;
  if (!canvas || !dashboard || !window.THREE) return;

  const prefersReducedMotion = window.matchMedia(
    "(prefers-reduced-motion: reduce)",
  ).matches;

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(
    75,
    canvas.clientWidth / Math.max(canvas.clientHeight, 1),
    0.1,
    1000,
  );

  const renderer = new THREE.WebGLRenderer({
    alpha: true,
    antialias: true,
    canvas,
  });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));

  function resize() {
    const w = canvas.clientWidth;
    const h = canvas.clientHeight;
    renderer.setSize(w, h, false);
    camera.aspect = w / Math.max(h, 1);
    camera.updateProjectionMatrix();
  }

  resize();
  window.addEventListener("resize", resize);

  const geometry = new THREE.SphereGeometry(2, 64, 64);

  const mood = Number(dashboard?.orb?.mood || 3);
  const moodStates = {
    1: { primary: 0xef4444, secondary: 0xf97316 },
    2: { primary: 0xf97316, secondary: 0xfacc15 },
    3: { primary: 0x14b8a6, secondary: 0x60a5fa },
    4: { primary: 0x3b82f6, secondary: 0x8b5cf6 },
    5: { primary: 0x8b5cf6, secondary: 0xec4899 },
  };
  const state = moodStates[mood] || moodStates[3];

  const material = new THREE.ShaderMaterial({
    uniforms: {
      time: { value: 0.0 },
      color1: { value: new THREE.Color(state.primary) },
      color2: { value: new THREE.Color(state.secondary) },
    },
    vertexShader: `
      varying vec2 vUv;
      varying vec3 vNormal;
      void main() {
        vUv = uv;
        vNormal = normalize(normalMatrix * normal);
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }
    `,
    fragmentShader: `
      uniform vec3 color1;
      uniform vec3 color2;
      uniform float time;
      varying vec2 vUv;
      varying vec3 vNormal;

      void main() {
        float intensity = pow(1.05 - dot(vNormal, vec3(0.0, 0.0, 1.0)), 2.0);
        vec3 finalColor = mix(color1, color2, vUv.y + sin(time) * 0.2);
        gl_FragColor = vec4(finalColor + (vec3(1.0) * intensity * 0.2), 0.95);
      }
    `,
    transparent: true,
  });

  const orb = new THREE.Mesh(geometry, material);
  scene.add(orb);
  camera.position.z = 5;

  function animate() {
    requestAnimationFrame(animate);

    const dt = prefersReducedMotion ? 0.006 : 0.015;
    material.uniforms.time.value += dt;

    orb.rotation.y += 0.003;
    orb.rotation.x += 0.001;

    const scale = 1 + Math.sin(Date.now() * 0.0015) * 0.03;
    orb.scale.set(scale, scale, scale);

    renderer.render(scene, camera);
  }

  animate();
})();
