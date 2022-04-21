from setuptools import setup


setup(
    name="turbsim-service",
    version="0.1.0",
    py_modules=["app"],
    install_requires=[
        "octue @ https://github.com/octue/octue-sdk-python/archive/fix/miscellaneous-fixes.zip",
    ],
)
