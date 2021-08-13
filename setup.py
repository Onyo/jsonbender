from setuptools import find_packages, setup

from jsonbender import __version__

setup(
    name="JSONBender",
    version=__version__,
    description="Library for transforming JSON data between different formats.",
    author="Elias Tandel",
    author_email="backend@onyo.com",
    url="https://github.com/Onyo/jsonbender",
    download_url="https://codeload.github.com/Onyo/jsonbender/tar.gz/" + __version__,
    keywords=["dsl", "edsl", "json"],
    packages=["jsonbender"],
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5",
    ],
)
