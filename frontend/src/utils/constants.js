import i18n from "@/i18n";

export const JUDGE_COLOR = {
  WRONG: {
    color: "#ffd025",
    textColor: "#ffffff",
  },
  CORRECT: {
    color: "#1abe6b",
    textColor: "#ffffff",
  },
  PENDING: {
    color: "#ffb574",
    textColor: "#ffffff",
  },
  ERROR: {
    color: "#ed3f13",
    textColor: "#ffffff",
  },
};

export const JUDGE_STATUS = {
  "-2": {
    name: "Compile Error",
    short: "CE",
    ...JUDGE_COLOR.ERROR,
  },
  "-1": {
    name: "Wrong Answer",
    short: "WA",
    ...JUDGE_COLOR.WRONG,
  },
  0: {
    name: "Accepted",
    short: "AC",
    ...JUDGE_COLOR.CORRECT,
  },
  1: {
    name: "Time Limit Exceeded",
    short: "TLE",
    ...JUDGE_COLOR.WRONG,
  },
  2: {
    name: "Time Limit Exceeded",
    short: "TLE",
    ...JUDGE_COLOR.WRONG,
  },
  3: {
    name: "Memory Limit Exceeded",
    short: "MLE",
    ...JUDGE_COLOR.WRONG,
  },
  4: {
    name: "Runtime Error",
    short: "RE",
    ...JUDGE_COLOR.ERROR,
  },
  5: {
    name: "System Error",
    short: "SE",
    ...JUDGE_COLOR.ERROR,
  },
  6: {
    name: "Pending",
    color: "yellow",
    ...JUDGE_COLOR.PENDING,
  },
  7: {
    name: "Judging",
    color: "blue",
    type: "info",
  },
  8: {
    name: "Partial Accepted",
    short: "PAC",
    ...JUDGE_COLOR.WRONG,
  },
  9: {
    name: "Submitting",
    color: "yellow",
    ...JUDGE_COLOR.PENDING,
  },
};

export const CONTEST_STATUS = {
  NOT_START: "1",
  UNDERWAY: "0",
  ENDED: "-1",
};

export const CONTEST_STATUS_REVERSE = {
  1: {
    name: i18n.t("m.Contest_Status_Not_Started"),
    color: "#F0A615",
  },
  0: {
    name: i18n.t("m.Contest_Status_Underway"),
    color: "#45DB78",
  },
  "-1": {
    name: i18n.t("m.Contest_Status_Ended"),
    color: "red",
  },
};

export const RULE_TYPE = {
  ACM: "ACM",
  OI: "OI",
};

export const CONTEST_TYPE = {
  PUBLIC: "Public",
  PRIVATE: "Password Protected",
};

export const USER_TYPE = {
  REGULAR_USER: "Regular User",
  ADMIN: "Admin",
  SUPER_ADMIN: "Super Admin",
};

export const PROBLEM_PERMISSION = {
  NONE: "None",
  OWN: "Own",
  ALL: "All",
};

export const STORAGE_KEY = {
  AUTHED: "authed",
  PROBLEM_CODE: "problemCode",
  languages: "languages",
};

export const DIFFICULTY_MAP = {
  VeryLow: {
    value: "매우 쉬움",
    textColor: "#95ef4c",
  },
  Low: {
    value: "쉬움",
    textColor: "#B5EAB0",
  },
  Mid: {
    value: "보통",
    textColor: "#7c7878",
  },
  High: {
    value: "어려움",
    textColor: "#ff8828",
  },
  VeryHigh: {
    value: "매우 어려움",
    textColor: "#c02b2b",
  },
};

