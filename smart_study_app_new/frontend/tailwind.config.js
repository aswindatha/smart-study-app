/**** shadcn-like tailwind setup ****/
/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ['class'],
  content: ['./index.html', './src/**/*.{ts,tsx,js,jsx}'],
  theme: {
    container: { center: true, padding: '2rem' },
    extend: {
      colors: {
        border: 'hsl(214 32% 91%)',
        background: 'hsl(0 0% 100%)',
        foreground: 'hsl(222.2 47.4% 11.2%)',
        primary: { DEFAULT: '#2563eb', foreground: '#ffffff' },
        secondary: { DEFAULT: '#f1f5f9', foreground: '#0f172a' },
        muted: { DEFAULT: '#f1f5f9', foreground: '#64748b' },
        card: { DEFAULT: '#ffffff', foreground: '#0f172a' },
      },
      borderRadius: {
        lg: '0.5rem',
        md: '0.375rem',
        sm: '0.25rem',
      },
      keyframes: {
        shimmer: {
          '0%': { backgroundPosition: '-1000px 0' },
          '100%': { backgroundPosition: '1000px 0' },
        },
      },
      animation: {
        shimmer: 'shimmer 2s infinite linear',
      },
    },
  },
  plugins: [],
}
