const FALLBACK_VALUE = "UNKNOWN";
const CODE_PLACE_URL = "https://code.pusan.ac.kr";

// Helper function returning value of an element safely
const getElementText = (selector, defaultValue = FALLBACK_VALUE) => {
  try {
    const element = document.querySelector(selector);
    return element ? element.textContent.trim() : defaultValue;
  } catch {
    return defaultValue;
  }
};

// Helper function returning values of multiple elements safely
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

const makeData = async ({
  problemId,
  title,
  status,
  difficulty,
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
  // Set Directory name as problem ID
  const directory = `${problemId}/${title}`;
  const commitMessage = currentDate;

  // 입출력 예제 포맷팅
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

  // README 내용 구성
  // TODO: 성능 요약 데이터 추출
  const readme = [
    `# [${problemId}] ${title}`,
    `### 채점 결과`,
    `${status}`,
    `## 제출 일자`,
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
    hint !== FALLBACK_VALUE ? `## 힌트\n${hint}\n` : "",
    `## 제약 사항`,
    `- ${timeLimit}`,
    `- ${memoryLimit}`,
  ]
    .filter(Boolean)
    .join("\n");

  console.log(readme);

  return { problemId, commitMessage, directory, readme, code };
};
