import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="jitools",
    version="1.1.1",
    license="GNU GPLv3",
    author="M.O. Abbott",
    author_email="moab_bot@protonmail.com",
    description="a Python-based set of utilities for just intonation (JI) pitch and pitch collection research and analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/moab-bot/jitools",
    project_urls={
        "Source": "https://github.com/moab-bot/jitools",
        "Bug Tracker": "https://github.com/moab-bot/jitools/issues",
        "Changelog": "https://github.com/moab-bot/jitools/blob/master/CHANGELOG.md",
    },
    keywords=[
        "just intonation",
        "microtonal",
        "music theory",
        "pitch",
        "ratio",
        "tuning",
        "Helmholtz-Ellis",
        "HEJI",
        "harmonic distance",
        "enharmonic",
    ],
    packages=setuptools.find_packages(),
    package_data={
        "jitools": ["resources/*.csv"]
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Education",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Scientific/Engineering :: Mathematics",
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