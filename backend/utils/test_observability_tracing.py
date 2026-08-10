import os
import unittest
from unittest.mock import patch

from utils import observability_tracing


class ObservabilityResourceContractTest(unittest.TestCase):

    def test_telemetry_environment_is_independent_from_django_environment(self):
        with patch.dict(
            os.environ,
            {
                "OJ_ENV": "production",
                "OTEL_DEPLOYMENT_ENVIRONMENT": "prod",
            },
            clear=True,
        ):
            environment = observability_tracing.get_deployment_environment()

        self.assertEqual(environment, "prod")

    def test_service_name_override_wins_over_import_order_default(self):
        with patch.dict(
            os.environ,
            {"OTEL_SERVICE_NAME": "codeplace-backend"},
            clear=True,
        ):
            service_name = observability_tracing.get_service_name("codeplace-celery")

        self.assertEqual(service_name, "codeplace-backend")


if __name__ == "__main__":
    unittest.main()
