import hashlib
import html
import json
import os
import re
import shutil
import tempfile
import zipfile
from html.parser import HTMLParser
from json.decoder import scanstring
from wsgiref.util import FileWrapper

from django.conf import settings
from django.db import transaction
from django.db.models import Q
from django.http import StreamingHttpResponse, FileResponse
from django.shortcuts import get_object_or_404
from django.utils import translation

from account.decorators import problem_permission_required, ensure_created_by
from contest.models import Contest, ContestStatus
from fps.parser import FPSHelper, FPSParser
from judge.dispatcher import SPJCompiler
from options.options import SysOptions
from submission.models import Submission, JudgeStatus
from utils.api import APIView, CSRFExemptAPIView, validate_serializer, APIError
from utils.constants import Difficulty
from utils.shortcuts import rand_str, natural_sort_key, get_difficulty
from utils.tasks import delete_files
from ..models import Problem, ProblemRuleType, ProblemTag
from ..serializers import (CreateContestProblemSerializer, CompileSPJSerializer, CreateProblemSerializer,
                           EditProblemSerializer, EditContestProblemSerializer, ProblemAdminSerializer,
                           TestCaseUploadForm, ContestProblemMakePublicSerializer, AddContestProblemSerializer,
                           ExportProblemSerializer, ExportProblemRequestSerialzier, UploadProblemForm,
                           ImportProblemSerializer, FPSProblemSerializer)
from ..utils import TEMPLATE_BASE, build_problem_template


class TestCaseZipProcessor(object):

    def process_zip(self, uploaded_zip_file, spj, dir=""):
        try:
            zip_file = zipfile.ZipFile(uploaded_zip_file, "r")
        except zipfile.BadZipFile:
            raise APIError("Bad zip file")
        name_list = zip_file.namelist()
        test_case_list = self.filter_name_list(name_list, spj=spj, dir=dir)
        if not test_case_list:
            raise APIError("Empty file")

        test_case_id = rand_str()
        test_case_dir = os.path.join(settings.TEST_CASE_DIR, test_case_id)
        os.mkdir(test_case_dir)
        os.chmod(test_case_dir, 0o710)

        size_cache = {}
        md5_cache = {}

        for item in test_case_list:
            with open(os.path.join(test_case_dir, item), "wb") as f:
                content = zip_file.read(f"{dir}{item}").replace(b"\r\n", b"\n")
                size_cache[item] = len(content)
                if item.endswith(".out"):
                    md5_cache[item] = hashlib.md5(content.rstrip()).hexdigest()
                f.write(content)
        test_case_info = {"spj": spj, "test_cases": {}}

        info = []

        if spj:
            for index, item in enumerate(test_case_list):
                data = {"input_name": item, "input_size": size_cache[item]}
                info.append(data)
                test_case_info["test_cases"][str(index + 1)] = data
        else:
            # ["1.in", "1.out", "2.in", "2.out"] => [("1.in", "1.out"), ("2.in", "2.out")]
            test_case_list = zip(*[test_case_list[i::2] for i in range(2)])
            for index, item in enumerate(test_case_list):
                data = {
                    "stripped_output_md5": md5_cache[item[1]],
                    "input_size": size_cache[item[0]],
                    "output_size": size_cache[item[1]],
                    "input_name": item[0],
                    "output_name": item[1]
                }
                info.append(data)
                test_case_info["test_cases"][str(index + 1)] = data

        with open(os.path.join(test_case_dir, "info"), "w", encoding="utf-8") as f:
            f.write(json.dumps(test_case_info, indent=4))

        for item in os.listdir(test_case_dir):
            os.chmod(os.path.join(test_case_dir, item), 0o640)

        return info, test_case_id

    def filter_name_list(self, name_list, spj, dir=""):
        ret = []
        prefix = 1
        if spj:
            while True:
                in_name = f"{prefix}.in"
                if f"{dir}{in_name}" in name_list:
                    ret.append(in_name)
                    prefix += 1
                    continue
                else:
                    return sorted(ret, key=natural_sort_key)
        else:
            while True:
                in_name = f"{prefix}.in"
                out_name = f"{prefix}.out"
                if f"{dir}{in_name}" in name_list and f"{dir}{out_name}" in name_list:
                    ret.append(in_name)
                    ret.append(out_name)
                    prefix += 1
                    continue
                else:
                    return sorted(ret, key=natural_sort_key)


