from setuptools import setup

setup(
     name="dropboxdrivefs",
     version="1.0.0",
     packages=["dropboxdrivefs"],
     install_requires=[
                       "fsspec",
                       "requests",
                       "dropbox",
                       ],
     author="Marine Chaput",
     author_email="marine.chaput@hotmail.fr",
     description="Dropbox implementation for Intake module",
     classifiers=[
                "Development Status :: 4 - Beta",
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
