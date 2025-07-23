import logging
import json
from typing import Dict, Optional
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger(__name__)


class TestCaseCacheManager:
    """테스트 케이스의 Input/Output을 캐싱하는 클래스입니다."""

    CACHE_PREFIX = "testcase"
    DEFAULT_TIMEOUT = 60 * 60  # 1 시간

    @classmethod
    def _get_cache_key(cls, testcase_dir: str, testcase_idx: int) -> str:
        """캐시 키를 생성합니다.

        캐시 키는 'testcase:테스트케이스_디렉토리:테스트케이스_인덱스' 형식입니다.

        Args:
            testcase_dir: 테스트 케이스 디렉토리 이름
            testcase_idx: 테스트 케이스 인덱스

        Returns:
            str: 생성된 캐시 키
        """
        return f"{cls.CACHE_PREFIX}:{testcase_dir}:{testcase_idx}"

    @classmethod
    def get_testcase(cls, testcase_dir: str, testcase_idx: int) -> Optional[Dict[str, str]]:
        """캐시에서 테스트 케이스의 Input/Output을 가져옵니다.

        캐시에 존재하지 않는 경우, 파일에서 읽어와 캐시에 저장합니다.

        Args:
            testcase_dir: 테스트 케이스 디렉토리 이름
            testcase_idx: 테스트 케이스 인덱스

        Returns:
            Optional[Dict[str, str]]: 테스트 케이스의 Input/Output 데이터. 
            캐시에 존재하지 않거나 파일을 읽는 데 실패한 경우 None을 반환합니다.
        """
        cache_key = cls._get_cache_key(testcase_dir, testcase_idx)

        testcase_data = cache.get(cache_key)
        if testcase_data:
            return json.loads(testcase_data) if isinstance(testcase_data, str) else testcase_data

        testcase_data = cls._read_testcase_from_file(testcase_dir, testcase_idx)
        if testcase_data:
            cache.set(cache_key, json.dumps(testcase_data), cls.DEFAULT_TIMEOUT)

        return testcase_data

    @classmethod
    def _read_testcase_from_file(cls, testcase_dir: str, testcase_idx: int) -> Optional[Dict[str, str]]:
        """파일에서 테스트 케이스의 Input/Output을 읽어옵니다.

        Args:
            testcase_dir: 테스트 케이스 디렉토리 이름
            testcase_idx: 테스트 케이스 인덱스

        Returns:
            Optional[Dict[str, str]]: 테스트 케이스의 Input/Output 데이터. 
            파일을 읽는 데 실패한 경우 None을 반환합니다.
        """

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
