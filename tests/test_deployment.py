import os
import unittest
from octue.cloud.pub_sub.service import Service
from octue.resources.service_backends import GCPPubSubBackend
from octue.resources import Datafile, Manifest, Dataset
from octue.cloud import storage


class TestDeployment(unittest.TestCase):

    @unittest.skipUnless(
        condition=os.getenv("RUN_DEPLOYMENT_TESTS", "").lower() == "true",
        reason="'RUN_DEPLOYMENT_TESTS' environment variable is False or not present.",
    )
    def test_cloud_run_integration(self):
        """Test that the Google Cloud Run integration works, providing a service that can be asked questions and send
        responses. An input dataset from Google Cloud Storage is used for this test.
        """
        PROJECT_NAME = os.environ["TEST_PROJECT_NAME"]
        SERVICE_ID = "octue.services.c3b47b47-cdfa-433d-b5a8-47a58f3bf7cb"

        input_file = Datafile(
            path=storage.path.generate_gs_path(os.environ["TEST_BUCKET_NAME"], "testing", "TurbSim.inp"),
            project_name=PROJECT_NAME,
        )

        input_manifest = Manifest(
            datasets=[Dataset(name="turbsim_input", files=[input_file])],
            keys={"turbsim_input": 0},
        )

        asker = Service(backend=GCPPubSubBackend(project_name=PROJECT_NAME))
        subscription, _ = asker.ask(service_id=SERVICE_ID, input_manifest=input_manifest)
        answer = asker.wait_for_answer(subscription, timeout=100000)

        self.assertIsNone(answer["output_values"])
        self.assertIsNotNone(answer["output_manifest"])
        self.assertIn("turbsim", list(answer['output_manifest'].datasets[0].files)[0].labels)
