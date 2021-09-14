import datetime
import os
from subprocess import Popen, PIPE, STDOUT, CalledProcessError
from threading import Thread

from octue.cloud import storage
from octue.resources import Datafile


def run(analysis):
    """Run a turbsim analysis on the input file specified in the input manifest, writing the output file to the cloud.

    :param octue.resources.analysis.Analysis analysis:
    :return None:
    """
    start_datetime = datetime.datetime.now()
    input_file = list(analysis.input_manifest.get_dataset("turbsim_input").files)[0]

    output_file = _run_and_log_turbsim(input_file, analysis.logger)
    analysis.output_manifest.get_dataset("turbsim_output").add(output_file)

    _save_output_to_cloud(output_file, start_datetime, analysis.logger)
    analysis.finalise()


def _run_and_log_turbsim(input_file, analysis_logger):
    """Run turbsim and forward any logs and error messages from stdout and stdout to the analysis logger.

    :param octue.resources.datafile.Datafile input_file:
    :param logging.Logger analysis_logger:
    :return octue.resources.datafile.Datafile: output file
    """
    analysis_logger.info("Starting turbulence simulation.")
    command = ["turbsim", input_file.get_local_path()]
    process = Popen(command, stdout=PIPE, stderr=STDOUT)
    Thread(target=_log_lines_from_stream, args=[process.stdout, analysis_logger]).start()
    process.wait()

    if process.returncode != 0:
        raise CalledProcessError(returncode=process.returncode, cmd="".join(command))

    analysis_logger.info("Finished turbulence simulation.")
    return Datafile(path=input_file.get_local_path() + ".bts", labels=["turbsim"])


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


def _log_lines_from_stream(stream, logger):
    """Log lines from the given stream.

    :param io.BufferedReader stream:
    :param logging.Logger logger:
    :return None:
    """
    with stream:
        for line in iter(stream.readline, b''):
            logger.info(line.decode().strip())
