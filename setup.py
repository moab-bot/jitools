import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="jitools",
    version="1.0.0",
    license="GNU GPLv3",
    author="M.O. Abbott",
    author_email="moab_bot@protonmail.com",
    description="a Python-based set of utilities for just intonation (JI) pitch and pitch collection research and analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/moab-bot/jitools",
    download_url = 'https://github.com/moab-bot/jitools/archive/v1.0.0.tar.gz',
    packages=setuptools.find_packages(),
    package_data={
    "jitools": ["resources/*.csv"]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10',
)