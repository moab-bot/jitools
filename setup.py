import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="jitools",
    version="0.2",
    license="GNU GPLv3",
    author="M.O. Abbott",
    author_email="moab_bot@protonmail.com",
    description="a Python-based set of utilities for just intonation (JI) pitch and pitch collection research and analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/moab-bot/jitools",
    download_url = 'https://github.com/moab-bot/jitools/archive/v_02.tar.gz',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8.5',
)