export const FIELD_MAP = {
  0: {
    value: "구현",
    boxColor: "#F8D093",
    backgroundImage: require("../assets/fieldBackground/implement.svg"),
    maxScore: 25600,
  },
  1: {
    value: "수학",
    boxColor: "#B5EAB0",
    backgroundImage: require("../assets/fieldBackground/math.svg"),
    maxScore: 25600,
  },
  2: {
    value: "자료구조",
    boxColor: "#F8B193",
    backgroundImage: require("../assets/fieldBackground/datastructure.svg"),
    maxScore: 25600,
  },
  3: {
    value: "탐색",
    boxColor: "#90B8E7",
    backgroundImage: require("../assets/fieldBackground/search.svg"),
    maxScore: 25600,
  },
  4: {
    value: "정렬",
    boxColor: "#d9c9ea",
    backgroundImage: require("../assets/fieldBackground/sort.svg"),
    maxScore: 25600,
  },
  5: {
    value: "알고리즘",
    boxColor: "#facbcb",
    backgroundImage: require("../assets/fieldBackground/algorithm.svg"),
    maxScore: 25600,
  },
};

export const TierImageSrc = {
  //unranked
  sprout: require("@/assets/tiers/unranked/sprout.svg"),

  //bronze
  bronze1: require("@/assets/tiers/bronze/bronze1.svg"),
  bronze2: require("@/assets/tiers/bronze/bronze2.svg"),
  bronze3: require("@/assets/tiers/bronze/bronze3.svg"),

  //silver
  silver1: require("@/assets/tiers/silver/silver1.svg"),
  silver2: require("@/assets/tiers/silver/silver2.svg"),
  silver3: require("@/assets/tiers/silver/silver3.svg"),

  //gold
  gold1: require("@/assets/tiers/gold/gold1.svg"),
  gold2: require("@/assets/tiers/gold/gold2.svg"),
  gold3: require("@/assets/tiers/gold/gold3.svg"),

  //platinum
  platinum1: require("@/assets/tiers/platinum/platinum1.svg"),
  platinum2: require("@/assets/tiers/platinum/platinum2.svg"),
  platinum3: require("@/assets/tiers/platinum/platinum3.svg"),

  //diamond
  diamond1: require("@/assets/tiers/diamond/diamond1.svg"),
  diamond2: require("@/assets/tiers/diamond/diamond2.svg"),
  diamond3: require("@/assets/tiers/diamond/diamond3.svg"),
};

export const FamilySiteContentSrc = {
  sw_convergence: {
    "src": require("@/assets/familyContents/micon_0.svg"),
    "banner_name": "부산대학교:소프트웨어융합교육원",
    "url": "https://swedu.pusan.ac.kr/"
  },
  sw_support: {
    "src": require("@/assets/familyContents/micon_1.svg"),
    "banner_name": "부산대학교:학생지원시스템",
    "url": "https://onestop.pusan.ac.kr/"
  },
  sw_plato: {
    "src": require("@/assets/familyContents/micon_2.svg"),
    "banner_name": "스마트교육플랫폼:PLATO",
    "url": "https://plato.pusan.ac.kr/"
  },
  sw_edwith: {
    "src": require("@/assets/familyContents/micon_3.svg"),
    "banner_name": "온라인강좌:인프런",
    "url": "https://inflearn.com/users/1370319"
  },
  sw_css: {
    "src": require("@/assets/familyContents/micon_4.svg"),
    "banner_name": "부산대학교:SW역량지원시스템",
    "url": "https://swcss.pusan.ac.kr/"
  },
};

export const LanguageImageSrc = {
  'C++' : require('@/assets/languages/cpp.png'),
  'Java' : require('@/assets/languages/java.png'),
  'Python3' : require('@/assets/languages/python.png'),
  'C' : require('@/assets/languages/c.png'),
  'JavaScript' : require('@/assets/languages/javascript.png'),
  'undefined' : require('@/assets/languages/c.png'),
};

export const AwardImageSrc = {
  1: require("@/assets/awards/first.svg"),
  2: require("@/assets/awards/second.svg"),
  3: require("@/assets/awards/third.svg"),
};

export function getTierImageSrc(tier) {
  return TierImageSrc[tier];
}

export function getAwardImageSrc(rank) {
  return AwardImageSrc[rank];
}

