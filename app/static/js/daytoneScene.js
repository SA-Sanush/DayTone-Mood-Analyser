/**
 * DayTone 3D Liquid Glass Engine (daytoneScene.js)
 * High-performance, anti-stretch WebGL layer with:
 * - True refractive liquid glass shader with chromatic rainbow dispersion & specular chrome highlights
 * - Automatic aspect-ratio protection preventing any squashing or stretching
 * - Responsive positioning framing the frosted glass card
 * - Dynamic contact drop-shadow
 */

(function () {
  'use strict';

  function initDaytoneScene() {
    const THREE = window.THREE || (typeof THREE !== 'undefined' ? THREE : null);
    if (!THREE) {
      setTimeout(initDaytoneScene, 100);
      return;
    }

    const canvas = document.getElementById('daytone-canvas');
    if (!canvas) return;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, 1, 0.1, 100);
    camera.position.set(0, 0, 6.0);

    const renderer = new THREE.WebGLRenderer({
      canvas,
      alpha: true,
      antialias: true,
      powerPreference: 'high-performance'
    });

    // Anti-stretch dynamic resize function
    function resizeRendererToDisplaySize() {
      const width = canvas.clientWidth || window.innerWidth;
      const height = canvas.clientHeight || window.innerHeight;
      const pixelRatio = Math.min(window.devicePixelRatio || 1, 2);
      const targetW = Math.floor(width * pixelRatio);
      const targetH = Math.floor(height * pixelRatio);

      const needResize = canvas.width !== targetW || canvas.height !== targetH;
      if (needResize && width > 0 && height > 0) {
        renderer.setPixelRatio(pixelRatio);
        renderer.setSize(width, height, false); // false prevents inline CSS style overrides
        camera.aspect = width / height;
        camera.updateProjectionMatrix();
      }
      return needResize;
    }
    resizeRendererToDisplaySize();

    // Lighting: Point lights for caustic reflections & ambient light
    const light1 = new THREE.PointLight(0x38bdf8, 3, 20); // Cyan rim light
    light1.position.set(4, 3, 4);
    scene.add(light1);

    const light2 = new THREE.PointLight(0x818cf8, 2.5, 20); // Indigo fill light
    light2.position.set(-4, -2, 2);
    scene.add(light2);

    const ambLight = new THREE.AmbientLight(0xffffff, 1.2);
    scene.add(ambLight);

    if (THREE.ACESFilmicToneMapping) {
      renderer.toneMapping = THREE.ACESFilmicToneMapping;
      renderer.toneMappingExposure = 1.05;
    }

    // --- 1. REAL PHYSICAL GLASS MATERIAL ---
    const material = new THREE.MeshPhysicalMaterial({
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

    // Gentle spherical breathing ripples injected into physical vertex pipeline
    material.userData.uTime = { value: 0 };
    material.onBeforeCompile = (shader) => {
      shader.uniforms.uTime = material.userData.uTime;
      shader.vertexShader = `uniform float uTime;\n` + shader.vertexShader;
      shader.vertexShader = shader.vertexShader.replace(
        '#include <begin_vertex>',
        `
        #include <begin_vertex>
        float wave = sin(transformed.x * 2.8 + uTime * 1.2) * 
                     cos(transformed.y * 2.8 + uTime * 1.2) * 
                     sin(transformed.z * 2.2 + uTime * 1.2) * 0.035;
        transformed += normal * wave;
        `
      );
    };

    // Pristine Sphere Geometry (Radius 1.6)
    const geometry = new THREE.SphereGeometry(1.6, 128, 128);
    const orb = new THREE.Mesh(geometry, material);

    // Dynamic Contact Soft Shadow Texture
    const shadowGeo = new THREE.PlaneGeometry(3.6, 3.6);
    const shadowCanvas = document.createElement('canvas');
    shadowCanvas.width = 128;
    shadowCanvas.height = 128;
    const sCtx = shadowCanvas.getContext('2d');
    const sGrad = sCtx.createRadialGradient(64, 64, 10, 64, 64, 60);
    sGrad.addColorStop(0, 'rgba(15, 23, 42, 0.6)');
    sGrad.addColorStop(0.5, 'rgba(15, 23, 42, 0.25)');
    sGrad.addColorStop(1, 'rgba(15, 23, 42, 0)');
    sCtx.fillStyle = sGrad;
    sCtx.fillRect(0, 0, 128, 128);

    const shadowTex = new THREE.CanvasTexture(shadowCanvas);
    const shadowMat = new THREE.MeshBasicMaterial({
      map: shadowTex,
      transparent: true,
      opacity: 0.5,
      depthWrite: false
    });
    const shadow = new THREE.Mesh(shadowGeo, shadowMat);
    shadow.rotation.x = -Math.PI / 2;
    shadow.position.y = -1.75;
    scene.add(shadow);

    // Responsive Positioning: Positioned center-right so it sits directly behind the glass card
    // Responsive Positioning: Positioned center-right so it sits directly behind the glass card
    let baseOrbX = 1.2;
    let baseOrbY = 0.05;
    let baseOrbZ = -0.5;
    let baseOrbScale = 1.05;

    function updateOrbPosition() {
      const isAuthPage = window.location.pathname.includes('/login') || 
                         window.location.pathname.includes('/register') ||
                         window.location.pathname === '/';
      if (!isAuthPage) {
        orb.visible = false;
        shadow.visible = false;
        return;
      }
      orb.visible = true;
      shadow.visible = true;

      const isDesktop = window.innerWidth >= 1024;
      if (isDesktop) {
        baseOrbX = 1.2;
        baseOrbY = 0.05;
        baseOrbZ = -0.5;
        baseOrbScale = 1.05;
      } else {
        baseOrbX = 0;
        baseOrbY = 0.2;
        baseOrbZ = -1.0;
        baseOrbScale = 0.85;
      }
      orb.position.set(baseOrbX, baseOrbY, baseOrbZ);
      orb.scale.set(baseOrbScale, baseOrbScale, baseOrbScale);
      shadow.position.set(baseOrbX, -1.75, baseOrbZ);
    }
    updateOrbPosition();
    scene.add(orb);

    // Floating Ambient Dust Particles
    const particleCount = 100;
    const posArray = new Float32Array(particleCount * 3);
    for (let i = 0; i < particleCount * 3; i += 3) {
      posArray[i] = (Math.random() - 0.5) * 14;
      posArray[i + 1] = (Math.random() - 0.5) * 9;
      posArray[i + 2] = (Math.random() - 0.5) * 6;
    }
    const particleGeo = new THREE.BufferGeometry();
    particleGeo.setAttribute('position', new THREE.BufferAttribute(posArray, 3));
    const particleMat = new THREE.PointsMaterial({
      size: 0.035,
      color: 0x93c5fd,
      transparent: true,
      opacity: 0.45
    });
    const particles = new THREE.Points(particleGeo, particleMat);
    scene.add(particles);

    // Mouse Parallax & Dynamic Scroll Tracking
    let targetX = 0;
    let targetY = 0;
    let currentScrollProgress = 0;
    let targetScrollProgress = 0;

    window.addEventListener('mousemove', (e) => {
      targetX = (e.clientX / window.innerWidth - 0.5) * 0.22;
      targetY = (e.clientY / window.innerHeight - 0.5) * 0.22;
    });

    function onScrollUpdate() {
      const maxScroll = Math.max(1, document.documentElement.scrollHeight - window.innerHeight);
      targetScrollProgress = Math.min(1, Math.max(0, window.scrollY / maxScroll));
    }
    window.addEventListener('scroll', onScrollUpdate, { passive: true });

    // Listen to Lenis scroll if available
    if (window.lenis) {
      window.lenis.on('scroll', (e) => {
        const maxScroll = Math.max(1, document.documentElement.scrollHeight - window.innerHeight);
        targetScrollProgress = Math.min(1, Math.max(0, (e.scroll || window.scrollY) / maxScroll));
      });
    }

    window.addEventListener('resize', () => {
      resizeRendererToDisplaySize();
      updateOrbPosition();
      onScrollUpdate();
    });

    // Smooth Render Loop with Organic Scroll Kinetics
    const clock = new THREE.Clock();
    function animate() {
      resizeRendererToDisplaySize();

      const elapsed = clock.getElapsedTime();
      if (material.userData && material.userData.uTime) {
        material.userData.uTime.value = elapsed;
      }
      if (material.uniforms && material.uniforms.uTime) {
        material.uniforms.uTime.value = elapsed;
      }

      // Ensure background sphere is never visible on dashboard or app pages
      orb.visible = false;
      shadow.visible = false;

      // Smooth scroll lerp
      currentScrollProgress += (targetScrollProgress - currentScrollProgress) * 0.07;

      // 3D orb kinetic motion driven by scroll progress
      const scrollYOffset = currentScrollProgress * -2.2;
      const scrollXOffset = Math.sin(currentScrollProgress * Math.PI) * 0.85;
      const scrollRotY = currentScrollProgress * Math.PI * 1.6;
      const scrollRotX = Math.sin(currentScrollProgress * Math.PI) * 0.4;

      orb.position.y = baseOrbY + scrollYOffset;
      orb.position.x = baseOrbX + (window.innerWidth >= 1024 ? -scrollXOffset : 0);
      shadow.position.y = -1.75 + scrollYOffset * 0.8;
      shadow.position.x = orb.position.x;

      orb.rotation.y = elapsed * 0.12 + scrollRotY + targetX;
      orb.rotation.x = Math.sin(elapsed * 0.22) * 0.08 + scrollRotX + targetY;

      particles.rotation.y = elapsed * 0.012 + currentScrollProgress * 0.5;
      particles.position.y = -scrollYOffset * 0.3;

      renderer.render(scene, camera);
      requestAnimationFrame(animate);
    }
    animate();

    // 3D Card Hover Tilt Micro-Interactions for glass elements
    function initCardTilt() {
      if (window.matchMedia('(pointer: coarse)').matches) return; // Skip touch screens

      const cards = document.querySelectorAll('.glass-card, .panel, .elevated-panel, .card, .dashboard-card');
      cards.forEach((card) => {
        if (card.dataset.tiltInitialized) return;
        card.dataset.tiltInitialized = 'true';

        card.addEventListener('mousemove', (e) => {
          const rect = card.getBoundingClientRect();
          const x = e.clientX - rect.left - rect.width / 2;
          const y = e.clientY - rect.top - rect.height / 2;
          const rotX = -(y / (rect.height / 2)) * 3.5;
          const rotY = (x / (rect.width / 2)) * 3.5;

          card.style.transform = `perspective(1000px) rotateX(${rotX.toFixed(2)}deg) rotateY(${rotY.toFixed(2)}deg) translateY(-2px)`;
          card.style.transition = 'transform 0.08s ease-out';
        });

        card.addEventListener('mouseleave', () => {
          card.style.transform = '';
          card.style.transition = 'transform 0.4s ease-out';
        });
      });
    }

    // ScrollTrigger Content Reveals
    function initScrollReveals() {
      if (window.gsap && window.ScrollTrigger) {
        try {
          ScrollTrigger.refresh();
        } catch(e) {}
        const revealTargets = document.querySelectorAll('.reveal-on-scroll');
        revealTargets.forEach((el) => {
          if (el.dataset.revealInit) return;
          el.dataset.revealInit = 'true';

          gsap.fromTo(el, 
            { opacity: 0, y: 22 },
            {
              opacity: 1,
              y: 0,
              duration: 0.75,
              ease: 'power2.out',
              scrollTrigger: {
                trigger: el,
                start: 'top 90%',
                toggleActions: 'play none none none'
              }
            }
          );
        });
      }
    }

    // Initialize interactive card tilt and scroll reveals on DOM ready and dynamic changes
    setTimeout(() => {
      initCardTilt();
      initScrollReveals();
      onScrollUpdate();
    }, 200);

    // Expose API for interactions
    window.DaytoneScene = {
      orb,
      mesh: orb,
      particles,
      material,
      camera,
      scene,
      renderer,
      updateOrbPosition,
      initCardTilt,
      initScrollReveals,
      pulse(scale = 1.2, duration = 0.5) {
        if (window.gsap) {
          gsap.to(orb.scale, {
            x: baseOrbScale * scale,
            y: baseOrbScale * scale,
            z: baseOrbScale * scale,
            duration: duration / 2,
            yoyo: true,
            repeat: 1,
            ease: 'power2.out'
          });
        }
      },
      setColorPalette(hexA, hexB, hexC, duration = 0.8) {
        // Uniform color morph if needed
      },
      disperse(duration = 0.8) {
        this.pulse(1.25, duration);
      }
    };
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initDaytoneScene);
  } else {
    initDaytoneScene();
  }
})();
