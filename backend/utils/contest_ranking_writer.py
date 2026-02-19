from problem.models import Problem
from utils.constants import ContestRuleType
from utils.shortcuts import column_string
import io
import xlsxwriter
import string


class ContestRankingWriter:

    def __init__(self, contest, data):
        self.contest = contest
        self.workbook = None
        self.worksheet = None
        self.data = data
        self.contest_problems = Problem.objects.filter(contest=self.contest, visible=True).order_by("_id")
        self.problem_ids = [item.id for item in self.contest_problems]
        self.__xlsx_style_format = {
            "contest_title": {
                'font_size': 30,
                'bold': True
            },
            "contest_type": {
                'font_size': 15,
                'bold': True
            },
            "contest_other_info": {
                'bold': True
            },
            "common_info": {
                'bg_color': '#DAE4C0',
                'bold': True
            },
            "problem_name": {
                'bg_color': '#DEEDF2',
                'bold': True
            },
            "contest_score": {
                'bg_color': '#F6D7B8',
                'bold': True
            },
        }
        self.common_participant_info_tag = ["순위", "닉네임", "실명", "이메일", "단과대학", "학과명", "학번"]
        self.table_start_pos_y = "7"    # 대회 결과 테이블이 작성되기 시작하는 row number

    @staticmethod
    def get_ac_state_name(is_ac):
        return "정답" if is_ac else ""

    def create_csv(self):
        """
        대회 결과 csv 파일을 생성합니다.
        """
        f = io.BytesIO()

        self.workbook = xlsxwriter.Workbook(f)
        self.worksheet = self.workbook.add_worksheet()

        self.write_contest_ranking_sheet_header()
        self.write_contest_result_table()

        self.worksheet.autofit()
        self.workbook.close()

        f.seek(0)
        return f

    def write_common_user_info_table_header(self):
        common_info_format = self.workbook.add_format(self.__xlsx_style_format["common_info"])
        pos_x_range = len(self.common_participant_info_tag)
        pos_x_list = list(string.ascii_uppercase)[:pos_x_range]
        for i in range(pos_x_range):
            position = pos_x_list[i] + self.table_start_pos_y
            self.worksheet.write(position, self.common_participant_info_tag[i], common_info_format)
        return pos_x_range

    def write_contest_ranking_sheet_header(self):
        """ 대회 성적표의 아래 내용을 포함한 머릿말을 작성합니다.
        - 대회 이름
        - 대회 타입
        - 대회 시작 및 종료 시간
        """
        contest_title_format = self.workbook.add_format(self.__xlsx_style_format["contest_title"])
        contest_type_format = self.workbook.add_format(self.__xlsx_style_format["contest_type"])
        contest_other_info_format = self.workbook.add_format(self.__xlsx_style_format["contest_other_info"])
        contest_type = f"{self.contest.rule_type} 타입"

        self.worksheet.write("A1", self.contest.title, contest_title_format)
        self.worksheet.write("A2", contest_type, contest_type_format)
        self.worksheet.write("A3", "대회 시작 시간", contest_other_info_format)
        self.worksheet.write("A4", "대회 종료 시간", contest_other_info_format)
        self.worksheet.write("A5", "[참고사항] 관리자를 제외한 결과만 표기됩니다.", contest_other_info_format)
        self.worksheet.write("B3", str(self.contest.start_time), contest_other_info_format)
        self.worksheet.write("B4", str(self.contest.end_time), contest_other_info_format)

    def write_contest_result_table(self):
        """
        성적표 테이블 헤더를 작성합니다
        """

        # 유저 정보를 작성할 공통 테이블 헤더를 작성합니다.
        common_info_len = self.write_common_user_info_table_header()

        # ACM(맞춘 문제 수) 또는 OI(총점) 테이블 헤더를 작성합니다.
        contest_score_format = self.workbook.add_format(self.__xlsx_style_format["contest_score"])
        contest_score_header_name = "맞춘 문제 수" if self.contest.rule_type == ContestRuleType.ACM else "총점"
        contest_score_header_pos = column_string(common_info_len + 1) + self.table_start_pos_y
        self.worksheet.write(contest_score_header_pos, contest_score_header_name, contest_score_format)

        # 대회 문제 정보 테이블 헤더를 작성합니다.
        problem_count = self.contest_problems.count()
        problem_name_format = self.workbook.add_format(self.__xlsx_style_format["problem_name"])
        for item in range(problem_count):
            problem_name = f"문제 {self.contest_problems[item]._id}"
            self.worksheet.write(column_string(9 + item) + self.table_start_pos_y, problem_name, problem_name_format)
        """
        성적표 테이블의 내용을 작성합니다
        """
        self.write_xlsx_ranking_content()

    def write_xlsx_user_info(self, row_idx, user_data):
        """사용자 기본 정보 작성"""
        base_row = row_idx + int(self.table_start_pos_y)
        user = user_data["user"]
        user_fields = [
            str(row_idx + 1), user["username"], user["real_name"] or "", user["email"] or "", user["school"] or "",
            user["major"] or "", user["student_id"] or ""
        ]

        header_by_contest_type = str(
            user_data["accepted_number"]) + '문제' if self.contest.rule_type == ContestRuleType.ACM else str(
                user["total_score"]) + '점'
        user_fields.append(header_by_contest_type)

        for col_idx, value in enumerate(user_fields):
            self.worksheet.write_string(base_row, col_idx, value)

        return base_row

    def write_xlsx_ranking_content(self):
        for index, item in enumerate(self.data):
            base_row = self.write_xlsx_user_info(index, item)

            for k, v in item["submission_info"].items():
                try:
                    problem_id = self.problem_ids.index(int(k))
                except ValueError:
                    continue
                value = self.get_ac_state_name(
                    v["is_ac"]) if self.contest.rule_type == ContestRuleType.ACM else f"{str(v)}점"
                self.worksheet.write_string(base_row, 8 + problem_id, value)
