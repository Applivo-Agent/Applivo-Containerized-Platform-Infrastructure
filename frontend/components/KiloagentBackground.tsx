"use client";
import React, { useEffect, useRef } from "react";

export function KiloagentBackground() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    if (!canvasRef.current) return;
    
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d", { alpha: false });
    if (!ctx) return;

    let animationFrameId: number;
    let width = 0;
    let height = 0;

    const fontSize = 11; // 10-12px requested
    // 0s, 1s, uppercase letters, symbols ($, #, @, %, &, *)
    const chars = "01ABCDEFGHIJKLMNOPQRSTUVWXYZ$#@%&*".split("");
    
    let columns = 0;
    let drops: number[] = [];

    const initGrid = () => {
      width = window.innerWidth;
      height = window.innerHeight;
      canvas.width = width;
      canvas.height = height;
      
      columns = Math.ceil(width / fontSize);
      drops = [];
      for (let x = 0; x < columns; x++) {
        // Start them at random vertical positions so screen is already full
        drops[x] = Math.random() * (height / fontSize);
      }
      
      // Base pure black background #0a0a0a
      ctx.fillStyle = "#0a0a0a";
      ctx.fillRect(0, 0, width, height);
    };

    window.addEventListener("resize", initGrid);
    initGrid();

    let lastTime = 0;
    const fps = 22; // Slower vertical scroll/cascade

    const draw = (time: number) => {
      animationFrameId = requestAnimationFrame(draw);

      if (time - lastTime < 1000 / fps) return;
      lastTime = time;

      // Draw black rectangle with low opacity to fade existing characters out
      // like the matrix code rain trail
      ctx.fillStyle = "rgba(10, 10, 10, 0.06)";
      ctx.fillRect(0, 0, width, height);

      ctx.font = `${fontSize}px monospace`;
      
      for (let i = 0; i < columns; i++) {
        const char = chars[Math.floor(Math.random() * chars.length)];
        
        // Base grey color (brighter for more central visibility)
        const opacity = 0.25 + (Math.random() * 0.35);
        const color = Math.random() < 0.02
          ? "rgba(180, 185, 180, 0.7)"
          : `rgba(80, 85, 80, ${opacity})`;

        // Random flicker / brighter greyish white
        ctx.fillStyle = color;
        const cy = drops[i] * fontSize;
        ctx.fillText(char, i * fontSize, cy);

        // Reset drop to top randomly, or if it goes off screen
        if (cy > height && Math.random() > 0.985) {
          drops[i] = 0;
        }

        // move downwards
        drops[i]++;
      }
    };

    animationFrameId = requestAnimationFrame(draw);

    return () => {
      window.removeEventListener("resize", initGrid);
      cancelAnimationFrame(animationFrameId);
    };
  }, []);

  return (
    <div className="absolute inset-0 z-0 bg-[#060606] overflow-hidden">
      <div className="absolute inset-0 z-0 bg-transparent" style={{ pointerEvents: 'none' }}>
        <canvas
          ref={canvasRef}
          className="w-full h-full mix-blend-screen opacity-100"
          style={{
            maskImage: 'radial-gradient(circle at 50% 45%, rgba(0,0,0,1) 15%, rgba(0,0,0,0.3) 45%, rgba(0,0,0,0) 70%)',
            WebkitMaskImage: 'radial-gradient(circle at 50% 45%, rgba(0,0,0,1) 15%, rgba(0,0,0,0.3) 45%, rgba(0,0,0,0) 70%)'
          }}
        />
      </div>
    </div>
  );
}