class TestCaseAPI(CSRFExemptAPIView, TestCaseZipProcessor):
    request_parsers = ()

    def get(self, request):
        problem_id = request.GET.get("problem_id")
        if not problem_id:
            return self.error("Parameter error, problem_id is required")
        try:
            problem = Problem.objects.get(id=problem_id)
        except Problem.DoesNotExist:
            return self.error("Problem does not exists")

        if problem.contest:
            ensure_created_by(problem.contest, request.user)
        else:
            ensure_created_by(problem, request.user)

        test_case_dir = os.path.join(settings.TEST_CASE_DIR, problem.test_case_id)
        if not os.path.isdir(test_case_dir):
            return self.error("Test case does not exists")
        name_list = self.filter_name_list(os.listdir(test_case_dir), problem.spj)
        name_list.append("info")
        file_name = os.path.join(test_case_dir, problem.test_case_id + ".zip")
        with zipfile.ZipFile(file_name, "w") as file:
            for test_case in name_list:
                file.write(f"{test_case_dir}/{test_case}", test_case)
        response = StreamingHttpResponse(FileWrapper(open(file_name, "rb")), content_type="application/octet-stream")

        response["Content-Disposition"] = f"attachment; filename=problem_{problem.id}_test_cases.zip"
        response["Content-Length"] = os.path.getsize(file_name)
        return response

    def post(self, request):
        form = TestCaseUploadForm(request.POST, request.FILES)
        if form.is_valid():
            spj = form.cleaned_data["spj"] == "true"
            file = form.cleaned_data["file"]
        else:
            return self.error("Upload failed")
        zip_file = f"/tmp/{rand_str()}.zip"
        with open(zip_file, "wb") as f:
            for chunk in file:
                f.write(chunk)
        info, test_case_id = self.process_zip(zip_file, spj=spj)
        os.remove(zip_file)
        return self.success({"id": test_case_id, "info": info, "spj": spj})


class CompileSPJAPI(APIView):

    @validate_serializer(CompileSPJSerializer)
    def post(self, request):
        data = request.data
        spj_version = rand_str(8)
        error = SPJCompiler(data["spj_code"], spj_version, data["spj_language"]).compile_spj()
        if error:
            return self.error(error)
        else:
            return self.success()


class ProblemBase(APIView):

    def common_checks(self, request):
        data = request.data

        if data["spj"]:
            if not data["spj_language"] or not data["spj_code"]:
                return "Invalid spj"
            if not data["spj_compile_ok"]:
                return "SPJ code must be compiled successfully"
            data["spj_version"] = hashlib.md5(
                (data["spj_language"] + ":" + data["spj_code"]).encode("utf-8")).hexdigest()
        else:
            data["spj_language"] = None
            data["spj_code"] = None
        if data["rule_type"] == ProblemRuleType.OI:
            total_score = 0
            for item in data["test_case_score"]:
                if item["score"] <= 0:
                    return "Invalid score"
                else:
                    total_score += item["score"]
            data["total_score"] = total_score
        data["languages"] = list(data["languages"])


class ProblemIdDuplicateCheckAPI(APIView):

    def _check_edit_mode(self, _id, problem_id):
        existing_problem = get_object_or_404(Problem, id=problem_id)
        if existing_problem._id != _id:
            duplicate_exists = Problem.objects.exclude(id=problem_id).filter(_id=_id).exists()
            if duplicate_exists:
                return self.error("Problem ID already exists")
        return self.success("Valid Problem ID")

    def _check_create_mode(self, _id):
        if Problem.objects.filter(_id=_id).exists():
            return self.error("Problem ID already exists")
        return self.success("Valid Problem ID")

    def post(self, request):

        data = request.data
        _id = data.get("_id")
        problem_id = data.get("problem_id")
        edit_status = data.get("edit_status", False)

        if edit_status:
            return self._check_edit_mode(_id, problem_id)
        else:
            return self._check_create_mode(_id)


class ProblemAPI(ProblemBase):

    @problem_permission_required
    @validate_serializer(CreateProblemSerializer)
    def post(self, request):
        data = request.data

        if Problem.objects.filter(_id=data["_id"]).exists():
            return self.error("Problem ID already exists")

        error_info = self.common_checks(request)
        if error_info:
            return self.error(error_info)

        # todo check filename and score info
        tags = data.pop("tags")
        data["created_by"] = request.user
        problem = Problem.objects.create(**data)
        # problem._id = str(problem.id)
        # problem.save()

        for item in tags:
            try:
                tag = ProblemTag.objects.get(name=item)
            except ProblemTag.DoesNotExist:
                tag = ProblemTag.objects.create(name=item)
            problem.tags.add(tag)
        return self.success(ProblemAdminSerializer(problem).data)

    @problem_permission_required
    def get(self, request):
        problem_id = request.GET.get("id")
        rule_type = request.GET.get("rule_type")
        user = request.user
        if problem_id:
            try:
                problem = Problem.objects.get(id=problem_id)
                ensure_created_by(problem, request.user)
                return self.success(ProblemAdminSerializer(problem).data)
            except Problem.DoesNotExist:
                return self.error("Problem does not exist")

        problems = Problem.objects.filter(contest_id__isnull=True).order_by("-create_time")
        if rule_type:
            if rule_type not in ProblemRuleType.choices():
                return self.error("Invalid rule_type")
            else:
                problems = problems.filter(rule_type=rule_type)

        keyword = request.GET.get("keyword", "").strip()
        if keyword:
            problems = problems.filter(Q(title__icontains=keyword) | Q(_id__icontains=keyword))
        if not user.can_mgmt_all_problem():
            problems = problems.filter(created_by=user)
        return self.success(self.paginate_data(request, problems, ProblemAdminSerializer))

    @problem_permission_required
    @validate_serializer(EditProblemSerializer)
    def put(self, request):
        data = request.data
        problem_id = data.pop("id")

        if Problem.objects.get(id=problem_id)._id != data["_id"] and Problem.objects.exclude(_id=data["_id"]).filter(
                _id=data["_id"]).exists():
            return "Problem ID already exists"

        try:
            problem = Problem.objects.get(id=problem_id)
            ensure_created_by(problem, request.user)
        except Problem.DoesNotExist:
            return self.error("Problem does not exist")

        error_info = self.common_checks(request)
        if error_info:
            return self.error(error_info)
        # todo check filename and score info
        tags = data.pop("tags")
        data["languages"] = list(data["languages"])

        for k, v in data.items():
            setattr(problem, k, v)
        problem.save()

        problem.tags.remove(*problem.tags.all())
        for tag in tags:
            try:
                tag = ProblemTag.objects.get(name=tag)
            except ProblemTag.DoesNotExist:
                tag = ProblemTag.objects.create(name=tag)
            problem.tags.add(tag)

        return self.success()

    @problem_permission_required
    def delete(self, request):
        id = request.GET.get("id")
        if not id:
            return self.error("Invalid parameter, id is required")
        try:
            problem = Problem.objects.get(id=id, contest_id__isnull=True)
        except Problem.DoesNotExist:
            return self.error("Problem does not exists")
        ensure_created_by(problem, request.user)
        # d = os.path.join(settings.TEST_CASE_DIR, problem.test_case_id)
        # if os.path.isdir(d):
        #     shutil.rmtree(d, ignore_errors=True)
        problem.delete()
        return self.success()


