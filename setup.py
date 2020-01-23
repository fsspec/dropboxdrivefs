from setuptools import setup
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
     name="dropboxdrivefs",
     version="1.0.3",
     packages=["dropboxdrivefs"],
     install_requires=[
                       "fsspec",
                       "requests",
                       "dropbox",
                       ],
     author="Marine Chaput",
     author_email="marine.chaput@hotmail.fr",
     description="Dropbox implementation for fsspec module",
     long_description = long_description,
     long_description_content_type = 'text/markdown',
     classifiers=[
                "Development Status :: 3 - Alpha",
                "Intended Audience :: Developers",
                "License :: OSI Approved :: BSD License",
                "Operating System :: OS Independent",
                "Programming Language :: Python :: 3.5",
                "Programming Language :: Python :: 3.6",
                "Programming Language :: Python :: 3.7",
                ],
     python_requires=">=3.5",
     license="BSD",
     zip_safe=False,
     )
