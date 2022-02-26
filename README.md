# Description

This package is one of the implementation available in the fsspec module. 

It can be used alone, or dask and intake by indicating the  protocol in the path file:
```
dropbox://file_path
```
Small nicety : file_path in dropbox needs to start at the root "/folder1/folder2/etc." which means your path when using the
protocol identifier should look like this : 
```
dropbox:///folder1/folder2/etc
```
Yes, with three /// ! What happen if not, for some reasons the dropbox api will remove everything before the first / 
in the path keep only what is after.

It can also be used directly from the fsspec module to download and upload files in the github account.

The upload part is using the dropbox API.

The download part is using the dropbox API to create a temporary link and then used the already existing webhdfs implementation.
Caching (see fsspec module) is available in that case.

Documentation of the fsspec module : https://github.com/intake/filesystem_spec/blob/master/docs/source/features.rst

## Install

```
pip install dropboxdrivefs
```

### How to obtain your access token? 

https://blogs.dropbox.com/developers/2014/05/generate-an-access-token-for-your-own-account/

## Thanks

Thanks to martindurant and TomAugspurger for the help to developping this implementation
see info about the development: https://github.com/intake/filesystem_spec/pull/207
