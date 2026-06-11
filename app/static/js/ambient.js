(function () {
  try {
    const canvas = document.getElementById('toneField');
    if (!canvas || !window.THREE) return;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(55, 1, 0.1, 100);
    camera.position.set(0, 0, 7);

    const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));

    const group = new THREE.Group();
    scene.add(group);

    const geometry = new THREE.IcosahedronGeometry(1.25, 2);
    const material = new THREE.MeshStandardMaterial({
      color: 0x5fd4c4,
      metalness: 0.22,
      roughness: 0.38,
      transparent: true,
      opacity: 0.86
    });
    const core = new THREE.Mesh(geometry, material);
    group.add(core);

    const ringMaterial = new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.18, side: THREE.DoubleSide });
    for (let i = 0; i < 3; i += 1) {
      const ring = new THREE.Mesh(new THREE.TorusGeometry(2 + i * 0.52, 0.012, 12, 160), ringMaterial);
      ring.rotation.x = Math.PI / 2.6 + i * 0.45;
      ring.rotation.y = i * 0.72;
      group.add(ring);
    }

    const particles = new THREE.BufferGeometry();
    const positions = [];
    for (let i = 0; i < 420; i += 1) {
      const radius = 2.4 + Math.random() * 3.2;
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      positions.push(
        radius * Math.sin(phi) * Math.cos(theta),
        radius * Math.sin(phi) * Math.sin(theta),
        radius * Math.cos(phi)
      );
    }
    particles.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
    const points = new THREE.Points(
      particles,
      new THREE.PointsMaterial({ color: 0xffffff, size: 0.018, transparent: true, opacity: 0.45 })
    );
    group.add(points);

    scene.add(new THREE.AmbientLight(0xffffff, 1.8));
    const light = new THREE.PointLight(0x63e6be, 16, 18);
    light.position.set(3, 2, 5);
    scene.add(light);
    const warm = new THREE.PointLight(0xff9b54, 8, 18);
    warm.position.set(-4, -3, 4);
    scene.add(warm);

    function resize() {
      const rect = canvas.getBoundingClientRect();
      renderer.setSize(rect.width, rect.height, false);
      camera.aspect = rect.width / Math.max(rect.height, 1);
      camera.updateProjectionMatrix();
    }

    function animate(time) {
      const t = time * 0.001;
      group.rotation.y = t * 0.18;
      core.rotation.x = t * 0.28;
      core.rotation.z = t * 0.2;
      points.rotation.y = -t * 0.05;
      renderer.render(scene, camera);
      requestAnimationFrame(animate);
    }

    resize();
    window.addEventListener('resize', resize);
    requestAnimationFrame(animate);
  } catch (err) {
    console.error("Ambient background initialization failed:", err);
  }
})();
