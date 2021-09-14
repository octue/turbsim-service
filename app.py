import datetime
import os
from subprocess import Popen, PIPE, STDOUT, CalledProcessError
from threading import Thread

from octue.cloud import storage
from octue.resources import Datafile


def run(analysis):
    start_datetime = datetime.datetime.now()
    input_file = list(analysis.input_manifest.get_dataset("turbsim_input").files)[0]

    output_file = _run_and_log_turbsim(analysis, input_file)
    analysis.output_manifest.get_dataset("turbsim_output").add(output_file)

    _save_output_to_cloud(analysis, output_file, start_datetime)
    analysis.finalise()


def _run_and_log_turbsim(analysis, input_file):
    analysis.logger.info("Starting turbulence simulation.")
    command = ["turbsim", input_file.get_local_path()]
    process = Popen(command, stdout=PIPE, stderr=STDOUT)
    Thread(target=_log_lines_from_stream, args=[process.stdout, analysis.logger]).start()
    process.wait()

    if process.returncode != 0:
        raise CalledProcessError(returncode=process.returncode, cmd="".join(command))

    analysis.logger.info("Finished turbulence simulation.")
    return Datafile(path=input_file.get_local_path() + ".bts", labels=["turbsim"])


def _save_output_to_cloud(analysis, output_file, start_datetime):
    output_cloud_path = storage.path.generate_gs_path(
        os.environ["BUCKET_NAME"],
        "turbsim",
        f"TurbSim-{start_datetime.isoformat().replace(':', '-')}.bts"
    )

    # This is temporary until https://github.com/octue/octue-sdk-python/pull/205 is merged - then it should be able to
    # be dealt with by the `finalise` method below.
    analysis.logger.info(f"Attempting to save output to {output_cloud_path}.")
    output_file.to_cloud(project_name=os.environ["PROJECT_NAME"], cloud_path=output_cloud_path)
    output_file.path = output_cloud_path
    analysis.logger.info("Output saved.")


def _log_lines_from_stream(stream, logger):
    with stream:
        for line in iter(stream.readline, b''):
            logger.info(line.decode().strip())
