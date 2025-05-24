export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        primary: '#6366F1',        // Indigo (main brand color)
        secondary: '#7C3AED',      // Purple
        accent: '#0EA5E9',         // Light Blue
        background: '#F0F4FF',     // Soft blue-gray
        card: '#FFFFFF',
      },
      fontFamily: {
        display: ['Poppins', 'sans-serif'],
        body: ['Inter', 'sans-serif']
      },
      boxShadow: {
        card: '0 8px 20px rgba(99, 102, 241, 0.1)',  // blueish glow
      },
      borderRadius: {
        xl: '1rem',
        '2xl': '1.5rem'
      }
    }
  },
  plugins: [],
}
