import React, { useRef, useMemo } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { Environment, Lightformer, Stats, AdaptiveDpr } from '@react-three/drei';
import * as THREE from 'three';
import { GlassObject } from './GlassObject.tsx';
import { timelineState } from '../hooks/useScrollTimeline.ts';

// Temporary FPS & WebGL info reporter
const PerfReporter: React.FC = () => {
  const { gl } = useThree();
  useFrame((_, delta) => {
    (window as any).__glInfo = {
      calls: gl.info.render.calls,
      triangles: gl.info.render.triangles,
      frame: gl.info.render.frame,
      delta,
      fps: delta > 0 ? Math.min(120, Math.round(1 / delta)) : 60,
    };
  });
  return null;
};

// 6 Instanced Floating Bubbles using cheap Fake-Glass physical material
// Positioned strictly in the outer side margins so they never overlap cards or text
const bubbleData = [
  { pos: [-4.6, 2.2, -2.5], r: 0.65 },
  { pos: [4.6, -1.2, -2.8], r: 0.75 },
  { pos: [-4.5, -2.2, -2.2], r: 0.6 },
  { pos: [4.5, 2.2, -3.2], r: 0.7 },
  { pos: [-4.8, 0.2, -3.0], r: 0.55 },
  { pos: [4.7, -2.5, -2.6], r: 0.6 },
];

const FloatingBubbles: React.FC = () => {
  const meshRef = useRef<THREE.InstancedMesh>(null);
  const dummy = useMemo(() => new THREE.Object3D(), []);
  const matRef = useRef<THREE.MeshPhysicalMaterial>(null);

  useFrame((state, delta) => {
    if (!meshRef.current || !matRef.current) return;
    const opacity = timelineState.bubblesOpacity;
    
    if (opacity <= 0.01) {
      meshRef.current.visible = false;
      return;
    }
    meshRef.current.visible = true;
    matRef.current.opacity = 0.18 * opacity;

    const time = state.clock.getElapsedTime();
    for (let i = 0; i < bubbleData.length; i++) {
      const b = bubbleData[i];
      dummy.position.set(
        b.pos[0] + Math.sin(time * 0.7 + i) * 0.12,
        b.pos[1] + Math.cos(time * 0.6 + i * 1.4) * 0.15,
        b.pos[2]
      );
      dummy.scale.set(b.r, b.r, b.r);
      dummy.rotation.y += delta * 0.08;
      dummy.updateMatrix();
      meshRef.current.setMatrixAt(i, dummy.matrix);
    }
    meshRef.current.instanceMatrix.needsUpdate = true;
  });

  return (
    <instancedMesh ref={meshRef} args={[undefined, undefined, bubbleData.length]} visible={false}>
      <sphereGeometry args={[1, 24, 24]} />
      <meshPhysicalMaterial
        ref={matRef}
        color="#e0f2fe"
        transmission={0}
        transparent={true}
        opacity={0}
        roughness={0.04}
        metalness={0.05}
        clearcoat={1}
        clearcoatRoughness={0.06}
        iridescence={1}
        iridescenceIOR={1.3}
        iridescenceThicknessRange={[100, 450]}
        sheen={0.8}
        sheenColor="#bae6fd"
        sheenRoughness={0.3}
        envMapIntensity={0.8}
        depthWrite={false}
      />
    </instancedMesh>
  );
};

