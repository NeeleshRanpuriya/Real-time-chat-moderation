/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'toxic-red': '#ef4444',
        'warning-orange': '#f97316',
        'safe-green': '#10b981',
      },
    },
  },
  plugins: [],
}
