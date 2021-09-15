import datetime
import os

from octue.cloud import storage
from octue.resources import Datafile
from octue.utils.processes import run_subprocess_and_log_stdout_and_stderr


def run(analysis):
    """Run a turbsim analysis on the input file specified in the input manifest, writing the output file to the cloud.

    :param octue.resources.analysis.Analysis analysis:
    :return None:
    """
    start_datetime = datetime.datetime.now()
    input_file = list(analysis.input_manifest.get_dataset("turbsim_input").files)[0]

    analysis.logger.info("Starting turbulence simulation.")
    run_subprocess_and_log_stdout_and_stderr(command=["turbsim", input_file.get_local_path()], logger=analysis.logger)
    analysis.logger.info("Finished turbulence simulation.")

    output_file = Datafile(path=input_file.get_local_path() + ".bts", labels=["turbsim"])
    analysis.output_manifest.get_dataset("turbsim_output").add(output_file)

    _save_output_to_cloud(output_file, start_datetime, analysis.logger)
    analysis.finalise()


def _save_output_to_cloud(output_file, start_datetime, analysis_logger):
    """Save the output file to the cloud. This is temporary until https://github.com/octue/octue-sdk-python/pull/205 is
    merged - then it should be able to be dealt with by the `analysis.finalise` method.

    :param octue.resources.datafile.Datafile output_file:
    :param datetime.datetime start_datetime:
    :param logging.Logger analysis_logger:
    :return None:
    """
    output_cloud_path = storage.path.generate_gs_path(
        os.environ["BUCKET_NAME"],
        "turbsim",
        f"TurbSim-{start_datetime.isoformat().replace(':', '-')}.bts"
    )

    analysis_logger.info(f"Attempting to save output to {output_cloud_path}.")
    output_file.to_cloud(project_name=os.environ["PROJECT_NAME"], cloud_path=output_cloud_path)
    output_file.path = output_cloud_path
    analysis_logger.info("Output saved.")