export function buildProblemCodeKey(problemID, contestID = null) {
  if (contestID) {
    return `${STORAGE_KEY.PROBLEM_CODE}_${contestID}_${problemID}`;
  }
  return `${STORAGE_KEY.PROBLEM_CODE}_NaN_${problemID}`;
}

export const GOOGLE_ANALYTICS_ID = "UA-111499601-1";

export const MONTH = {
  JAN: {
    name: i18n.t("m.JAN"),
    number: 1,
  },
  FEB: {
    name: i18n.t("m.FEB"),
    number: 2,
  },
  MAR: {
    name: i18n.t("m.MAR"),
    number: 3,
  },
  APR: {
    name: i18n.t("m.APR"),
    number: 4,
  },
  MAY: {
    name: i18n.t("m.MAY"),
    number: 5,
  },
  JUN: {
    name: i18n.t("m.JUN"),
    number: 6,
  },
  JUL: {
    name: i18n.t("m.JUL"),
    number: 7,
  },
  AUG: {
    name: i18n.t("m.AUG"),
    number: 8,
  },
  SEP: {
    name: i18n.t("m.SEP"),
    number: 9,
  },
  OCT: {
    name: i18n.t("m.OCT"),
    number: 10,
  },
  NOV: {
    name: i18n.t("m.NOV"),
    number: 11,
  },
  DEC: {
    name: i18n.t("m.DEC"),
    number: 12,
  },
};

