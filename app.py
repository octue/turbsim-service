import datetime
import logging
import os

import coolname
from octue.cloud import storage
from octue.resources import Datafile, Dataset
from octue.utils.processes import run_subprocess_and_log_stdout_and_stderr


logger = logging.getLogger(__name__)


def run(analysis):
    """Run a turbsim analysis on the input file specified in the input manifest, writing the output file to the cloud.

    :param octue.resources.Analysis analysis:
    :return None:
    """
    start_datetime = datetime.datetime.now()
    input_file = analysis.input_manifest.datasets["turbsim"].files.one()

    logger.info("Starting turbsim analysis.")
    run_subprocess_and_log_stdout_and_stderr(command=["turbsim", input_file.local_path], logger=logger)

    output_file = Datafile(
        path=os.path.splitext(input_file.local_path)[0] + ".bts",
        timestamp=start_datetime,
        labels=["turbsim", "output"],
    )

    analysis.output_manifest.datasets["turbsim"] = Dataset(path=os.path.dirname(input_file.local_path))
    analysis.output_manifest.datasets["turbsim"].add(output_file)

    analysis.finalise(upload_output_datasets_to=storage.path.join(analysis.output_location, coolname.generate_slug()))
    logger.info("Finished turbsim analysis.")
