export const ojStatisticalData = {

  graph: {
    dataStructure: 0.4,
    searching: 0.8,
    mathematics: 0.4,
    sorting: 0.2,
    implementation: 0.6,
  },

  table: {
    dataStructure: {
      veryEasy: 0.9,
      easy: 0.8,
      medium: 0.6,
      hard: 0.3,
      veryHard: 0.1,
      myProgress: 0.4,
      averageProgress: 0.6,
      myRank: 'A',
    },
    searching: {
      veryEasy: 0.9,
      easy: 0.8,
      medium: 0.6,
      hard: 0.3,
      veryHard: 0.1,
      myProgress: 0.4,
      averageProgress: 0.6,
      myRank: 'A',
    },
    mathematics: {
      veryEasy: 0.9,
      easy: 0.8,
      medium: 0.6,
      hard: 0.3,
      veryHard: 0.1,
      myProgress: 0.4,
      averageProgress: 0.6,
      myRank: 'A',
    },
    sorting: {
      veryEasy: 0.9,
      easy: 0.8,
      medium: 0.6,
      hard: 0.3,
      veryHard: 0.1,
      myProgress: 0.4,
      averageProgress: 0.6,
      myRank: 'A',
    },
    implementation: {
      veryEasy: 0.9,
      easy: 0.8,
      medium: 0.6,
      hard: 0.3,
      veryHard: 0.1,
      myProgress: 0.4,
      averageProgress: 0.6,
      myRank: 'A',
    },
  }
}

let problemId = 0;

const problemTitles20 = [
  "두 수의 합 (Two Sum)",
  "정수 뒤집기 (Reverse Integer)",
  "로마 숫자를 정수로 변환 (Roman to Integer)",
  "가장 긴 공통 접두사 (Longest Common Prefix)",
  "올바른 괄호 (Valid Parentheses)",
  "두 정렬된 리스트의 병합 (Merge Two Sorted Lists)",
  "정렬된 배열에서 중복 제거 (Remove Duplicates from Sorted Array)",
  "문자열에서 부분 문자열 찾기 (Implement strStr())",
  "팰린드롬 숫자 (Palindrome Number)",
  "물의 양이 가장 많은 컨테이너 (Container With Most Water)",
  "이진 트리의 최대 깊이 (Maximum Depth of Binary Tree)",
  "두 정렬된 배열의 중앙 값 (Median of Two Sorted Arrays)",
  "전위 표기식을 후위 표기식으로 변환 (Convert Preorder to Postorder Expression)",
  "유효한 소괄호 문자열 (Valid Parenthesis String)",
  "삼각형에서 최소 경로 합 (Triangle Minimum Path Sum)",
  "배열에서 반복되지 않는 첫 번째 정수 찾기 (First Non-Repeating Integer in an Array)",
  "두 정수의 최대 공약수 (Greatest Common Divisor of Two Integers)",
  "문자열 압축 (String Compression)",
  "뒤집힌 단어순서로 문장 구성 (Reverse Words in a Sentence)",
  "두 개의 정렬된 배열의 중앙값 (Median of Two Sorted Arrays)"
];

const problemTitles10 = [
  "소수 판별 (Check Prime Number)",
  "배열 회전 (Rotate Array)",
  "최대 서브배열 합 (Maximum Subarray Sum)",
  "이진 검색 (Binary Search)",
  "팩토리얼 계산 (Factorial Calculation)",
  "최대 공통 부분 문자열 (Longest Common Substring)",
  "순열 생성 (Generate Permutations)",
  "그래프 경로 찾기 (Find Path in a Graph)",
  "비트 조작 (Bit Manipulation)",
  "숫자의 자릿수 합 구하기 (Sum of Digits)"
];

const makeProblem = (title) => {
  const field = (Math.floor(Math.random() * 5) + 1).toString();
  const difficulty = (Math.floor(Math.random() * 5) + 1).toString();
  problemId += 1
  // 시간은 오늘로부터 1년 이내의 랜덤한 시간으로 설정
  const submitTime = new Date(Date.now() - Math.floor(Math.random() * 31536000000));
  return {
    id: problemId, // Integer
    field: field, // '0'~'5' 의 문자열
    title: title, // String
    difficulty: difficulty, // '0'~'5' 의 문자열
    submitTime: submitTime // Date ex : 2019-01-01T00:00:00.000Z
  }
}

// makeProblem을 이용하여 문제 목록을 생성
export const solvedProblems = problemTitles10.map(makeProblem);
export const failedProblems = problemTitles20.map(makeProblem);

export const userProblemData = {
  solved: {
    amount: 10,
    problems: solvedProblems
  },
  failed: {
    amount: 20,
    problems: failedProblems
  }
}
