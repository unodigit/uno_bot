export default [
  {
    files: ['**/*.{ts,tsx}'],
    languageOptions: {
      ecmaVersion: 2020,
      sourceType: 'module',
      globals: {
        browser: true,
        node: true,
      },
    },
    plugins: {
      reactHooks: require('eslint-plugin-react-hooks'),
      reactRefresh: require('eslint-plugin-react-refresh'),
    },
    rules: {
      'react-refresh/only-export-components': [
        'warn',
        { allowConstantExport: true },
      ],
    },
  },
]
