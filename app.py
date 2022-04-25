import datetime
import logging
import os
import shutil

import coolname
from octue.cloud import storage
from octue.resources import Datafile, Dataset
from octue.utils.processes import run_subprocess_and_log_stdout_and_stderr


logger = logging.getLogger(__name__)


OUTPUT_FILENAME = "TurbSim.bts"


def run(analysis):
    """Run a turbsim analysis on the input file specified in the input manifest, writing the output file to the cloud.

    :param octue.resources.Analysis analysis:
    :return None:
    """
    start_datetime = datetime.datetime.now()

    input_dataset = analysis.input_manifest.datasets["turbsim"]
    input_dataset.download_all_files()
    input_file = input_dataset.files.one()

    logger.info("Starting turbsim analysis.")
    run_subprocess_and_log_stdout_and_stderr(command=["turbsim", input_file.local_path], logger=logger)

    original_output_file_path = os.path.splitext(input_file.local_path)[0] + ".bts"
    new_output_file_path = os.path.join(os.path.split(input_file.local_path)[0], OUTPUT_FILENAME)

    if original_output_file_path != new_output_file_path:
        shutil.copy(original_output_file_path, new_output_file_path)

    # Instantiate a datafile for the output file (it has the same name as the input file but with a ".bts" extension).
    output_file = Datafile(
        path=os.path.splitext(input_file.local_path)[0] + ".bts",
        timestamp=start_datetime,
        labels=["turbsim", "output"],
    )

    analysis.output_manifest.datasets["turbsim"] = Dataset(path=os.path.dirname(input_file.local_path))
    analysis.output_manifest.datasets["turbsim"].add(output_file)

    analysis.finalise(upload_output_datasets_to=storage.path.join(analysis.output_location, coolname.generate_slug()))
    logger.info("Finished turbsim analysis.")
