# setup.py
from setuptools import setup, find_packages

setup(
    name="network_simulator",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'networkx>=3.1',
        'matplotlib>=3.5.2',
        'numpy>=1.21.0',
    ],
)