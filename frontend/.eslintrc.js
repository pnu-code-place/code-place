module.exports = {
  root: true,
  // 각 환경의 전역 변수 인식
  env: {
    browser: true, // for browser
    node: true, // for node.js
  },
  parser: "vue-eslint-parser",
  parserOptions: {
    parser: "babel-eslint",
    sourceType: "module",
  },
  // Apply external rule-sets
  extends: ["eslint:recommended", "plugin:vue/essential", "prettier"],
  // Vue 파일 지원 ESLint 확장플러그인 등록
  plugins: ["vue"],
  // add your custom rules here
  rules: {
    // allow paren-less arrow functions
    "arrow-parens": 0,
    // allow async-await
    "generator-star-spacing": 0,
    // allow debugger during development
    "no-debugger": process.env.NODE_ENV === "production" ? 2 : 0,
    "no-irregular-whitespace": [
      "error",
      {
        skipComments: true,
        skipTemplates: true,
      },
    ],
    "no-unused-vars": ["warn"],
    quotes: ["off", "single"],
  },
}