class ContestProblemAPI(ProblemBase):

    @validate_serializer(CreateContestProblemSerializer)
    def post(self, request):
        data = request.data
        try:
            contest = Contest.objects.get(id=data.pop("contest_id"))
            ensure_created_by(contest, request.user)
        except Contest.DoesNotExist:
            return self.error("Contest does not exist")

        if data["rule_type"] != contest.rule_type:
            return self.error("Invalid rule type")

        _id = data["_id"]
        if not _id:
            return self.error("Display ID is required")

        if Problem.objects.filter(_id=_id, contest=contest).exists():
            return self.error("Duplicate Display id")

        error_info = self.common_checks(request)
        if error_info:
            return self.error(error_info)

        # todo check filename and score info
        data["contest"] = contest
        tags = data.pop("tags")
        data["created_by"] = request.user
        problem = Problem.objects.create(**data)

        for item in tags:
            try:
                tag = ProblemTag.objects.get(name=item)
            except ProblemTag.DoesNotExist:
                tag = ProblemTag.objects.create(name=item)
            problem.tags.add(tag)
        return self.success(ProblemAdminSerializer(problem).data)

    def get(self, request):
        problem_id = request.GET.get("id")
        contest_id = request.GET.get("contest_id")
        user = request.user
        if problem_id:
            try:
                problem = Problem.objects.get(id=problem_id)
                ensure_created_by(problem.contest, user)
            except Problem.DoesNotExist:
                return self.error("Problem does not exist")
            return self.success(ProblemAdminSerializer(problem).data)

        if not contest_id:
            return self.error("Contest id is required")
        try:
            contest = Contest.objects.get(id=contest_id)
            ensure_created_by(contest, user)
        except Contest.DoesNotExist:
            return self.error("Contest does not exist")
        problems = Problem.objects.filter(contest=contest).order_by("-create_time")
        if user.is_admin():
            problems = problems.filter(contest__created_by=user)
        keyword = request.GET.get("keyword")
        if keyword:
            problems = problems.filter(title__contains=keyword)
        return self.success(self.paginate_data(request, problems, ProblemAdminSerializer))

    @validate_serializer(EditContestProblemSerializer)
    def put(self, request):
        data = request.data
        user = request.user

        try:
            contest = Contest.objects.get(id=data.pop("contest_id"))
            ensure_created_by(contest, user)
        except Contest.DoesNotExist:
            return self.error("Contest does not exist")

        if data["rule_type"] != contest.rule_type:
            return self.error("Invalid rule type")

        problem_id = data.pop("id")

        try:
            problem = Problem.objects.get(id=problem_id, contest=contest)
        except Problem.DoesNotExist:
            return self.error("Problem does not exist")

        _id = data["_id"]
        if not _id:
            return self.error("Display ID is required")
        if Problem.objects.exclude(id=problem_id).filter(_id=_id, contest=contest).exists():
            return self.error("Display ID already exists")

        error_info = self.common_checks(request)
        if error_info:
            return self.error(error_info)
        # todo check filename and score info
        tags = data.pop("tags")
        data["languages"] = list(data["languages"])

        for k, v in data.items():
            setattr(problem, k, v)
        problem.save()

        problem.tags.remove(*problem.tags.all())
        for tag in tags:
            try:
                tag = ProblemTag.objects.get(name=tag)
            except ProblemTag.DoesNotExist:
                tag = ProblemTag.objects.create(name=tag)
            problem.tags.add(tag)
        return self.success()

    def delete(self, request):
        id = request.GET.get("id")
        if not id:
            return self.error("Invalid parameter, id is required")
        try:
            problem = Problem.objects.get(id=id, contest_id__isnull=False)
        except Problem.DoesNotExist:
            return self.error("Problem does not exists")
        ensure_created_by(problem.contest, request.user)
        if Submission.objects.filter(problem=problem).exists():
            return self.error("Can't delete the problem as it has submissions")
        # d = os.path.join(settings.TEST_CASE_DIR, problem.test_case_id)
        # if os.path.isdir(d):
        #    shutil.rmtree(d, ignore_errors=True)
        problem.delete()
        return self.success()


