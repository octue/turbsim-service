import os
import unittest

from octue.resources import Datafile, Manifest, Dataset, Child
from octue.cloud import storage


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
        service_id = "octue.services.c3b47b47-cdfa-433d-b5a8-47a58f3bf7cb"

        input_manifest = Manifest(
            datasets={"turbsim": storage.path.generate_gs_path("openfast-data", "testing", "turbsim")}
        )

        child = Child(
            name="turbsim-service",
            id=service_id,
            backend={"name": "GCPPubSubBackend", "project_name": project_name},
        )

        answer = child.ask(input_manifest=input_manifest, timeout=360)

        self.assertIsNone(answer["output_values"])
        self.assertIsNotNone(answer["output_manifest"])

        output_file = list(answer['output_manifest'].datasets[0].files)[0]
        self.assertIn("turbsim", output_file.labels)

        storage.client.GoogleCloudStorageClient(project_name).delete(cloud_path=output_file.absolute_path)
