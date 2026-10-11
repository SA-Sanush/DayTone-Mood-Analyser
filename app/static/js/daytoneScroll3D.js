/**
 * DayTone 100% Video Recreation 3D Engine (daytoneScroll3D.js)
 * Features:
 * - True refractive liquid glass shader with chromatic rainbow Fresnel dispersion
 * - Slender liquid Torus with fluted corrugation and acute stress spike morph
 * - Dynamic contact drop-shadow projected on 3D floor
 * - 3D Perspective coordinate grid with registration crosshairs
 * - Finale liquid glass Sanctuary Orb on pedestal with orbiting micro-droplets
 */

const THREE = window.THREE || (typeof THREE !== 'undefined' ? THREE : null);

export class DaytoneScrollyEngine {
  constructor(canvas) {
    this.canvas = canvas;
    const THREE_LIB = window.THREE || THREE;
    if (!THREE_LIB) {
      console.error('[DayTone] THREE is not loaded.');
      return;
    }
    this.THREE = THREE_LIB;
    this.scene = new this.THREE.Scene();

    this.camera = new this.THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 100);
    this.camera.position.set(0, 0, 5.8);

    this.renderer = new this.THREE.WebGLRenderer({
      canvas: this.canvas,
      alpha: true,
      antialias: true,
      powerPreference: 'high-performance'
    });
    this.renderer.setSize(window.innerWidth, window.innerHeight);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    if (this.THREE.ACESFilmicToneMapping) {
      this.renderer.toneMapping = this.THREE.ACESFilmicToneMapping;
      this.renderer.toneMappingExposure = 1.05;
    }

