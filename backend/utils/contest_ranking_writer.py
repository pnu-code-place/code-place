from utils.constants import ContestRuleType

def column_string(n):
    string = ""
    while n > 0:
        n, remainder = divmod(n - 1, 26)
        string = chr(65 + remainder) + string
    return string

def convert_ms_to_time(ms):
    seconds = ms // 1000
    hours = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return f"{hours}시간 {minutes}분 {seconds}초"


class ContestRankingWriter:

    def __init__(self, contest, workbook, worksheet, data, contest_problems, problem_ids):
        self.contest = contest
        self.workbook = workbook
        self.worksheet = worksheet
        self.data = data
        self.contest_problems = contest_problems
        self.problem_ids = problem_ids

    def write_xlsx_common_contest_info(self):
        workbook = self.workbook
        worksheet = self.worksheet
        # write contest info
        contest_title = workbook.add_format({'font_size': 30, 'bold': True})
        worksheet.write("A1", self.contest.title, contest_title)
        contest_type = workbook.add_format({'font_size': 15, 'bold': True})
        worksheet.write("A2", "OI 타입" if self.contest.rule_type == ContestRuleType.OI else "ACM 타입", contest_type)

        contest_other_info = workbook.add_format({'bold': True})
        worksheet.write("A3", "대회 시작 시간", contest_other_info)
        worksheet.write("B3", str(self.contest.start_time), contest_other_info)
        worksheet.write("A4", "대회 종료 시간", contest_other_info)
        worksheet.write("B4", str(self.contest.end_time), contest_other_info)

        ranking_bg = workbook.add_format({'bg_color': '#EEECE2', 'bold': True})
        user_info_bg = workbook.add_format({'bg_color': '#DAE4C0', 'bold': True})
        worksheet.write("A6", "순위", ranking_bg)
        worksheet.write("B6", "닉네임", user_info_bg)
        worksheet.write("C6", "실명", user_info_bg)
        worksheet.write("D6", "이메일", user_info_bg)
        worksheet.write("E6", "단과대학", user_info_bg)
        worksheet.write("F6", "학과명", user_info_bg)
        worksheet.write("G6", "학번", user_info_bg)

    def write_xlsx_acm_ranking(self):
        workbook = self.workbook
        worksheet = self.worksheet

        score_bg = workbook.add_format({'bg_color': '#F6D7B8', 'bold': True})
        worksheet.write("H6", "맞춘 문제 수", score_bg)
        worksheet.write("I6", "총 제출 횟수", score_bg)

        for item in range(self.contest_problems.count()):
            problems_bg = workbook.add_format({'bg_color': '#DEEDF2', 'bold': True})
            worksheet.write(column_string(12 + item) + "6", f"문제 {self.contest_problems[item]._id}번", problems_bg)

        for index, item in enumerate(self.data):
            worksheet.write_string(index + 6, 0, str(index + 1))
            worksheet.write_string(index + 6, 1, item["user"]["username"])
            worksheet.write_string(index + 6, 2, item["user"]["real_name"] or "")
            worksheet.write_string(index + 6, 3, item["user"]["email"] or "")
            worksheet.write_string(index + 6, 4, item["user"]["school"] or "")
            worksheet.write_string(index + 6, 5, item["user"]["major"] or "")
            worksheet.write_string(index + 6, 6, item["user"]["student_id"] or "")

            for k, v in item["submission_info"].items():
                ac_state = "정답" if v["is_ac"] else "오답"
                try:
                    problem_id = self.problem_ids.index(int(k))
                except ValueError:
                    continue
                worksheet.write_string(index + 6, 10 + problem_id, ac_state)

    def write_xlsx_oi_ranking(self):
        workbook = self.workbook
        worksheet = self.worksheet

        total_score_bg = workbook.add_format({'bg_color': '#F6D7B8', 'bold': True})
        worksheet.write("H6", "총점", total_score_bg)
        for item in range(self.contest_problems.count()):
            problems_bg = workbook.add_format({'bg_color': '#DEEDF2', 'bold': True})
            worksheet.write(column_string(10 + item) + "6", f"문제 {self.contest_problems[item]._id}번",
                            problems_bg)
        for index, item in enumerate(self.data):
            worksheet.write_string(index + 6, 0, str(index + 1))
            worksheet.write_string(index + 6, 1, item["user"]["username"])
            worksheet.write_string(index + 6, 2, item["user"]["real_name"] or "")
            worksheet.write_string(index + 6, 3, item["user"]["email"] or "")
            worksheet.write_string(index + 6, 4, item["user"]["school"] or "")
            worksheet.write_string(index + 6, 5, item["user"]["major"] or "")
            worksheet.write_string(index + 6, 6, item["user"]["student_id"] or "")
            worksheet.write_string(index + 6, 7, str(item["total_score"]) + '점')
            for k, v in item["submission_info"].items():
                worksheet.write_string(index + 6, 9 + self.problem_ids.index(int(k)), str(v) + '점')