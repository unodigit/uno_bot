/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#2563EB',
          dark: '#1D4ED8',
        },
        secondary: '#10B981',
        surface: '#F3F4F6',
        text: {
          DEFAULT: '#1F2937',
          muted: '#6B7280',
        },
        border: '#E5E7EB',
        error: '#EF4444',
        success: '#10B981',
        warning: '#F59E0B',
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'sans-serif'],
      },
      fontSize: {
        'xs': ['12px', { lineHeight: '16px' }],
        'sm': ['14px', { lineHeight: '20px' }],
        'base': ['16px', { lineHeight: '24px' }],
        'lg': ['18px', { lineHeight: '28px' }],
        'xl': ['20px', { lineHeight: '28px' }],
        '2xl': ['24px', { lineHeight: '32px' }],
        '3xl': ['30px', { lineHeight: '36px' }],
        '4xl': ['36px', { lineHeight: '40px' }],
      },
      fontWeight: {
        light: '300',
        normal: '400',
        medium: '500',
        semibold: '600',
        bold: '700',
      },
      spacing: {
        'xs': '4px',
        'sm': '8px',
        'md': '16px',
        'lg': '24px',
        'xl': '32px',
      },
      boxShadow: {
        'sm': '0 1px 2px 0 rgb(0 0 0 / 0.05)',
        'md': '0 4px 6px -1px rgb(0 0 0 / 0.1)',
        'lg': '0 10px 15px -3px rgb(0 0 0 / 0.1)',
        'xl': '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
      },
      transitionDuration: {
        '150': '150ms',
        '300': '300ms',
      },
      keyframes: {
        'pulse-subtle': {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.8' },
        },
        'toast-slide-in': {
          '0%': { transform: 'translateY(100%)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        'toast-slide-out': {
          '0%': { transform: 'translateY(0)', opacity: '1' },
          '100%': { transform: 'translateY(100%)', opacity: '0' },
        },
      },
      animation: {
        'pulse-subtle': 'pulse-subtle 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'toast-in': 'toast-slide-in 0.3s ease-out forwards',
        'toast-out': 'toast-slide-out 0.3s ease-in forwards',
      },
    },
  },
  plugins: [
    // Custom scrollbar plugin for consistent styling
    function({ addUtilities }) {
      addUtilities({
        // Screen reader only utility
        '.sr-only': {
          position: 'absolute',
          width: '1px',
          height: '1px',
          padding: '0',
          margin: '-1px',
          overflow: 'hidden',
          clip: 'rect(0, 0, 0, 0)',
          whiteSpace: 'nowrap',
          borderWidth: '0',
        },
        // Not screen reader only (undo sr-only)
        '.not-sr-only': {
          position: 'static',
          width: 'auto',
          height: 'auto',
          padding: '0',
          margin: '0',
          overflow: 'visible',
          clip: 'auto',
          whiteSpace: 'normal',
        },
        // Focus visible utility for better keyboard navigation
        '.focus-visible': {
          outline: '2px solid #2563EB',
          outlineOffset: '2px',
        },
        // Skip to content utility
        '.skip-to-content': {
          position: 'absolute',
          top: '-40px',
          left: '0',
          background: '#2563EB',
          color: 'white',
          padding: '8px',
          textDecoration: 'none',
          zIndex: '100',
        },
        '.skip-to-content:focus': {
          top: '0',
        },
        // Custom scrollbar utilities
        '.scrollbar-thin': {
          scrollbarWidth: 'thin',
          scrollbarColor: '#9CA3AF transparent',
        },
        '.scrollbar-thin::-webkit-scrollbar': {
          width: '6px',
          height: '6px',
        },
        '.scrollbar-thin::-webkit-scrollbar-track': {
          background: 'transparent',
        },
        '.scrollbar-thin::-webkit-scrollbar-thumb': {
          backgroundColor: '#9CA3AF',
          borderRadius: '3px',
        },
        '.scrollbar-thin::-webkit-scrollbar-thumb:hover': {
          backgroundColor: '#6B7280',
        },
        // Custom scrollbar for chat messages (primary color)
        '.scrollbar-primary': {
          scrollbarWidth: 'thin',
          scrollbarColor: '#2563EB transparent',
        },
        '.scrollbar-primary::-webkit-scrollbar': {
          width: '6px',
          height: '6px',
        },
        '.scrollbar-primary::-webkit-scrollbar-track': {
          background: 'transparent',
        },
        '.scrollbar-primary::-webkit-scrollbar-thumb': {
          backgroundColor: '#2563EB',
          borderRadius: '3px',
        },
        '.scrollbar-primary::-webkit-scrollbar-thumb:hover': {
          backgroundColor: '#1D4ED8',
        },
      });
    },
  ],
}
