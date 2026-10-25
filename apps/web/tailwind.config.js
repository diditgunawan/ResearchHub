/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        rf: {
          ground: '#F6F8F9',
          surface: '#FFFFFF',
          ink: '#12202B',
          muted: '#4A5B68',
          nav: '#34495A',
          primary: '#0B5C7A',
          'primary-strong': '#0B4A63',
          line: '#D7DEE3',
          'line-input': '#8695A1',
          'info-bg': '#E3F0F5',
          'info-text': '#0B4A63',
          'ok-bg': '#E4F3EA',
          'ok-text': '#14532D',
          'warn-bg': '#FDF0DC',
          'warn-text': '#7A3E00',
          'bad-bg': '#FBE4E4',
          'bad-text': '#8A1C1C',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        serif: ['Source Serif 4', 'Georgia', 'serif'],
      }
    },
  },
  plugins: [],
}
