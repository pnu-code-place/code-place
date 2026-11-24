"""Run public problem samples without creating submissions or reading private test cases."""
from copy import deepcopy
import signal

from judge.dispatcher import ChooseJudgeServer, DispatcherBase
from options.options import SysOptions
from problem.utils import parse_problem_template
from submission.models import JudgeStatus


class SampleRunError(Exception):
    pass


class SampleRunner(DispatcherBase):
    OUTPUT_LIMIT = 64 * 1024
    REQUEST_TIMEOUT = 60
    JUDGE_MIN_OUTPUT_LIMIT = 16 * 1024 * 1024
    RESULT_TYPES = {
        JudgeStatus.ACCEPTED: "accepted",
        JudgeStatus.WRONG_ANSWER: "wrong_answer",
        JudgeStatus.CPU_TIME_LIMIT_EXCEEDED: "time_limit",
        JudgeStatus.REAL_TIME_LIMIT_EXCEEDED: "time_limit",
        JudgeStatus.MEMORY_LIMIT_EXCEEDED: "memory_limit",
        JudgeStatus.RUNTIME_ERROR: "runtime_error",
        JudgeStatus.SYSTEM_ERROR: "system_error",
    }

    def __init__(self, problem, language, code):
        super().__init__()
        self.problem = problem
        self.language = language
        self.code = code

    def _case_type(self, row, sample):
        case_type = self.RESULT_TYPES.get(row.get("result"))
        if case_type != "runtime_error":
            return case_type
        output = row.get("output") or ""
        output_limit = max(self.JUDGE_MIN_OUTPUT_LIMIT, len(sample["output"].encode("utf-8")) * 2)
        if row.get("signal") == signal.SIGXFSZ or len(output.encode("utf-8")) >= output_limit:
            return "output_limit"
        if self.language == "Python3" and "OSError: [Errno 27] File too large" in output:
            return "output_limit"
        return case_type

    def _runtime_error_message(self, row, output):
        fallback = f"프로그램이 비정상 종료되었습니다. (종료 코드: {row.get('exit_code')}, 시그널: {row.get('signal')})"
        if self.language == "Python3":
            traceback = output.rfind("Traceback (most recent call last):")
            return output[traceback:] if traceback >= 0 else fallback
        return output or fallback

    def run(self):
        samples = deepcopy(self.problem.samples)
        result = {
            "timeLimit": self.problem.time_limit,
            "memoryLimit": self.problem.memory_limit,
            "cases": [],
        }
        if not samples:
            return result

        language = next((item for item in SysOptions.languages if item["name"] == self.language), None)
        if language is None:
            raise SampleRunError("지원하지 않는 실행 언어입니다.")

        code = self.code
        if self.language in self.problem.template:
            template = parse_problem_template(self.problem.template[self.language])
            code = f"{template['prepend']}\n{code}\n{template['append']}"

        data = {
            "language_config": deepcopy(language["config"]),
            "src": code,
            "max_cpu_time": self.problem.time_limit,
            "max_memory": self.problem.memory_limit * 1024 * 1024,
            "test_case": [{"input": sample["input"], "output": sample["output"]} for sample in samples],
            "output": True,
            "io_mode": self.problem.io_mode,
        }
        if self.problem.spj:
            spj_language = next((item for item in SysOptions.spj_languages if item["name"] == self.problem.spj_language), None)
            if spj_language is None:
                raise SampleRunError("스페셜 저지 실행 설정을 찾을 수 없습니다.")
            data.update({
                "spj_version": self.problem.spj_version,
                "spj_config": deepcopy(spj_language["spj"]["config"]),
                "spj_compile_config": deepcopy(spj_language["spj"]["compile"]),
                "spj_src": self.problem.spj_code,
            })

        with ChooseJudgeServer() as server:
            if server is None:
                raise SampleRunError("사용 가능한 실행 서버가 없습니다. 잠시 후 다시 시도해주세요.")
            response = self._request(
                self._get_target_url(server, "/judge"), data=data, timeout=self.REQUEST_TIMEOUT,
            )

        if not isinstance(response, dict):
            raise SampleRunError("실행 서버의 응답을 받지 못했습니다. 다시 시도해주세요.")
        if response.get("err") == "CompileError":
            result["compileError"] = str(response.get("data") or "컴파일 오류가 발생했습니다.")[:self.OUTPUT_LIMIT]
            return result
        if response.get("err") or not isinstance(response.get("data"), list):
            raise SampleRunError("예제 실행 중 서버 오류가 발생했습니다. 다시 시도해주세요.")

        try:
            rows = {int(row["test_case"]): row for row in response["data"]}
        except (KeyError, TypeError, ValueError):
            raise SampleRunError("예제 실행 결과가 올바르지 않습니다. 다시 시도해주세요.")
        if len(response["data"]) != len(samples) or set(rows) != set(range(1, len(samples) + 1)):
            raise SampleRunError("예제 실행 결과가 누락되었습니다. 다시 시도해주세요.")

        for index, sample in enumerate(samples, 1):
            row = rows[index]
            case_type = self._case_type(row, sample)
            if case_type is None:
                raise SampleRunError("예제 실행 결과가 올바르지 않습니다. 다시 시도해주세요.")
            output = row.get("output") or ""
            error = ""
            if case_type == "runtime_error":
                error = self._runtime_error_message(row, output)
            elif case_type == "system_error":
                error = "예제 실행 중 채점 서버 오류가 발생했습니다. 다시 시도해주세요."
            result["cases"].append({
                "type": case_type,
                "input": sample["input"],
                "expected": sample["output"],
                "output": "" if case_type == "output_limit" else output[:self.OUTPUT_LIMIT],
                "outputTruncated": case_type == "output_limit" or len(output) > self.OUTPUT_LIMIT,
                "error": error[:self.OUTPUT_LIMIT],
                "time": row.get("cpu_time"),
                # JudgeServer returns bytes; the result panel displays KB/MB.
                "memory": round(row["memory"] / 1024, 2) if row.get("memory") is not None else None,
            })
        return result
