import datetime
import os
import subprocess

from octue.cloud import storage
from octue.resources import Datafile


def run(analysis):
    start_datetime = datetime.datetime.now()
    input_file = list(analysis.input_manifest.get_dataset("turbsim_input").files)[0]

    analysis.logger.info("Starting turbulence simulation.")
    subprocess.run(["turbsim", input_file.get_local_path()])
    analysis.logger.info("Finished turbulence simulation.")

    output_file = Datafile(path="TurbSim.bts", labels=["turbsim"])
    analysis.output_manifest.get_dataset("turbsim_output").add(output_file)

    output_cloud_path = storage.path.generate_gs_path(
        os.environ["BUCKET_NAME"],
        "turbsim",
        f"TurbSim-{start_datetime.isoformat().replace(':', '-')}.bts"
    )

    # This is temporary until https://github.com/octue/octue-sdk-python/pull/205 is merged - then it should be able to
    # be dealt with by the `finalise` method below.
    analysis.logger.info(f"Attempting to save output to {output_cloud_path}.")
    output_file.to_cloud(project_name=os.environ["PROJECT_NAME"], cloud_path=output_cloud_path)
    analysis.logger.info("Output saved.")

    analysis.finalise()
