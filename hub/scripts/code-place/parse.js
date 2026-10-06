const FALLBACK_VALUE = "UNKNOWN";

/**
 * Processes parsed problem data and converts it into information needed for file creation
 * @async
 * @param {Object} options - Problem data object
 * @param {string|number} options.problemId - Problem ID
 * @param {string} options.title - Problem title
 * @param {string} [options.status="Accepted"] - Submission status
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
 * @param {string} [options.memoryCost] - Formatted memory cost
 * @param {string} [options.timeCost] - Formatted time cost
 * @returns {Promise<Object>} Object containing information needed for file creation
 */
const makeData = async ({
  problemId,
  title,
  status = "Accepted",
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
  memoryCost,
  timeCost,
}) => {
  const currentDate = getDateString(new Date(Date.now()));
  const directory = `${SOLUTIONS_DIRECTORY}/[${problemId}] ${title}`;

  const summaryFileName = `${SUMMARY_FILENAME}`;
  const ext = LANGUAGE_EXTENSIONS[language] || "txt";
  const sourceCodeFileName = `${SOLUTION_FILENAME}.${ext}`;
  const commitMessage = currentDate;

  // Formatting sample input & output
  const formatSamples = (inputs, outputs) => {
    let result = [];
    const inList = Array.isArray(inputs) ? inputs : [];
    const outList = Array.isArray(outputs) ? outputs : [];
    const maxExamples = Math.max(inList.length, outList.length);
    for (let i = 0; i < maxExamples; i++) {
      const input = inList[i] || FALLBACK_VALUE;
      const output = outList[i] || FALLBACK_VALUE;

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

  // Create Summary Content
  const hasPerf = Boolean(memoryCost && timeCost);
  const summary = [
    `# [${problemId}] ${title}`,
    `### 채점 결과`,
    `${status}`,
    `### 제출 일자`,
    `${currentDate}`,
    hasPerf ? `### 성능 요약` : `### 성능 요약[추후 구현 예정]`,
    `- 메모리: ${memoryCost || "N/A KB"}`,
    `- 시간: ${timeCost || "N/A ms"}`,
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
    hint && hint !== FALLBACK_VALUE ? `### 힌트\n${hint}\n` : "",
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
