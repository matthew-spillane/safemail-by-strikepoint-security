/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        dark: {
          bg: '#0a0a0a',
          card: '#111111',
          border: '#2a2a2a',
        },
        accent: '#e8412a',
        muted: '#a0a0a0',
      },
    },
  },
  plugins: [],
}
