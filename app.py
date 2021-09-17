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
    input_file = list(analysis.input_manifest.get_dataset("turbsim").files)[0]

    analysis.logger.info("Starting turbulence simulation.")
    run_subprocess_and_log_stdout_and_stderr(command=["turbsim", input_file.local_path], logger=analysis.logger)
    analysis.logger.info("Finished turbulence simulation.")

    # Get the output file and add it to the output dataset.
    output_file = Datafile(path=input_file.local_path + ".bts", timestamp=start_datetime, labels=["turbsim", "output"])

    analysis.output_manifest.get_dataset("turbsim").add(output_file)

    # Upload the output file to the cloud.
    output_file.to_cloud(
        project_name=os.environ["PROJECT_NAME"],
        cloud_path=storage.path.generate_gs_path(
            os.environ["BUCKET_NAME"], "turbsim", f"TurbSim-{start_datetime.isoformat().replace(':', '-')}.bts")
    )

    analysis.logger.info(f"Output saved to {output_file.cloud_path}.")

    # Validate the output manifest.
    analysis.finalise()
