import os
import unittest

from octue.log_handlers import apply_log_handler
from octue.resources import Child, Manifest


apply_log_handler()


REPOSITORY_ROOT = os.path.dirname(os.path.dirname(__file__))


class TestDeployment(unittest.TestCase):
    @unittest.skipUnless(
        condition=os.getenv("RUN_DEPLOYMENT_TESTS", "0").lower() == "1",
        reason="'RUN_DEPLOYMENT_TESTS' environment variable is 0 or not present.",
    )
    def test_cloud_run_integration(self):
        """Test that the Google Cloud Run integration works, providing a service that can be asked questions and send
        responses. An input dataset from Google Cloud Storage is used for this test.
        """
        project_name = os.environ["TEST_PROJECT_NAME"]
        service_id = "aerosense/turbsim-service"

        input_manifest = Manifest(datasets={"turbsim": "gs://openfast-data/testing/turbsim"})

        child = Child(
            name="turbsim-service",
            id=service_id,
            backend={"name": "GCPPubSubBackend", "project_name": project_name},
        )

        answer = child.ask(input_manifest=input_manifest, timeout=360)

        self.assertIsNone(answer["output_values"])
        self.assertIsNotNone(answer["output_manifest"])
        self.assertTrue(len(answer["output_manifest"].datasets["turbsim"].files), 1)
