#
# (C) Copyright 2021 Tillmann Heidsieck
#
# SPDX-License-Identifier: MIT
#
from setuptools import find_packages
from setuptools import setup


setup(
    name="iota",
    setup_requires=['setuptools-git-versioning'],
    version_config=True,
    url="https://github.com/junkdna/esp8266-control-server",
    license="BSD",
    maintainer="Tillmann Heidsieck",
    maintainer_email="theidsieck@leenox.de",
    description="Simple server for updating and IOT devices",
    long_description="",  # TODO,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=["flask", "flask_api", "PyNaCl"],
    extras_require={"test": ["pytest", "coverage"]},
)
