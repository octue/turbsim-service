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

    cloud_path = storage.path.generate_gs_path(
        os.environ["BUCKET_NAME"], "turbsim", f"TurbSim-{start_datetime.isoformat().replace(':', '-')}.bts"
    )

    # Upload the output file to the cloud.
    storage.client.GoogleCloudStorageClient(os.environ["PROJECT_NAME"]).upload_file(
        local_path=input_file.local_path + ".bts",
        cloud_path=cloud_path,
    )
    analysis.logger.info(f"Output saved to {cloud_path}.")

    # Get the output file and add it to the output dataset.
    output_file = Datafile(path=cloud_path, project_name=os.environ["PROJECT_NAME"], timestamp=start_datetime, labels=["turbsim", "output"])
    analysis.output_manifest.get_dataset("turbsim").add(output_file)

    # Validate the output manifest.
    analysis.finalise()
