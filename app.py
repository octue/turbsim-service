import datetime
import os
import re
import subprocess
import tempfile

from octue.cloud import storage
from octue.resources import Datafile


FLOAT_REGEX = re.compile("\w*\d+[\.\d+]?\w+")


def run(analysis):
    start_datetime = datetime.datetime.now()

    with tempfile.TemporaryDirectory() as temporary_directory:
        input_path = os.path.join(temporary_directory, "TurbSim.inp")

        analysis.logger.debug("Attempting to update input TurbSim.inp file with input values.")

        with open(input_path, "w") as f:
            f.writelines(
                update_turbsim_input_file(
                    reference_height=analysis.input_values["reference_height"],
                    wind_speed=analysis.input_values["wind_speed"]
                )
            )

        analysis.logger.info("Starting turbulence simulation.")
        subprocess.run(["turbsim", input_path])
        analysis.logger.info("Finished turbulence simulation.")

        output = Datafile(path=os.path.join(temporary_directory, "TurbSim.bts"), labels=["turbsim"])
        output_cloud_path = storage.path.generate_gs_path(os.environ["BUCKET_NAME"], f"TurbSim-{start_datetime}.bts")

        analysis.logger.info(f"Attempting to save output to {output_cloud_path}.")
        output.to_cloud(project_name=os.environ["PROJECT_NAME"], cloud_path=output_cloud_path)
        analysis.logger.info("Output saved.")

    analysis.output_values = ["It worked!"]


def update_turbsim_input_file(reference_height, wind_speed):
    new_lines = []

    with open("/app/data/TurbSim.inp") as f:
        for line in f.readlines():

            if "RefHt" in line:
                line = FLOAT_REGEX.sub(str(reference_height), line)

            if "URef" in line:
                line = FLOAT_REGEX.sub(str(wind_speed), line)

            new_lines.append(line)

    return new_lines
