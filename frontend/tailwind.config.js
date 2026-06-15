/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        serif: ['"Playfair Display"', 'serif'],
        sans: ['"Inter Tight"', 'sans-serif'],
      },
      colors: {
        dark: {
          950: 'rgb(var(--bg-main))',      // #000000
          900: 'rgb(var(--bg-secondary))', // #121212
          800: 'rgb(var(--bg-card))',      // #0A0A0A
          700: 'rgba(var(--glass-bg), 0.9)',
        },
        accent: {
          500: 'rgb(var(--accent-primary))',
          600: 'rgb(var(--accent-dark))',
          400: 'rgb(var(--accent-light))',
        },
        border: 'rgba(var(--border-color), var(--border-opacity))',
      },
      backgroundImage: {
        'gradient-gold': 'linear-gradient(135deg, rgba(var(--accent-primary), 0.1), rgba(var(--accent-secondary), 0.05))',
      },
      boxShadow: {
        'glass-sm': '0 4px 16px rgba(0, 0, 0, 0.4)',
        'glass-md': '0 8px 32px rgba(0, 0, 0, 0.5)',
        'gold-glow': '0 0 20px rgba(var(--accent-primary), 0.2)',
      },
      animation: {
        'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'gold-shift': 'gold-shift 8s ease infinite alternate',
      },
    },
  },
  plugins: [],
}
