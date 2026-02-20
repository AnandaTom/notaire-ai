/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        ivory: '#fdfcfa',
        cream: '#f9f7f4',
        sand: '#f3efe9',
        champagne: '#e8e2d9',
        gold: {
          DEFAULT: '#c4a35a',
          light: '#d4bc7c',
          dark: '#9a7d3a',
        },
        charcoal: '#2c2c2c',
        graphite: '#4a4a4a',
        slate: '#7a7a7a',
        navy: {
          DEFAULT: '#1e3a5f',
          light: '#2d4a6f',
          active: '#243D5C',
        },
        success: {
          DEFAULT: '#16a34a',
          light: '#dcfce7',
        },
        warning: {
          DEFAULT: '#d97706',
          light: '#fef3c7',
        },
        error: {
          DEFAULT: '#dc2626',
          light: '#fee2e2',
        },
        info: {
          DEFAULT: '#2563eb',
          light: '#dbeafe',
        },
      },
      fontFamily: {
        serif: ['Cormorant Garamond', 'Georgia', 'serif'],
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
