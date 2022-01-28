from os import path

from setuptools import setup

here = path.abspath(path.dirname(__file__))
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="dropboxdrivefs",
    version="1.3.1",
    packages=["dropboxdrivefs"],
    install_requires=["fsspec", "requests", "dropbox"],
    author="Marine Chaput",
    author_email="marine.chaput@hotmail.fr",
    url = "https://github.com/fsspec/dropboxdrivefs",
    description="Dropbox implementation for fsspec module",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",

    ],
    python_requires=">=3.5",
    license="BSD",
    zip_safe=False,
)
