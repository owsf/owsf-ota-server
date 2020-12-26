import io

from setuptools import find_packages
from setuptools import setup

#with io.open("README.rst", "rt", encoding="utf8") as f:
#    readme = f.read()

setup(
    name="iota",
    version="1.0.0",
    url="http://flask.pocoo.org/docs/tutorial/",
    license="BSD",
    maintainer="Tillmann Heidsieck",
    maintainer_email="theidsieck@leenox.de",
    description="Simple server for updating and IOT devices",
    long_description="",#readme,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=["flask", "flask_api", "packaging", "nacl", "json"],
    extras_require={"test": ["pytest", "coverage"]},
)
