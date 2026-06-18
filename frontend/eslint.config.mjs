import babelParser from "@babel/eslint-parser"
import js from "@eslint/js"
import prettier from "eslint-config-prettier"
import vue from "eslint-plugin-vue"
import globals from "globals"
import vueParser from "vue-eslint-parser"

const parserOptions = {
  babelOptions: {
    babelrc: false,
    configFile: false,
  },
  ecmaVersion: "latest",
  requireConfigFile: false,
  sourceType: "module",
}

export default [
  {
    ignores: ["dist/**", "node_modules/**", "static/**"],
  },
  js.configs.recommended,
  ...vue.configs["flat/vue2-essential"],
  {
    files: ["src/**/*.js"],
    languageOptions: {
      globals: {
        ...globals.browser,
        ...globals.node,
      },
      parser: babelParser,
      parserOptions,
    },
  },
  {
    files: ["src/**/*.vue"],
    languageOptions: {
      globals: {
        ...globals.browser,
        ...globals.node,
      },
      parser: vueParser,
      parserOptions: {
        ...parserOptions,
        parser: babelParser,
      },
    },
  },
  {
    files: ["src/**/*.{js,vue}"],
    rules: {
      "arrow-parens": 0,
      "generator-star-spacing": 0,
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
  },
  prettier,
]
