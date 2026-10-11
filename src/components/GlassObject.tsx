import React, { useMemo, useRef, memo } from 'react';
import { useFrame } from '@react-three/fiber';
import { MeshTransmissionMaterial } from '@react-three/drei';
import * as THREE from 'three';
import { timelineState } from '../hooks/useScrollTimeline.ts';

export interface GlassObjectProps {
  samples?: number;
}

export const GlassObject: React.FC<GlassObjectProps> = memo(({
  samples = 10,
}) => {
  const meshRef = useRef<THREE.Mesh>(null);
  const groupRef = useRef<THREE.Group>(null);
  const mouseTarget = useRef({ x: 0, y: 0 });

  // Uniforms for GPU morphing and displacements
  const uniformsRef = useRef({
    uMorph: { value: 0 },
    uRidges: { value: 1 },
    uRuffle: { value: 0 },
    uSpike: { value: 0 },
    uTime: { value: 0 },
  });

  // 128x64 parametric grid (8,385 vertices, perfect sleek density)
  const radialSegs = 128;
  const tubularSegs = 64;
  const vertexCount = (radialSegs + 1) * (tubularSegs + 1);

  // Pre-generate base Sphere, Torus and Angle coordinates ONCE
  const geometry = useMemo(() => {
    const sPos = new Float32Array(vertexCount * 3);
    const sNorm = new Float32Array(vertexCount * 3);
    const tPos = new Float32Array(vertexCount * 3);
    const tNorm = new Float32Array(vertexCount * 3);
    const angles = new Float32Array(vertexCount * 4);
    const uvs = new Float32Array(vertexCount * 2);
    const indices: number[] = [];

    const sphereR = 1.15;
    const torusR = 1.0;
    const torusTube = 0.38;

    let ptr = 0;
    let aPtr = 0;
    let uvPtr = 0;

    for (let j = 0; j <= tubularSegs; j++) {
      const v = (j / tubularSegs) * Math.PI * 2;
      const phi = (j / tubularSegs) * Math.PI;

      for (let i = 0; i <= radialSegs; i++) {
        const u = (i / radialSegs) * Math.PI * 2;

        // Base Sphere (radius = 1.15)
        const sx = sphereR * Math.sin(phi) * Math.cos(u);
        const sy = sphereR * Math.cos(phi);
        const sz = sphereR * Math.sin(phi) * Math.sin(u);
        sPos[ptr] = sx;
        sPos[ptr + 1] = sy;
        sPos[ptr + 2] = sz;

        const sLen = Math.sqrt(sx * sx + sy * sy + sz * sz) || 1;
        sNorm[ptr] = sx / sLen;
        sNorm[ptr + 1] = sy / sLen;
        sNorm[ptr + 2] = sz / sLen;

        // Base Torus: Major radius R = 1.0, Tube radius r = 0.38
        const cosV = Math.cos(v);
        const sinV = Math.sin(v);
        const cosU = Math.cos(u);
        const sinU = Math.sin(u);

        tPos[ptr] = (torusR + torusTube * cosV) * cosU;
        tPos[ptr + 1] = torusTube * sinV;
        tPos[ptr + 2] = (torusR + torusTube * cosV) * sinU;

        tNorm[ptr] = cosV * cosU;
        tNorm[ptr + 1] = sinV;
        tNorm[ptr + 2] = cosV * sinU;

        angles[aPtr] = u;
        angles[aPtr + 1] = v;
        angles[aPtr + 2] = phi;
        angles[aPtr + 3] = 0.0;

        uvs[uvPtr] = i / radialSegs;
        uvs[uvPtr + 1] = j / tubularSegs;

        ptr += 3;
        aPtr += 4;
        uvPtr += 2;
      }
    }

    for (let j = 0; j < tubularSegs; j++) {
      for (let i = 0; i < radialSegs; i++) {
        const a = (radialSegs + 1) * j + i;
        const b = (radialSegs + 1) * (j + 1) + i;
        const c = (radialSegs + 1) * (j + 1) + i + 1;
        const d = (radialSegs + 1) * j + i + 1;

        indices.push(a, b, d);
        indices.push(b, c, d);
      }
    }

    const geo = new THREE.BufferGeometry();
    geo.setIndex(indices);
    geo.setAttribute('position', new THREE.BufferAttribute(sPos, 3));
    geo.setAttribute('normal', new THREE.BufferAttribute(sNorm, 3));
    geo.setAttribute('aTorusPos', new THREE.BufferAttribute(tPos, 3));
    geo.setAttribute('aTorusNorm', new THREE.BufferAttribute(tNorm, 3));
    geo.setAttribute('aAngles', new THREE.BufferAttribute(angles, 4));
    geo.setAttribute('uv', new THREE.BufferAttribute(uvs, 2));

    return geo;
  }, []);

  // Vertex shader compilation hook: GPU morphing & analytical normal computation
  const handleBeforeCompile = (shader: any) => {
    shader.uniforms.uMorph = uniformsRef.current.uMorph;
    shader.uniforms.uRidges = uniformsRef.current.uRidges;
    shader.uniforms.uRuffle = uniformsRef.current.uRuffle;
    shader.uniforms.uSpike = uniformsRef.current.uSpike;
    shader.uniforms.uTime = uniformsRef.current.uTime;

    shader.vertexShader = `
attribute vec3 aTorusPos;
attribute vec3 aTorusNorm;
attribute vec4 aAngles;

uniform float uMorph;
uniform float uRidges;
uniform float uRuffle;
uniform float uSpike;
uniform float uTime;

// Evaluates base blend between Sphere and Torus
vec3 evalBasePos(vec3 sP, vec3 tP, float m) {
  return mix(sP, tP, m);
}

vec3 evalBaseNorm(vec3 sN, vec3 tN, float m) {
  return normalize(mix(sN, tN, m));
}

// Exact radial displacement formula
float evalDisp(vec3 bPos, float u, float v, float m, float t, float r_ridge, float r_ruf, float r_spk) {
  float invM = 1.0 - m;
  
  // 1. HERO: Clean subtle concentric embossed rings (4% radius = 0.046)
  float ridge = sin(bPos.y * 14.0 + t * 0.4) * 0.04 * invM * r_ridge;
  
  // 2. ACT 2: Radial ruffle around the tube: amp * sin(k * theta_major) * (0.5 + 0.5 * sin(m * phi_tube))
  // k = 18, m = 3, amp ramping up to 0.12
  float ruffle = 0.11 * sin(18.0 * u + t * 1.5) * (0.5 + 0.5 * sin(3.0 * v)) * m * r_ruf;
  
  // 3. DEVICE: Spiky crystalline urchin using sharper spikes pow(abs(noise), 3)
  float rawSpike = max(0.0, sin(14.0 * u + v * 6.0 + t * 1.2));
  float spike = pow(rawSpike, 3.0) * 0.30 * m * r_spk;
  
  return ridge + ruffle + spike;
}
` + shader.vertexShader;

    shader.vertexShader = shader.vertexShader.replace(
      '#include <beginnormal_vertex>',
      `
  float u_val = aAngles.x;
  float v_val = aAngles.y;
  float phi_val = aAngles.z;

  vec3 bP0 = evalBasePos(position, aTorusPos, uMorph);
  vec3 bN0 = evalBaseNorm(normal, aTorusNorm, uMorph);
  float d0 = evalDisp(bP0, u_val, v_val, uMorph, uTime, uRidges, uRuffle, uSpike);
  vec3 p0 = bP0 + bN0 * d0;

  // Tangent calculation via finite difference without pole artifacts
  float eps = 0.006;
  float u_next = u_val + eps;
  float v_next = v_val + eps;
  float phi_next = phi_val + eps * 0.5;

  vec3 sPos_u = vec3(1.15 * sin(phi_val) * cos(u_next), 1.15 * cos(phi_val), 1.15 * sin(phi_val) * sin(u_next));
  vec3 sNorm_u = normalize(sPos_u);
  vec3 tPos_u = vec3((1.0 + 0.38 * cos(v_val)) * cos(u_next), 0.38 * sin(v_val), (1.0 + 0.38 * cos(v_val)) * sin(u_next));
  vec3 tNorm_u = vec3(cos(v_val) * cos(u_next), sin(v_val), cos(v_val) * sin(u_next));
  vec3 bPu = evalBasePos(sPos_u, tPos_u, uMorph);
  vec3 bNu = evalBaseNorm(sNorm_u, tNorm_u, uMorph);
  float du = evalDisp(bPu, u_next, v_val, uMorph, uTime, uRidges, uRuffle, uSpike);
  vec3 pu = bPu + bNu * du;

  vec3 sPos_v = vec3(1.15 * sin(phi_next) * cos(u_val), 1.15 * cos(phi_next), 1.15 * sin(phi_next) * sin(u_val));
  vec3 sNorm_v = normalize(sPos_v);
  vec3 tPos_v = vec3((1.0 + 0.38 * cos(v_next)) * cos(u_val), 0.38 * sin(v_next), (1.0 + 0.38 * cos(v_next)) * sin(u_val));
  vec3 tNorm_v = vec3(cos(v_next) * cos(u_val), sin(v_next), cos(v_next) * sin(u_val));
  vec3 bPv = evalBasePos(sPos_v, tPos_v, uMorph);
  vec3 bNv = evalBaseNorm(sNorm_v, tNorm_v, uMorph);
  float dv = evalDisp(bPv, u_val, v_next, uMorph, uTime, uRidges, uRuffle, uSpike);
  vec3 pv = bPv + bNv * dv;

  vec3 dPdu = pu - p0;
  vec3 dPdv = pv - p0;
  vec3 computedNormal = normalize(cross(dPdv, dPdu));
  if (dot(computedNormal, bN0) < 0.0) {
    computedNormal = -computedNormal;
  }
  if (length(computedNormal) < 0.1) {
    computedNormal = bN0;
  }
  vec3 objectNormal = computedNormal;
  #ifdef USE_TANGENT
    vec3 objectTangent = vec3( tangent.xyz );
  #endif
`
    );

    shader.vertexShader = shader.vertexShader.replace(
      '#include <begin_vertex>',
      'vec3 transformed = p0;'
    );

    // Uniform declarations in fragment shader
    shader.fragmentShader = `
uniform float uSpike;
` + shader.fragmentShader;

    // Subtle iridescent fresnel rim & crystalline cyan radiance
    shader.fragmentShader = shader.fragmentShader.replace(
      '#include <dithering_fragment>',
      `
      #include <dithering_fragment>
      vec3 viewD = normalize( - vViewPosition );
      float fRim = clamp( 1.0 - max( 0.0, dot( normal, viewD ) ), 0.0, 1.0 );
      float rimPow = pow( fRim, 3.0 );
      vec3 iridCol = mix( vec3(0.35, 0.85, 1.0), vec3(0.95, 0.55, 0.98), rimPow );
      gl_FragColor.rgb += iridCol * rimPow * 0.35;

      // Sparkling cyan crystalline radiance specifically for the urchin in Scene 4
      gl_FragColor.rgb += vec3(0.25, 0.85, 1.0) * uSpike * 0.45 * rimPow + vec3(0.08, 0.40, 0.65) * uSpike * 0.22;
      `
    );
  };

  // Run update inside useFrame: DAMPING, zero CPU loops, zero computeVertexNormals
  useFrame((state, delta) => {
    if (!groupRef.current) return;

    if (timelineState.scale <= 0.01) {
      groupRef.current.visible = false;
      return;
    }
    groupRef.current.visible = true;

    // Smooth transform damping
    groupRef.current.position.x = THREE.MathUtils.damp(groupRef.current.position.x, timelineState.posX, 6, delta);
    groupRef.current.position.y = THREE.MathUtils.damp(groupRef.current.position.y, timelineState.posY, 6, delta);
    groupRef.current.position.z = THREE.MathUtils.damp(groupRef.current.position.z, timelineState.posZ, 6, delta);

    const curScale = groupRef.current.scale.x;
    const nextScale = THREE.MathUtils.damp(curScale, timelineState.scale, 6, delta);
    groupRef.current.scale.set(nextScale, nextScale, nextScale);

    groupRef.current.rotation.x = THREE.MathUtils.damp(groupRef.current.rotation.x, timelineState.rotX, 6, delta);
    groupRef.current.rotation.y = THREE.MathUtils.damp(groupRef.current.rotation.y, timelineState.rotY, 6, delta);
    groupRef.current.rotation.z = THREE.MathUtils.damp(groupRef.current.rotation.z, timelineState.rotZ, 6, delta);

    // Damped shader uniforms
    uniformsRef.current.uMorph.value = THREE.MathUtils.damp(uniformsRef.current.uMorph.value, timelineState.morph, 6, delta);
    uniformsRef.current.uRidges.value = THREE.MathUtils.damp(uniformsRef.current.uRidges.value, timelineState.ridges, 6, delta);
    uniformsRef.current.uRuffle.value = THREE.MathUtils.damp(uniformsRef.current.uRuffle.value, timelineState.flutes, 6, delta);
    uniformsRef.current.uSpike.value = THREE.MathUtils.damp(uniformsRef.current.uSpike.value, timelineState.spikes, 6, delta);
    uniformsRef.current.uTime.value += delta;

    // Subtle pointer parallax using delta time
    mouseTarget.current.x = state.pointer.x * 0.12;
    mouseTarget.current.y = state.pointer.y * 0.10;
    groupRef.current.rotation.y += (mouseTarget.current.x - groupRef.current.rotation.y) * 3 * delta;
    groupRef.current.rotation.x += (-mouseTarget.current.y - groupRef.current.rotation.x) * 3 * delta;

    if (meshRef.current) {
      meshRef.current.rotation.z += delta * 0.05;
    }
  });

  return (
    <group ref={groupRef} position={[0, 0.62, 0]} scale={[0.7, 0.7, 0.7]}>
      <mesh ref={meshRef} geometry={geometry}>
        <MeshTransmissionMaterial
          onBeforeCompile={handleBeforeCompile}
          color="#ffffff"
          transmission={1.0}
          thickness={0.3}
          roughness={0.04}
          ior={1.22}
          chromaticAberration={0.08}
          anisotropicBlur={0.16}
          distortion={0.12}
          distortionScale={0.3}
          temporalDistortion={0.03}
          attenuationColor="#ffffff"
          attenuationDistance={4.0}
          backside={false}
          clearcoat={1}
          clearcoatRoughness={0.03}
          envMapIntensity={1.5}
          iridescence={1.0}
          iridescenceIOR={1.35}
          iridescenceThicknessRange={[150, 480]}
          samples={samples}
          resolution={1024}
          toneMapped={true}
        />
      </mesh>
    </group>
  );
});