class ImportContestProblemAPI(APIView):

    def post(self, request):
        """기존에 존재하는 대회의 문제를 다른 대회로 복사하는 API."""
        data = request.data
        from_contest_id = data.get("from_contest_id")
        to_contest_id = data.get("contest_id")

        if not from_contest_id or not to_contest_id:
            return self.error("from_contest_id and contest_id are required")

        try:
            from_contest = Contest.objects.get(id=from_contest_id)
            to_contest = Contest.objects.get(id=to_contest_id)
        except Contest.DoesNotExist:
            return self.error("Contest does not exist")

        # Permission check
        ensure_created_by(to_contest, request.user)
        if not request.user.is_super_admin():
            if from_contest.created_by != request.user:
                return self.error("You don't have permission to import from this contest.")

        source_problems = Problem.objects.filter(contest=from_contest).order_by('create_time')

        with transaction.atomic():
            for problem in source_problems:
                # 이미 존재하는 문제는 건너띔 - _id로 판단
                if Problem.objects.filter(contest=to_contest, _id=problem._id).exists():
                    continue

                tags = problem.tags.all()

                # 새로운 테스트케이스 디렉토리 복사
                new_test_case_id = None
                if problem.test_case_id:
                    src_dir = os.path.join(settings.TEST_CASE_DIR, problem.test_case_id)
                    if os.path.isdir(src_dir):
                        new_test_case_id = rand_str()
                        dest_dir = os.path.join(settings.TEST_CASE_DIR, new_test_case_id)
                        shutil.copytree(src_dir, dest_dir)

                # PK를 None으로 설정하여 새 객체로 저장
                problem.pk = None

                problem.contest = to_contest
                problem.is_public = False
                problem.visible = True
                if new_test_case_id:
                    problem.test_case_id = new_test_case_id
                problem.submission_number = 0
                problem.accepted_number = 0
                problem.statistic_info = {}
                problem.created_by = request.user
                problem.save()
                problem.tags.set(tags)

        return self.success()


class MakeContestProblemPublicAPIView(APIView):

    @validate_serializer(ContestProblemMakePublicSerializer)
    @problem_permission_required
    def post(self, request):
        data = request.data
        display_id = data.get("display_id")
        if Problem.objects.filter(_id=display_id, contest_id__isnull=True).exists():
            return self.error("Duplicate display ID")

        try:
            problem = Problem.objects.get(id=data["id"])
        except Problem.DoesNotExist:
            return self.error("Problem does not exist")

        if not problem.contest or problem.is_public:
            return self.error("Already be a public problem")
        problem.is_public = True
        problem.save()
        # https://docs.djangoproject.com/en/1.11/topics/db/queries/#copying-model-instances
        tags = problem.tags.all()
        problem.pk = None
        problem.contest = None
        problem._id = display_id
        problem.visible = False
        problem.submission_number = problem.accepted_number = 0
        problem.statistic_info = {}
        problem.save()
        problem.tags.set(tags)
        return self.success()


class AddContestProblemAPI(APIView):

    @validate_serializer(AddContestProblemSerializer)
    def post(self, request):
        data = request.data
        try:
            contest = Contest.objects.get(id=data["contest_id"])
            problem = Problem.objects.get(id=data["problem_id"])
        except (Contest.DoesNotExist, Problem.DoesNotExist):
            return self.error("Contest or Problem does not exist")

        if contest.status == ContestStatus.CONTEST_ENDED:
            return self.error("Contest has ended")
        if Problem.objects.filter(contest=contest, _id=data["display_id"]).exists():
            return self.error("Duplicate display id in this contest")

        tags = problem.tags.all()
        problem.pk = None
        problem.contest = contest
        problem.is_public = True
        problem.visible = True
        problem._id = request.data["display_id"]
        problem.submission_number = problem.accepted_number = 0
        problem.statistic_info = {}
        problem.save()
        problem.tags.set(tags)
        return self.success()


