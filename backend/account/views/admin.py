import os
import random
import re
import string
from datetime import datetime, timedelta

import requests
import xlsxwriter

from django.db import transaction, IntegrityError
from django.db.models import Q, Case, When, Value, IntegerField, Count, F
from django.db.models.functions import TruncMonth, ExtractWeekDay
from django.http import HttpResponse
from django.contrib.auth.hashers import make_password

from school.models import College, Department
from submission.models import Submission
from utils.api import APIView, validate_serializer
from utils.constants import EMAIL_SUFFIX, GENERATE_MOCK_USERNAME_URL
from utils.shortcuts import rand_str

from ..decorators import super_admin_required
from ..models import AdminType, ProblemPermission, User, UserProfile, UserScore, UserSolved
from ..serializers import EditUserSerializer, UserAdminSerializer, GenerateUserSerializer, UserAdminStatisticsSerializer
from ..serializers import ImportUserSeralizer

class UserAdminStatisticAPI(APIView):
    @super_admin_required
    def get(self, request):
        all_user = User.objects.all()

        stats_data = {
            "all_users": all_user.count(),
            "super_admins": all_user.filter(admin_type=AdminType.SUPER_ADMIN).count(),
            "admins": all_user.filter(admin_type=AdminType.ADMIN).count(),
            "regular_users": all_user.filter(admin_type=AdminType.REGULAR_USER).count(),
            "disabled_users": all_user.filter(is_disabled=True).count()
        }

        # 학과별 사용자 수 통계
        department_stats = (
            User.objects.values('userprofile__major')
            .annotate(value=Count('id'))
            .values('value', name=F('userprofile__major'))
            .order_by('-value')
        )

        # None 값 처리 (학과가 지정되지 않은 사용자)
        department_stats = list(department_stats)
        for stat in department_stats:
            if stat['name'] is None:
                stat['name'] = '미지정'

        stats_data['department_statistics'] = department_stats

        # 월별 가입자 수 통계
        current_year = datetime.now().year
        start_date = datetime(current_year, 1, 1)
        end_date = datetime(current_year, 12, 31)

        monthly_stats = (
            User.objects.filter(create_time__range=(start_date, end_date))
            .annotate(month=TruncMonth('create_time'))
            .values('month')
            .annotate(count=Count('id'))
            .order_by('month')
        )

        months = ['1월', '2월', '3월', '4월', '5월', '6월',
                  '7월', '8월', '9월', '10월', '11월', '12월']
        counts = [0] * 12

        for stat in monthly_stats:
            month_index = stat['month'].month - 1
            counts[month_index] = stat['count']

        stats_data['monthly_statistics'] = {
            'year': current_year,
            'xAxis': months,
            'series': counts
        }

        # 주간 가입자 수 통계
        today = datetime.now().date()
        start_of_week = today - timedelta(days=today.weekday())  # 이번 주 월요일
        end_of_week = start_of_week + timedelta(days=6)  # 이번 주 일요일

        weekly_stats = (
            User.objects.filter(create_time__date__range=(start_of_week, end_of_week))
            .annotate(weekday=ExtractWeekDay('create_time'))
            .values('weekday')
            .annotate(count=Count('id'))
            .order_by('weekday')
        )

        weekdays = ['월', '화', '수', '목', '금', '토', '일']
        counts = [0] * 7

        for stat in weekly_stats:
            index = (stat['weekday'] - 2) % 7
            counts[index] = stat['count']

        # 주차 정보 계산
        year = today.year
        month = today.month
        month_names = ['1월', '2월', '3월', '4월', '5월', '6월',
                       '7월', '8월', '9월', '10월', '11월', '12월']
        month_name = month_names[month - 1]

        # 해당 월의 첫 날
        first_day_of_month = today.replace(day=1)
        # 첫 주의 월요일 (이전 달의 날짜가 될 수 있음)
        first_monday = first_day_of_month - timedelta(days=first_day_of_month.weekday())
        # 현재 날짜가 첫 주의 월요일로부터 몇 주 떨어져 있는지 계산
        week_of_month = ((today - first_monday).days // 7) + 1

        week_info = f"{year}년 {month_name} {week_of_month}주차"

        stats_data['weekly_statistics'] = {
            'week_info': week_info,
            'date_range': {
                'start': start_of_week.strftime('%Y-%m-%d'),
                'end': end_of_week.strftime('%Y-%m-%d'),
            },
            'xAxis': weekdays,
            'series': counts
        }

        serializer = UserAdminStatisticsSerializer(stats_data)

        return self.success(serializer.data)



class UserAdminAPI(APIView):
    @validate_serializer(ImportUserSeralizer)
    @super_admin_required
    def post(self, request):
        """
        Import User
        """
        data = request.data["users"]

        user_list = []
        for user_data in data:
            if len(user_data) != 4 or len(user_data[0]) > 32:
                return self.error(f"Error occurred while processing data '{user_data}'")
            user_list.append(User(username=user_data[0], password=make_password(user_data[1]), email=user_data[2]))

        try:
            with transaction.atomic():
                ret = User.objects.bulk_create(user_list)
                UserProfile.objects.bulk_create(
                    [UserProfile(user=ret[i], real_name=data[i][3]) for i in range(len(ret))])
            return self.success()
        except IntegrityError as e:
            # Extract detail from exception message
            #    duplicate key value violates unique constraint "user_username_key"
            #    DETAIL:  Key (username)=(root11) already exists.
            return self.error(str(e).split("\n")[1])

    @validate_serializer(EditUserSerializer)
    @super_admin_required
    def put(self, request):
        """
        Edit user api
        """
        data = request.data
        try:
            user = User.objects.get(id=data["id"])
        except User.DoesNotExist:
            return self.error("User does not exist")
        if User.objects.filter(username=data["username"].lower()).exclude(id=user.id).exists():
            return self.error("Username already exists")
        # if UserProfile.objects.filter(student_id=data["student_id"]).exists():
        #     return self.error("Student Id already exists")
        # if User.objects.filter(email=data["email"].lower()).exclude(id=user.id).exists():
        #     return self.error("Email already exists")

        pre_username = user.username
        user.username = data["username"].lower()
        # user.email = data["email"].lower()
        user.admin_type = data["admin_type"]
        user.is_disabled = data["is_disabled"]

        if data["admin_type"] == AdminType.ADMIN:
            user.problem_permission = data["problem_permission"]
        elif data["admin_type"] == AdminType.SUPER_ADMIN:
            user.problem_permission = ProblemPermission.ALL
        else:
            user.problem_permission = ProblemPermission.NONE

        if data["password"]:
            user.set_password(data["password"])

        if data["college"] and data["department"]:
            college = College.objects.get(id=data["college"])
            department = Department.objects.get(id=data["department"])
            UserProfile.objects.filter(user=user).update(college=college, department=department, school=college.college_name, major=department.department_name)

        if data["student_id"]:
            UserProfile.objects.filter(user=user).update(student_id=data["student_id"])

        if data["open_api"]:
            # Avoid reset user appkey after saving changes
            if not user.open_api:
                user.open_api_appkey = rand_str()
        else:
            user.open_api_appkey = None
        user.open_api = data["open_api"]

        if data["two_factor_auth"]:
            # Avoid reset user tfa_token after saving changes
            if not user.two_factor_auth:
                user.tfa_token = rand_str()
        else:
            user.tfa_token = None

        user.two_factor_auth = data["two_factor_auth"]

        user.save()
        if pre_username != user.username:
            Submission.objects.filter(username=pre_username).update(username=user.username)

        UserProfile.objects.filter(user=user).update(real_name=data["real_name"])
        return self.success(UserAdminSerializer(user).data)

    @super_admin_required
    def get(self, request):
        """
        User list api / Get user by id
        """
        user_id = request.GET.get("id")
        if user_id:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return self.error("User does not exist")
            return self.success(UserAdminSerializer(user).data)

        user = User.objects.all().order_by("-create_time")

        admin_type = request.GET.get("admin_type", None)

        if admin_type == "Regular":
            user = user.filter(admin_type=AdminType.REGULAR_USER)
        if admin_type == "Admin":
            user = user.exclude(admin_type=AdminType.REGULAR_USER).order_by(
                Case(
                    When(admin_type=AdminType.SUPER_ADMIN, then=Value(0)),
                    default=Value(1),
                    output_field=IntegerField()
                ),
                'id'
            )

        keyword = request.GET.get("keyword", None)
        if keyword:
            user = user.filter(Q(username__icontains=keyword) |
                               Q(userprofile__real_name__icontains=keyword) |
                               Q(email__icontains=keyword))

        college = request.GET.get("college", None)
        if college:
            user = user.filter(Q(userprofile__college_id=college))

        department = request.GET.get("department", None)
        if department:
            user = user.filter(Q(userprofile__department_id=department))

        return self.success(self.paginate_data(request, user, UserAdminSerializer))

    @super_admin_required
    def delete(self, request):
        id = request.GET.get("id")
        if not id:
            return self.error("Invalid Parameter, id is required")
        ids = id.split(",")
        if str(request.user.id) in ids:
            return self.error("Current user can not be deleted")
        User.objects.filter(id__in=ids).delete()
        return self.success()


class GenerateUserAPI(APIView):

    @staticmethod
    def generateMockUsername():
        resp = requests.post(GENERATE_MOCK_USERNAME_URL)
        return resp.json()['data']

    @staticmethod
    def generateMockPassword():
        # 문자 집합 정의
        lowercase = string.ascii_lowercase
        uppercase = string.ascii_uppercase
        digits = string.digits
        special_chars = "@$!%*#?&"

        # 각 문자 유형에서 최소 1개씩 선택
        password = [
            random.choice(lowercase),
            random.choice(uppercase),
            random.choice(digits),
            random.choice(special_chars)
        ]

        # 나머지 4개 문자를 모든 가능한 문자에서 랜덤하게 선택
        all_chars = lowercase + uppercase + digits + special_chars
        password.extend(random.choice(all_chars) for _ in range(4))

        # 문자열 순서를 섞음
        random.shuffle(password)

        # 리스트를 문자열로 변환
        return ''.join(password)

    @super_admin_required
    def get(self, request):
        """
        download users excel
        """
        file_id = request.GET.get("file_id")
        if not file_id:
            return self.error("Invalid Parameter, file_id is required")
        if not re.match(r"^[a-zA-Z0-9]+$", file_id):
            return self.error("Illegal file_id")
        file_path = f"/tmp/{file_id}.xlsx"
        if not os.path.isfile(file_path):
            return self.error("File does not exist")
        with open(file_path, "rb") as f:
            raw_data = f.read()
        os.remove(file_path)
        response = HttpResponse(raw_data)
        response["Content-Disposition"] = "attachment; filename=users.xlsx"
        response["Content-Type"] = "application/xlsx"
        return response

    @validate_serializer(GenerateUserSerializer)
    @super_admin_required
    def post(self, request):
        """
        더미 사용자 생성 API
        """
        data = request.data

        college = College.objects.get(id=data["college"])
        department = Department.objects.get(id=data["department"])

        file_id = rand_str(8)
        filename = f"/tmp/{file_id}.xlsx"
        workbook = xlsxwriter.Workbook(filename)
        worksheet = workbook.add_worksheet()
        worksheet.set_column("A:B", 20)
        worksheet.write("A1", "Username")
        worksheet.write("B1", "Email")
        worksheet.write("C1", "Password")
        i = 1

        user_list = []
        for number in range(1, data["num_of_mock"] + 1):
            mock_email = f"{data['prefix']}{number}_{rand_str(5)}{EMAIL_SUFFIX}"
            raw_password = self.generateMockPassword()
            mock_username = self.generateMockUsername()
            user = User(email=mock_email, username=mock_username, password=make_password(raw_password))
            user.raw_password = raw_password
            user_list.append(user)

        try:
            with transaction.atomic():
                ret = User.objects.bulk_create(user_list)
                UserProfile.objects.bulk_create(
                    [UserProfile(user=user, school=college.college_name, major=department.department_name, \
                                 college=college, department=department, \
                                 real_name=rand_str(3), student_id="2000" + str(random.randint(9999, 99999))) for user
                     in ret])
                UserScore.objects.bulk_create([UserScore(user=user) for user in ret])
                UserSolved.objects.bulk_create([UserSolved(user=user) for user in ret])
                for item in user_list:
                    worksheet.write_string(i, 0, item.username)
                    worksheet.write_string(i, 1, item.email)
                    worksheet.write_string(i, 2, item.raw_password)
                    i += 1
                workbook.close()
                return self.success({"file_id": file_id})
        except IntegrityError as e:
            # Extract detail from exception message
            #    duplicate key value violates unique constraint "user_username_key"
            #    DETAIL:  Key (username)=(root11) already exists.
            return self.error(str(e).split("\n")[1])
