(function () {
  try {
    const canvas = document.getElementById('toneField');
    if (!canvas || !window.THREE) return;

    const THREE = window.THREE;

    // GLSL 3D Simplex Noise for smooth organic surface deformation
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

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(55, 1, 0.1, 100);
    camera.position.set(0, 0, 7);

    const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));

    const group = new THREE.Group();
    scene.add(group);

    // Safe, high-density SphereGeometry for smooth displacement mapping
    const geometry = new THREE.SphereGeometry(1.45, 64, 64);
    
    // Shader Material representing the dynamic wellness orb
    const material = new THREE.ShaderMaterial({
      uniforms: {
        uTime: { value: 0 },
        uColor: { value: new THREE.Color(0x0f9f8f) },    // Default DayTone primary-2 (teal)
        uColorAlt: { value: new THREE.Color(0x2563eb) }, // Default DayTone primary (blue)
        uNoiseFrequency: { value: 0.38 },
        uNoiseAmplitude: { value: 0.18 },
        uMouseEffect: { value: 0.0 }
      },
      vertexShader: noiseGLSL + `
        uniform float uTime;
        uniform float uNoiseFrequency;
        uniform float uNoiseAmplitude;
        uniform float uMouseEffect;
        varying vec3 vNormal;
        varying vec3 vPosition;
        varying float vDisplacement;

        void main() {
          vNormal = normalize(normalMatrix * normal);
          
          // Calculate dynamic noise displacement warped by cursor hover
          float freq = uNoiseFrequency + uMouseEffect * 0.16;
          float amp = uNoiseAmplitude + uMouseEffect * 0.08;
          float noise = snoise(position * freq + vec3(uTime * 0.45));
          
          vec3 newPosition = position + normal * noise * amp;
          vPosition = newPosition;
          vDisplacement = noise;
          
          gl_Position = projectionMatrix * modelViewMatrix * vec4(newPosition, 1.0);
        }
      `,
      fragmentShader: `
        precision highp float;
        uniform vec3 uColor;
        uniform vec3 uColorAlt;
        varying vec3 vNormal;
        varying vec3 vPosition;
        varying float vDisplacement;

        void main() {
          vec3 lightDir = normalize(vec3(1.0, 1.0, 1.2));
          vec3 viewDir = normalize(vec3(0.0, 0.0, 1.0));
          
          vec3 normal = normalize(vNormal);
          float diffuse = max(dot(normal, lightDir), 0.0);
          
          // Soft velvet/rim lighting glow effect
          float rim = pow(1.0 - max(dot(normal, viewDir), 0.0), 3.0);
          
          // Smooth blend of the two tone colors based on Simplex displacement
          vec3 blendedColor = mix(uColor, uColorAlt, (vDisplacement + 1.0) * 0.5);
          
          vec3 finalColor = blendedColor * (diffuse * 0.72 + 0.38) + (vec3(1.0) * rim * 0.32);
          gl_FragColor = vec4(finalColor, 0.88);
        }
      `,
      transparent: true
    });

    const core = new THREE.Mesh(geometry, material);
    group.add(core);

    // Dynamic background particles
    const particlesCount = 380;
    const particles = new THREE.BufferGeometry();
    const positions = [];
    for (let i = 0; i < particlesCount; i += 1) {
      const radius = 2.2 + Math.random() * 4.2;
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
      new THREE.PointsMaterial({ color: 0xffffff, size: 0.016, transparent: true, opacity: 0.38 })
    );
    group.add(points);

    // Lights
    scene.add(new THREE.AmbientLight(0xffffff, 1.5));
    const light = new THREE.PointLight(0x5fd4c4, 12, 15);
    light.position.set(3, 2, 5);
    scene.add(light);
    const warm = new THREE.PointLight(0xff9b54, 6, 15);
    warm.position.set(-4, -3, 4);
    scene.add(warm);

    // Mouse Tracking State
    let mouse = { x: 0, y: 0, targetX: 0, targetY: 0, speed: 0 };
    window.addEventListener('mousemove', (e) => {
      mouse.targetX = (e.clientX / window.innerWidth) * 2 - 1;
      mouse.targetY = -(e.clientY / window.innerHeight) * 2 - 1;
    });

    const clock = new THREE.Clock();

    function animate() {
      requestAnimationFrame(animate);

      // Dynamic client size check prevents rendering bugs when canvas starts at 0x0
      const w = canvas.clientWidth;
      const h = canvas.clientHeight;
      if (w > 0 && h > 0 && (canvas.width !== w || canvas.height !== h)) {
        renderer.setSize(w, h, false);
        camera.aspect = w / h;
        camera.updateProjectionMatrix();
      }

      const t = clock.getElapsedTime();

      // Interpolated mouse tracking for smooth responsive inertia
      const dx = mouse.targetX - mouse.x;
      const dy = mouse.targetY - mouse.y;
      mouse.x += dx * 0.08;
      mouse.y += dy * 0.08;
      
      // Calculate speed factor to influence shape deformation on sudden movement
      const distanceMoved = Math.sqrt(dx * dx + dy * dy);
      mouse.speed += (distanceMoved - mouse.speed) * 0.1;

      // Group rotation with 3D parallax effect matching cursor coordinates
      group.rotation.y = t * 0.08 + mouse.x * 0.35;
      group.rotation.x = mouse.y * 0.25;

      // Spin background points
      points.rotation.y = -t * 0.03;

      // Update shader uniforms
      material.uniforms.uTime.value = t;
      material.uniforms.uMouseEffect.value = Math.min(mouse.speed * 4.0, 1.2) + Math.abs(mouse.x + mouse.y) * 0.15;

      renderer.render(scene, camera);
    }

    animate();
  } catch (err) {
    console.error("Interactive ambient background initialization failed:", err);
  }
})();
