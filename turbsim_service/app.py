import datetime
import logging
import os

from octue.resources import Datafile, Dataset
from octue.utils.files import RegisteredTemporaryDirectory
from octue.utils.processes import run_logged_subprocess


logger = logging.getLogger(__name__)


OUTPUT_EXTENSION = ".bts"
OUTPUT_FILENAME = "TurbSim" + OUTPUT_EXTENSION


def run(analysis):
    """Run a turbsim analysis on the input file specified in the input manifest, writing the output file to the cloud.

    :param octue.resources.Analysis analysis:
    :return None:
    """
    start_datetime = datetime.datetime.now()

    temporary_directory = RegisteredTemporaryDirectory().name
    input_dataset = analysis.input_manifest.datasets["turbsim"]

    number_of_files = len(input_dataset.files)

    if number_of_files not in {1, 2}:
        raise ValueError(
            "The input dataset should only contain either 1 or 2 input files - a 'TurbSim.inp' file and, optionally, "
            f"a profile or timeseries file; received {number_of_files} files."
        )

    input_dataset.download(temporary_directory)

    input_file = input_dataset.files.filter(name="TurbSim.inp").one()
    logger.info("Starting turbsim analysis.")
    run_logged_subprocess(command=["turbsim", input_file.local_path], logger=logger)

    old_output_filename = os.path.splitext(input_file.local_path)[0] + OUTPUT_EXTENSION

    new_temporary_directory = RegisteredTemporaryDirectory().name
    new_output_filename = os.path.join(new_temporary_directory, OUTPUT_FILENAME)
    os.rename(old_output_filename, new_output_filename)

    # Instantiate a datafile for the output file.
    with Datafile(path=new_output_filename, mode="a") as (datafile, f):
        datafile.timestamp = start_datetime
        datafile.labels = ["turbsim", "output"]

    analysis.output_manifest.datasets["turbsim"] = Dataset(name="turbsim", path=new_temporary_directory)
    logger.info("Finished turbsim analysis.")
