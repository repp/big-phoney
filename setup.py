import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="big_phoney",
    version="0.0.1",
    author="Ryan Epp",
    author_email="hey@ryanepp.com",
    description="Get phonetic spellings and syllable counts for any english word!",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/repp/big-phoney",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved ::  GNU GPL v3.0 License",
        "Operating System :: OS Independent",
    ),
)
