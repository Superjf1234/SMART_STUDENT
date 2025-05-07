/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./mi_app_estudio/**/*.{js,ts,jsx,tsx,py}",
    "./.web/pages/**/*.{js,ts,jsx,tsx}",
    "./.web/components/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Poppins', 'sans-serif'],
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}