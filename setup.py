from setuptools import setup


setup(
    name="turbsim-service",
    version="0.2.0",
    author="Marcus Lugg <marcus@octue.com>",
    py_modules=["app"],
    install_requires=[
        "coolname>=1.1,<2",
        "octue==0.50.1",
    ],
)
