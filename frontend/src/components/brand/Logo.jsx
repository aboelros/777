import React from 'react';

/**
 * Automio Official Monolithic Logo
 * Implements the strict geometric IO/A pattern defined in the design system.
 */
export const Logo = ({ className = '', size = 24 }) => {
  return (
    <div className={`flex items-center gap-3 ${className}`}>
      <svg 
        width={size} 
        height={size} 
        viewBox="0 0 24 24" 
        fill="none" 
        xmlns="http://www.w3.org/2000/svg"
        className="text-automio-amber"
      >
        {/* 'A' Structure - Parallel Tracks with Diagonal */}
        <path d="M4 22V2" stroke="currentColor" strokeWidth="2.5" strokeLinecap="square"/>
        <path d="M10 22V2" stroke="currentColor" strokeWidth="2.5" strokeLinecap="square"/>
        <path d="M4 12L10 6" stroke="currentColor" strokeWidth="2.5" strokeLinecap="square"/>
        
        {/* 'I/O' Structure - Input/Output */}
        <path d="M20 18V22" stroke="currentColor" strokeWidth="2.5" strokeLinecap="square"/>
        <circle cx="20" cy="8" r="5" stroke="currentColor" strokeWidth="2.5"/>
      </svg>
      <span className="font-sans font-semibold tracking-[0.1em] text-white uppercase" style={{ fontSize: size * 0.75 }}>
        Automio
      </span>
    </div>
  );
};

export default Logo;
