export const DashboardSectionProp = {
  ojStatus: {
    rank_image: "https://cdn-icons-png.flaticon.com/512/473/473406.png", // 랭킹 이미지
    rank: 1, // 랭킹
    rank_percent: 0.1, // 랭킹 퍼센트 ( 상위 10% )
    score: 101, // 종합 점수
    submission_number: 100, // 제출 횟수
    accepted_number: 100, // 맞은 횟수
    total_score: 56000, // 현재 점수
    rank_next: 60000, // 다음 랭킹의 허들
    rank_current: 50000, // 이전 랭킹의 허들
    miracle_current: 10, // 현재 연속 코딩일수
    miracle_record: 20 // 최고 연속 코딩일수
  },

  categoryInfo: {
    data_structure: {
      score: 34,
      ranking: 60,
      ranking_percent: 0.3,
    },
    mathematics: {
      score: 20,
      ranking: 101,
      ranking_percent: 0.505,
    },
    sorting: {
      score: 45,
      ranking: 34,
      ranking_percent: 0.17,
    },
    implementation: {
      score: 61,
      ranking: 20,
      ranking_percent: 0.101,
    },
    searching: {
      score: 3,
      ranking: 190,
      ranking_percent: 0.95,
    }
  },

  difficultyInfo: {
    very_easy: {
      solve_number: 33,
      total_score: 330,
    },
    easy: {
      solve_number: 20,
      total_score: 400,
    },
    medium: {
      solve_number: 10,
      total_score: 800,
    },
    hard: {
      solve_number: 4,
      total_score: 640,
    },
    very_hard: {
      solve_number: 1,
      total_score: 320,
    }
  },
  archives: {
    acquired: [
      {
        id: 1,
        title: "업적",
        image: "https://cdn-icons-png.flaticon.com/512/473/473406.png",
        description: "업적은 아래와 같이 표시됩니다.",
        date: "2019-01-01",
      },
      {
        id: 2,
        title: "업적",
        image: "https://cdn-icons-png.flaticon.com/512/473/473406.png",
        description: "업적은 아래와 같이 표시됩니다.",
        date: "2019-01-01",
      }
    ],
    not_acquired: [
      {
        id: 2,
        title: "업적",
        image: "https://cdn-icons-png.flaticon.com/512/473/473406.png",
        description: "업적은 아래와 같이 표시됩니다.",
        date: "2019-01-01",
      }
    ]
  }
}

export const ProblemSectionProp = {
  ranking_percent: 0.3,
  solved: { // 해결한 문제들을 표시합니다.
    count: 4,
    problems: [
      {
        id: 1001,
        title: 'A+B',
        submitTime: '2021-07-02T08:25:49.443682Z',
        difficulty: 'easy',
      },
      {
        id: 1002,
        title: 'A-B',
        submitTime: '2021-07-02T08:25:49.443682Z',
        difficulty: 'easy',
      },
      {
        id: 1003,
        title: 'A*B',
        submitTime: '2021-07-02T08:25:49.443682Z',
        difficulty: 'easy',
      },
      {
        id: 1004,
        title: 'A/B',
        submitTime: '2021-07-02T08:25:49.443682Z',
        difficulty: 'easy',
      },
    ],
  },
  failed: { // 시도했으나 풀지 못한 문제들을 표시합니다.
    count: 4,
    problems: [
      {
        id: 1001,
        title: 'A+B',
        submitTime: '2021-07-02T08:25:49.443682Z',
        difficulty: 'easy',
      },
      {
        id: 1002,
        title: 'A-B',
        submitTime: '2021-07-02T08:25:49.443682Z',
        difficulty: 'easy',
      },
      {
        id: 1003,
        title: 'A*B',
        submitTime: '2021-07-02T08:25:49.443682Z',
        difficulty: 'easy',
      },
      {
        id: 1004,
        title: 'A/B',
        submitTime: '2021-07-02T08:25:49.443682Z',
        difficulty: 'easy',
      },
    ],
  }
}
