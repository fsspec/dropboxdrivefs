# Description

This package is one of the implementation available in the fsspec module. It can be used with alone, or dask and intake by indicating the  protocol in the path file:
```
dropbox://file_path
```

Be careful: There are for the moment at least no unity/integration tests on this implementation (alpha version).

It can also be used directly from the fsspec module to download and upload files in the github account.

The upload part is using the dropbox API.

The download part is using the dropbox API to create a temporary link and then used the already existing https implementation.
Caching (see fsspec module) is available in that case.

Documentation of the fsspec module : https://github.com/intake/filesystem_spec/blob/master/docs/source/features.rst

## Install

```
pip install dropboxdrivefs
```

## Thanks

Thanks to martindurant and TomAugspurger for the help to developping this implementation
see info about the development: https://github.com/intake/filesystem_spec/pull/207
