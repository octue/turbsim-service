import os
import unittest

from octue.log_handlers import apply_log_handler
from octue.resources import Child, Manifest


apply_log_handler()


REPOSITORY_ROOT = os.path.dirname(os.path.dirname(__file__))
SRUID = "octue/turbsim-service:refs-pull-2-merg"


class TestDeployment(unittest.TestCase):
    @unittest.skipUnless(
        condition=os.getenv("RUN_DEPLOYMENT_TESTS", "0").lower() == "1",
        reason="'RUN_DEPLOYMENT_TESTS' environment variable is 0 or not present.",
    )
    def test_cloud_run_deployment(self):
        """Test that the Google Cloud Run integration works, providing a service that can be asked questions and send
        responses. An input dataset from Google Cloud Storage is used for this test.
        """
        input_manifest = Manifest(datasets={"turbsim": f"gs://{os.environ['TEST_BUCKET_NAME']}/turbsim"})

        child = Child(id=SRUID, backend={"name": "GCPPubSubBackend", "project_name": os.environ["TEST_PROJECT_NAME"]})
        answer = child.ask(input_manifest=input_manifest, timeout=360)

        self.assertIsNone(answer["output_values"])
        self.assertIsNotNone(answer["output_manifest"])
        self.assertTrue(len(answer["output_manifest"].datasets["turbsim"].files), 1)