class ExportProblemAPI(APIView):

    def choose_answers(self, user, problem):
        ret = []
        for item in problem.languages:
            submission = Submission.objects.filter(
                problem=problem, user_id=user.id, language=item,
                result=JudgeStatus.ACCEPTED).order_by("-create_time").first()
            if submission:
                ret.append({"language": submission.language, "code": submission.code})
        return ret

    def process_one_problem(self, zip_file, user, problem, index):
        info = ExportProblemSerializer(problem).data
        info["answers"] = self.choose_answers(user, problem=problem)
        compression = zipfile.ZIP_DEFLATED
        zip_file.writestr(
            zinfo_or_arcname=f"{index}/problem.json", data=json.dumps(info, indent=4), compress_type=compression)
        problem_test_case_dir = os.path.join(settings.TEST_CASE_DIR, problem.test_case_id)
        with open(os.path.join(problem_test_case_dir, "info")) as f:
            info = json.load(f)
        for k, v in info["test_cases"].items():
            zip_file.write(
                filename=os.path.join(problem_test_case_dir, v["input_name"]),
                arcname=f"{index}/testcase/{v['input_name']}",
                compress_type=compression)
            if not info["spj"]:
                zip_file.write(
                    filename=os.path.join(problem_test_case_dir, v["output_name"]),
                    arcname=f"{index}/testcase/{v['output_name']}",
                    compress_type=compression)

    @validate_serializer(ExportProblemRequestSerialzier)
    def get(self, request):
        problems = Problem.objects.filter(id__in=request.data["problem_id"])
        for problem in problems:
            if problem.contest:
                ensure_created_by(problem.contest, request.user)
            else:
                ensure_created_by(problem, request.user)
        path = f"/tmp/{rand_str()}.zip"
        with zipfile.ZipFile(path, "w") as zip_file:
            for index, problem in enumerate(problems):
                self.process_one_problem(zip_file=zip_file, user=request.user, problem=problem, index=index + 1)
        delete_files.apply_async(args=(path,), countdown=300)
        resp = FileResponse(open(path, "rb"))
        resp["Content-Type"] = "application/zip"
        resp["Content-Disposition"] = "attachment;filename=problem-export.zip"
        return resp


class ImageTagParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tags = []

    def handle_starttag(self, tag, attrs):
        if tag == "img":
            self.tags.append((self.getpos(), self.get_starttag_text(), attrs))


