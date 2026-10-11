import React, { useRef, useState, useCallback } from 'react';

export interface TiltCardProps {
  children: React.ReactNode;
  className?: string;
  contentClassName?: string;
  maxTilt?: number; // max tilt degrees, default 12
  scale?: number; // hover scale, default 1.02
  perspective?: number; // perspective in px, default 1000
  glare?: boolean; // specular light reflection, default true
  glareMaxOpacity?: number; // glare max opacity, default 0.3
  onClick?: () => void;
  style?: React.CSSProperties;
}

export const TiltCard: React.FC<TiltCardProps> = ({
  children,
  className = '',
  contentClassName = '',
  maxTilt = 12,
  scale = 1.02,
  perspective = 1000,
  glare = true,
  glareMaxOpacity = 0.25,
  onClick,
  style = {},
}) => {
  const cardRef = useRef<HTMLDivElement>(null);
  const glareRef = useRef<HTMLDivElement>(null);
  const [isHovered, setIsHovered] = useState(false);

  const handleMouseMove = useCallback(
    (e: React.MouseEvent<HTMLDivElement>) => {
      if (!cardRef.current) return;
      const rect = cardRef.current.getBoundingClientRect();
      if (rect.width === 0 || rect.height === 0) return;

      const x = (e.clientX - rect.left) / rect.width; // 0 to 1
      const y = (e.clientY - rect.top) / rect.height; // 0 to 1

      // tilt angles: y controls rotateX (invert), x controls rotateY
      const rotateX = (y - 0.5) * -maxTilt * 2;
      const rotateY = (x - 0.5) * maxTilt * 2;

      cardRef.current.style.transform = `perspective(${perspective}px) rotateX(${rotateX.toFixed(2)}deg) rotateY(${rotateY.toFixed(2)}deg) scale3d(${scale}, ${scale}, ${scale})`;

      if (glare && glareRef.current) {
        glareRef.current.style.background = `radial-gradient(circle at ${(x * 100).toFixed(1)}% ${(y * 100).toFixed(1)}%, rgba(255, 255, 255, ${glareMaxOpacity}) 0%, rgba(255, 255, 255, 0.04) 45%, transparent 75%)`;
        glareRef.current.style.opacity = '1';
      }
    },
    [maxTilt, scale, perspective, glare, glareMaxOpacity]
  );

  const handleMouseEnter = useCallback(() => {
    setIsHovered(true);
    if (cardRef.current) {
      cardRef.current.style.transition = 'transform 0.12s ease-out';
    }
    if (glareRef.current) {
      glareRef.current.style.opacity = '1';
      glareRef.current.style.transition = 'opacity 0.2s ease-out';
    }
  }, []);

  const handleMouseLeave = useCallback(() => {
    setIsHovered(false);
    if (cardRef.current) {
      cardRef.current.style.transform = `perspective(${perspective}px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)`;
      cardRef.current.style.transition = 'transform 0.6s cubic-bezier(0.23, 1, 0.32, 1)';
    }
    if (glareRef.current) {
      glareRef.current.style.opacity = '0';
      glareRef.current.style.transition = 'opacity 0.6s cubic-bezier(0.23, 1, 0.32, 1)';
    }
  }, [perspective]);

  return (
    <div
      ref={cardRef}
      onMouseMove={handleMouseMove}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      onClick={onClick}
      style={{
        transformStyle: 'preserve-3d',
        willChange: 'transform',
        ...style,
      }}
      className={`relative overflow-hidden ${className}`}
    >
      {/* Specular Glare Layer */}
      {glare && (
        <div
          ref={glareRef}
          className="pointer-events-none absolute inset-0 z-30 rounded-[inherit] opacity-0 transition-opacity"
          style={{
            mixBlendMode: 'overlay',
          }}
        />
      )}

      {/* Card Content with 3D depth preservation */}
      <div 
        className={`relative z-10 w-full h-full ${contentClassName}`} 
        style={{ transformStyle: 'preserve-3d' }}
      >
        {children}
      </div>
    </div>
  );
};
