# Description

This package is a complement to the Intake project. It is one of the implementation which can be used from the fsspec module.

Be careful: There are for the moment at least no unity/integration tests on this implementation (alpha version).

How to use in an intake catalog :

    - url_path: dropbox://file_path
    - storage_options = {'token':''} <-- app token access generated from your dropbox account

Documentation of the intake module: https://intake.readthedocs.io/en/latest/quickstart.html

It can also be used directly from the fsspec module to download and upload files in the github account.

The upload part is using the dropbox API.

The download part is using the dropbox API to create a temporary link and then used the already existing https implementation.

Caching (see fsspec module) is available in that case.

Documentation of the fsspec module : https://github.com/intake/filesystem_spec/blob/master/docs/source/features.rst

## Install

```bash
pip install dropboxdrivefs
```
or
```bash
conda install -c conda-forge dropboxdrivefs
```

## Thanks

Thanks to martindurant and TomAugspurger for the help to developping this implementation
see info about the development: https://github.com/intake/filesystem_spec/pull/207