class ImportProblemAPI(CSRFExemptAPIView, TestCaseZipProcessor):
    request_parsers = ()
    image_fields = ("description", "input_description", "output_description", "hint")
    image_suffixes = (".gif", ".jpg", ".jpeg", ".bmp", ".png")

    def find_image_tags(self, value):
        parser = ImageTagParser()
        parser.feed(value)
        parser.close()
        line_starts = [0]
        for line in value.split("\n")[:-1]:
            line_starts.append(line_starts[-1] + len(line) + 1)
        tags = []
        for (lineno, offset), text, attrs in parser.tags:
            src = dict(attrs).get("src") or ""
            if src.startswith("images/"):
                start = line_starts[lineno - 1] + offset
                tags.append((start, start + len(text), text, attrs, src))
        return tags

    json_error_messages = {
        "Expecting value": "값이 와야 합니다",
        "Expecting ',' delimiter": "쉼표(,)가 빠졌습니다",
        "Expecting ':' delimiter": "콜론(:)이 빠졌습니다",
        "Expecting property name enclosed in double quotes": "키는 큰따옴표로 감싸야 합니다 (마지막 쉼표가 남아 있는지 확인해주세요)",
        "Unterminated string starting at": "문자열이 닫히지 않았습니다",
        "Invalid control character at": "문자열 안에 줄바꿈이나 탭 같은 제어 문자가 있습니다",
        "Invalid \\escape": "잘못된 이스케이프 문자입니다",
        "Extra data": "JSON이 끝난 뒤에 내용이 더 있습니다",
    }

    def fail(self, message):
        raise APIError({"message": message, "errors": [self.error_item("", "", "zip", message)]})

    def error_item(self, problem_dir, title, location, message, field="", line=None, column=None, detail=""):
        return {"dir": problem_dir, "title": title, "location": location, "field": field, "message": message,
                "line": line, "column": column, "detail": detail}

    def add_error(self, problem_dir, title, location, message, **kwargs):
        self.errors.append(self.error_item(problem_dir, title, location, message, **kwargs))

    def add_field_error(self, problem_dir, title, path, message, location="problem.json", target=None):
        field = "".join(f"[{key}]" if isinstance(key, int) else f".{key}" for key in path).lstrip(".")
        pos = self.find_json_position(self.problem_text, path)
        if pos is not None and target and self.problem_text.find(target, pos) != -1:
            pos = self.problem_text.find(target, pos)
        line = None if pos is None else self.json_location(self.problem_text, pos)[0]
        self.add_error(problem_dir, title, location, message, field=field, line=line)

    def flatten_errors(self, errors, path=()):
        if isinstance(errors, dict):
            for key, value in errors.items():
                yield from self.flatten_errors(value, path + (key,))
        elif errors and all(isinstance(item, str) for item in errors):
            yield path, errors[0]
        else:
            for index, value in enumerate(errors):
                if value:
                    yield from self.flatten_errors(value, path + (index,))

    def find_json_position(self, text, path):
        decoder = json.JSONDecoder()
        whitespace = re.compile(r"\s*")

        def skip(pos):
            return whitespace.match(text, pos).end()

        pos = skip(0)
        found = None
        for key in path:
            if text[pos] == "{" and isinstance(key, str):
                pos = skip(pos + 1)
                while text[pos] == '"':
                    name, pos = scanstring(text, pos + 1)
                    pos = skip(skip(pos) + 1)
                    if name == key:
                        break
                    pos = skip(decoder.raw_decode(text, pos)[1])
                    if text[pos] == ",":
                        pos = skip(pos + 1)
                else:
                    return found
            elif text[pos] == "[" and isinstance(key, int):
                pos = skip(pos + 1)
                for _ in range(key):
                    if text[pos] == "]":
                        return found
                    pos = skip(decoder.raw_decode(text, pos)[1])
                    if text[pos] == ",":
                        pos = skip(pos + 1)
                if text[pos] == "]":
                    return found
            else:
                return found
            found = pos
        return found

    def code_snippet(self, text, lineno, colno, width=100):
        lines = text.split("\n")
        start, end = max(lineno - 3, 0), min(lineno + 2, len(lines))
        digits = len(str(end))
        snippet = []
        for number in range(start + 1, end + 1):
            line = lines[number - 1]
            offset = 0
            if len(line) > width:
                center = colno - 1 if number == lineno else 0
                offset = max(min(center - width // 2, len(line) - width), 0)
                line = ("…" if offset else "") + line[offset:offset + width] + ("…" if offset + width < len(line) else "")
            snippet.append(f"{'>' if number == lineno else ' '} {number:>{digits}} | {line}")
            if number == lineno:
                snippet.append(f"  {' ' * digits} | {' ' * (colno - 1 - offset + (1 if offset else 0))}^")
        return "\n".join(snippet)

    def json_location(self, text, pos):
        lineno = text.count("\n", 0, pos) + 1
        colno = pos - text.rfind("\n", 0, pos)
        return lineno, colno

    def collect_images(self, problem_info, problem_dir, name_list):
        images = {}
        for field in self.image_fields:
            for *_, src in self.find_image_tags(problem_info[field]["value"]):
                if f"{problem_dir}/{src}" not in name_list:
                    self.add_field_error(problem_dir, problem_info["title"], (field, "value"),
                                         f"{src} 파일이 없습니다", location="images", target=src)
                elif os.path.splitext(src)[-1].lower() not in self.image_suffixes:
                    suffixes = ", ".join(suffix[1:] for suffix in self.image_suffixes)
                    self.add_field_error(problem_dir, problem_info["title"], (field, "value"),
                                         f"{src}는 지원하지 않는 형식입니다 ({suffixes})", location="images",
                                         target=src)
                else:
                    images[src] = f"{problem_dir}/{src}"
        return images

    def check_test_cases(self, problem_info, problem_dir, name_list):
        prefix = f"{problem_dir}/testcase/"
        spj = problem_info["spj"] is not None
        names = {name[len(prefix):] for name in name_list if name.startswith(prefix)}
        numbers = [int(name.split(".")[0]) for name in names if re.fullmatch(r"\d+\.(in|out)", name)]
        if "1.in" not in names:
            required = "1.in" if spj else "1.in, 1.out"
            self.add_error(problem_dir, problem_info["title"], "testcase", f"테스트케이스가 없습니다 ({required}부터 필요)")
            return []
        suffixes = (".in",) if spj else (".in", ".out")
        expected = [f"{number}{suffix}" for number in range(1, max(numbers) + 1) for suffix in suffixes]
        missing = [name for name in expected if name not in names]
        if missing:
            self.add_error(problem_dir, problem_info["title"], "testcase", f"{', '.join(missing)} 파일이 없습니다")
        return expected

    def check_test_case_score(self, problem_info, problem_dir, test_cases):
        if problem_info["rule_type"] != ProblemRuleType.OI:
            return
        if not problem_info["test_case_score"]:
            self.add_field_error(problem_dir, problem_info["title"], ("test_case_score",),
                                 "OI 문제는 테스트케이스별 점수가 필요합니다")
            return
        for index, item in enumerate(problem_info["test_case_score"]):
            for key in ("input_name", "output_name"):
                if test_cases and item[key] not in test_cases:
                    self.add_field_error(problem_dir, problem_info["title"], ("test_case_score", index, key),
                                         f"testcase 폴더에 {item[key]} 파일이 없습니다")

    def check_display_id(self, problem_info, problem_dir, display_ids):
        display_id = problem_info["display_id"]
        if display_id in display_ids:
            self.add_field_error(problem_dir, problem_info["title"], ("display_id",),
                                 f"{display_ids[display_id]} 폴더의 문제와 Problem ID '{display_id}'가 겹칩니다")
        elif Problem.objects.filter(_id=display_id).exists():
            self.add_field_error(problem_dir, problem_info["title"], ("display_id",),
                                 f"Problem ID '{display_id}'인 문제가 이미 있습니다")
        display_ids.setdefault(display_id, problem_dir)

    def save_images(self, zip_file, problem_info, images):
        urls = {}
        for src, path in images.items():
            name = rand_str(10) + os.path.splitext(src)[-1].lower()
            target_path = os.path.join(settings.UPLOAD_DIR, name)
            self.created_files.append(target_path)
            with zip_file.open(path) as source, open(target_path, "wb") as target:
                shutil.copyfileobj(source, target)
            urls[src] = f"{settings.UPLOAD_PREFIX}/{name}"
        for field in self.image_fields:
            value = problem_info[field]["value"]
            for start, end, text, attrs, src in reversed(self.find_image_tags(value)):
                attrs_html = "".join(
                    f" {key}" if key != "src" and val is None
                    else f' {key}="{html.escape(urls[src] if key == "src" else val)}"'
                    for key, val in attrs)
                closing = " />" if text.rstrip().endswith("/>") else ">"
                value = f"{value[:start]}<img{attrs_html}{closing}{value[end:]}"
            problem_info[field]["value"] = value

    def post(self, request):
        self.created_files = []
        try:
            return self.import_problems(request)
        except Exception:
            for path in self.created_files:
                if os.path.isdir(path):
                    shutil.rmtree(path, ignore_errors=True)
                elif os.path.exists(path):
                    os.remove(path)
            raise

    def import_problems(self, request):
        form = UploadProblemForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data["file"]
            tmp_file = f"/tmp/{rand_str()}.zip"
            with open(tmp_file, "wb") as f:
                for chunk in file:
                    f.write(chunk)
        else:
            self.fail("업로드할 zip 파일을 선택해주세요")

        try:
            zip_file = zipfile.ZipFile(tmp_file, "r")
        except zipfile.BadZipFile:
            self.fail("올바른 zip 파일이 아닙니다")

        count = 0
        self.errors = []
        display_ids = {}
        with zip_file:
            name_list = zip_file.namelist()
            if "problem.json" in name_list:
                self.fail("problem.json은 문제 폴더 안에 있어야 합니다 (예: 1/problem.json)")

            # 공백이 있는 경우도 처리할 수 있도록 수정
            problem_dirs = set()
            for name in name_list:
                parts = name.split('/')
                if len(parts) >= 2 and parts[-1] == 'problem.json':
                    problem_dirs.add('/'.join(parts[:-1]))
            missing_dirs = self.find_dirs_without_problem_json(name_list, problem_dirs)
            if not problem_dirs and not missing_dirs:
                self.fail("zip에 problem.json이 없습니다")
            for problem_dir in missing_dirs:
                self.add_error(problem_dir, "", "problem.json", "problem.json 파일이 없습니다")

            with transaction.atomic():
                for problem_dir in sorted(problem_dirs, key=natural_sort_key):
                    if self.import_problem(request, zip_file, tmp_file, problem_dir, name_list, display_ids):
                        count += 1
                if self.errors:
                    problem_count = len({error["dir"] for error in self.errors})
                    raise APIError({"message": f"{problem_count}개 문제에서 {len(self.errors)}개 오류가 발생했습니다",
                                    "errors": self.errors})
        return self.success({"import_count": count})

    def find_dirs_without_problem_json(self, name_list, problem_dirs):
        dirs = set()
        for name in name_list:
            parts = name.split("/")
            if parts[0] == "__MACOSX":
                continue
            for index, part in enumerate(parts[:-1]):
                if part in ("testcase", "images"):
                    dirs.add("/".join(parts[:index]))
                    break
            else:
                if len(parts) >= 2:
                    dirs.add(parts[0])
        return sorted((d for d in dirs if d and d not in problem_dirs
                       and not any(p.startswith(d + "/") for p in problem_dirs)), key=natural_sort_key)

    def import_problem(self, request, zip_file, tmp_file, problem_dir, name_list, display_ids):
        try:
            with zip_file.open(f"{problem_dir}/problem.json") as f:
                text = f.read().decode("utf-8-sig")
        except UnicodeDecodeError:
            self.add_error(problem_dir, "", "problem.json", "UTF-8로 인코딩된 파일이 아닙니다")
            return False
        try:
            raw_info = json.loads(text)
        except json.JSONDecodeError as e:
            reason = self.json_error_messages.get(e.msg, e.msg)
            self.add_error(problem_dir, "", "problem.json", f"JSON 문법 오류: {reason}", line=e.lineno,
                           column=e.colno, detail=self.code_snippet(text, e.lineno, e.colno))
            return False

        self.problem_text = text
        title = raw_info.get("title") if isinstance(raw_info, dict) else None
        title = title if isinstance(title, str) else ""
        serializer = ImportProblemSerializer(data=raw_info)
        with translation.override("ko"):
            valid = serializer.is_valid()
        if not valid:
            for path, message in self.flatten_errors(serializer.errors):
                self.add_field_error(problem_dir, title, path, str(message))
            return False

        problem_info = serializer.data
        for item in problem_info["template"].keys():
            if item not in SysOptions.language_names:
                self.add_field_error(problem_dir, title, ("template", item), f"지원하지 않는 언어입니다 ({item})")

        problem_info["display_id"] = problem_info["display_id"][:24]
        for k, v in problem_info["template"].items():
            problem_info["template"][k] = build_problem_template(v["prepend"], v["template"], v["append"])

        test_cases = self.check_test_cases(problem_info, problem_dir, name_list)
        self.check_test_case_score(problem_info, problem_dir, test_cases)
        images = self.collect_images(problem_info, problem_dir, name_list)
        self.check_display_id(problem_info, problem_dir, display_ids)
        if self.errors:
            return False

        spj = problem_info["spj"] is not None
        rule_type = problem_info["rule_type"]
        test_case_score = problem_info["test_case_score"]

        # process test case
        _, test_case_id = self.process_zip(tmp_file, spj=spj, dir=f"{problem_dir}/testcase/")
        self.created_files.append(os.path.join(settings.TEST_CASE_DIR, test_case_id))
        self.save_images(zip_file, problem_info, images)

        problem_obj = Problem.objects.create(
            _id=problem_info["display_id"],
            title=problem_info["title"],
            description=problem_info["description"]["value"],
            input_description=problem_info["input_description"]["value"],
            output_description=problem_info["output_description"]["value"],
            hint=problem_info["hint"]["value"],
            test_case_score=test_case_score if test_case_score else [],
            time_limit=problem_info["time_limit"],
            memory_limit=problem_info["memory_limit"],
            samples=problem_info["samples"],
            template=problem_info["template"],
            rule_type=problem_info["rule_type"],
            source=problem_info["source"],
            spj=spj,
            spj_code=problem_info["spj"]["code"] if spj else None,
            spj_language=problem_info["spj"]["language"] if spj else None,
            spj_version=rand_str(8) if spj else "",
            languages=SysOptions.language_names,
            created_by=request.user,
            visible=True,
            field=problem_info["field"],
            difficulty=get_difficulty(problem_info["difficulty"]),
            total_score=sum(item["score"] for item in test_case_score) if rule_type == ProblemRuleType.OI else 0,
            test_case_id=test_case_id)
        for tag_name in problem_info["tags"]:
            tag_obj, _ = ProblemTag.objects.get_or_create(name=tag_name)
            problem_obj.tags.add(tag_obj)
        return True


class FPSProblemImport(CSRFExemptAPIView):
    request_parsers = ()

    def _create_problem(self, problem_data, creator):
        if problem_data["time_limit"]["unit"] == "ms":
            time_limit = problem_data["time_limit"]["value"]
        else:
            time_limit = problem_data["time_limit"]["value"] * 1000
        template = {}
        prepend = {}
        append = {}
        for t in problem_data["prepend"]:
            prepend[t["language"]] = t["code"]
        for t in problem_data["append"]:
            append[t["language"]] = t["code"]
        for t in problem_data["template"]:
            our_lang = lang = t["language"]
            if lang == "Python":
                our_lang = "Python3"
            template[our_lang] = TEMPLATE_BASE.format(prepend.get(lang, ""), t["code"], append.get(lang, ""))
        spj = problem_data["spj"] is not None
        Problem.objects.create(
            _id=f"fps-{rand_str(4)}",
            title=problem_data["title"],
            description=problem_data["description"],
            input_description=problem_data["input"],
            output_description=problem_data["output"],
            hint=problem_data["hint"],
            test_case_score=problem_data["test_case_score"],
            time_limit=time_limit,
            memory_limit=problem_data["memory_limit"]["value"],
            samples=problem_data["samples"],
            template=template,
            rule_type=ProblemRuleType.ACM,
            source=problem_data.get("source", ""),
            spj=spj,
            spj_code=problem_data["spj"]["code"] if spj else None,
            spj_language=problem_data["spj"]["language"] if spj else None,
            spj_version=rand_str(8) if spj else "",
            visible=False,
            languages=SysOptions.language_names,
            created_by=creator,
            difficulty=Difficulty.MID,
            test_case_id=problem_data["test_case_id"])

    def post(self, request):
        form = UploadProblemForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data["file"]
            with tempfile.NamedTemporaryFile("wb") as tf:
                for chunk in file.chunks(4096):
                    tf.file.write(chunk)

                tf.file.flush()
                os.fsync(tf.file)

                problems = FPSParser(tf.name).parse()
        else:
            return self.error("Parse upload file error")

        helper = FPSHelper()
        with transaction.atomic():
            for _problem in problems:
                test_case_id = rand_str()
                test_case_dir = os.path.join(settings.TEST_CASE_DIR, test_case_id)
                os.mkdir(test_case_dir)
                score = []
                for item in helper.save_test_case(_problem, test_case_dir)["test_cases"].values():
                    score.append({"score": 0, "input_name": item["input_name"], "output_name": item.get("output_name")})
                problem_data = helper.save_image(_problem, settings.UPLOAD_DIR, settings.UPLOAD_PREFIX)
                s = FPSProblemSerializer(data=problem_data)
                if not s.is_valid():
                    return self.error(f"Parse FPS file error: {s.errors}")
                problem_data = s.data
                problem_data["test_case_id"] = test_case_id
                problem_data["test_case_score"] = score
                self._create_problem(problem_data, request.user)
        return self.success({"import_count": len(problems)})
