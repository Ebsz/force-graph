import setuptools
from setuptools import setup

setup(
    name="force-graph",
    version="0.1.0",
    author="Einar Sønju",
    install_requires = [
        "pygame"
    ],
    description="Force-directed graph drawing",
    packages = setuptools.find_packages(),
)
