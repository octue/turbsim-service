import json
import os
import unittest
from unittest.mock import patch

from octue import Runner
from octue.cloud import storage
from octue.log_handlers import apply_log_handler
from octue.resources import Manifest


apply_log_handler()


REPOSITORY_ROOT = os.path.dirname(os.path.dirname(__file__))
TWINE_PATH = os.path.join(REPOSITORY_ROOT, "twine.json")

with open(os.path.join(REPOSITORY_ROOT, "app_configuration.json")) as f:
    OUTPUT_LOCATION = json.load(f)["output_location"]


class TestApp(unittest.TestCase):
    def test_app(self):
        """Test that the app takes input and produces an output manifest with a dataset containing a single `.bts` file."""
        runner = Runner(app_src=REPOSITORY_ROOT, twine=TWINE_PATH)

        input_manifest = Manifest(
            datasets={"turbsim": storage.path.generate_gs_path("openfast-data", "testing", "turbsim")}
        )

        # Mock running an OpenFAST analysis by creating an empty output file.
        with patch("app.run_subprocess_and_log_stdout_and_stderr", self._create_mock_output_file):
            analysis = runner.run(input_manifest=input_manifest.serialise(), output_location=OUTPUT_LOCATION)

        self.assertIsNone(analysis.output_values)
        self.assertIsNotNone(analysis.output_manifest)
        self.assertTrue(len(analysis.output_manifest.datasets["turbsim"].files), 1)

        with analysis.output_manifest.datasets["turbsim"].files.one() as (datafile, f):
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
