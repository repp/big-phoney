import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="big_phoney",
    version="1.0.0",
    author="Ryan Epp",
    author_email="hey@ryanepp.com",
    description="Get phonetic spellings and syllable counts for any english word. " +
                "Works with made up and non-dictionary words.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/repp/big-phoney",
    packages=setuptools.find_packages(exclude=['dev', 'test']),
    package_data={'': ['data/*']},
    include_package_data=True,
    install_requires=['numpy', 'keras', 'inflect', 'h5py'],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ),
)
