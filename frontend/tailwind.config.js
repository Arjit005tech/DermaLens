/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        clinic: {
          bg: "#F7F5F2",
          ink: "#1F2421",
          sage: "#5B7A6B",
          sageDark: "#3E5A4C",
          clay: "#C77B5A",
          line: "#E4E0D8",
        },
      },
      fontFamily: {
        display: ["'Fraunces'", "serif"],
        body: ["'Inter'", "sans-serif"],
      },
    },
  },
  plugins: [],
};
