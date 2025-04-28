const RESULT_CATEGORY = {
  RESULT_ACCEPTED: "Accepted",
};

// Code Place URL
const CODE_PLACE_URL = "https://code.pusan.ac.kr";
// Problem Page URL Regular Expression
// PROBLEM_URL_REGEX.test('code.pusan.ac.kr/problem/231) - True (문제 풀이 페이지에서는 실행됨)
// PROBLEM_URL_REGEX.test('code.pusan.ac.kr/problem) - False (문제 리스트 페이지에서는 실행되지 않음)
const PROBLEM_URL_REGEX = /code\.pusan\.ac\.kr\/problem\/\d+/;

// Root directory for Code Place solutions
// All solutions will be stored in ${SOLUTIONS_DIRECTORY}/
const SOLUTIONS_DIRECTORY = "code_place";
// Summary filename
const SUMMARY_FILENAME = "README.md";
// Solution's base filename. Extensions should be added according to the programming language.
// EX) filename = `${SOLUTION_FILENAME}.${LANGUAGES[language]}`
const SOLUTION_FILENAME = "solution";

// prettier-ignore
// Mapper between Language - File Extension
const LANGUAGE_EXTENSIONS = {
  'C': "c",
  "C++": "cpp",
  "Golang": "go",
  "Java": "java",
  "Javascript": "js",
  "Python3": "py"
}
