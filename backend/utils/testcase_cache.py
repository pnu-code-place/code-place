import logging
import json
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger(__name__)


class TestCaseCacheManager:
    CACHE_PREFIX = "testcase"
    DEFAULT_TIMEOUT = 60 * 60  # 1 시간

    @classmethod
    def _get_cache_key(cls, testcase_dir: str, testcase_idx: int):
        return f"{cls.CACHE_PREFIX}:{testcase_dir}:{testcase_idx}"

    @classmethod
    def get_testcase(cls, testcase_dir: str, testcase_idx: int):
        cache_key = cls._get_cache_key(testcase_dir, testcase_idx)

        testcase_data = cache.get(cache_key)
        if testcase_data:
            return json.loads(testcase_data) if isinstance(testcase_data, str) else testcase_data

        testcase_data = cls._read_testcase_from_file(testcase_dir, testcase_idx)
        if testcase_data:
            cache.set(cache_key, json.dumps(testcase_data), cls.DEFAULT_TIMEOUT)

        return testcase_data

    @classmethod
    def _read_testcase_from_file(cls, testcase_dir: str, testcase_idx: int):
        input_file_path = f"{settings.TEST_CASE_DIR}/{testcase_dir}/{testcase_idx}.in"
        output_file_path = f"{settings.TEST_CASE_DIR}/{testcase_dir}/{testcase_idx}.out"

        try:
            with open(input_file_path, 'r', encoding='utf-8') as f:
                input_data = f.read()

            with open(output_file_path, 'r', encoding='utf-8') as f:
                output_data = f.read()
        except (FileNotFoundError, IOError) as e:
            logger.error(f"Failed to read testcase file: {e}")
            return None

        return {'input': input_data, 'output': output_data}
