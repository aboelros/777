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
        sans: ['"Inter Tight"', '"Plus Jakarta Sans"', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'ui-monospace', 'SFMono-Regular', 'Menlo', 'monospace'],
      },
      colors: {
        // Canonical Brand Tokens
        brand: {
          primary: 'rgb(var(--color-brand-primary) / <alpha-value>)',
          hover: 'rgb(var(--color-brand-hover) / <alpha-value>)',
          active: 'rgb(var(--color-brand-active) / <alpha-value>)',
          accent: 'rgb(var(--color-brand-accent) / <alpha-value>)',
          glow: 'rgb(var(--color-brand-glow) / <alpha-value>)',
        },
        // Semantic Surfaces
        surface: {
          DEFAULT: 'rgb(var(--color-bg-card) / <alpha-value>)',
          main: 'rgb(var(--color-bg-main) / <alpha-value>)',
          secondary: 'rgb(var(--color-bg-secondary) / <alpha-value>)',
          card: 'rgb(var(--color-bg-card) / <alpha-value>)',
          subtle: 'rgb(var(--color-bg-subtle) / <alpha-value>)',
          hover: 'rgb(var(--color-bg-hover) / <alpha-value>)',
        },
        // Semantic Typography
        primary: 'rgb(var(--color-text-primary) / <alpha-value>)',
        secondary: 'rgb(var(--color-text-secondary) / <alpha-value>)',
        muted: 'rgb(var(--color-text-muted) / <alpha-value>)',
        disabled: 'rgb(var(--color-text-disabled) / <alpha-value>)',
        // Semantic Status Colors
        status: {
          success: 'rgb(var(--color-status-success) / <alpha-value>)',
          warning: 'rgb(var(--color-status-warning) / <alpha-value>)',
          danger: 'rgb(var(--color-status-danger) / <alpha-value>)',
          info: 'rgb(var(--color-status-info) / <alpha-value>)',
        },
        // Borders
        border: {
          DEFAULT: 'rgba(var(--border-color), var(--border-opacity, 0.12))',
          subtle: 'rgba(var(--color-border-subtle), 0.08)',
          strong: 'rgba(var(--color-brand-accent), 0.3)',
        },
        // Backward Compatibility
        dark: {
          950: 'rgb(var(--color-bg-main) / <alpha-value>)',
          900: 'rgb(var(--color-bg-secondary) / <alpha-value>)',
          800: 'rgb(var(--color-bg-card) / <alpha-value>)',
          700: 'rgb(var(--color-bg-subtle) / <alpha-value>)',
        },
        accent: {
          DEFAULT: 'rgb(var(--color-brand-glow) / <alpha-value>)',
          500: 'rgb(var(--color-brand-glow) / <alpha-value>)',
          600: 'rgb(var(--color-brand-hover) / <alpha-value>)',
          400: 'rgb(var(--color-brand-accent) / <alpha-value>)',
        },
      },
      borderRadius: {
        'xl': '0.75rem',
        '2xl': '1rem',
        '3xl': '1.5rem',
      },
      boxShadow: {
        'surface-sm': '0 2px 8px -2px rgba(0, 0, 0, 0.25)',
        'surface-md': '0 4px 16px -4px rgba(0, 0, 0, 0.35)',
        'surface-lg': '0 12px 32px -8px rgba(0, 0, 0, 0.5)',
        'brand-glow': '0 0 20px rgba(56, 189, 248, 0.25)',
      },
    },
  },
  plugins: [],
}