export const LANGUAGE_INFO = [
  {
    name: "C",
    image: require("@/assets/languages/c.png"),
    description: "C 언어는 1970년대 초반에 벨 연구소의 데니스 리치와 브라이언 커니핸이 개발한 프로그래밍 언어입니다. " +
      "시스템 소프트웨어, 운영체제(특히 유닉스), 임베디드 시스템, 컴파일러 개발 등 다양한 분야에서 사용됩니다. " +
      "C 언어는 저수준 메모리 조작이 가능하고, 효율성과 속도가 뛰어나며, 하드웨어에 가까운 작업을 수행하는 데 적합합니다. " +
      "또한, 다른 많은 프로그래밍 언어(C++, C#, 자바 등)의 기초가 되는 중요한 언어로 널리 알려져 있습니다." +
      " C 언어는 간결하고 강력한 구조를 가지고 있어, 배우기 쉽고 활용도가 높습니다.",
    lectures: [
      "프로그래밍원리와실습",
      "유닉스기초",
      "임베디드시스템",
      "임베디드시스템설계및실험",
      "어드벤처디자인"
    ],
    tags: ["C언어", "C프로그래밍", "시스템프로그래밍"]
  },
  {
    name: "C++",
    image: require("@/assets/languages/cpp.png"),
    description: "C++는 1980년대 초반에 벨 연구소의 비야네 스트롭스트룹이 C 언어를 기반으로 개발한 객체 지향 프로그래밍 언어입니다. " +
      "C++는 C 언어의 절차적 프로그래밍 기능에 클래스와 객체를 도입하여 코드 재사용성과 유연성을 높였습니다. " +
      "C++는 시스템 소프트웨어, 게임 개발, 그래픽, 금융 애플리케이션, 실시간 시뮬레이션 등 다양한 분야에서 사용됩니다. " +
      "다중 상속, 템플릿, 예외 처리와 같은 고급 기능을 제공하며, 저수준 메모리 조작도 지원합니다. " +
      "C++는 성능과 효율성을 중시하는 응용 프로그램 개발에 강점을 가지고 있으며, C와의 호환성도 뛰어납니다.",
    lectures: [
      "C++프로그래밍과실습",
      "자료구조"
    ]
  },
  {
    name: "Java",
    image: require("@/assets/languages/java.png"),
    description: "Java는 1995년 썬 마이크로시스템즈(현재는 오라클)에서 개발한 객체 지향 프로그래밍 언어입니다. " +
      "\"한 번 작성하면 어디서나 실행된다\"는 철학을 기반으로, JVM(Java Virtual Machine) 위에서 실행되어 플랫폼 독립성을 제공합니다. " +
      "Java는 안정성과 확장성이 뛰어나고, 대규모 엔터프라이즈 애플리케이션, 웹 애플리케이션, 모바일 애플리케이션(Android) 등 다양한 분야에서 사용됩니다. " +
      "풍부한 표준 라이브러리와 강력한 개발 도구를 갖추고 있으며, 쓰레딩, 메모리 관리, 네트워킹 등 강력한 기능을 지원합니다. " +
      "코드의 가독성과 유지보수성이 높아, 교육용 언어로도 널리 사용됩니다.",
    lectures: [
      "플랫폼기반프로그래밍"
    ]
  },
  {
    name: "Python",
    image: require("@/assets/languages/python.png"),
    description: "Python은 1991년 네덜란드의 귀도 반 로섬이 개발한 고급 프로그래밍 언어로, 간결하고 읽기 쉬운 문법을 가지고 있습니다. " +
      "Python은 다양한 프로그래밍 패러다임(객체 지향, 절차적, 함수형 프로그래밍)을 지원하며, 동적 타입과 자동 메모리 관리 기능을 제공합니다. " +
      "웹 개발, 데이터 과학, 인공지능, 자동화, 스크립트 작성 등 여러 분야에서 널리 사용됩니다. " +
      "풍부한 표준 라이브러리와 강력한 서드파티 패키지 생태계 덕분에 빠른 개발과 유지보수가 용이합니다. " +
      "또한, 플랫폼 독립적이며, 초보자와 전문가 모두에게 적합한 언어로 평가받고 있습니다.",
    lectures: [
      "컴퓨터및프로그래밍입문",
      "데이터과학입문",
      "AI프로그래밍",
      "인공지능",
      "머신러닝"
    ]
  },
  {
    name: "JavaScript",
    image: require("@/assets/languages/javascript.png"),
    description: "JavaScript는 1995년 넷스케이프의 브렌던 아이크가 개발한 프로그래밍 언어로, 주로 웹 브라우저에서 동작하는 스크립트 언어입니다. " +
      "JavaScript는 동적이고 인터랙티브한 웹 페이지를 만들기 위해 사용되며, HTML과 CSS와 함께 웹 개발의 핵심 요소 중 하나입니다. " +
      "클라이언트 측에서 실행되지만, Node.js와 같은 런타임 환경을 통해 서버 측 프로그래밍에도 사용됩니다. " +
      "JavaScript는 이벤트 기반 프로그래밍, 비동기 처리, JSON 데이터 처리 등의 기능을 제공하여, 웹 애플리케이션, 게임 개발, 모바일 앱 개발 등에 널리 활용됩니다. " +
      "최신 프레임워크와 라이브러리(React, Angular, Vue.js 등)의 등장으로 JavaScript의 활용 범위가 더욱 확장되었습니다.",
    lectures: [
      "인터넷과웹기초",
      "웹응용프로그래밍",
      "컴퓨터그래픽스(WebGL)",
    ]
  }
]

export const TIER_SCORE= [
  {
    name: "sprout",
    score: {
      1: 0,
    },
    imageSrc: TierImageSrc.sprout
  },
  {
    name: "Bronze",
    score: {
      3 : 100,
      2 : 300,
      1 : 500,
    },
    imageSrc: TierImageSrc.bronze1
  },
  {
    name: "Silver",
    score: {
      3 : 700,
      2 : 1100,
      1 : 1500
    },
    imageSrc: TierImageSrc.silver1
  },
  {
    name: "Gold",
    score : {
      3: 1900,
      2: 3500,
      1: 5100,
    },
    imageSrc: TierImageSrc.gold1
  },
  {
    name: "Platinum",
    score : {
      3: 6700,
      2: 13100,
      1: 19500,
    },
    imageSrc: TierImageSrc.platinum1
  },
  {
    name: "Diamond",
    score: {
      3: 25900,
      2: 38700,
      1: 51500,
    },
    imageSrc: TierImageSrc.diamond1
  },
]
