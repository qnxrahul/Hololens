/** @type {import('tailwindcss').Config} */
export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          DEFAULT: "#24A0ED",
          dark: "#1A73E8",
        },
      },
    },
  },
  plugins: [],
};
