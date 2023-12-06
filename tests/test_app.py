import json
import os
import unittest
from unittest.mock import patch

from octue import Runner
from octue.cloud import storage
from octue.log_handlers import apply_log_handler
from octue.resources import Dataset, Manifest


apply_log_handler()


REPOSITORY_ROOT = os.path.dirname(os.path.dirname(__file__))
TWINE_PATH = os.path.join(REPOSITORY_ROOT, "twine.json")

with open(os.path.join(REPOSITORY_ROOT, "app_configuration.json")) as f:
    OUTPUT_LOCATION = storage.path.join(json.load(f)["output_location"], "testing", "turbsim")


class TestApp(unittest.TestCase):
    def test_app(self):
        """Test that the app takes input and produces an output manifest with a dataset containing a single `.bts` file."""
        runner = Runner(app_src=REPOSITORY_ROOT, twine=TWINE_PATH, output_location=OUTPUT_LOCATION)

        input_manifest = Manifest(datasets={"turbsim": f"gs://{os.environ['TEST_BUCKET_NAME']}/turbsim"})

        # Mock running an OpenFAST analysis by creating an empty output file.
        with patch("app.run_logged_subprocess", self._create_mock_output_file):
            analysis = runner.run(input_manifest=input_manifest.serialise())

        self.assertIsNone(analysis.output_values)
        self.assertIsNotNone(analysis.output_manifest)
        self.assertTrue(len(analysis.output_manifest.datasets["turbsim"].files), 1)

        output_dataset = Dataset(path=analysis.output_manifest.datasets["turbsim"].path)

        with output_dataset.files.one() as (datafile, f):
            self.assertEqual(f.read(), "This is a mock TurbSim output file.")

    @staticmethod
    def _create_mock_output_file(command, logger):
        """Create a mock TurbSim output file.

        :param list(str) command:
        :param logging.Logger logger:
        :return None:
        """
        with open(os.path.splitext(command[1])[0] + ".bts", "w") as f:
            f.write("This is a mock TurbSim output file.")
