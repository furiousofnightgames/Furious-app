/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        cyan: {
          300: '#a5f3fc',
          400: '#22d3ee',
          500: '#06b6d4',
          600: '#0891b2',
        },
        slate: {
          800: '#1e293b',
          900: '#0f172a',
        }
      },
      fontFamily: {
        sans: ['Space Mono', 'monospace'],
        orbitron: ['Orbitron', 'sans-serif'],
      },
      animation: {
        'spin': 'spin 1s linear infinite',
      },
      backdropBlur: {
        'sm': '4px',
        'md': '8px',
        'lg': '12px',
      },
      transitionDuration: {
        '0': '0ms',
        '75': '75ms',
        '100': '100ms',
        '150': '150ms',
        '200': '200ms',
        '300': '300ms',
        '500': '500ms',
        '700': '700ms',
        '1000': '1000ms',
      },
      transitionTimingFunction: {
        'linear': 'linear',
        'in': 'cubic-bezier(0.4, 0, 1, 1)',
        'out': 'cubic-bezier(0, 0, 0.2, 1)',
        'in-out': 'cubic-bezier(0.4, 0, 0.2, 1)',
      }
    },
  },
  plugins: [],
}
