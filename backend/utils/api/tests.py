from django.urls import reverse
from django.test.testcases import TestCase
from rest_framework.test import APIClient

from account.models import AdminType, ProblemPermission, User, UserProfile, College, Department


class APITestCase(TestCase):
    client_class = APIClient

    def create_user(self, email, username, password, real_name="real", student_id="202412345", college_id="1", department_id="1", admin_type=AdminType.REGULAR_USER, login=True,
                    problem_permission=ProblemPermission.NONE):
        user = User.objects.create(email=email, username=username, admin_type=admin_type, problem_permission=problem_permission)
        user.set_password(password)
        school = College.objects.get(id=college_id)
        major = Department.objects.get(id=department_id)
        UserProfile.objects.create(user=user, real_name=real_name, student_id=student_id, college_id=college_id, department_id=department_id, school=school, major=major)
        user.save()
        if login:
            self.client.login(email=email, password=password)
        return user

    def create_school_fixtures(self, college_id, college_name, department_id, department_name):
        college = College.objects.create(id=college_id, college_name=college_name)
        department = Department.objects.create(id=department_id, department_name=department_name, college_id=college_id)
        college.save()
        department.save()

    def create_admin(self, email="admin@admin.com", username="admin", password="admin1234!", login=True):
        return self.create_user(email=email, username=username, password=password, admin_type=AdminType.ADMIN,
                                problem_permission=ProblemPermission.OWN,
                                login=login)

    def create_super_admin(self, email="root@root.com", username="root", password="root1234!", login=True):
        return self.create_user(email=email, username=username, password=password, admin_type=AdminType.SUPER_ADMIN,
                                problem_permission=ProblemPermission.ALL, login=login)

    def reverse(self, url_name, *args, **kwargs):
        return reverse(url_name, *args, **kwargs)

    def assertSuccess(self, response):
        if not response.data["error"] is None:
            raise AssertionError("response with errors, response: " + str(response.data))

    def assertFailed(self, response, msg=None):
        self.assertTrue(response.data["error"] is not None)
        if msg:
            self.assertEqual(response.data["data"], msg)
