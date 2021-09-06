import os
import re
import subprocess
import tempfile


FLOAT_REGEX = re.compile("\w*\d+[\.\d+]?\w+")


def run(analysis):
    with tempfile.TemporaryDirectory() as temporary_directory:
        input_path = os.path.join(temporary_directory, "TurbSim.inp")

        with open(input_path, "w") as f:
            f.writelines(
                create_turbsim_file_contents(
                    reference_height=analysis.input_values["reference_height"],
                    wind_speed=analysis.input_values["wind_speed"]
                )
            )

        subprocess.run(["turbsim", input_path])

    analysis.output_values = ["It worked!"]


def create_turbsim_file_contents(reference_height, wind_speed):
    new_lines = []

    with open("/app/data/TurbSim.inp") as f:
        for line in f.readlines():

            if "RefHt" in line:
                line = FLOAT_REGEX.sub(str(reference_height), line)

            if "URef" in line:
                line = FLOAT_REGEX.sub(str(wind_speed), line)

            new_lines.append(line)

    return new_lines
