'use client';

import React, { useRef, useMemo, useState } from 'react';
import { Canvas } from '@react-three/fiber';
import { Environment, OrbitControls, Float, Text, MeshDistortMaterial, Stars, ContactShadows, useCursor } from '@react-three/drei';
import * as THREE from 'three';
import { motion } from 'framer-motion-3d';
import gsap from 'gsap';

function TaskNode({ position, title, status, color }: any) {
  const mesh = useRef<THREE.Mesh>(null);
  const [hovered, setHover] = useState(false);
  useCursor(hovered);

  const handleClick = () => {
    if (mesh.current) {
        gsap.to(mesh.current.scale, { x: 1.5, y: 1.5, z: 1.5, duration: 0.3, yoyo: true, repeat: 1 });
    }
  };

  return (
    <Float speed={2} rotationIntensity={0.5} floatIntensity={1}>
      <motion.mesh 
        ref={mesh} 
        position={position}
        onClick={handleClick}
        onPointerOver={() => setHover(true)}
        onPointerOut={() => setHover(false)}
        whileHover={{ scale: 1.1 }}
      >
        <boxGeometry args={[2, 1, 0.1]} />
        <meshPhysicalMaterial 
            color={color} 
            transmission={0.9} 
            opacity={1} 
            metalness={0} 
            roughness={0} 
            ior={1.5} 
            thickness={0.5} 
            specularIntensity={1}
        />
        <Text
          position={[0, 0, 0.06]}
          fontSize={0.2}
          color="white"
          anchorX="center"
          anchorY="middle"
        >
          {title}
        </Text>
      </motion.mesh>
    </Float>
  );
}

function ConnectionLines({ nodes }: any) {
    const points = useMemo(() => {
        const p = [];
        for (let i = 0; i < nodes.length - 1; i++) {
            p.push(new THREE.Vector3(...nodes[i].position));
            p.push(new THREE.Vector3(...nodes[i+1].position));
        }
        return p;
    }, [nodes]);
    
    return (
        <lineSegments>
            <bufferGeometry>
                <bufferAttribute
                    attach="attributes-position"
                    count={points.length}
                    array={new Float32Array(points.flatMap(p => [p.x, p.y, p.z]))}
                    itemSize={3}
                />
            </bufferGeometry>
            <lineBasicMaterial color="#4f46e5" transparent opacity={0.3} />
        </lineSegments>
    );
}

export default function ThreeWorkspace() {
  const nodes = [
    { id: 1, position: [-3, 2, -2], title: "Frontend Scaffold", color: "#4f46e5" },
    { id: 2, position: [0, 0, 0], title: "API Integration", color: "#ec4899" },
    { id: 3, position: [3, -2, -1], title: "Database Schema", color: "#10b981" },
    { id: 4, position: [2, 3, -3], title: "3D Workspace", color: "#8b5cf6" },
  ];

  return (
    <div className="w-full h-full absolute inset-0 bg-slate-950 overflow-hidden rounded-3xl border border-white/10 shadow-[0_0_50px_rgba(79,70,229,0.15)] cursor-grab active:cursor-grabbing">
      <Canvas camera={{ position: [0, 0, 8], fov: 45 }} dpr={[1, 2]}>
        <color attach="background" args={['#020617']} />
        <ambientLight intensity={0.5} />
        <directionalLight position={[10, 10, 5]} intensity={1} castShadow />
        <spotLight position={[-10, -10, -10]} intensity={2} color="#4f46e5" />
        
        {/* Particle System / Stars */}
        <Stars radius={100} depth={50} count={5000} factor={4} saturation={0} fade speed={1} />
        
        {/* Interactive Data Nodes */}
        {nodes.map(node => (
            <TaskNode key={node.id} {...node} />
        ))}
        <ConnectionLines nodes={nodes} />

        {/* Decorative Grid Floor */}
        <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -5, 0]}>
            <planeGeometry args={[50, 50, 50, 50]} />
            <meshBasicMaterial color="#334155" wireframe transparent opacity={0.15} />
        </mesh>
        
        {/* Animated Background Blob representing Project Velocity */}
        <Float speed={1} rotationIntensity={2} floatIntensity={2}>
            <mesh position={[-5, 2, -10]} scale={5}>
                <sphereGeometry args={[1, 64, 64]} />
                <MeshDistortMaterial color="#4f46e5" speed={2} distort={0.4} radius={1} transparent opacity={0.3} />
            </mesh>
        </Float>
        
        <ContactShadows position={[0, -4.5, 0]} opacity={0.4} scale={20} blur={2} far={10} />
        <Environment preset="city" />
        
        {/* Smooth Camera Controls */}
        <OrbitControls 
            enablePan={true} 
            enableZoom={true} 
            enableRotate={true}
            autoRotate
            autoRotateSpeed={0.5}
            minPolarAngle={Math.PI / 4}
            maxPolarAngle={Math.PI / 1.5}
        />
      </Canvas>
    </div>
  );
}
