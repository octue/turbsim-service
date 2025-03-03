import os
import unittest

from octue.log_handlers import apply_log_handler
from octue.resources import Child, Manifest

apply_log_handler()


REPOSITORY_ROOT = os.path.dirname(os.path.dirname(__file__))
SRUID = "octue/turbsim-service:0.5.1"
BUCKET_NAME = "octue-octue-twined-services-octue-twined"
PROJECT_NAME = "octue-twined-services"


@unittest.skipUnless(
    condition=os.getenv("RUN_DEPLOYMENT_TESTS", "0").lower() == "1",
    reason="'RUN_DEPLOYMENT_TESTS' environment variable is 0 or not present.",
)
class TestDeployment(unittest.TestCase):
    def test_with_input_file_only(self):
        """Test that the Google Cloud Run integration works, providing a service that can be asked questions and send
        responses. An input dataset from Google Cloud Storage is used for this test.
        """
        child = Child(id=SRUID, backend={"name": "GCPPubSubBackend", "project_name": PROJECT_NAME})

        input_manifest = Manifest(datasets={"turbsim": f"gs://{BUCKET_NAME}/turbsim-service/testing/turbsim"})
        answer, question_uuid = child.ask(input_manifest=input_manifest, timeout=360)

        self.assertIsNone(answer["output_values"])
        self.assertIsNotNone(answer["output_manifest"])
        self.assertTrue(len(answer["output_manifest"].datasets["turbsim"].files), 1)

    def test_with_input_file_and_profile_file(self):
        """Test that the deployed service works with an input file and profile file. An input dataset from Google Cloud
        Storage is used for this test."""
        child = Child(id=SRUID, backend={"name": "GCPPubSubBackend", "project_name": PROJECT_NAME})

        input_manifest = Manifest(
            datasets={"turbsim": f"gs://{BUCKET_NAME}/turbsim-service/testing/turbsim_with_profile"}
        )
        answer, question_uuid = child.ask(input_manifest=input_manifest, timeout=360)

        self.assertIsNone(answer["output_values"])
        self.assertIsNotNone(answer["output_manifest"])
        self.assertTrue(len(answer["output_manifest"].datasets["turbsim"].files), 1)
