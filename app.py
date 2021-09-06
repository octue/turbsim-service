import re
import subprocess

FLOAT_REGEX = re.compile("\w*\d+[\.\d+]?\w+")


def run(analysis):
    input_file = analysis.input_manifest.get_dataset("turbsim-input").files.pop()
    input_path = input_file.get_local_path()

    with open(input_path, "w") as f:
        f.writelines(
            create_turbsim_file_contents(
                reference_height=analysis.input_values["reference_height"],
                wind_speed=analysis.input_values["wind_speed"]
            )
        )

    subprocess.run(["turbsim", input_path])


def create_turbsim_file_contents(reference_height, wind_speed):
    new_lines = []

    with open("/app/TurbSim.inp") as f:
        for line in f.readlines():

            if "RefHt" in line:
                line = FLOAT_REGEX.sub(reference_height, line)

            if "URef" in line:
                line = FLOAT_REGEX.sub(wind_speed, line)

            new_lines.append(line)

    return new_lines
