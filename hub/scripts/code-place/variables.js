const RESULT_CATEGORY = {
  RESULT_ACCEPTED: "Accepted",
};

// Code Place URL
const CODE_PLACE_URL = "https://code.pusan.ac.kr";
// Problem Page URL Regular Expression
const PROBLEM_URL_REGEX = /code\.pusan\.ac\.kr\/problem/;

// Root directory for Code Place solutions
// All solutions will be stored in ${SOLUTIONS_DIRECTORY}/
SOLUTIONS_DIRECTORY = "code_place";
// Summary filename
SUMMARY_FILENAME = "README.md";
// Solution's base filename. Extensions should be added according to the programming language.
// EX) filename = `${SOLUTION_FILENAME}.${LANGUAGES[language]}`
SOLUTION_FILENAME = "solution";

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
