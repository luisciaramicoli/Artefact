/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        emporio: {
          50: '#fdf8f4',
          100: '#f9eee3',
          200: '#f2dbc7',
          300: '#e7c0a2',
          400: '#d99e74',
          500: '#cb7d4d',
          600: '#bd653d',
          700: '#9d4f32',
          800: '#7f412d',
          900: '#673827',
          950: '#381c13',
        }
      }
    },
  },
  plugins: [],
}
