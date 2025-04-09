import React, { useEffect, useRef, useState } from "react";

interface HeaderAnimationProps {
  isDarkMode: boolean;
}

interface Particle {
  x: number;
  y: number;
  size: number;
  speedX: number;
  speedY: number;
  shape: number;
}

const HeaderAnimation: React.FC<HeaderAnimationProps> = ({ isDarkMode }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [particles, setParticles] = useState<Particle[]>([]);

  useEffect(() => {
    if (!canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    // Set canvas size with proper device pixel ratio
    const updateCanvasSize = () => {
      const devicePixelRatio = window.devicePixelRatio || 1;
      const rect = canvas.getBoundingClientRect();

      // Set display size (css pixels)
      canvas.style.width = `${rect.width}px`;
      canvas.style.height = `${rect.height}px`;

      // Set actual size in memory (scaled to account for extra pixel density)
      canvas.width = rect.width * devicePixelRatio;
      canvas.height = rect.height * devicePixelRatio;

      // Normalize coordinate system to use css pixels
      ctx.scale(devicePixelRatio, devicePixelRatio);
    };

    updateCanvasSize();
    window.addEventListener("resize", updateCanvasSize);

    // Create particles with better sizing relative to viewport
    const newParticles: Particle[] = [];
    const minDimension = Math.min(window.innerWidth, window.innerHeight);
    const scaleFactor = minDimension / 1000; // Normalize sizes based on viewport

    for (let i = 0; i < 12; i++) {
      newParticles.push({
        x: Math.random() * window.innerWidth,
        y: Math.random() * window.innerHeight,
        size: (20 + Math.random() * 40) * scaleFactor, // Adjust size based on viewport
        speedX: (Math.random() - 0.5) * 1.2 * scaleFactor,
        speedY: Math.random() * 0.4 * scaleFactor,
        shape: Math.floor(Math.random() * 3),
      });
    }

    setParticles(newParticles);

    return () => {
      window.removeEventListener("resize", updateCanvasSize);
    };
  }, []);

  // Animation loop
  useEffect(() => {
    if (!canvasRef.current || particles.length === 0) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    // Get background color based on theme
    const backgroundColor = isDarkMode ? "#0B2026" : "#EEEDE9";
    const primaryColor = "#FF3621";

    let animationFrame: number;

    const animate = () => {
      // Clear canvas with theme-specific color
      ctx.fillStyle = backgroundColor;

      // Use CSS dimensions (adjusted for device pixel ratio)
      const width = canvas.width / (window.devicePixelRatio || 1);
      const height = canvas.height / (window.devicePixelRatio || 1);

      ctx.fillRect(0, 0, width, height);

      // Update and draw particles
      particles.forEach((particle) => {
        // Update position
        particle.x += particle.speedX;
        particle.y += particle.speedY;

        // Bounce off edges
        if (particle.x < 0 || particle.x > width) particle.speedX *= -1;
        if (particle.y < 0 || particle.y > height) particle.speedY *= -1;

        // Draw particle
        ctx.beginPath();
        ctx.fillStyle = primaryColor;

        if (particle.shape === 0) {
          // Circle
          ctx.arc(particle.x, particle.y, particle.size / 2, 0, Math.PI * 2);
        } else if (particle.shape === 1) {
          // Square
          ctx.rect(
            particle.x - particle.size / 2,
            particle.y - particle.size / 2,
            particle.size,
            particle.size,
          );
        } else {
          // Triangle
          const height = particle.size * 0.866;
          ctx.moveTo(particle.x, particle.y - height / 2);
          ctx.lineTo(particle.x - particle.size / 2, particle.y + height / 2);
          ctx.lineTo(particle.x + particle.size / 2, particle.y + height / 2);
          ctx.closePath();
        }

        ctx.fill();
      });

      animationFrame = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      cancelAnimationFrame(animationFrame);
    };
  }, [particles, isDarkMode]);

  return (
    <canvas
      ref={canvasRef}
      style={{
        position: "absolute",
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        width: "100%",
        height: "100%",
      }}
    />
  );
};

export default HeaderAnimation;
