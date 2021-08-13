from setuptools import find_packages, setup

from jsonbender import __version__

setup(
    name="jsonbender2",
    version=__version__,
    description="Library for transforming JSON data between different formats.",
    author="Roman Zimmermann",
    author_email="torotil@gmail.com",
    url="https://github.com/moreonion/jsonbender",
    download_url="https://codeload.github.com/moreonion/jsonbender/tar.gz/" + __version__,
    keywords=["dsl", "edsl", "json"],
    packages=["jsonbender"],
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
