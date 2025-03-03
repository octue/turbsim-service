import os
import tempfile
import unittest
from unittest.mock import patch

from octue import Runner
from octue.configuration import load_service_and_app_configuration
from octue.log_handlers import apply_log_handler
from octue.resources import Dataset, Manifest

apply_log_handler()


REPOSITORY_ROOT = os.path.dirname(os.path.dirname(__file__))
BUCKET_NAME = "octue-octue-twined-services-octue-twined"
PROJECT_NAME = "octue-twined-services"


class TestApp(unittest.TestCase):
    def test_error_raised_if_input_dataset_empty(self):
        """Test that an error is raised if the input dataset is empty."""
        with tempfile.TemporaryDirectory() as temporary_directory:
            service_configuration, app_configuration = load_service_and_app_configuration(
                service_configuration_path=os.path.join(REPOSITORY_ROOT, "octue.yaml")
            )

            runner = Runner.from_configuration(
                service_configuration=service_configuration,
                app_configuration=app_configuration,
                project_name=PROJECT_NAME,
                service_id="octue/turbsim-service:test",
            )

            input_manifest = Manifest(datasets={"turbsim": temporary_directory})

            with self.assertRaises(ValueError):
                runner.run(input_manifest=input_manifest.serialise())

    def test_error_raised_if_input_dataset_has_more_than_two_files(self):
        """Test that an error is raised if the input dataset has more than two files."""
        with tempfile.TemporaryDirectory() as temporary_directory:
            for i in range(3):
                with open(os.path.join(temporary_directory, f"file_{i}"), "w") as f:
                    f.write("Hello")

            service_configuration, app_configuration = load_service_and_app_configuration(
                service_configuration_path=os.path.join(REPOSITORY_ROOT, "octue.yaml")
            )

            runner = Runner.from_configuration(
                service_configuration=service_configuration,
                app_configuration=app_configuration,
                project_name=PROJECT_NAME,
                service_id="octue/turbsim-service:test",
            )

            input_manifest = Manifest(datasets={"turbsim": temporary_directory})

            with self.assertRaises(ValueError):
                runner.run(input_manifest=input_manifest.serialise())

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
            project_name=PROJECT_NAME,
            service_id="octue/turbsim-service:test",
        )

        input_manifest = Manifest(datasets={"turbsim": f"gs://{BUCKET_NAME}/turbsim-service/testing/turbsim"})

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
            project_name=PROJECT_NAME,
            service_id="octue/turbsim-service:test",
        )

        input_manifest = Manifest(
            datasets={"turbsim": f"gs://{BUCKET_NAME}/turbsim-service/testing/turbsim_with_profile"}
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
