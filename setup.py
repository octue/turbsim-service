from setuptools import setup


setup(
    name="turbsim-service",
    version="0.1.1",
    author="cortadocodes <cortado.codes@protonmail.com>",
    py_modules=["app"],
    install_requires=[
        "coolname>=1.1,<2",
        "octue @ https://github.com/octue/octue-sdk-python/archive/enhancement/automatically-upload-output-datasets-to-output-location.zip",
    ],
)