// Pedestal for Scene 5 finale (seated underneath the centered sphere)
const SanctuaryPedestal: React.FC = () => {
  const groupRef = useRef<THREE.Group>(null);

  useFrame((_, delta) => {
    if (!groupRef.current) return;
    const targetScale = timelineState.pedestalScale;
    if (targetScale <= 0.01 && groupRef.current.scale.x <= 0.01) {
      groupRef.current.visible = false;
      return;
    }
    groupRef.current.visible = true;
    const nextScale = THREE.MathUtils.damp(groupRef.current.scale.x, targetScale, 6, delta);
    groupRef.current.scale.set(nextScale, nextScale, nextScale);
  });

  return (
    <group ref={groupRef} position={[0, -0.95, 0]} scale={[0, 0, 0]} visible={false}>
      {/* Dark Slate Architectural Cylinder */}
      <mesh position={[0, 0, 0]}>
        <cylinderGeometry args={[1.15, 1.25, 0.32, 48]} />
        <meshStandardMaterial color="#1e293b" roughness={0.4} metalness={0.6} />
      </mesh>
      {/* Concentric Cyan Ring Accent */}
      <mesh position={[0, 0.17, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <ringGeometry args={[0.7, 1.08, 48]} />
        <meshBasicMaterial color="#38bdf8" transparent opacity={0.6} side={THREE.DoubleSide} />
      </mesh>
    </group>
  );
};

// Ambient floating cosmic dust particles
const DustParticles: React.FC<{ count?: number }> = ({ count = 50 }) => {
  const pointsRef = useRef<THREE.Points>(null);

  const particlesGeo = useMemo(() => {
    const positions = new Float32Array(count * 3);
    for (let i = 0; i < count * 3; i += 3) {
      positions[i] = (Math.random() - 0.5) * 16;
      positions[i + 1] = (Math.random() - 0.5) * 12;
      positions[i + 2] = (Math.random() - 0.5) * 8;
    }
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    return geo;
  }, [count]);

  useFrame((_, delta) => {
    if (pointsRef.current) {
      pointsRef.current.rotation.y += delta * 0.01;
    }
  });

  return (
    <points ref={pointsRef} geometry={particlesGeo}>
      <pointsMaterial size={0.03} color="#93c5fd" transparent opacity={0.35} />
    </points>
  );
};

export const Scene: React.FC = () => {
  return (
    <div className="fixed inset-0 w-screen h-screen pointer-events-none z-0 overflow-hidden">
      <Canvas
        camera={{ position: [0, 0, 5.5], fov: 45 }}
        dpr={[1, 1.5]}
        gl={{
          antialias: false,
          alpha: true,
          powerPreference: 'high-performance',
          toneMapping: THREE.ACESFilmicToneMapping,
          toneMappingExposure: 1.2,
        }}
        frameloop="always"
      >
        <AdaptiveDpr pixelated />

        {/* Studio HDRI Environment with soft studio ambiance and round light panels */}
        <Environment environmentIntensity={1.4} blur={0.7}>
          <color attach="background" args={["#7b8ca3"]} />
          {/* Top Key Large Soft Round Panel */}
          <Lightformer
            form="circle"
            intensity={1.5}
            position={[0, 6, -2]}
            scale={[10, 10, 1]}
            target={[0, 0, 0]}
            color="#ffffff"
          />
          {/* Direct Backlight / Rim Round Panel */}
          <Lightformer
            form="circle"
            intensity={1.2}
            position={[0, 0, -4]}
            scale={[9, 9, 1]}
            target={[0, 0, 0]}
            color="#dbeafe"
          />
          {/* Soft Side Fill Round Panel */}
          <Lightformer
            form="circle"
            intensity={1.0}
            position={[4, -1, -3]}
            scale={[8, 8, 1]}
            target={[0, 0, 0]}
            color="#f0f9ff"
          />
        </Environment>

        {/* Studio Lighting */}
        <ambientLight intensity={1.8} />
        <directionalLight position={[5, 8, 6]} intensity={2.0} color="#ffffff" />
        <pointLight position={[4, 3, 4]} intensity={4.0} distance={20} color="#38bdf8" />
        <pointLight position={[-4, -2, 2]} intensity={3.5} distance={20} color="#c084fc" />

        {/* Focused Cyan Key Light & Rim Light for Device Urchin */}
        <pointLight position={[-0.74, 0.4, 2.2]} intensity={6.0} distance={12} color="#38bdf8" />
        <pointLight position={[-2.5, 0.2, 1.8]} intensity={4.5} distance={15} color="#818cf8" />

        {/* Floating Subtle Particles */}
        <DustParticles />

        {/* Scene 5 Cheap Instanced Soap Bubbles in side margins */}
        <FloatingBubbles />

        {/* ONLY ONE transmission object in the entire scene */}
        <GlassObject samples={10} />

        {/* Scene 5 Architectural Pedestal */}
        <SanctuaryPedestal />

        {/* Temporary Performance Monitoring */}
        <PerfReporter />
        <Stats />
      </Canvas>
    </div>
  );
};
export default Scene;
