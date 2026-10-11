/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
    "./app/templates/**/*.html",
    "./app/static/js/**/*.js"
  ],
  darkMode: ['class', '[data-theme="nocturne"]'],
  theme: {
    extend: {
      colors: {
        navy: {
          900: '#0b1220',
          800: '#151d2e',
        },
        slate: {
          950: '#030712',
          900: '#0f172a',
          800: '#1e293b',
        }
      },
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', 'Inter', 'sans-serif'],
        display: ['"Plus Jakarta Sans"', 'Inter', 'sans-serif'],
      },
      backdropBlur: {
        glass: '20px',
      }
    },
  },
  plugins: [],
}
