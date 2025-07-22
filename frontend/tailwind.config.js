/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        background: 'var(--background)',
        foreground: 'var(--foreground)',
        // NavImpact Brand Colors
        'impact-teal': '#0D9488',
        'energy-coral': '#F97316',
        'mist-white': '#FAFAFB',
        'cool-gray': '#CBD5E1',
        'mint-breeze': '#A7F3D0',
        'warm-amber': '#FBBF24',
        'soft-crimson': '#F87171',
      },
    },
  },
  plugins: [],
} 