from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in obarcode/__init__.py
from obarcode import __version__ as version

setup(
	name="obarcode",
	version=version,
	description="Barcode for Retail application",
	author="Lovin Maxwell",
	author_email="lovinmaxwell@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
