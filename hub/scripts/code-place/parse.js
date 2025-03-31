const FALLBACK_VALUE = "UNKNOWN";

/**
 * Safely retrieves the text content of an element matching the selector
 * @param {string} selector - CSS selector to find the element
 * @param {string} [defaultValue=FALLBACK_VALUE] - Default value to return if element is not found
 * @returns {string} Text content of the element or default value
 */
const getElementText = (selector, defaultValue = FALLBACK_VALUE) => {
  try {
    const element = document.querySelector(selector);
    return element ? element.textContent.trim() : defaultValue;
  } catch {
    return defaultValue;
  }
};

/**
 * Safely retrieves the text content of multiple elements matching the selector
 * @param {string} selector - CSS selector to find elements
 * @param {Array} [defaultValue=[]] - Default value to return if no elements are found
 * @returns {Array<string>} Array of text content from elements or default value
 */
const getElementsText = (selector, defaultValue = []) => {
  try {
    const elements = document.querySelectorAll(selector);
    return elements.length > 0
      ? Array.from(elements).map((elem) => elem.textContent.trim())
      : defaultValue;
  } catch {
    return defaultValue;
  }
};

/**
 * Parses problem data from the webpage
 * @async
 * @returns {Promise<Object>} The parsed problem data processed by makeData function
 */
const parseData = async () => {
  // Parsing Problem Title
  const fullTitle = getElementText('[id^="problem-title"]');
  let problemId = FALLBACK_VALUE;
  let title = FALLBACK_VALUE;

  const firstDotIdx = fullTitle.indexOf(". ");
  if (firstDotIdx !== -1) {
    problemId = fullTitle.substring(0, firstDotIdx).trim() || FALLBACK_VALUE;
    title = fullTitle.substring(firstDotIdx + 2).trim() || FALLBACK_VALUE;
  }

  const status = getElementText(".submissionState");
  const difficulty = getElementText('[id^="problem-difficulty-"]');
  const description = getElementText('[id^="problem-description-"]');
  const language = getElementText('[id^="code-language-"]');
  const inputDescription = getElementText('[id^="problem-input-desc-"]');
  const outputDescription = getElementText('[id^="problem-output-desc-"]');
  const inputSample = getElementsText('[id^="problem-sample-input-"]');
  const outputSample = getElementsText('[id^="problem-sample-output-"]');
  const timeLimit = getElementText('[id^="problem-time-limit-"]');
  const memoryLimit = getElementText('[id^="problem-memory-limit-"]');
  const hint = getElementText('[id^="problem-hint-"]');

  // Parsing Code
  const codeLines = document.querySelectorAll(".CodeMirror-line");
  const lines = Array.from(codeLines).map((line) => line.textContent);
  const code = lines.join("\n");

  return makeData({
    problemId,
    title,
    status,
    difficulty,
    language,
    description,
    inputDescription,
    outputDescription,
    inputSample,
    outputSample,
    timeLimit,
    memoryLimit,
    hint,
    code,
  });
};

/**
 * Processes parsed problem data and converts it into information needed for file creation
 * @async
 * @param {Object} options - Problem data object
 * @param {string} options.problemId - Problem ID
 * @param {string} options.title - Problem title
 * @param {string} options.status - Submission status
 * @param {string} options.difficulty - Problem difficulty
 * @param {string} options.language - Code Language
 * @param {string} options.description - Problem description
 * @param {string} options.inputDescription - Input description
 * @param {string} options.outputDescription - Output description
 * @param {Array<string>} options.inputSample - Array of example inputs
 * @param {Array<string>} options.outputSample - Array of example outputs
 * @param {string} options.timeLimit - Time limit
 * @param {string} options.memoryLimit - Memory limit
 * @param {string} options.hint - Problem hint
 * @param {string} options.code - Submitted code
 * @returns {Promise<Object>} Object containing information needed for file creation
 */
const makeData = async ({
  problemId,
  title,
  status,
  difficulty,
  language,
  description,
  inputDescription,
  outputDescription,
  inputSample,
  outputSample,
  timeLimit,
  memoryLimit,
  hint,
  code,
}) => {
  const currentDate = getDateString(new Date(Date.now()));
  const directory = `${SOLUTIONS_DIRECTORY}/[${problemId}] ${title}`;

  const summaryFileName = `${SUMMARY_FILENAME}`;
  const sourceCodeFileName = `${SOLUTION_FILENAME}.${LANGUAGE_EXTENSIONS[language]}`;
  const commitMessage = currentDate;

  // Formatting sample input & output
  const formatSamples = (inputs, outputs) => {
    let result = [];

    const maxExamples = Math.max(inputs.length, outputs.length);
    for (let i = 0; i < maxExamples; i++) {
      const input = inputs[i] || FALLBACK_VALUE;
      const output = outputs[i] || FALLBACK_VALUE;

      result.push(`**예제 입력 ${i + 1}**`);
      result.push("```");
      result.push(input);
      result.push("```");
      result.push(`**예제 출력 ${i + 1}**`);
      result.push("```");
      result.push(output);
      result.push("```");
    }

    return result.join("\n");
  };

  // Create README.md
  // TODO: Implement Performance Analytics
  const summary = [
    `# [${problemId}] ${title}`,
    `### 채점 결과`,
    `${status}`,
    `### 제출 일자`,
    `${currentDate}`,
    `### 성능 요약[추후 구현 예정]`,
    `- 메모리: N/A KB`,
    `- 시간: N/A ms`,
    "---",
    `### 문제 링크`,
    `${CODE_PLACE_URL}/problem/${problemId}`,
    `### 난이도`,
    `${difficulty}`,
    `### 문제 설명`,
    description,
    `### 입력`,
    inputDescription,
    `### 출력`,
    outputDescription,
    `### 예제 입력/출력`,
    formatSamples(inputSample, outputSample),
    hint !== FALLBACK_VALUE ? `### 힌트\n${hint}\n` : "",
    `### 제약 사항`,
    `- ${timeLimit}`,
    `- ${memoryLimit}`,
  ]
    .filter(Boolean)
    .join("\n");

  log(summary);

  return {
    problemId,
    commitMessage,
    directory,
    summaryFileName,
    sourceCodeFileName,
    summary,
    code,
  };
};
