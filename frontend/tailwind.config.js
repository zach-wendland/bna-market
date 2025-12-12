/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Cottage-Core: Warm neutrals & natural accents
        cottage: {
          cream: '#F5F1E8',
          sand: '#E8DCC8',
          wheat: '#C9B896',
          sage: '#7A9B76',
          terracotta: '#A67B5B',
          forest: '#5B7065',
          bark: '#4A3728',
        },
        // Cyberpunk: Neon glows & crisp UI
        cyber: {
          cyan: '#00F5FF',
          magenta: '#FF2E97',
          violet: '#B026FF',
          navy: '#0A0E27',
          deepBlue: '#1A1F3A',
          glow: '#00F5FF',
        },
        // Primary mapped to cyber-violet
        primary: {
          50: '#faf5ff',
          100: '#f3e8ff',
          200: '#e9d5ff',
          300: '#d8b4fe',
          400: '#c084fc',
          500: '#B026FF', // cyber-violet
          600: '#9333ea',
          700: '#7e22ce',
          800: '#6b21a8',
          900: '#581c87',
          950: '#3b0764',
        },
        // Accent mapped to cyber-cyan
        accent: {
          50: '#ecfeff',
          100: '#cffafe',
          200: '#a5f3fc',
          300: '#67e8f9',
          400: '#22d3ee',
          500: '#00F5FF', // cyber-cyan
          600: '#0891b2',
          700: '#0e7490',
          800: '#155e75',
          900: '#164e63',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'slide-down': 'slideDown 0.3s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideDown: {
          '0%': { opacity: '0', transform: 'translateY(-10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        glow: {
          '0%': { boxShadow: '0 0 5px rgba(0, 245, 255, 0.4)' },
          '100%': { boxShadow: '0 0 20px rgba(0, 245, 255, 0.6), 0 0 30px rgba(0, 245, 255, 0.3)' },
        },
      },
      boxShadow: {
        'glow-cyan': '0 0 15px rgba(0, 245, 255, 0.5)',
        'glow-magenta': '0 0 15px rgba(255, 46, 151, 0.5)',
        'glow-violet': '0 0 15px rgba(176, 38, 255, 0.5)',
      },
    },
  },
  plugins: [],
}
