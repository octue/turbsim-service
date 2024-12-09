import os
import unittest
from unittest.mock import patch

from octue import Runner
from octue.configuration import load_service_and_app_configuration
from octue.log_handlers import apply_log_handler
from octue.resources import Dataset, Manifest


apply_log_handler()


REPOSITORY_ROOT = os.path.dirname(os.path.dirname(__file__))


class TestApp(unittest.TestCase):
    def test_with_turbsim_input_file_only(self):
        """Test that the app works with a TurbSim input file only and produces an output manifest with a dataset
        containing a single `.bts` file.
        """
        service_configuration, app_configuration = load_service_and_app_configuration(
            service_configuration_path=os.path.join(REPOSITORY_ROOT, "octue.yaml")
        )

        runner = Runner.from_configuration(
            service_configuration=service_configuration,
            app_configuration=app_configuration,
            project_name=os.environ["TEST_PROJECT_NAME"],
            service_id="octue/turbsim-service:test",
        )

        input_manifest = Manifest(datasets={"turbsim": f"gs://{os.environ['TEST_BUCKET_NAME']}/turbsim"})

        # Mock running an OpenFAST analysis by creating an empty output file.
        with patch("octue.utils.processes.run_logged_subprocess", self._create_mock_output_file):
            analysis = runner.run(input_manifest=input_manifest.serialise())

        self.assertIsNone(analysis.output_values)
        self.assertIsNotNone(analysis.output_manifest)
        self.assertTrue(len(analysis.output_manifest.datasets["turbsim"].files), 1)

        output_dataset = Dataset(path=analysis.output_manifest.datasets["turbsim"].path)

        with output_dataset.files.one() as (datafile, f):
            self.assertEqual(f.read(), "This is a mock TurbSim output file.")

    def test_with_turbsim_input_file_and_profile_file(self):
        """Test that the TurbSim service works when a profile file is provided alongside the input file."""
        service_configuration, app_configuration = load_service_and_app_configuration(
            service_configuration_path=os.path.join(REPOSITORY_ROOT, "octue.yaml")
        )

        runner = Runner.from_configuration(
            service_configuration=service_configuration,
            app_configuration=app_configuration,
            project_name=os.environ["TEST_PROJECT_NAME"],
            service_id="octue/turbsim-service:test",
        )

        input_manifest = Manifest(
            datasets={
                "turbsim": f"gs://{os.environ['TEST_BUCKET_NAME']}/turbsim_with_profile"
            }
        )

        self.assertEqual(len(input_manifest.datasets["turbsim"].files), 2)

        # Mock running an OpenFAST analysis by creating an empty output file.
        with patch("octue.utils.processes.run_logged_subprocess", self._create_mock_output_file):
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
