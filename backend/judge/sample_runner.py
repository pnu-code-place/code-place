"""Run public problem samples without creating submissions or reading private test cases."""
from copy import deepcopy
import re
import signal

from judge.dispatcher import ChooseJudgeServer, DispatcherBase, process_pending_task
from options.options import SysOptions
from problem.utils import parse_problem_template
from submission.models import JudgeStatus


class SampleRunError(Exception):
    pass


class SampleRunJudgeServer(ChooseJudgeServer):
    def has_capacity(self, server):
        return server.task_number < server.cpu_core


class SampleRunner(DispatcherBase):
    DISPLAY_CHAR_LIMIT = 65536
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

    # 채점 서버는 stdout과 stderr를 하나의 output으로 돌려준다.
    # 언어별 에러 시작 표시를 찾아 그 부분만 보여주고, 못 찾으면 출력 대신 종료 원인을 안내한다.
    ERROR_START_PATTERNS = {
        "C": re.compile(r"^.*Assertion `.*' failed\.?$", re.MULTILINE),
        "C++": re.compile(r"^(terminate called .*|.*Assertion `.*' failed\.?)$", re.MULTILINE),
        "Java": re.compile(r"^Exception in thread .*$", re.MULTILINE),
        "Golang": re.compile(r"^(panic: |fatal error: ).*$", re.MULTILINE),
        "JavaScript": re.compile(r"^[A-Za-z_$][\w$]*(Error|Exception)\b.*\n {4}at ", re.MULTILINE),
    }
    SIGNAL_MESSAGES = {
        signal.SIGSEGV: "잘못된 메모리 접근 (SIGSEGV). 배열 범위를 벗어났거나 잘못된 포인터를 사용했는지 확인해주세요.",
        signal.SIGBUS: "잘못된 메모리 접근 (SIGBUS). 잘못된 포인터를 사용했는지 확인해주세요.",
        signal.SIGFPE: "산술 오류 (SIGFPE). 0으로 나누었는지 확인해주세요.",
        signal.SIGABRT: "프로그램이 강제 종료되었습니다 (SIGABRT). assert 실패나 처리되지 않은 예외가 있는지 확인해주세요.",
        signal.SIGKILL: "프로그램이 강제 종료되었습니다 (SIGKILL).",
    }

    @staticmethod
    def _python_traceback(output):
        start = output.rfind("Traceback (most recent call last):")
        if start < 0:
            return ""
        # stdout은 버퍼링되어 traceback 뒤에 붙을 수 있으므로, 들여쓴 줄 다음의 예외 줄까지만 자른다.
        lines = output[start:].splitlines()
        block = [lines[0]]
        for line in lines[1:]:
            block.append(line)
            if line and not line[0].isspace():
                break
        return "\n".join(block)

    @staticmethod
    def _java_stack_trace(output, start):
        # 스택 트레이스(\tat ..., Caused by: ...)가 끝나는 곳까지만 자르고 뒤에 붙은 stdout은 제외한다.
        lines = output[start:].splitlines()
        block = [lines[0]]
        for line in lines[1:]:
            if not (line[:1].isspace() or line.startswith("Caused by: ")):
                break
            block.append(line)
        return "\n".join(block)

    def _exit_reason(self, row):
        signal_number = row.get("signal") or 0
        if signal_number in self.SIGNAL_MESSAGES:
            return self.SIGNAL_MESSAGES[signal_number]
        if signal_number:
            return f"프로그램이 시그널 {signal_number}번으로 비정상 종료되었습니다."
        exit_code = row.get("exit_code")
        if exit_code:
            return f"프로그램이 0이 아닌 종료 코드({exit_code})로 끝났습니다. 정상 종료 시 0을 반환하는지 확인해주세요."
        return "프로그램이 비정상 종료되었습니다."

    def _runtime_error_message(self, row, output):
        if self.language == "Python3":
            diagnostic = self._python_traceback(output)
        else:
            pattern = self.ERROR_START_PATTERNS.get(self.language)
            match = pattern.search(output) if pattern else None
            if not match:
                diagnostic = ""
            elif self.language == "Java":
                diagnostic = self._java_stack_trace(output, match.start())
            else:
                diagnostic = output[match.start():].strip()
        return diagnostic or self._exit_reason(row)

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

        with SampleRunJudgeServer() as server:
            if server is None:
                raise SampleRunError("사용 가능한 실행 서버가 없습니다. 잠시 후 다시 시도해주세요.")
            response = self._request(
                self._get_target_url(server, "/judge"), data=data, timeout=self.REQUEST_TIMEOUT,
            )
        # 슬롯이 비었으니, 실행이 슬롯을 차지하는 동안 대기열에 쌓인 제출을 이어서 채점한다.
        process_pending_task()

        if not isinstance(response, dict):
            raise SampleRunError("실행 서버의 응답을 받지 못했습니다. 다시 시도해주세요.")
        if response.get("err") == "CompileError":
            result["compileError"] = str(response.get("data") or "컴파일 오류가 발생했습니다.")[:self.DISPLAY_CHAR_LIMIT]
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
                "output": "" if case_type == "output_limit" else output[:self.DISPLAY_CHAR_LIMIT],
                "outputTruncated": case_type == "output_limit" or len(output) > self.DISPLAY_CHAR_LIMIT,
                "error": error[:self.DISPLAY_CHAR_LIMIT],
                "time": row.get("cpu_time"),
                # JudgeServer returns bytes; the result panel displays KB/MB.
                "memory": round(row["memory"] / 1024, 2) if row.get("memory") is not None else None,
            })
        return result
