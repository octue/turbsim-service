from setuptools import setup


setup(
    name="turbsim-service",
    version="0.1.0",
    author="cortadocodes <cortado.codes@protonmail.com>",
    py_modules=["app"],
    install_requires=[
        "coolname>=1.1,<2",
        "octue @ https://github.com/octue/octue-sdk-python/archive/fix/validate-output-location-outside-of-twine.zip",
    ],
)
