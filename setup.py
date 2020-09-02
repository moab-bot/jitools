import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="jitools",
    packages = ['jitools']
    version="0.1",
    license="GNU GPLv3",
    author="M.O. Abbott",
    author_email="moab_bot@protonmail.com",
    description="utilities for just intonation pitch and pitch collection analysis",
    url="https://github.com/moab-bot/jitools",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU GPLv3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
