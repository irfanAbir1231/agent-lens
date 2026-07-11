import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        ink: "#14213d",
        canvas: "#f4f6f8",
      },
      boxShadow: {
        panel: "0 1px 2px rgba(15, 23, 42, 0.05)",
      },
    },
  },
  plugins: [],
};

export default config;
