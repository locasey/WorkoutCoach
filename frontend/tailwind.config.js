/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'muted-teal': '#8eb19d',
        'carbon-black': '#1e1b18',
        'almond-silk': '#eacdc2',
        'persian-blue': '#072ac8',
        'rust-brown': '#a44200',
      },
    },
  },
  plugins: [],
}

