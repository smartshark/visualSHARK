module.exports = {
  root: true,
  env: {
    node: true
  },
  'extends': [
    'plugin:vue/essential',
    'eslint:recommended'
  ],
  rules: {
    'no-console': process.env.NODE_ENV === 'production' ? 'error' : 'off',
    'no-debugger': process.env.NODE_ENV === 'production' ? 'error' : 'off',
    'vue/require-prop-type-constructor': 'off',
    'vue/require-v-for-key': 'off',
    'vue/no-mutating-props': 'off',
    'no-console': 'off'
  },
  parserOptions: {
    parser: 'babel-eslint'
  }
}