    this.initLighting();
    this.initTorus();
    this.initContactShadow();
    this.initPerspectiveGrid();
    this.initFinaleOrb();
    this.initParticles();
    this.addResize();
    this.clock = new this.THREE.Clock();
    this.animate();
  }

  initLighting() {
    const THREE = this.THREE;
    // 3. Add Point Lights to catch glass caustics & reflections
    const light1 = new THREE.PointLight(0x38bdf8, 3, 20); // Cyan rim light
    light1.position.set(4, 3, 4);
    this.scene.add(light1);

    const light2 = new THREE.PointLight(0x818cf8, 2.5, 20); // Indigo fill light
    light2.position.set(-4, -2, 2);
    this.scene.add(light2);

    const ambientLight = new THREE.AmbientLight(0xffffff, 1.2);
    this.scene.add(ambientLight);
  }

  initTorus() {
    const THREE = this.THREE;
    // 1. Proportions matching the video (slender ring, not a thick donut)
    this.geometry = new THREE.TorusGeometry(1.2, 0.26, 64, 160);

    // 2. Real Physical Glass Material
    const glassMaterial = new THREE.MeshPhysicalMaterial({
      color: 0xffffff,
      metalness: 0.1,
      roughness: 0.05,
      transmission: 0.95,          // 95% transparent glass
      ior: 1.52,                   // Index of refraction (glass)
      thickness: 1.2,              // Light refraction depth
      specularIntensity: 1.0,
      specularColor: 0xffffff,
      iridescence: 0.8,            // Rainbow color dispersion on edges
      iridescenceIOR: 1.3,
      transparent: true,
      opacity: 1.0
    });

    // Vertex deformation hooks for organic breathing ripple & Act 2 fluted spike morph
    glassMaterial.userData.uTime = { value: 0 };
    glassMaterial.userData.uSpikes = { value: 0.0 };
    glassMaterial.userData.uFluteFreq = { value: 18.0 };

    glassMaterial.onBeforeCompile = (shader) => {
      shader.uniforms.uTime = glassMaterial.userData.uTime;
      shader.uniforms.uSpikes = glassMaterial.userData.uSpikes;
      shader.uniforms.uFluteFreq = glassMaterial.userData.uFluteFreq;

      shader.vertexShader = `
        uniform float uTime;
        uniform float uSpikes;
        uniform float uFluteFreq;
      ` + shader.vertexShader;

      shader.vertexShader = shader.vertexShader.replace(
        '#include <begin_vertex>',
        `
        #include <begin_vertex>
        float ripple = sin(transformed.x * 3.5 + uTime * 1.4) * cos(transformed.y * 3.5 + uTime * 1.4) * 0.025;
        float angle = atan(transformed.y, transformed.x);
        float flutes = sin(angle * uFluteFreq + uTime * 1.5) * 0.08;
        float backRimFactor = max(0.0, sin(angle + 1.2));
        float sharpPeaks = pow(max(0.0, sin(angle * 7.0 + 0.8)), 3.5) * 0.32 * backRimFactor;
        float totalDisplacement = ripple + (flutes + sharpPeaks) * uSpikes;
        transformed += normal * totalDisplacement;
        `
      );
    };

    this.material = glassMaterial;
    // Proxy for GSAP scrollController timeline
    this.material.uniforms = {
      uTime: glassMaterial.userData.uTime,
      uSpikes: glassMaterial.userData.uSpikes,
      uFluteFreq: glassMaterial.userData.uFluteFreq
    };

    this.torus = new THREE.Mesh(this.geometry, this.material);
    this.torus.rotation.x = Math.PI * 0.35; // Forward tilt matching video
    this.scene.add(this.torus);
  }

  initContactShadow() {
    const THREE = this.THREE;
    // Dynamic soft blurred ambient occlusion drop-shadow beneath torus
    const shadowGeo = new THREE.PlaneGeometry(3.6, 3.6);
    
    // Radial soft shadow texture
    const canvas = document.createElement('canvas');
    canvas.width = 128;
    canvas.height = 128;
    const ctx = canvas.getContext('2d');
    const grad = ctx.createRadialGradient(64, 64, 10, 64, 64, 60);
    grad.addColorStop(0, 'rgba(15, 23, 42, 0.65)');
    grad.addColorStop(0.5, 'rgba(15, 23, 42, 0.28)');
    grad.addColorStop(1, 'rgba(15, 23, 42, 0)');
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, 128, 128);

    const shadowTex = new THREE.CanvasTexture(canvas);
    const shadowMat = new THREE.MeshBasicMaterial({
      map: shadowTex,
      transparent: true,
      opacity: 0.55,
      depthWrite: false
    });

    this.shadow = new THREE.Mesh(shadowGeo, shadowMat);
    this.shadow.rotation.x = -Math.PI / 2;
    this.shadow.position.set(0.35, -1.75, 0.25);
    this.scene.add(this.shadow);
  }

  initPerspectiveGrid() {
    const THREE = this.THREE;
    // 3D Perspective Grid Floor beneath the torus
    const size = 32;
    const divisions = 40;
    this.grid = new THREE.GridHelper(size, divisions, 0x38bdf8, 0x94a3b8);
    this.grid.position.y = -1.8;
    this.grid.material.opacity = 0.22;
    this.grid.material.transparent = true;
    this.scene.add(this.grid);

    // Glowing coordinate disc under torus in Act 2
    const discGeo = new THREE.RingGeometry(0.8, 2.2, 48);
    const discMat = new THREE.MeshBasicMaterial({
      color: 0x38bdf8,
      transparent: true,
      opacity: 0.0,
      side: THREE.DoubleSide
    });
    this.disc = new THREE.Mesh(discGeo, discMat);
    this.disc.rotation.x = -Math.PI / 2;
    this.disc.position.y = -1.78;
    this.scene.add(this.disc);
  }

  initFinaleOrb() {
    const THREE = this.THREE;
    // Act 4 finale: Grand liquid glass sphere on architectural pedestal
    this.finaleGroup = new THREE.Group();
    this.finaleGroup.position.set(0, -0.15, -0.4);
    this.finaleGroup.scale.set(0.001, 0.001, 0.001); // Hidden initially

    // 1. Crystal liquid sphere
    const orbGeo = new THREE.SphereGeometry(1.28, 96, 96);
    this.orbMesh = new THREE.Mesh(orbGeo, this.material);
    this.finaleGroup.add(this.orbMesh);

    // 2. Architectural pedestal cylinder
    const pedGeo = new THREE.CylinderGeometry(1.35, 1.45, 0.45, 64);
    const pedMat = new THREE.MeshStandardMaterial({
      color: 0x1e293b,
      roughness: 0.25,
      metalness: 0.65
    });
    const pedMesh = new THREE.Mesh(pedGeo, pedMat);
    pedMesh.position.y = -1.35;
    this.finaleGroup.add(pedMesh);

    // Concentric glowing halo ring on top surface of pedestal
    const ringGeo = new THREE.RingGeometry(0.85, 1.25, 64);
    const ringMat = new THREE.MeshBasicMaterial({
      color: 0x38bdf8,
      side: THREE.DoubleSide,
      transparent: true,
      opacity: 0.7
    });
    const ringMesh = new THREE.Mesh(ringGeo, ringMat);
    ringMesh.rotation.x = -Math.PI / 2;
    ringMesh.position.y = -1.12;
    this.finaleGroup.add(ringMesh);

    // 3. Floating micro-droplets
    this.droplets = [];
    const dropGeo = new THREE.SphereGeometry(0.12, 32, 32);
    for (let i = 0; i < 7; i++) {
      const drop = new THREE.Mesh(dropGeo, this.material);
      const angle = (i / 7) * Math.PI * 2;
      drop.position.set(
        Math.cos(angle) * (1.7 + Math.random() * 0.5),
        (Math.random() - 0.5) * 1.2,
        Math.sin(angle) * (1.7 + Math.random() * 0.5)
      );
      drop.scale.setScalar(0.6 + Math.random() * 0.8);
      this.finaleGroup.add(drop);
      this.droplets.push(drop);
    }

    this.scene.add(this.finaleGroup);
  }

  initParticles() {
    const THREE = this.THREE;
    const count = 110;
    const pos = new Float32Array(count * 3);
    for (let i = 0; i < count * 3; i += 3) {
      pos[i] = (Math.random() - 0.5) * 16;
      pos[i + 1] = (Math.random() - 0.5) * 10;
      pos[i + 2] = (Math.random() - 0.5) * 8;
    }
    const pGeo = new THREE.BufferGeometry();
    pGeo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    const pMat = new THREE.PointsMaterial({
      size: 0.032,
      color: 0xbae6fd,
      transparent: true,
      opacity: 0.45
    });
    this.particles = new THREE.Points(pGeo, pMat);
    this.scene.add(this.particles);
  }

  addResize() {
    window.addEventListener('resize', () => {
      this.camera.aspect = window.innerWidth / window.innerHeight;
      this.camera.updateProjectionMatrix();
      this.renderer.setSize(window.innerWidth, window.innerHeight);
      this.renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    });
  }

  animate() {
    const elapsed = this.clock.getElapsedTime();
    this.material.uniforms.uTime.value = elapsed;

    // Torus gentle idle oscillation
    this.torus.rotation.z = elapsed * 0.12;

    // Micro-droplet bobbing
    if (this.droplets && this.finaleGroup.scale.x > 0.05) {
      this.droplets.forEach((d, idx) => {
        d.position.y += Math.sin(elapsed * 2.0 + idx) * 0.003;
      });
    }

    // Shadow tracking
    if (this.shadow) {
      this.shadow.position.x = this.torus.position.x + 0.35;
      this.shadow.position.z = this.torus.position.z + 0.25;
      this.shadow.scale.setScalar(this.torus.scale.x);
    }

    this.particles.rotation.y = elapsed * 0.015;

    this.renderer.render(this.scene, this.camera);
    requestAnimationFrame(this.animate.bind(this));
  }
}

export class DaytoneScrollEngine extends DaytoneScrollyEngine {}

if (typeof window !== 'undefined') {
  window.DaytoneScrollyEngine = DaytoneScrollyEngine;
  window.DaytoneScrollEngine = DaytoneScrollyEngine;
}
